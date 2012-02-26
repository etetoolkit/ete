import numpy
import logging
import os
log = logging.getLogger("main")

from nprlib.master_task import Task
from nprlib.master_job import Job
from nprlib.utils import (load_node_size, PhyloTree, SeqGroup, generate_id,
                          get_node2content, NPR_TREE_STYLE, NodeStyle, DEBUG,
                          faces)
from nprlib import db
from nprlib.errors import TaskError

__all__ = ["TreeSplitter"]

class TreeSplitter(Task):
    def __init__(self, nodeid, seqtype, task_tree, main_tree, conf):
        # Initialize task
        Task.__init__(self, nodeid, "treemerger", "Outgroup-free-TreeSplitter")
        self.conf = conf
        self.args = conf["tree_splitter"]
        self.task_tree_file = task_tree
        self.main_tree = main_tree
        self.seqtype = seqtype
        self.rf = None, None # Robinson foulds to orig partition
        self.set_a = None
        self.set_b = None
        self.init()
        self.left_part_file = os.path.join(self.taskdir, "left.msf")
        self.right_part_file = os.path.join(self.taskdir, "right.msf")
        self.pruned_tree = os.path.join(self.taskdir, "pruned_tree.nw")
        self.out_policy = "None"
        self.min_outs = 0
        
    def finish(self):
        def euc_dist(x, y):
            return len(x.symmetric_difference(y)) / float((len(x) + len(y)))
        
        ttree = PhyloTree(self.task_tree_file)
        mtree = self.main_tree
        ttree.dist = 0

        cladeid, target_seqs, out_seqs = db.get_node_info(self.nodeid)
        self.out_seqs = out_seqs
        self.target_seqs = target_seqs

        ttree_content = ttree.get_node2content()
            
        if mtree:
            #cladeid = generate_id([n.name for n in ttree_content[ttree]])
            target_node = mtree.search_nodes(cladeid=cladeid)[0]
            
            target_left = set([_n.name for _n in target_node.children[0]])
            target_right = set([_n.name for _n in target_node.children[1]])

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
            #if DEBUG():
            #    print '\n'.join(map(str, partition_pairs))
                
            outgroup = partition_pairs[0][3]
            ttree.set_outgroup(outgroup)
            self.rf = target_node.robinson_foulds(ttree)
            ttree.dist = target_node.dist
            ttree.support = target_node.support
            
            parent = target_node.up
            target_node.detach()
            parent.add_child(ttree)

            if DEBUG():
                target_node.children[0].img_style["fgcolor"] = "orange"
                target_node.children[0].img_style["size"] = 20
                target_node.children[1].img_style["fgcolor"] = "orange"
                target_node.children[1].img_style["size"] = 20
                target_node.img_style["bgcolor"] = "lightblue"
                
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face( faces.TextFace("MainTree:"
                    " Pre iteration partition",
                    fgcolor="blue"), 0)
                mtree.show(tree_style=NPR_TREE_STYLE)
                target_node.children[0].set_style(None)
                target_node.children[1].set_style(None)
                target_node.set_style(None)
                
                outgroup.img_style["fgcolor"]="Green"
                outgroup.img_style["size"]= 12
                ttree.img_style["bgcolor"] = "lightblue"
                outgroup.add_face(faces.TextFace("DIST=%s" % partition_pairs[0][0]), 0, "branch-top")
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("Optimized node. Most similar outgroup with previous iteration is shown", fgcolor="blue"), 0)

                ttree.add_face(faces.TextFace("RF=%s, (%s)"%(self.rf), fsize=8, ), 0, "branch-bottom")
                ttree.show(tree_style=NPR_TREE_STYLE)
            
        else:
            outgroup = ttree.get_midpoint_outgroup()
            ttree.set_outgroup(outgroup)
            self.main_tree = ttree
            if DEBUG():
                outgroup.img_style["size"] = 20
                outgroup.img_style["fgcolor"] = "green"
                NPR_TREE_STYLE.title.clear()
                NPR_TREE_STYLE.title.add_face(faces.TextFace("First iteration split.Outgroup is in green", fgcolor="blue"), 0)
                ttree.show(tree_style=NPR_TREE_STYLE)

        # Reloads node2content of the rooted tree and generate cladeids
        ttree_content = ttree.get_node2content()
        for n, content in ttree_content.iteritems():
            cid = generate_id([_n.name for _n in content])
            n.add_feature("cladeid", cid)

        seqs_a = set([_n.name for _n in ttree_content[ttree.children[0]]])
        seqs_b = set([_n.name for _n in ttree_content[ttree.children[1]]])
        self.set_a = (seqs_a, set())
        self.set_b = (seqs_b, set())
        open(self.left_part_file, "w").write('\n'.join(
            [','.join(seqs_a), ""]))
        open(self.right_part_file, "w").write('\n'.join(
            [','.join(seqs_b), ""]))

        ttree.write(outfile=self.pruned_tree)
        

        
    def check(self):
        if os.path.exists(self.left_part_file) and \
                os.path.exists(self.right_part_file) and \
                os.path.getsize(self.left_part_file) and \
                os.path.getsize(self.right_part_file):
            return True
        return False
            
      
