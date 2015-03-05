# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
from collections import defaultdict
import logging

from ete2.tools.phylobuild_lib.utils import (DEBUG, GLOBALS, SeqGroup, tobool, sec2time, read_time_file,
                                  _max, _min, _mean, _std, _median)
from ete2.tools.phylobuild_lib.apps import APP2CLASS
from ete2.tools.phylobuild_lib import task as all_tasks
from ete2.tools.phylobuild_lib import db
from ete2.tools.phylobuild_lib.errors import ConfigError, DataError, TaskError
from ete2.tools.phylobuild_lib.master_task import register_task_recursively, isjob

log = logging.getLogger("main")
                
class IterConfig(dict):
    def __init__(self, conf, wkname, size, seqtype):
        """Special dict to extract the value of each parameter given
         the properties of a task: size and seqtype. 
        """
        dict.__init__(self, conf[wkname])
       
        self.conf = conf
        self.seqtype = seqtype
        self.size = size
        self['npr_wf_type'] = conf['_npr'].get('wf_type', None)
        self['npr_workflows'] = conf['_npr'].get('workflows', [])
        self['switch_aa_similarity'] = conf['_npr'].get('nt_switch_thr', 1.0)
        if conf[wkname]["_app"] == self['npr_wf_type']:
            self['max_iters'] = conf['_npr'].get('max_iters', 1)  # 1 = no npr by default!
        else:
            self['max_iters'] = 1
            
        self['_tree_splitter'] = '@default_tree_splitter'
        
        # if max_outgroup size is 0, means that no rooting is done in child NPR trees
        self['use_outgroup'] = conf['default_tree_splitter']['_max_outgroup_size'] != 0
        
    def __getattr__(self, v):
        try:
            return dict.__getattr__(self, v)
        except AttributeError:
            return self.__getitem__(v)

    def __getitem__(self, v):
        # Automatically switch among nt and aa bindings
        if v in set(["tree_builder", "aligner", "model_tester",
                     "alg_cleaner"]):
            v = "%s_%s" %(self.seqtype, v)
        
        try:
            value = dict.__getitem__(self, "_%s" %v)
        except KeyError, e:
            return dict.__getitem__(self, v)
        else:
            # If list, let's take the correct element
            if type(value) == list:
                raise ValueError('This should not occur. Please report the error!')
                
            if type(value) != str:
                return value
            elif value.lower() == "none":
                return None, None
            elif value.startswith("@"):
                classname = APP2CLASS[self.conf[value[1:]]["_app"]]
                return value[1:], getattr(all_tasks, classname) 
            else:
                return value
                
def process_new_tasks(task, new_tasks, conf):
    # Basic registration and processing of newly generated tasks
    parent_taskid = task.taskid if task else None
    for ts in new_tasks:
        log.log(22, "Registering new task: %s", ts)
        register_task_recursively(ts, parentid=parent_taskid)
        conf["_nodeinfo"][ts.nodeid].setdefault("tasks", []).append(ts)
        # sort task by nodeid
        #GLOBALS["nodeinfo"][ts.nodeid].setdefault("tasks", []).append(ts)
        if task:
            # Clone processor, in case tasks belong to a side workflow
            ts.task_processor = task.task_processor
            ts.configid = task.configid
            ts.threadid = task.threadid
            ts.main_tree = task.main_tree
            # NPR allows switching the workflow associated to new tasks, if so,
            # child task should have a target_wkname attribute already,
            # otherwise we assume the same parent workflow
            if not hasattr(ts, "target_wkname"):
                ts.target_wkname = task.target_wkname
            
        #db.add_runid2task(ts.threadid, ts.taskid)

def inc_iternumber(threadid):
    current_iter = get_iternumber(threadid)
    GLOBALS["threadinfo"][threadid]["last_iter"] = current_iter + 1
    return current_iter + 1

def get_iternumber(threadid):
    return GLOBALS["threadinfo"][threadid].setdefault("last_iter", 1)

def get_identity(fname): 
    s = SeqGroup(fname)
    seqlen = len(s.id2seq.itervalues().next())
    ident = list()
    for i in xrange(seqlen):
        states = defaultdict(int)
        for seq in s.id2seq.itervalues():
            if seq[i] != "-":
                states[seq[i]] += 1
        values = states.values()
        if values:
            ident.append(float(max(values))/sum(values))
    return (_max(ident), _min(ident), 
            _mean(ident), _std(ident))
    

def get_seqs_identity(alg, seqs):
    ''' Returns alg statistics regarding a set of sequences'''
    seqlen = len(alg.get_seq(seqs[0]))
    ident = list()
    for i in xrange(seqlen):
        states = defaultdict(int)
        for seq_id in seqs:
            seq = alg.get_seq(seq_id)
            if seq[i] != "-":
                states[seq[i]] += 1
        values = states.values()
        if values:
            ident.append(float(max(values))/sum(values))
    return (_max(ident), _min(ident), 
            _mean(ident), _std(ident))

    
def split_tree(task_tree_node, task_outgroups, main_tree, alg_path, npr_conf, threadid, target_cladeids):
    """Browses a task tree from root to leaves and yields next
    suitable nodes for NPR iterations. Each yielded node comes with
    the set of target and outgroup tips. 
    """


    def processable_node(_n):
        """This an internal function that returns true if a given node
        is suitable for a NPR iteration. It can be used as
        "is_leaf_fn" when traversing a tree.

        Note that this function uses several variables which change within the
        split_tree function, so must be kept within its namespace.

        """
        is_leaf = False
        for wkname, wkfilter in npr_conf.npr_workflows:
            # if node is not in the targets or does not meet size filters, skip
            # workflow
            if _n is master_node or \
               (_TARGET_NODES and _n not in _TARGET_NODES) or \
               (target_cladeids and _n.cladeid not in target_cladeids) or \
               len(n2content[_n]) < max(wkfilter.get("min_size", 3), 3) or \
               ("max_size" in wkfilter and len(n2content[_n]) > wkfilter["max_size"]):
                continue

            # If seq_sim filter used, calculate node stats
            if ALG and ("min_seq_sim" in wkfilter or "max_seq_sim" in wkfilter): 
                if not hasattr(_n, "seqs_mean_ident"):
                    log.log(20, "Calculating node sequence stats...")
                    mx, mn, avg, std = get_seqs_identity(ALG,
                                                         [__n.name for __n in n2content[_n]])
                    _n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
                                    seqs_mean_ident=avg, seqs_std_ident=std)
                    log.log(20, "mx=%s, mn=%s, avg=%s, std=%s" %(mx, mn, avg, std))
                    

                if _n.seqs_mean_ident < wkfilter["min_seq_sim"]:
                    continue
                    
                if _n.seqs_mean_ident > wkfilter["max_seq_sim"]:
                    continue

                    
            else:
                _n.add_features(seqs_max_ident=None, seqs_min_ident=None,
                                seqs_mean_ident=None, seqs_std_ident=None)

            if "min_support" in wkfilter:
                # If we are optimizing only lowly supported nodes, and nodes are
                # optimized without an outgroup, our target node is actually the
                # parent of lowly supported nodes. Therefore, I check if support
                # is low in children nodes, and return this node if so.
                if not npr_conf.use_outgroup:
                    if not [_ch for _ch in _n.children if _ch.support <= wkfilter["min_support"]]:
                        continue
                # Otherwise, just skip the node if it above the min support
                elif _n.support > wkfilter["min_support"]:
                    continue

            # At this point, node passed all filters of this workflow were met,
            # so it can be optimized
            is_leaf = True
            _n._target_wkname = wkname
            break
                
        return is_leaf
        
    log.log(20, "Loading tree content...")
    n2content = main_tree.get_cached_content()
    if alg_path:
        log.log(20, "Loading associated alignment to check seq. similarity")
        raw_alg = db.get_task_data(*alg_path.split("."))
        ALG = SeqGroup(raw_alg)
    else:
        ALG = None

    log.log(20, "Finding next NPR nodes...")
    # task_tree_node is actually a node in main_tree, since it has been
    # already merged
    trees_to_browse = [task_tree_node]
    npr_nodes = 0
    # loads current tree content, so we can check not reconstructing exactly the
    # same tree
    tasktree_content = set([leaf.name for leaf in n2content[task_tree_node]]) | set(task_outgroups)
    while trees_to_browse: 
        master_node = trees_to_browse.pop()

        # if custom taxa levels are defined as targets, find them in this
        # subtree
        _TARGET_NODES = defaultdict(list) # this container is used by
                                          # processable_node function
        opt_levels = GLOBALS[threadid].get('_optimized_levels', None)
        if opt_levels is not None:
            # any descendant of the already processed node is suitable for
            # selection. If the ancestor of level-species is on top of the
            # task_tree_node, it will be discarded
            avail_nodes = set(master_node.get_descendants())
            for lin in opt_levels:
                sp2lin, lin2sp = GLOBALS["lineages"]
                optimized, strict_monophyly = opt_levels[lin]
                if not optimized:
                    ancestor = main_tree.get_common_ancestor(*lin2sp[lin])
                    if ancestor in avail_nodes:
                        # check that the node satisfies level monophyly config
                        ancestor_content = set([x.name for x in n2content[ancestor]])
                        if not strict_monophyly or lin2sp[lin] == ancestor_content:
                            _TARGET_NODES[ancestor].append(lin)
                        elif strict_monophyly:
                            log.log(26, "Discarding not monophyletic level @@11:%s@@1:" %lin)
                    else:
                        log.log(26, "Discarding upper clade @@11:%s@@1:" %lin)
                        
        for node in master_node.iter_leaves(is_leaf_fn=processable_node):
            if opt_levels:
                log.log(28, "Trying to optimizing custom tree level: @@11:%s@@1:" %_TARGET_NODES[node])
                for lin in _TARGET_NODES[node]:
                    # Marks the level as optimized, so is not computed again
                    opt_levels[lin][0] = True
           
            log.log(28, "Found possible target node of size %s branch support %f" %(len(n2content[node]), node.support))
            log.log(28, "First suitable workflow: %s" %(node._target_wkname))

            # Finds best outgroup for the target node
            if npr_conf.use_outgroup:
                splitterconfname, _ = npr_conf.tree_splitter
                splitterconf = GLOBALS[threadid][splitterconfname]
                #seqs, outs = select_outgroups(node, n2content, splitterconf)
                #seqs, outs = select_closest_outgroup(node, n2content, splitterconf)
                seqs, outs = select_sister_outgroup(node, n2content, splitterconf)
            else:
                seqs = set([_i.name for _i in n2content[node]])
                outs = set()
                
                
            if seqs | outs == tasktree_content:
                log.log(26, "Discarding target node of size %s, due to identity with its parent node" %len(n2content[node]))
                #print tasktree_content
                #print seqs
                #print outs
                trees_to_browse.append(node)
            else:
                npr_nodes += 1
                yield node, seqs, outs, node._target_wkname
    log.log(28, "%s nodes will be optimized", npr_nodes)

def get_next_npr_node(threadid, ttree, task_outgroups, mtree, alg_path, npr_conf, target_cladeids=None):
    current_iter = get_iternumber(threadid)
    if npr_conf.max_iters and current_iter >= npr_conf.max_iters:
        log.warning("Maximum number of iterations reached!")
        return

    if not npr_conf.npr_workflows:
        log.log(26, "NPR is disabled")
        return
        
    for node, seqs, outs, wkname in split_tree(ttree, task_outgroups, mtree, alg_path,
                                               npr_conf, threadid, target_cladeids):
        if npr_conf.max_iters and current_iter < npr_conf.max_iters:
            log.log(28,
                    "@@16:Target node of size %s with %s outgroups marked for a new NPR iteration!@@1:" %(
                        len(seqs),
                        len(outs)))
            # Yield new iteration
            inc_iternumber(threadid)
            yield node, seqs, outs, wkname
                     
def select_closest_outgroup(target, n2content, splitterconf):
    def sort_outgroups(x,y):
        r = cmp(x[1], y[1]) # closer node
        if r == 0:
            r = -1 * cmp(len(n2content[x[0]]), len(n2content[y[0]])) # larger node
            if r == 0:
                r = -1 * cmp(x[0].support, y[0].support) # higher supported node
                if r == 0:
                    return cmp(x[0].cladeid, y[0].cladeid) # by content name
                else:
                    return r
            else:
                return r
        else:
            return r
    
    if not target.up:
        raise TaskError(None, "Cannot select outgroups for the root node!")
        
    # Prepare cutoffs
    out_topodist = tobool(splitterconf["_outgroup_topology_dist"])
    max_outgroup_size = max(int(float(splitterconf["_max_outgroup_size"]) * len(n2content[target])), 1)
    out_min_support = float(splitterconf["_min_outgroup_support"])

    log.log(26, "Max outgroup size allowed %d" %max_outgroup_size)
    
    # Gets a list of outside nodes an their distance to current target node
    n2targetdist = distance_matrix_new(target, leaf_only=False,
                                               topology_only=out_topodist)

    valid_nodes = sorted([(node, ndist) for node, ndist in n2targetdist.iteritems()
                          if not(n2content[node] & n2content[target])
                          and node.support >= out_min_support 
                          and len(n2content[node])<=max_outgroup_size],
                         sort_outgroups)
    if valid_nodes:
        best_outgroup = valid_nodes[0][0]
    else:
        print '\n'.join(sorted(["%s Size:%d Dist:%f Supp:%f" %(node.cladeid, len(n2content[node]), ndist, node.support)
                                for node, ndist in n2targetdist.iteritems()],
                               sort_outgroups))
        raise TaskError(None, "Could not find a suitable outgroup!")

    log.log(20,
            "Found possible outgroup Size:%d Distance:%f Support:%f",
            len(n2content[best_outgroup]), n2targetdist[best_outgroup], best_outgroup.support)
   
    log.log(20, "Supports: %0.2f (children=%s)", best_outgroup.support,
            ','.join(["%0.2f" % ch.support for ch in
                      best_outgroup.children]))
    
    log.log(24, "best outgroup topology:\n%s", best_outgroup)
    #print target
    #print target.get_tree_root()
   
    seqs = [n.name for n in n2content[target]]
    outs = [n.name for n in n2content[best_outgroup]]
    
    return set(seqs), set(outs)

            
def select_sister_outgroup(target, n2content, splitterconf):
    def sort_outgroups(x,y):
        r = cmp(x[1], y[1]) # closer node
        if r == 0:
            r = -1 * cmp(len(n2content[x[0]]), len(n2content[y[0]])) # larger node
            if r == 0:
                r = -1 * cmp(x[0].support, y[0].support) # higher supported node
                if r == 0:
                    return cmp(x[0].cladeid, y[0].cladeid) # by content name
                else:
                    return r
            else:
                return r
        else:
            return r
    
    if not target.up:
        raise TaskError(None, "Cannot select outgroups for the root node!")
        
    # Prepare cutoffs
    out_topodist = tobool(splitterconf["_outgroup_topology_dist"])
    out_min_support = float(splitterconf["_min_outgroup_support"])
    if splitterconf["_max_outgroup_size"].strip().endswith("%"):
        max_outgroup_size = max(1, round((float(splitterconf["_max_outgroup_size"].strip("%"))/100) * len(n2content[target])))
        log.log(26, "Max outgroup size allowed %s = %d" %(splitterconf["_max_outgroup_size"], max_outgroup_size))
    else:
        max_outgroup_size = max(1, int(splitterconf["_max_outgroup_size"]))
        log.log(26, "Max outgroup size allowed %d" %max_outgroup_size)
    
    # Gets a list of outside nodes an their distance to current target node
    n2targetdist = distance_matrix_new(target, leaf_only=False,
                                               topology_only=out_topodist)

    sister_content = n2content[target.get_sisters()[0]]
    
    valid_nodes = sorted([(node, ndist) for node, ndist in n2targetdist.iteritems()
                          if not(n2content[node] & n2content[target])
                          and n2content[node].issubset(sister_content)
                          and node.support >= out_min_support 
                          and len(n2content[node])<=max_outgroup_size],
                         sort_outgroups)
    if valid_nodes:
        best_outgroup = valid_nodes[0][0]
    else:
        print '\n'.join(sorted(["%s Size:%d Distance:%f Support:%f" %(node.cladeid, len(n2content[node]), ndist, node.support)
                                for node, ndist in n2targetdist.iteritems()],
                               sort_outgroups))
        raise TaskError(None, "Could not find a suitable outgroup!")

    log.log(20,
            "Found possible outgroup Size:%d Dist:%f Supp:%f",
            len(n2content[best_outgroup]), n2targetdist[best_outgroup], best_outgroup.support)
   
    log.log(20, "Supports: %0.2f (children=%s)", best_outgroup.support,
            ','.join(["%0.2f" % ch.support for ch in
                      best_outgroup.children]))
    
    log.log(24, "best outgroup topology:\n%s", best_outgroup)
    #print target
    #print target.get_tree_root()
   
    seqs = [n.name for n in n2content[target]]
    outs = [n.name for n in n2content[best_outgroup]]
    
    return set(seqs), set(outs)

            



      
def select_outgroups(target, n2content, splitterconf):
    """Given a set of target sequences, find the best set of out
    sequences to use. Several ways can be selected to find out
    sequences:
    """
    
    name2dist = {"min": _min, "max": _max,
                 "mean":_mean, "median":_median}
  
    
    #policy = splitterconf["_outgroup_policy"]  # node or leaves
    out_topodist = tobool(splitterconf["_outgroup_topology_dist"])
    optimal_out_size = int(splitterconf["_max_outgroup_size"])
    #out_distfn = splitterconf["_outgroup_dist"]
    out_min_support = float(splitterconf["_outgroup_min_support"])
    
    if not target.up:
        raise TaskError(None, "Cannot select outgroups for the root node!")
    if not optimal_out_size:
        raise TaskError(None, "You are trying to set 0 outgroups!")

    # Gets a list of outside nodes an their distance to current target node
    n2targetdist = distance_matrix_new(target, leaf_only=False,
                                               topology_only=out_topodist)

    #kk, test = distance_matrix(target, leaf_only=False,
    #                       topology_only=False)

    #for x in test:
    #    if test[x] != n2targetdist[x]:
    #        print x
    #        print test[x],  n2targetdist[x]
    #        print x.get_distance(target)
    #        raw_input("ERROR!")
        
    score = lambda _n: (_n.support,
                        #len(n2content[_n])/float(optimal_out_size),
                        1 - (abs(optimal_out_size - len(n2content[_n])) / float(max(optimal_out_size, len(n2content[_n])))), # outgroup size
                        1 - (n2targetdist[_n] / max_dist) #outgroup proximity to target
                        ) 
    
    def sort_outgroups(x,y):
        score_x = set(score(x))
        score_y = set(score(y))
        while score_x:
            min_score_x = min(score_x)

            v = cmp(min_score_x, min(score_y))
            if v == 0:
                score_x.discard(min_score_x)
                score_y.discard(min_score_x)
            else:
                break
        # If still equal, sort by cladid to maintain reproducibility
        if v == 0:
            v = cmp(x.cladeid, y.cladeid)
        return v
        
    #del n2targetdist[target.get_tree_root()]
    max_dist = max(n2targetdist.values())
    valid_nodes = [n for n in n2targetdist if \
                       not n2content[n] & n2content[target] and
                       n.support >= out_min_support]
    if not valid_nodes:
        raise TaskError(None, "Could not find a suitable outgroup (min_support=%s)"\
                      %out_min_support)
    valid_nodes.sort(sort_outgroups, reverse=True)
    best_outgroup = valid_nodes[0]
    seqs = [n.name for n in n2content[target]]
    outs = [n.name for n in n2content[best_outgroup]]
   
    log.log(20,
            "Found possible outgroup of size %s: score (support,size,dist)=%s",
            len(outs), score(best_outgroup))
   
    log.log(20, "Supports: %0.2f (children=%s)", best_outgroup.support,
            ','.join(["%0.2f" % ch.support for ch in
                      best_outgroup.children]))
    
    if DEBUG():
        root = target.get_tree_root()
        for _seq in outs:
            tar =  root & _seq
            tar.img_style["fgcolor"]="green"
            tar.img_style["size"] = 12
            tar.img_style["shape"] = "circle"
        target.img_style["bgcolor"] = "lightblue"
        NPR_TREE_STYLE.title.clear()
        NPR_TREE_STYLE.title.add_face( faces.TextFace("MainTree:"
            " Outgroup selection is mark in green. Red=optimized nodes ",
            fgcolor="blue"), 0)
        root.show(tree_style=NPR_TREE_STYLE)
        for _n in root.traverse():
            _n.img_style = None
        
    return set(seqs), set(outs)
        
def distance_matrix_new(target, leaf_only=False, topology_only=False):
    t = target.get_tree_root()
    real_outgroup = t.children[0]
    t.set_outgroup(target)
        
    n2dist = {target:0}
    for n in target.get_descendants("preorder"):
        n2dist[n] = n2dist[n.up] + (topology_only or n.dist)

    sister = target.get_sisters()[0]
    n2dist[sister] = (topology_only or sister.dist)+ (topology_only or target.dist)
    for n in sister.get_descendants("preorder"):
        n2dist[n] = n2dist[n.up] + (topology_only or n.dist)

    t.set_outgroup(real_outgroup)

    ## Slow Test. 
    # for n in t.get_descendants():
    #     if float(str(target.get_distance(n))) != float(str(n2dist[n])):
    #         print n
    #         print target.get_distance(n), n2dist[n]
    #         raw_input("ERROR")
    return n2dist


def assembly_tree(runid):
    task_nodes = db.get_runid_nodes(runid)
    task_nodes.reverse()
    
    main_tree = None
    iternumber = 1
    while task_nodes:
        cladeid, packtree, size = task_nodes.pop(-1)
        if not packtree:
            continue
        tree = db.decode(packtree)

        # print tree.dist
        # Restore original gene names
        for leaf in tree.iter_leaves():
            leaf.add_features(safename=leaf.name)
            leaf.name = leaf.realname
            
        if main_tree:
            # substitute node in main tree by the optimized one
            target_node = main_tree.search_nodes(cladeid=cladeid)[0]
            target_node.up.add_child(tree)
            target_node.detach()
        else:
            main_tree = tree

        iter_name = "Iter_%04d_%dseqs" %(iternumber, size)
        tree.add_features(iternumber=iternumber)
        iternumber += 1
    return main_tree, iternumber 
       
    
def get_cmd_log(task):
    cmd_lines = []
    if getattr(task, 'get_launch_cmd', None):
        launch_cmd = task.get_launch_cmd()
        tm_s, tm_e = read_time_file(task.time_file)
        cmd_lines.append([task.jobid, sec2time(tm_e - tm_s), task.jobname, launch_cmd])
    if getattr(task, 'jobs', None):
        for subtask in task.jobs:
            cmd_lines.extend(get_cmd_log(subtask))
    return cmd_lines
