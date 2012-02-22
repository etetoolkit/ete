import os
import shutil
import sys
import re

import logging
log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, OrderedDict

__all__ = ["Phyml"]

class Phyml(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_tree, model, seqtype, conf):
        base_args = OrderedDict({
                "--model": "", 
                "--no_memory_check": "", 
                "--quiet": "",
                "--constraint_tree": ""})

        TreeTask.__init__(self, nodeid, "tree", "Phyml", 
                      base_args, conf["phyml"])

        self.conf = conf
        self.constrain_tree = constrain_tree
        self.alg_phylip_file = alg_file
        self.alg_basename = basename(self.alg_phylip_file)
        if seqtype == "aa":
            self.model = model or conf["phyml"]["_aa_model"]
        elif seqtype == "nt":
            self.model = model or conf["phyml"]["_nt_model"]
        self.seqtype = seqtype
        self.lk = None

        self.init()
        self.tree_file = os.path.join(self.taskdir, "final_tree.nw")
      
        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        j = self.jobs[0]
        fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
        if os.path.exists(fake_alg_file):
            os.remove(fake_alg_file)
        os.symlink(self.alg_phylip_file, fake_alg_file)

    def load_jobs(self):
        args = self.args.copy()
        args["--model"] = self.model
        args["--datatype"] = self.seqtype
        args["--input"] = self.alg_basename
        if self.constrain_tree:
            args["--constraint_tree"] = self.constrain_tree
            args["-u"] = self.constrain_tree
        else:
            del args["--constraint_tree"]
        job = Job(self.conf["app"]["phyml"], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        lks = []
        j = self.jobs[0]
        tree_file = os.path.join(j.jobdir,
                                 self.alg_basename+"_phyml_tree.txt")
        stats_file = os.path.join(j.jobdir,
                                  self.alg_basename+"_phyml_stats.txt")

        m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                      open(stats_file).read())
        lk = float(m.groups()[0])
        self.lk =  lk
        tree = PhyloTree(tree_file)        
        tree.write(outfile=self.tree_file)
        TreeTask.finish(self)
