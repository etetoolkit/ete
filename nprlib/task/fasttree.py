import os
import sys
import re
import shutil

import logging
log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, OrderedDict, GLOBALS

__all__ = ["FastTree"]

class FastTree(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_tree, model, seqtype, confname):
        self.confname = confname
        self.alg_phylip_file = alg_file
        self.constrain_tree = constrain_tree
        self.alg_basename = basename(self.alg_phylip_file)
        self.seqtype = seqtype
        self.tree_file = ""

        if model:
            log.warning("FastTree does not support model selection. However, "
                        "you could switch from JTT (default) to WAG by adding a "
                        "-wag flag in the fastTree section of the config file.")
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

        TreeTask.__init__(self, nodeid, "tree", "FastTree", base_args,
                          GLOBALS["config"][confname])

        self.init()

        self.tree_file = os.path.join(self.taskdir, "final_tree.nw")
        if self.constrain_tree:
            t = PhyloTree(self.constrain_tree)
            cons_alg = ""

            if len(t.children) > 2:
                for ch in t.children:
                    if not ch.is_leaf():
                        for x in ch.get_leaf_names():
                            cons_alg += ">%s\n1\n" %x
                    else:
                        cons_alg += ">%s\n0\n" %ch.name
            else:
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
        conf = GLOBALS["config"]
        appname = conf[self.confname]["_app"]
        
        job = Job(conf["app"][appname], args, parent_ids=[self.nodeid])
        job.cores = conf["threading"][appname]
        self.jobs.append(job)

    def finish(self):
        job = self.jobs[-1]
        shutil.copy(job.stdout_file, self.tree_file)
        TreeTask.finish(self)

