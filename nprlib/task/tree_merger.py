import numpy
import logging
import os
log = logging.getLogger("main")

from nprlib.master_task import Task
from nprlib.master_job import Job
from nprlib.utils import (load_node_size, PhyloTree, SeqGroup, generate_id,
                          get_node2content)
from nprlib import db

from nprlib.utils import NodeStyle, TreeStyle
st = NodeStyle()
ts = TreeStyle
st['fgcolor'] = 'red'
st['size'] = 20


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
        self.out_policy = self.args["_outgroup_policy"]
        self.min_outs = self.args["_outgroup_size"]
        self.init()
        self.left_part_file = os.path.join(self.taskdir, "left.msf")
        self.right_part_file = os.path.join(self.taskdir, "right.msf")
        self.pruned_tree = os.path.join(self.taskdir, "pruned_tree.nw")
        
    def finish(self):
        ttree = PhyloTree(self.task_tree_file)
        ttree.dist = 0
        
        #log.debug("Task Tree: %s", ttree)

        cladeid, target_seqs, out_seqs = db.get_node_info(self.nodeid)
        self.out_seqs = out_seqs
        self.target_seqs = target_seqs
        # Root task_tree. If outgroup seqs are available, uses manual
        # rooting. Otherwise, it means that task_tree is the result of
        # the first iteration, so it will try automatic rooting based
        # on dictionary or midpoint.
        if out_seqs:
            log.log(28, "Rooting tree using %d custom seqs" %
                     len(out_seqs))

            log.debug("Out seqs:    %s", out_seqs)
            log.debug("Target seqs: %s", target_seqs)
            if len(out_seqs) > 1:
                # Root to a non-outgroup leave to leave all outgroups
                # in one side.
                outgroup = ttree.get_common_ancestor(out_seqs)
                if outgroup is ttree:
                    outgroup = ttree.get_common_ancestor(target_seqs)
            else:
                outgroup = ttree & list(out_seqs)[0]

            if outgroup is not ttree:
                ttree.set_outgroup(outgroup)
                ttree = ttree.get_common_ancestor(target_seqs)
            else:
                raise ValueError("Outgroup was split")
        else:
            #log.log(28, "Rooting tree to the largest-best-supported node")
            #ttree.set_outgroup(ttree.get_midpoint_outgroup())
            ## Pre load node size for better performance
            #load_node_size(ttree)
            #supports = []
            #for n in ttree.get_descendants("levelorder"):
            #    if n.is_leaf():
            #        continue
            #    st = n.get_sisters()
            #    if len(st) == 1:
            #        min_size = min([st[0]._size, n._size])
            #        min_support = min([st[0].support, n.support])
            #        supports.append([min_support, min_size, n])
            #    else:
            #        log.warning("Skipping multifurcation in basal tree")
            # 
            ## Roots to the best supported and larger partitions
            #supports.sort()
            #supports.reverse()
            #ttree.set_outgroup(supports[0][2])
            log.log(28, "Rooting tree to the farthest node")
            rootdist = root_distance_matrix(ttree)
            max_dist = 0
            for n1 in ttree.iter_leaves():
                sum_dist = 0
                for n2 in ttree.iter_leaves():
                    dist = rootdist[n1]+rootdist[n2]
                    sum_dist += dist
                if sum_dist >= max_dist:
                    farthest_node = n1
            ttree.set_outgroup(farthest_node)

        seqs_a, outs_a, seqs_b, outs_b = select_outgroups(ttree, self.main_tree,
                                                          self.args)
        self.set_a = (seqs_a, outs_a)
        self.set_b = (seqs_b, outs_b)
        open(self.left_part_file, "w").write('\n'.join(
            [','.join(seqs_a), ','.join(outs_a)]))
        open(self.right_part_file, "w").write('\n'.join(
            [','.join(seqs_b), ','.join(outs_b)]))

        ttree.write(outfile=self.pruned_tree)

            
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
    n2rdist = {root:0.0}
    for n in root.iter_descendants("preorder"):
        n2rdist[n] = n2rdist[n.up] + n.dist
    return n2rdist

def select_outgroups(ttree, mtree, args):
    policy = args["_outgroup_policy"]
    min_outs = args["_outgroup_size"]
   
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

    best_dist_to_a = dist_fn([d[0] for d in  to_a_dists])
    best_dist_to_b = dist_fn([d[0] for d in  to_b_dists])


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

    log.debug("Rank outgroups for left side: %s" %\
              ', '.join(['%s:%f' %(_n,_v) for _v,_n in rank_outs_a[:4]]))
    log.debug("Rank outgroups for right side: %s" %\
              ', '.join(['%s:%f' %(_n,_v) for _v,_n in rank_outs_b[:4]]))

    missing_outs = min_outs - min(len(outs_a), len(outs_b))

    if mtree and (min_outs - min(len(outs_a), len(outs_b)) > 0):
        cladeid = generate_id(ttree.get_leaf_names())
        # Fist, find task tree node within main tree
        n2content = get_node2content(mtree)
        _node = None
        for _node, content in n2content.iteritems():
            if generate_id(content) == cladeid:
                break
        # Now, add out seqs from sister group
        while _node.up and (min_outs - min(len(outs_a), len(outs_b)) > 0):
            _extra = n2content[_node.get_sisters()[0]]
            outs_a.extend(_extra)
            outs_b.extend(_extra)
            _node = _node.up
        
    outs_a = outs_a[:min_outs]
    outs_b = outs_b[:min_outs]
    
    if min(len(outs_a), len(outs_b)) < min_outs:
        log.log(28, "Outgroup size not possible for one or both children partitions.")
        
    return map(set, [seqs_a, outs_a, seqs_b, outs_b])

        
