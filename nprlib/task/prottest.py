import os
import re
import logging
import shutil
log = logging.getLogger("main")

from nprlib.master_task import ModelTesterTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, GLOBALS, PHYML_CITE, pjoin

__all__ = ["Prottest"]

class Prottest(ModelTesterTask):
    def __init__(self, nodeid, alg_fasta_file, alg_phylip_file,
                 constrain_tree, conf, confname):
        GLOBALS["citator"].add(PHYML_CITE)
        
        self.alg_phylip_file = alg_phylip_file
        self.alg_fasta_file = alg_fasta_file
        self.confname = confname
        self.conf = conf
        self.lk_mode = conf[confname]["_lk_mode"]
        if self.lk_mode == "raxml":
            phyml_optimization = "n"
        elif self.lk_mode == "phyml":
            phyml_optimization = "lr"
        else:
            raise ValueError("Choose a valid lk_mode value (raxml or phyml)")

        base_args = {
            "--datatype": "aa",
            "--input": self.alg_phylip_file,
            "--bootstrap": "0",
            "-o": phyml_optimization,
            "--model": None, # I will iterate over this value when
                             # creating jobs
            "--quiet": ""
            }
        self.models = conf[confname]["_models"]
        task_name = "Prottest-[%s]" %','.join(self.models)
        ModelTesterTask.__init__(self, nodeid, "mchooser", task_name, 
                      base_args, conf[confname])
        
        self.best_model = None
        self.seqtype = "aa"
        self.init()
                
    def load_jobs(self):
        conf = self.conf
        for m in self.models:
            args = self.args.copy()
            args["--model"] = m
            bionj_job = Job(conf["app"]["phyml"], args,
                      parent_ids=[self.nodeid])
            bionj_job.jobname += "-bionj-" + m
            bionj_job.jobcat = "bionj"
            bionj_job.add_input_file(self.alg_phylip_file, bionj_job.jobdir)
            self.jobs.append(bionj_job)

            if self.lk_mode == "raxml":
                raxml_args = {
                    "-f": "e", 
                    "-s": pjoin(bionj_job.jobdir, self.alg_phylip_file),
                    "-m": "PROTGAMMA%s" % m,
                    "-n": self.alg_phylip_file+"."+m,
                    "-t": pjoin(bionj_job.jobdir,
                                       self.alg_phylip_file+"_phyml_tree.txt")
                    }
                raxml_job = Job(conf["app"]["raxml"], raxml_args,
                                parent_ids=[bionj_job.jobid])
                raxml_job.jobname += "-lk-optimize"
                raxml_job.dependencies.add(bionj_job)
                raxml_job.model = m
                raxml_job.jobcat = "raxml"
                self.jobs.append(raxml_job)

    def finish(self):
        lks = []
        if self.lk_mode == "phyml":
            for job in self.jobs:
                if job.jobcat != "bionj": continue
                phyml_job = job
                tree_file = pjoin(phyml_job.jobdir,
                                  self.alg_phylip_file+"_phyml_tree.txt")
                stats_file = pjoin(phyml_job.jobdir,
                                   self.alg_phylip_file+"_phyml_stats.txt")
                tree = PhyloTree(tree_file)
                m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                              open(stats_file).read())
                lk = float(m.groups()[0])
                tree.add_feature("lk", lk)
                tree.add_feature("model", phyml_job.args["--model"])
                lks.append([float(tree.lk), tree.model, tree])
        elif self.lk_mode == "raxml":
            for job in self.jobs:
                if job.jobcat != "raxml": continue
                raxml_job = job
                lk = open(pjoin(raxml_job.jobdir, "RAxML_log.%s"
                                %raxml_job.args["-n"])).readline().split()[1]
                tree = PhyloTree(raxml_job.args["-t"])
                tree.add_feature("lk", lk)
                tree.add_feature("model", raxml_job.model)
            lks.append([lk, tree.model, tree])
        lks.sort()
        lks.reverse()
        # choose the model with higher likelihood
        best_model = lks[-1][1]
        best_tree = lks[-1][2]
        ModelTesterTask.store_data(self, best_model, lks)
        
