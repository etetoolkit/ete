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
    def __init__(self, cladeid, alg_file, model, seqtype, conf):
        self.conf = conf
        self.alg_phylip_file = alg_file
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
            base_args["-nt"] = ""
        elif self.seqtype == "aa":
            pass
        else:
            raise ValueError("Unknown seqtype %s" %self.seqtype)

        TreeTask.__init__(self, cladeid, "tree", "FastTree", 
                      base_args, conf["fasttree"])

        # input alg must be the last argument 
        self.args[self.alg_phylip_file] = ""

        self.init()
        self.tree_file = os.path.join(self.taskdir, "final_tree.nw")

    def load_jobs(self):
        args = self.args.copy()
        job = Job(self.conf["app"]["fasttree"], args, parent_ids=[self.cladeid])
        self.jobs.append(job)

    def finish(self):
        job = self.jobs[-1]
        shutil.copy(job.stdout_file, self.tree_file)
        TreeTask.finish(self)
