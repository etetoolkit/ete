import numpy
import logging
import os
log = logging.getLogger("main")

from nprlib.master_task import Task
from nprlib.master_job import Job
from nprlib.utils import load_node_size, PhyloTree, SeqGroup, generate_id
from nprlib import db

__all__ = ["TreeMerger"]

class TreeMerger(Task):
    def __init__(self, nodeid, seqtype, task_tree, main_tree, conf):
        # Initialize task
        Task.__init__(self, nodeid, "treemerger", "Standard-TreeMerger")
        self.conf = conf
        self.args = conf["tree_merger"]
        self.task_tree_file = task_tree
        self.main_tree = main_tree
        self.seqtype = seqtype
        self.set_a = None
        self.set_b = None
        self.init()
        self.left_part_file = os.path.join(self.taskdir, "left.msf")
        self.right_part_file = os.path.join(self.taskdir, "right.msf")

    def finish(self):
        mtree = self.main_tree
        ttree = PhyloTree(self.task_tree_file)
       
        #log.debug("Task Tree: %s", ttree)
        #log.debug("Main Tree: %s", mtree)

        cladeid, target_seqs, out_seqs = db.get_node_info(self.nodeid)

        # Locate current node in the main tree containing the same
        # seqs as the task tree
        if mtree:
            target_node = fast_search_node(cladeid, mtree)
        else:
            target_node = None

        # Root task_tree. If outgroup seqs are available, uses manual
        # rooting. Otherwise, it means that task_tree is the result of
        # the first iteration, so it will try automatic rooting based
        # on dictionary or midpoint.
        if out_seqs:
            log.log(28, "Rooting tree using %d custom seqs" %
                     len(out_seqs))

            log.debug(out_seqs)
            if len(out_seqs) > 1:
                # Root to a non-outgroup leave to leave all outgroups
                # in one side.
                ttree.set_outgroup(list(target_seqs)[0])
                outgroup = ttree.get_common_ancestor(out_seqs)
            else:
                outgroup = ttree & list(out_seqs)[0]

            ttree.set_outgroup(outgroup)
            ttree = ttree.get_common_ancestor(core_seqs)

            # If out_seqs were taken from upper parts of the main
            # tree, discard them. Otherwise, keep them, because it
            # means that previous iteration returned a tree with the
            # same number of sister nodes as outgroups needed (so the
            # tree was reconstructed without anchor outgroups).
            if out_seqs & target_seqs:
                ttree.detach()
        else:
            log.log(28, "Rooting tree to the largest-best-supported node")
            ttree.set_outgroup(ttree.get_midpoint_outgroup())
            # Pre load node size for better performance
            load_node_size(ttree)
            supports = []
            for n in ttree.get_descendants("levelorder"):
                if n.is_leaf():
                    continue
                st = n.get_sisters()
                if len(st) == 1:
                    min_size = min([st[0]._size, n._size])
                    min_support = min([st[0].support, n.support])
                    supports.append([min_support, min_size, n])
                else:
                    log.warning("Skipping multifurcation in basal tree")

            # Roots to the best supported and larger partitions
            supports.sort()
            supports.reverse()
            ttree.set_outgroup(supports[0][2])

        seqs_a, outs_a, seqs_b, outs_b = select_outgroups(ttree, mtree,
                                                          target_node, self.args)
        self.set_a = (seqs_a, outs_a)
        self.set_b = (seqs_b, outs_b)
        open(self.left_part_file, "w").write('\n'.join(
            [','.join(seqs_a), ','.join(outs_a)]))
        open(self.right_part_file, "w").write('\n'.join(
            [','.join(seqs_b), ','.join(outs_b)]))

        # Updates main tree with the results extracted from task_tree
        if mtree is None:
            mtree = ttree
        else:
            log.log(26, "Merging tree with previous iterations.")
            # target = fast_search_node(self.cladeid, mtree)
            # Switch nodes in the main_tree so current tree topology
            # is incorporated.
            up = target_node.up
            target_node.detach()
            up.add_child(ttree)
        # Store merged tree
        self.main_tree = mtree
            
    def check(self):
        if os.path.exists(self.left_part_file) and \
                os.path.exists(self.right_part_file) and \
                os.path.getsize(self.left_part_file) and \
                os.path.getsize(self.right_part_file):
            return True
        return False
            
def fast_search_node(cladeid, tree):
    for n in tree.traverse():
        if n.cladeid == cladeid:
            return n

def root_distance_matrix(root):
    root.dist = 0.0
    n2rdist = {root:0.0}
    for n in root.iter_descendants("preorder"):
        n2rdist[n] = n2rdist[n.up] + n.dist
    return n2rdist


def get_node2content(node, store={}):
    for ch in node.children:
        get_node2content(ch, store=store)

    if node.children:
        val = []
        for ch in node.children:
            val.extend(store[ch])
        store[node] = val
    else:
        store[node] = [node.name]
    return store

def select_outgroups(ttree, mtree, target_node, args):
    policy = args["_outgroup_policy"]
    min_outs = args["_outgroup_size"]
    
    tnode2names = get_node2content(ttree)
    # Annotate current tree
    log.log(28, "Annotating new tree.")
    for n, names in tnode2names.iteritems():
        n.add_features(cladeid=generate_id(names))
    
    # Extract the two new partitions (potentially representing two
    # new iterations in the pipeline). Note that outgroup node, if
    # necessary, was detached previously.
    a = ttree.children[0]
    b = ttree.children[1]

    # Sequences grouped by each of the new partitions
    seqs_a = a.get_leaf_names()
    seqs_b = b.get_leaf_names()

    # To detect the best outgroups of each of the new partitions
    # (a and b), I calculate the branch length distances from them
    # (a and b) to all leaf nodes in its corresponding sister
    # node.
    log.log(26, "Calculating node distances...")
    to_b_dists = []
    to_a_dists = []
    n2rootdist = root_distance_matrix(ttree)
    for b_leaf in b.iter_leaves():
        dist = n2rootdist[b_leaf] + a.dist
        #dist1 = b_leaf.get_distance(a)
        #print dist, dist1
        to_a_dists.append([dist, b_leaf.name])

    for a_leaf in a.iter_leaves():
        dist = n2rootdist[a_leaf] + b.dist
        #dist1 = a_leaf.get_distance(b)
        #print dist, dist1
        to_b_dists.append([dist, a_leaf.name])

    # Then we can sort outgroups prioritizing sequences whose
    # distances are close to the mean (avoiding the closest and
    # farthest sequences).
    if policy == "mean_dist":
        dist_fn = numpy.mean
    elif policy == "median_dist":
        dist_fn = numpy.median
    elif policy == "max_dist":
        dist_fn = numpy.max
    elif policy == "min_dist":
        dist_fn = numpy.min

    best_dist_to_b = dist_fn([d[0] for d in  to_b_dists])
    best_dist_to_a = dist_fn([d[0] for d in  to_a_dists])

    rank_outs_a = sorted(to_a_dists, 
                         lambda x,y: cmp(abs(x[0] - best_dist_to_a),
                                         abs(y[0] - best_dist_to_a),
                                         ))

    rank_outs_b = sorted(to_b_dists, 
                         lambda x,y: cmp(abs(x[0] - best_dist_to_b),
                                         abs(y[0] - best_dist_to_b),
                                         ))
    outs_a = [e[1] for e in rank_outs_a]
    outs_b = [e[1] for e in rank_outs_b]

    log.log(22, "Best distance to node A: %s" %best_dist_to_a)
    log.log(22, "Best outgroup for A: %s" %rank_outs_a[:5])
    log.log(22, "Best distance to node B: %s" %best_dist_to_b)
    log.log(22, "Best outgroup for B: %s" %rank_outs_b[:5])

    missing_outs = min_outs - min(len(outs_a), len(outs_b))
    if missing_outs > 0:
        # Try to extend outgroups using the upper tree
        _node = target_node
        while _node:
            _extra = mnode2names[_node.get_sisters()[0]]
            outs_a.extend(_extra)
            outs_b.extend(_extra)
    outs_a = outs_a[:min_outs]
    outs_b = outs_b[:min_outs]
    
    if min(len(outs_a), len(outs_b)) < min_outs:
        log.log(28, "Outgroup size not possible for one or both children partitions.")
        
    return map(set, [seqs_a, outs_a, seqs_b, outs_b])



        
