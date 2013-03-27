import os
import sys
import logging
import re
import shutil
from glob import glob

log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import (basename, Tree, OrderedDict,
                          GLOBALS, RAXML_CITE, pjoin, DATATYPES)
from nprlib import db

__all__ = ["Raxml"]

class Raxml(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_id, model,
                 seqtype, conf, confname):
        GLOBALS["citator"].add(RAXML_CITE)
               
        base_args = OrderedDict()
        self.confname = confname
        self.conf = conf
        self.alg_phylip_file = alg_file
        self.constrain_tree = None
        if constrain_id:
            print contrain_id, "!!!!"
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_tree)
        TreeTask.__init__(self, nodeid, "tree", "RaxML", 
                          base_args, conf[confname])

        max_cores = GLOBALS["_max_cores"]
        if conf[confname]["_app"] == "raxml" or max_cores == 1:
            threads = 1
            raxml_bin = conf["app"]["raxml"]
        elif conf[confname]["_app"] == "raxml-pthreads":
            threads = conf["threading"].get("raxml-pthreads")
            raxml_bin = conf["app"]["raxml-pthreads"]
        
        self.raxml_bin = raxml_bin
        self.threads = threads
        self.seqtype = seqtype
        self.compute_alrt = conf[confname].get("_alrt_calculation", None)

        # Process raxml options
        model = model or conf[confname]["_aa_model"]
        method = conf[confname].get("_method", "GAMMA").upper()
        if seqtype.lower() == "aa":
            self.model_string =  'PROT%s%s' %(method, model.upper())
            self.model = model 
        elif seqtype.lower() == "nt":
            self.model_string =  'GTR%s' %method
            self.model = "GTR"
        else:
            raise ValueError("Unknown seqtype %s", seqtype)
        #inv = conf[confname].get("pinv", "").upper()
        #freq = conf[confname].get("ebf", "").upper()

        self.init()
        
    def load_jobs(self):
        
        args = OrderedDict(self.args)
        args["-s"] = pjoin(GLOBALS["input_dir"], self.alg_phylip_file)
        args["-m"] = self.model_string
        args["-n"] = self.alg_phylip_file
        if self.constrain_tree:
            args["-g"] = pjoin(GLOBALS["input_dir"], self.constrain_tree)
        tree_job = Job(self.raxml_bin, args, parent_ids=[self.nodeid])
        tree_job.jobname += "-"+self.model_string
        tree_job.cores = self.threads
        # Register input files for running the job
        tree_job.add_input_file(self.alg_phylip_file)
        if self.constrain_tree:
            tree_job.add_input_file(self.constrain_tree)
        self.jobs.append(tree_job)

        self.out_tree_file = os.path.join(tree_job.jobdir,
                                     "RAxML_bestTree." + self.alg_phylip_file)
        
        if self.compute_alrt == "raxml":
            alrt_args = tree_job.args.copy()
            if self.constrain_tree:
                del alrt_args["-g"]
            alrt_args["-f"] =  "J"
            alrt_args["-t"] = self.out_tree_file
            alrt_job = Job(self.raxml_bin, alrt_args,
                           parent_ids=[tree_job.jobid])
            alrt_job.jobname += "-alrt"
            alrt_job.dependencies.add(tree_job)
            alrt_job.cores = self.threads
            self.jobs.append(alrt_job)

        elif self.compute_alrt == "phyml":
            alrt_args = {
                "-o": "n",
                "-i": self.alg_phylip_file,
                "--bootstrap": "-2",
                "-d": self.seqtype,
                "-u": self.out_tree_file,
                "--model": self.model,
                "--quiet": "",
                "--no_memory_check": "",
                }

            #if self.constrain_tree:
            #    alrt_args["--constraint_tree"] = self.constrain_tree
               
            alrt_job = Job(self.conf["app"]["phyml"],
                           alrt_args, parent_ids=[tree_job.jobid])
            alrt_job.add_input_file(self.alg_phylip_file, alrt_job.jobdir)
            alrt_job.jobname += "-alrt"
            alrt_job.dependencies.add(tree_job)
            self.jobs.append(alrt_job)

    def finish(self):
        #first job is the raxml tree
        def parse_alrt(match):
            dist = match.groups()[0]
            support = float(match.groups()[1])/100.0
            return "%g:%s" %(support, dist)
        
        if self.compute_alrt == "raxml":
            alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               "RAxML_fastTreeSH_Support." + self.alg_phylip_file)
            raw_nw = open(alrt_tree_file).read()
            nw, nsubs = re.subn(":(\d+\.\d+)\[(\d+)\]", parse_alrt, raw_nw, re.MULTILINE)
            tree = Tree(nw)                                   
        elif self.compute_alrt == "phyml":
            alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                          self.alg_phylip_file +"_phyml_tree.txt")
            tree = Tree(alrt_tree_file)
        else:
            tree = Tree(self.out_tree_file)
            
        TreeTask.store_data(self, tree.write(), {})
        

        
        
