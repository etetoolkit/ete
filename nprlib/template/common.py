from collections import defaultdict
import logging

import numpy

from nprlib.utils import DEBUG, GLOBALS, SeqGroup, tobool
from nprlib.apps import APP2CLASS
from nprlib import task as all_tasks
from nprlib import db
from nprlib.errors import ConfigError, DataError, TaskError
from nprlib.master_task import register_task_recursively

log = logging.getLogger("main")

CONFIG_SPECS = """
[npr]
max_iters = integer(minv=1)
switch_aa_similarity = float_list(minv=0.0, maxv=1.0)
max_seq_similarity = float_list(minv=0.0, maxv=1.0)
min_branch_support = float_list(minv=0, maxv=1)
min_npr_size = integer_list(minv=3)
tree_splitter = list()

[genetree]
max_seqs = correlative_integer_list(minv=0)
workflow = list()
npr = list()
tree_splitter = list()

[supermatrix]
max_seqs = correlative_integer_list(minv=0)
workflow = list()
npr = list()
"""

                
class IterConfig(dict):
    def __init__(self, conf, workflow, size, seqtype):
        """Special dict to extract the value of each parameter given
         the properties of a task: size and seqtype. 
        """
        dict.__init__(self, conf[workflow])
       
        self.conf = conf
        self.seqtype = seqtype
        self.size = size
        self.index = None
       
        index_slide = 0
        while self.index is None: 
            try:
                max_seqs = conf[workflow]["max_seqs"][index_slide]
            except IndexError:
                raise DataError("Target species [%d] has size not considered in current config file" %self.size)
            else:
                if self.size <= max_seqs:
                    self.index = index_slide
                else:
                    index_slide += 1
        # Updates the dictionary with the workflow application config
        appcfg = conf[workflow]['workflow'][self.index]
        if appcfg.startswith('@'):
            self.update(conf[appcfg[1:]])
        nprcfg = conf[workflow]['npr'][self.index]
        if nprcfg.startswith('@'):
            self.update(conf[nprcfg[1:]])
        elif nprcfg == 'none':
            self['max_iters'] = 1
            
        
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
            value = dict.__getitem__(self, v)
        except KeyError, e:
            return None
        else:
            # If list, let's take the correct element
            if type(value) == list:
                value = value[self.index]
                
            if type(value) != str:
                return value
            elif value.lower() == "none":
                return None, None
            elif value.startswith("@"):
                classname = APP2CLASS[self.conf[value[1:]]["_app"]]
                return value[1:], getattr(all_tasks, classname) 
            else:
                return value

def process_new_tasks(task, new_tasks):
    # Basic registration and processing of newly generated tasks
    parent_taskid = task.taskid if task else None
    for ts in new_tasks:
        log.log(22, "Registering new task: %s", ts)
        register_task_recursively(ts, parentid=parent_taskid)
        # sort task by nodeid
        GLOBALS["nodeinfo"][ts.nodeid].setdefault("tasks", []).append(ts)
        if task:
            # Clone processor, in case tasks belong to a side workflow
            ts.task_processor = task.task_processor
            ts.configid = task.configid
            ts.threadid = task.threadid
            ts.main_tree = task.main_tree
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
    return (numpy.max(ident), numpy.min(ident), 
            numpy.mean(ident), numpy.std(ident))
    

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
    return (numpy.max(ident), numpy.min(ident), 
            numpy.mean(ident), numpy.std(ident))

    
def split_tree(task_tree_node, task_outgroups, main_tree, alg_path, npr_conf, threadid, target_cladeids):
    """Browses a task tree from root to leaves and yields next
    suitable nodes for NPR iterations. Each yielded node comes with
    the set of target and outgroup tips. 
    """
    
    def processable_node(_n):
        """This an internal function that returns true if a given node
        is suitable for a NPR iteration. It can be used as
        "is_leaf_fn" when traversing a tree.

        Note that this function uses several variables which change
        within split_tree function.

        """
        _isleaf = False
        if len(n2content[_n]) >= npr_conf.min_npr_size \
           and _n is not master_node \
           and (not _TARGET_NODES or _n in _TARGET_NODES) \
           and (target_cladeids is None or _n.cladeid in target_cladeids):
                        
            if ALG and npr_conf.max_seq_simiarity < 1.0: 
                if not hasattr(_n, "seqs_mean_ident"):
                    log.log(20, "Calculating node sequence stats...")
                    mx, mn, avg, std = get_seqs_identity(ALG,
                                                         [__n.name for __n in n2content[_n]])
                    _n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
                                   seqs_mean_ident=avg, seqs_std_ident=std)
                    log.log(20, "mx=%s, mn=%s, avg=%s, std=%s" %(mx, mn, avg, std))
            else:
                _n.add_features(seqs_max_ident=None, seqs_min_ident=None,
                                seqs_mean_ident=None, seqs_std_ident=None)

            if _n.seqs_mean_ident >= npr_conf.max_seq_similarity:
                # If sequences are too similar, do not optimize
                # this node even if it is lowly supported
                _is_leaf = False
            elif not npr_conf.outgroup_size and npr_conf.min_branch_support <= 1.0:
                # If we are optimizing only lowly supported nodes,
                # and nodes are optimized without outgroup, our
                # target node is actually the parent of lowly
                # supported nodes. Therefore, I check if support
                # is low in children nodes, and return this node
                # if so.
                for _ch in _n.children:
                    if _ch.support <= npr_conf.min_branch_support:
                        _isleaf = True
                        break
            elif _n.support <= npr_conf.min_branch_support:
                # If sequences are different enough and node is
                # not well supported, optimize it. 
                _isleaf = True
            
        return _isleaf
        
    log.log(20, "Loading tree content...")
    n2content = main_tree.get_cached_content()
    if alg_path:
        log.log(20, "Loading associated alignment to check seq. similarity")
        raw_alg = db.get_task_data(*alg_path.split("."))
        ALG = SeqGroup(raw_alg)
    else:
        ALG = None
    #for n in task.task_tree_node.traverse(): 
    #    content = n2content[n]
    #    mx, mn, avg, std = get_seqs_identity(ALG, [node.name for node in content])
    #    n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
    #                   seqs_mean_ident=avg, seqs_std_ident=std)

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
        if GLOBALS["optimized_levels"]:
            # any descendant of the already processed node is suitable for
            # selection. If the ancestor of level-species is on top of the
            # task_tree_node, it will be discarded
            avail_nodes = set(master_node.get_descendants())
            for lin in GLOBALS["optimized_levels"]:
                sp2lin, lin2sp = GLOBALS["lineages"]
                optimized, strict_monophyly = GLOBALS["optimized_levels"][lin]
                if not optimized:
                    ancestor = main_tree.get_common_ancestor(*lin2sp[lin])
                    if ancestor in avail_nodes:
                        # check that the node satisfies level monophyly config
                        ancestor_content = set([x.name for x in n2content[ancestor]])
                        if not strict_monophyly or lin2sp[lin] == ancestor_content:
                            _TARGET_NODES[ancestor].append(lin)
                        elif strict_monophyly:
                            log.log(28, "Discarding not monophyletic level @@11:%s@@1:" %lin)
                    else:
                        log.log(28, "Discarding upper clade @@11:%s@@1:" %lin)
                        
        for node in master_node.iter_leaves(is_leaf_fn=processable_node):
            if GLOBALS["optimized_levels"]:
                log.log(28, "Trying to optimizing custom tree level: @@11:%s@@1:" %_TARGET_NODES[node])
                for lin in _TARGET_NODES[node]:
                    # Marks the level as optimized, so is not computed again
                    GLOBALS["optimized_levels"][lin][0] = True
           
            log.log(28, "Found possible target node of size %s and branch support %f" %(len(n2content[node]), node.support))

            # Finds best outgroup for the target node
            if npr_conf.outgroup_size == 0:
                seqs = set([_i.name for _i in n2content[node]])
                outs = set()
            else:
                splitterconfname, _ = npr_conf.tree_splitter
                splitterconf = GLOBALS[threadid][splitterconfname]
                #seqs, outs = select_outgroups(node, n2content, splitterconf)
                #seqs, outs = select_closest_outgroup(node, n2content, splitterconf)
                seqs, outs = select_sister_outgroup(node, n2content, splitterconf)
                
                
            if seqs | outs == tasktree_content:
                log.log(28, "Discarding target node of size %s, due to identity with its parent node" %len(n2content[node]))
                #print tasktree_content
                #print seqs
                #print outs
                trees_to_browse.append(node)
            else:
                npr_nodes += 1
                log.log(28,
                        "@@16:Target node of size %s with %s outgroups marked for a new NPR iteration!@@1:" %(
                        len(seqs),
                        len(outs)))
                yield node, seqs, outs
    log.log(28, "%s nodes will be optimized", npr_nodes)

def get_next_npr_node(threadid, ttree, task_outgroups, mtree, alg_path, npr_conf, target_cladeids=None):
    current_iter = get_iternumber(threadid)
    if npr_conf.max_iters and current_iter >= npr_conf.max_iters:
        log.warning("Maximum number of iterations reached!")
        return
        
    for node, seqs, outs in split_tree(ttree, task_outgroups, mtree, alg_path,
                                       npr_conf, threadid, target_cladeids):
        if npr_conf.max_iters and current_iter < npr_conf.max_iters:

            if DEBUG():
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("MainTree:"
                                                             "Gold color:Newly generated task nodes",
                                                             fgcolor="blue"), 0)
                node.img_style["fgcolor"] = "Gold"
                node.img_style["size"] = 30

            log.log(28, "Selected node: %s targets, %s outgroups", len(seqs), len(outs))
            # Yield new iteration
            inc_iternumber(threadid)
            yield node, seqs, outs
                    
    if DEBUG():
        mtree.show(tree_style=NPR_TREE_STYLE)
        for _n in mtree.traverse():
            _n.img_style = None
 
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
    max_outgroup_size = max(int(float(splitterconf["_outgroup_size"]) * len(n2content[target])), 1)
    out_min_support = float(splitterconf["_outgroup_min_support"])

    log.log(28, "Max outgroup size allowed %d" %max_outgroup_size)
    
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
    out_min_support = float(splitterconf["_outgroup_min_support"])
    if splitterconf["_outgroup_size"].strip().endswith("%"):
        max_outgroup_size = max(1, round((float(splitterconf["_outgroup_size"].strip("%"))/100) * len(n2content[target])))
        log.log(28, "Max outgroup size allowed %s = %d" %(splitterconf["_outgroup_size"], max_outgroup_size))
    else:
        max_outgroup_size = max(1, int(splitterconf["_outgroup_size"]))
        log.log(28, "Max outgroup size allowed %d" %max_outgroup_size)
    
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
        print '\n'.join(sorted(["%s Size:%d Dist:%f Supp:%f" %(node.cladeid, len(n2content[node]), ndist, node.support)
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
    
    name2dist = {"min": numpy.min, "max": numpy.max,
                 "mean":numpy.mean, "median":numpy.median}
  
    
    #policy = splitterconf["_outgroup_policy"]  # node or leaves
    out_topodist = tobool(splitterconf["_outgroup_topology_dist"])
    optimal_out_size = int(splitterconf["_outgroup_size"])
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
        
  
    
