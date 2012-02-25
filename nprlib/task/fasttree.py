import os
import sys
import re
import shutil

import logging
log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, OrderedDict

__all__ = ["FastTree"]

class FastTree(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_tree, model, seqtype, conf):
        self.conf = conf
        self.alg_phylip_file = alg_file
        self.constrain_tree = constrain_tree
        self.alg_basename = basename(self.alg_phylip_file)
        self.seqtype = seqtype
        self.tree_file = ""

        if model:
            log.warning("FastTree does not allow for model selection. However,"
                        "you could set several options regarding models in the "
                        "fasttree section of the config file.")
        self.model = None
        self.lk = None

        base_args = OrderedDict()
        base_args["-nopr"] = ""
        if self.seqtype == "nt":
            base_args["-gtr -nt"] = ""
        elif self.seqtype == "aa":
            pass
        else:
            raise ValueError("Unknown seqtype %s" %self.seqtype)

        TreeTask.__init__(self, nodeid, "tree", "FastTree", 
                      base_args, conf["fasttree"])
        self.init()

        self.tree_file = os.path.join(self.taskdir, "final_tree.nw")
        if self.constrain_tree:
            t = PhyloTree(self.constrain_tree)
            cons_alg = ""
            for x in t.children[0].get_leaf_names():
                cons_alg += ">%s\n1\n" %x
            for x in t.children[1].get_leaf_names():
                cons_alg += ">%s\n0\n" %x
            
            C = open(os.path.join(self.jobs[0].jobdir, "constraint_alg.fasta"), "w")
            C.write(cons_alg)
            C.close()


        
    def load_jobs(self):
        args = self.args.copy()

        #temp fix p2x
        if self.seqtype == "nt":
            del args["-wag"]
        
        if self.constrain_tree:
            args["-constraints"] = "constraint_alg.fasta"
        args[self.alg_phylip_file] = ""
        job = Job(self.conf["app"]["fasttree"], args, parent_ids=[self.nodeid])
      
        self.jobs.append(job)

    def finish(self):
        job = self.jobs[-1]
        shutil.copy(job.stdout_file, self.tree_file)
        TreeTask.finish(self)

