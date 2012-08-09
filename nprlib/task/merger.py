import numpy
import logging
import os
log = logging.getLogger("main")

from nprlib.master_task import TreeMergeTask
from nprlib.master_job import Job
from nprlib.utils import (load_node_size, PhyloTree, SeqGroup, generate_id,
                          get_node2content, NPR_TREE_STYLE, NodeStyle, DEBUG,
                          faces)
from nprlib import db
from nprlib.errors import TaskError

__all__ = ["TreeMerger"]

class TreeMerger(TreeMergeTask):
    def __init__(self, nodeid, seqtype, task_tree, conf):
        # Initialize task
        TreeMergeTask.__init__(self, nodeid, "treemerger", "TreeMerger")
        self.conf = conf
        self.args = conf["tree_splitter"]
        self.task_tree_file = task_tree
        self.main_tree = None
        self.task_tree = None
        self.seqtype = seqtype
        self.rf = None, None # Robinson foulds to orig partition
        self.outgroup_match_dist = 0.0
        self.outgroup_match = ""
        self.pre_iter_support = None # support of the node pre-iteration
        self.init()
        self.pruned_tree = os.path.join(self.taskdir, "pruned_tree.nw")
        
    def finish(self):
        def euc_dist(x, y):
            return len(x.symmetric_difference(y)) / float((len(x) + len(y)))
        
        ttree = PhyloTree(self.task_tree_file)
        mtree = self.main_tree
        ttree.dist = 0

        cladeid, target_seqs, out_seqs = db.get_node_info(self.threadid, self.nodeid)
        self.out_seqs = out_seqs
        self.target_seqs = target_seqs

        ttree_content = ttree.get_node2content()
        if mtree and not out_seqs:
            mtree_content = mtree.get_node2content()
            log.log(28, "Finding best scoring outgroup from previous iteration.")
            #cladeid = generate_id([n.name for n in ttree_content[ttree]])
            #orig_target = mtree.search_nodes(cladeid=cladeid)[0]
            #target_left = set([_n.name for _n in orig_target.children[0]])
            #target_right = set([_n.name for _n in orig_target.children[1]])
            for _n in mtree_content:
                if _n.cladeid == cladeid:
                    orig_target = _n 
            target_left = set([_n.name for _n in mtree_content[orig_target.children[0]]])
            target_right = set([_n.name for _n in mtree_content[orig_target.children[1]]])
                    
            partition_pairs = []
            everything = set([_n.name for _n in ttree_content[ttree]])
            for n, content in ttree_content.iteritems():
                if n is ttree:
                    continue
                left = set([_n.name for _n in content])
                right =  everything - left
                d1 = euc_dist(left, target_left)
                d2 = euc_dist(left, target_right)
                best_match = min(d1, d2)
                partition_pairs.append([best_match, left, right, n])

            partition_pairs.sort()
            
            self.outgroup_match_dist = partition_pairs[0][0]
            #self.outgroup_match = '#'.join( ['|'.join(partition_pairs[0][1]),
            #                      '|'.join(partition_pairs[0][2])] )

            
            outgroup = partition_pairs[0][3]
            ttree.set_outgroup(outgroup)
      
            ttree.dist = orig_target.dist
            ttree.support = orig_target.support

            if DEBUG():
                orig_target.children[0].img_style["fgcolor"] = "orange"
                orig_target.children[0].img_style["size"] = 20
                orig_target.children[1].img_style["fgcolor"] = "orange"
                orig_target.children[1].img_style["size"] = 20
                orig_target.img_style["bgcolor"] = "lightblue"
                
                NPR_TREE_STYLE.title.add_face( faces.TextFace("MainTree: Pre iteration partition", fgcolor="blue"), 0)
                mtree.show(tree_style=NPR_TREE_STYLE)
                NPR_TREE_STYLE.title.clear()

                orig_target.children[0].set_style(None)
                orig_target.children[1].set_style(None)
                orig_target.set_style(None)

            # Merge task and main trees
            parent = orig_target.up
            orig_target.detach()
            parent.add_child(ttree)

            if DEBUG():
                outgroup.img_style["fgcolor"]="Green"
                outgroup.img_style["size"]= 12
                ttree.img_style["bgcolor"] = "lightblue"
                outgroup.add_face(faces.TextFace("DIST=%s" % partition_pairs[0][0]), 0, "branch-top")
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("Optimized node. Most similar outgroup with previous iteration is shown", fgcolor="blue"), 0)
                ttree.show(tree_style=NPR_TREE_STYLE)

        elif mtree and out_seqs:
            log.log(26, "Rooting tree using %d custom seqs" %
                   len(out_seqs))

            self.outgroup_match = '|'.join(out_seqs)
                        
            #log.log(22, "Out seqs:    %s", len(out_seqs))
            #log.log(22, "Target seqs: %s", target_seqs)
            if len(out_seqs) > 1:
                outgroup = ttree.get_common_ancestor(out_seqs)
                # if out_seqs are not grouped in a single node
                if outgroup is ttree:
                    # root to target seqs and retry out_seqs
                    target = ttree.get_common_ancestor(target_seqs)
                    ttree.set_outgroup(target)
                    outgroup = ttree.get_common_ancestor(out_seqs)
            else:
                outgroup = ttree & list(out_seqs)[0]

            if outgroup is not ttree:
                ttree.set_outgroup(outgroup)
                
                orig_target = self.main_tree.get_common_ancestor(target_seqs)
                found_target = outgroup.get_sisters()[0]

                if DEBUG():
                    for _seq in out_seqs:
                        tar =  ttree & _seq
                        tar.img_style["fgcolor"]="green"
                        tar.img_style["size"] = 12
                        tar.img_style["shape"] = "circle"
                    outgroup.img_style["fgcolor"]="lightgreen"
                    outgroup.img_style["size"]= 12
                    found_target.img_style["bgcolor"] = "lightblue"
                    NPR_TREE_STYLE.title.clear()
                    NPR_TREE_STYLE.title.add_face(faces.TextFace("Optimized node. Outgroup is in green and distance to original partition is shown", fgcolor="blue"), 0)
                    ttree.show(tree_style=NPR_TREE_STYLE)
                    
                ttree = ttree.get_common_ancestor(target_seqs)
                outgroup.detach()
                self.pre_iter_support = orig_target.support
                # Use previous dist and support
                ttree.dist = orig_target.dist
                ttree.support = orig_target.support
                parent = orig_target.up
                orig_target.detach()
                parent.add_child(ttree)
            else:
                raise TaskError("Outgroup was split")
               
        else:
            def sort_outgroups(x,y):
                # higher support first
                v = -1 * cmp(x.support, y.support)
                   
                if not v:
                #    # Sort by optimal size
                #    #v = cmp(abs(optimal_out_size - len(ttree_content[x])),
                #    #        abs(optimal_out_size - len(ttree_content[y])))
                    v = -1 * cmp(len(ttree_content[x]), len(ttree_content[y]))
                    
                # If equal supports, sort by closeness to midpoint
                if not v: 
                    v = cmp(n2targetdist[x], n2targetdist[y])
                   
                    
                return v
                            
            optimal_out_size = self.args["_min_size"]
            log.log(28, "Rooting close to midpoint.")
            outgroup = ttree.get_midpoint_outgroup()
            # n2rootdist, n2targetdist = distance_matrix(outgroup, leaf_only=False,
            #                                            topology_only=False)
            n2targetdist = distance_matrix_new(outgroup, leaf_only=False,
                                               topology_only=False)

            
            #del n2targetdist[ttree]
            valid_nodes = [n for n in ttree_content.keys() if n is not ttree]
            valid_nodes.sort(sort_outgroups)
            #for n in valid_nodes[:10]:
            #    print n, n.support, len(ttree_content[n]), n2targetdist[n]
            
            best_outgroup = valid_nodes[0]
            log.log(28, "Rooting to node of size %s", len(ttree_content[best_outgroup]))                       
            ttree.set_outgroup(best_outgroup)
            self.main_tree = ttree
            orig_target = ttree
            if DEBUG():
                outgroup.img_style["size"] = 20
                outgroup.img_style["fgcolor"] = "lightgreen"
                best_outgroup.img_style["size"] = 20
                best_outgroup.img_style["fgcolor"] = "green"
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("First iteration split. midpoint outgroup is in lightgreen, selected in green", fgcolor="blue"), 0)
                ttree.show(tree_style=NPR_TREE_STYLE)

        tn = orig_target.copy()
        self.pre_iter_task_tree = tn
        self.rf = orig_target.robinson_foulds(ttree)
        self.pre_iter_support = orig_target.support

                
        # Reloads node2content of the rooted tree and generate cladeids
        ttree_content = self.main_tree.get_node2content()
        for n, content in ttree_content.iteritems():
            cid = generate_id([_n.name for _n in content])
            n.add_feature("cladeid", cid)

        ttree.write(outfile=self.pruned_tree)
        self.task_tree = ttree
        if DEBUG():
            for _n in self.main_tree.traverse():
                _n.img_style = None
        
    def check(self):
        if os.path.exists(self.pruned_tree):
            return True
        return False

def root_distance_matrix(root):
    n2rdist = {root:0.0}
    for n in root.iter_descendants("preorder"):
        n2rdist[n] = n2rdist[n.up] + n.dist
    return n2rdist

def distance_matrix(target, leaf_only=False, topology_only=False):
    # Detect the root and the target branch
    root = target
    while root.up:
        target_branch = root
        root = root.up
    # Calculate distances to the root
    n2rdist = {root:0.0}        
    for n in root.get_descendants("preorder"):
        dist = 1.0 if topology_only else n.dist
        n2rdist[n] = n2rdist[n.up] + dist

    # Calculate distances to the target node
    n2tdist = {}        
    for n in root.traverse():
        ancestor = root.get_common_ancestor(n, target)
        if not leaf_only or n.is_leaf():
            #if ancestor != target:
            n2tdist[n] = n2rdist[target] + n2rdist[n] - n2rdist[ancestor]
    return n2rdist, n2tdist


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
    
        
      
