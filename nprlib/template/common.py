from collections import defaultdict
import logging

import numpy

from nprlib.utils import DEBUG, GLOBALS, SeqGroup
from nprlib import task as all_tasks
from nprlib import db
from nprlib.master_task import register_task_recursively

log = logging.getLogger("main")

CONFIG_SPECS = """

[genetree]
max_iters = integer(minv=1)

max_seqs = correlative_integer_list(minv=0)
switch_aa_similarity = float_list(minv=0.0, maxv=1.0)
max_seq_similarity = float_list(minv=0.0, maxv=1.0)
min_branch_support = float_list(minv=0, maxv=1)

aa_aligner = list()
aa_alg_cleaner = list()
aa_model_tester = list()
aa_tree_builder = list()

nt_aligner = list()
nt_alg_cleaner = list()
nt_model_tester = list()
nt_tree_builder = list()

outgroup_size = integer_list(minv=0),
outgroup_dist = list(),
outgroup_min_support = float_list(minv=0, maxv=1),
outgroup_topodist = bool_list(),
outgroup_policy = list(),


[sptree]
max_iters = integer(minv=1)

max_seqs = correlative_integer_list(minv=0)
switch_aa_similarity = float_list(minv=0.0, maxv=1.0)
max_seq_similarity = float_list(minv=0.0, maxv=1.0)
min_branch_support = float_list(minv=0, maxv=1)

aa_tree_builder = list()
nt_tree_builder = list()

outgroup_size = integer_list(minv=0)
outgroup_dist = list()
outgroup_min_support = float_list(minv=0, maxv=1)
outgroup_topodist = boolean_list()
outgroup_policy = list()

cog_selector = list()
alg_concatenator = list()

"""

class IterConfig(dict):
    def __init__(self, workflow, size, seqtype):
        """Special dict to extract the value of each parameter given
         the properties of a task: size and seqtype. 
        """
        
        wconf = GLOBALS["config"][workflow]
        dict.__init__(self, wconf)

        self.seqtype = seqtype
        self.size = size
        self.index = None

        index_slide = 0
        while self.index is None: 
            try: 
                max_seqs = wconf["max_seqs"][index_slide]
            except IndexError:
                raise DataError("Number of seqs [%d] not considered in current config" %self.size)
            else:
                if self.size <= max_seqs:
                    self.index = index_slide
                else:
                    index_slide += 1

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
                return None
            elif value.startswith("@"):
                return getattr(all_tasks, GLOBALS["config"][value[1:]]["_class"])
            else:
                return value

def process_new_tasks(task, new_tasks):
    # Basic registration and processing of newly generated tasks
    parent_taskid = task.taskid if task else None
    for ts in new_tasks:
        log.log(24, "Registering new task: %s", ts)
        register_task_recursively(ts, parentid=parent_taskid)
        # sort task by nodeid
        GLOBALS["nodeinfo"][ts.nodeid].setdefault("tasks", []).append(ts)
        if task:
            # Clone processor, in case tasks belong to a side workflow
            ts.task_processor = task.task_processor
            ts.threadid = task.threadid
            ts.main_tree = task.main_tree
        db.add_runid2task(ts.threadid, ts.taskid)
            
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

    
def split_tree(task_tree, main_tree, alg_path, npr_conf):
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
        if len(n2content[_n]) > 2 and _n is not master_node:
            if ALG and npr_conf.max_seq_simiarity < 1.0: 
                if not hasattr(_n, "seqs_mean_ident"):
                    log.log(20, "Calculating node sequence stats...")

                    mx, mn, avg, std = get_seqs_identity(ALG,
                                                         [__n.name for __n in n2content[_n]])
                    _n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
                                   seqs_mean_ident=avg, seqs_std_ident=std)
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
                    if _ch.support <= nmp_conf.min_branch_support:
                        _isleaf = True
                        break
            elif _n.support <= npr_conf.min_branch_support:
                # If sequences are different enough and node is
                # not well supported, optimize it. 
                _isleaf = True
        return _isleaf
        
    log.log(20, "Loading tree content...")
    n2content = main_tree.get_node2content()
    if alg_path: 
        log.log(20, "Loading by-node sequence similarity...")
        ALG = SeqGroup(alg_path)
    else:
        ALG = None
    #for n in task.task_tree.traverse(): 
    #    content = n2content[n]
    #    mx, mn, avg, std = get_seqs_identity(ALG, [node.name for node in content])
    #    n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
    #                   seqs_mean_ident=avg, seqs_std_ident=std)

    log.log(20, "Finding next NPR nodes...")
    # task_tree is actually a node in main_tree, since it has been
    # already merged
    trees_to_browse = [task_tree]
    
    while trees_to_browse: 
        master_node = trees_to_browse.pop()
        root_content = set([leaf.name for leaf in n2content[master_node]])
        for node in master_node.iter_leaves(is_leaf_fn=processable_node):
            if npr_conf.outgroup_size == 0:
                seqs = set([_i.name for _i in n2content[node]])
                outs = set()
            else:
                seqs, outs = select_outgroups(node, n2content, npr_conf)
            if seqs | outs == root_content:
                log.log(28, "Discarding NPR node due to identity with its parent")
                trees_to_browse.append(node)
            else:
                yield node, seqs, outs
            

def get_next_npr_node(threadid, ttree, mtree, alg_path, npr_conf):
    current_iter = get_iternumber(threadid)
    if npr_conf.max_iters and current_iter >= npr_conf.max_iters:
        log.log(28, "Maximum number of iterations reached!")
        return
        
    for node, seqs, outs in split_tree(ttree, mtree, alg_path, npr_conf):
        if npr_conf.max_iters and current_iter < npr_conf.max_iters:

            if DEBUG():
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("MainTree:"
                                                             "Gold color:Newly generated task nodes",
                                                             fgcolor="blue"), 0)
                node.img_style["fgcolor"] = "Gold"
                node.img_style["size"] = 30

            log.log(28, "Selected node = targets:%s outgroups: %s ", len(seqs), len(outs))
            # Yield new iteration
            inc_iternumber(threadid)
            yield node, seqs, outs
                    
    if DEBUG():
        mtree.show(tree_style=NPR_TREE_STYLE)
        for _n in mtree.traverse():
            _n.img_style = None

        
      
def select_outgroups(target, n2content, options):
    """Given a set of target sequences, find the best set of out
    sequences to use. Several ways can be selected to find out
    sequences:
    """
    
    name2dist = {"min": numpy.min, "max": numpy.max,
                 "mean":numpy.mean, "median":numpy.median}

    policy = options.outgroup_policy  # node or leaves
    out_topodist = options.outgroup_topodist
    optimal_out_size = options.outgroup_size
    out_distfn = options.outgroup_dist
    out_min_support = options.outgroup_min_support

    if not target.up:
        raise ValueError("Cannot select outgroups for root node!")
    if not optimal_out_size:
        raise ValueError("You are trying to set 0 outgroups!")
    
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
    valid_nodes = [n for n in n2targetdist if not n2content[n] & n2content[target]]
    valid_nodes.sort(sort_outgroups, reverse=True)
    best_outgroup = valid_nodes[0]

    seqs = [n.name for n in n2content[target]]
    outs = [n.name for n in n2content[best_outgroup]]
   
    log.log(20, "Found possible outgroup. Size:%s Score(support,size,dist):%s", len(outs), score(best_outgroup))
   
    log.log(20, "Supports: %0.2f (children=%s)", best_outgroup.support,
            ','.join(["%0.2f" % ch.support for ch in
                      best_outgroup.children]))

    
    #for x in valid_nodes[:10]:
    #    print score(x), min(score(x))
        
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
        n2dist[n] = n2dist[n.up] + n.dist

    sister = target.get_sisters()[0]
    n2dist[sister] = sister.dist + target.dist
    for n in sister.get_descendants("preorder"):
        n2dist[n] = n2dist[n.up] + n.dist

    t.set_outgroup(real_outgroup)

    ## Slow Test. 
    # for n in t.get_descendants():
    #     if float(str(target.get_distance(n))) != float(str(n2dist[n])):
    #         print n
    #         print target.get_distance(n), n2dist[n]
    #         raw_input("ERROR")
    return n2dist
