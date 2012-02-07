import os
import re
import logging
log = logging.getLogger("main")

from nprlib.master_task import ModelTesterTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree

__all__ = ["Prottest"]

class Prottest(ModelTesterTask):
    def __init__(self, nodeid, alg_fasta_file, alg_phylip_file,
                 constrain_tree, conf):
        self.alg_phylip_file = alg_phylip_file
        self.alg_fasta_file = alg_fasta_file
        self.alg_basename = basename(self.alg_phylip_file)
        self.conf = conf
        base_args = {
            "--datatype": "aa",
            "--input": self.alg_basename,
            "--bootstrap": "0",
            "-o": "lr",
            "--model": None, # I will iterate over this value when
                             # creating jobs
            "--quiet": ""
            }

        ModelTesterTask.__init__(self, nodeid, "mchooser", "Prottest", 
                      base_args, conf["prottest"])

        self.best_model = None
        self.seqtype = "aa"
        self.models = self.conf["prottest"]["_models"]
        self.init()
        self.best_model_file = os.path.join(self.taskdir, "best_model.txt")
        self.tree_file = None #os.path.join(self.taskdir, "final_tree.nw")

        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        for j in self.jobs:
            fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
            if os.path.exists(fake_alg_file):
                os.remove(fake_alg_file)
            os.symlink(self.alg_phylip_file, fake_alg_file)

    def load_jobs(self):
        for m in self.models:
            args = self.args.copy()
            args["--model"] = m
            job = Job(self.conf["app"]["phyml"], args,
                      parent_ids=[self.nodeid])
            self.jobs.append(job)
        log.log(26, self.models)

    def finish(self):
        lks = []
        for j in self.jobs:
            tree_file = os.path.join(j.jobdir,
                                     self.alg_basename+"_phyml_tree.txt")
            stats_file = os.path.join(j.jobdir,
                                      self.alg_basename+"_phyml_stats.txt")
            tree = PhyloTree(tree_file)
            m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                          open(stats_file).read())
            lk = float(m.groups()[0])
            tree.add_feature("lk", lk)
            tree.add_feature("model", j.args["--model"])
            lks.append([float(tree.lk), tree.model, tree])
        lks.sort()
        lks.reverse()
        # choose the model with higher likelihood
        best_model = lks[-1][1]
        best_tree = lks[-1][2]
        open(self.best_model_file, "w").write(best_model)
        if self.tree_file:
            tree.write(self.tree_file)
        ModelTesterTask.finish(self)
        
