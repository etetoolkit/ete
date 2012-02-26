import os
import sys
import logging
import re
import shutil
from glob import glob

log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, OrderedDict

__all__ = ["Raxml"]

class Raxml(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_tree,  model, seqtype, conf):
        # PTHREADS version needs at least -T2, which is actually
        # similar to the normal version
        threads = int(conf["raxml"].get(
                "_max_cores", conf["main"]["_max_cores"]))

        if threads > conf["main"]["_max_cores"]:
            threads = conf["main"]["_max_cores"]
            log.warning("RAxML execution will be limited to [%d] threads." %
                        threads)
        if threads > 1:
            raxml_bin = conf["app"]["raxml-pthreads"]
            base_args = OrderedDict({"-T": threads})
        else:
            raxml_bin = conf["app"]["raxml"]
            base_args = OrderedDict()

        TreeTask.__init__(self, nodeid, "tree", "RaxML", 
                          base_args, conf["raxml"])

        self.raxml_bin = raxml_bin
        self.threads = threads
        self.conf = conf
        self.constrain_tree = constrain_tree
        self.seqtype = seqtype
        self.alg_phylip_file = alg_file
        self.compute_alrt = conf["raxml"].get("_alrt_calculation", None)

        # Process raxml options
        model = model or conf["raxml"]["_aa_model"]
        method = conf["raxml"].get("_method", "GAMMA").upper()
        if seqtype.lower() == "aa":
            self.model_string =  'PROT%s%s' %(method, model.upper())
            self.model = model 
        elif seqtype.lower() == "nt":
            self.model_string =  'GTR%s' %method
            self.model = "GTR"
        else:
            raise ValueError("Unknown seqtype %s", seqtype)
        #inv = conf["raxml"].get("pinv", "").upper()
        #freq = conf["raxml"].get("ebf", "").upper()

        self.init()
        self.tree_file = os.path.join(self.taskdir, "final_tree.nw")

        self.ml_tree_file = os.path.join(self.jobs[0].jobdir,
                                    "RAxML_bestTree." + self.nodeid)
        
        if self.compute_alrt == "raxml":
            self.jobs[1].args["-t"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               "RAxML_fastTreeSH_Support." +\
                                                   self.nodeid)
        elif self.compute_alrt == "phyml":
            #fake_alg_file = os.path.join(self.jobs[1].jobdir, basename(self.alg_phylip_file))
            #if os.path.exists(fake_alg_file):
            #    os.remove(fake_alg_file)
            #os.symlink(self.alg_phylip_file, fake_alg_file)
            self.jobs[1].args["-u"] = self.ml_tree_file
            self.alrt_tree_file = os.path.join(self.jobs[1].jobdir,
                                               basename(self.alg_phylip_file) +"_phyml_tree.txt")
        else:
            self.alrt_tree_file = None

    def load_jobs(self):
        if self.threads > 1:
            bin = self.conf["app"]["raxml-pthreads"]
        else:
            bin = self.conf["app"]["raxml"]
        
        args = self.args.copy()
        args["-s"] = self.alg_phylip_file
        args["-m"] = self.model_string
        args["-n"] = self.nodeid
        if self.constrain_tree:
            args["-g"] = self.constrain_tree
        tree_job = Job(self.raxml_bin, args, parent_ids=[self.nodeid])
        tree_job.cores = self.threads
        self.jobs.append(tree_job)

        if self.compute_alrt == "raxml":
            alrt_args = tree_job.args.copy()
            if self.constrain_tree:
                del alrt_args["-g"]
            alrt_args["-f"] =  "J"
            alrt_args["-t"] = None # It will be after init()
            alrt_job = Job(self.raxml_bin, alrt_args,
                           parent_ids=[tree_job.jobid], jobname="raxml-alrt")       
            alrt_job.dependencies.add(tree_job)
            alrt_job.cores = self.threads
            self.jobs.append(alrt_job)

        elif self.compute_alrt == "phyml":
            alrt_args = {
                "-o": "n",
                "-i": self.alg_phylip_file,
                "--bootstrap": "-2",
                "-d": self.seqtype,
                "-u": None,
                "--model": self.model,
                "--quiet": "",
                "--no_memory_check": "",
                }

            #if self.constrain_tree:
            #    alrt_args["--constraint_tree"] = self.constrain_tree
               
            alrt_job = Job(self.conf["app"]["phyml"], alrt_args,
                           parent_ids=[tree_job.jobid], jobname="phyml-alrt")
            alrt_job.dependencies.add(tree_job)
            self.jobs.append(alrt_job)

    def finish(self):
        #first job is the raxml tree
        def parse_alrt(match):
            dist = match.groups()[0]
            support = float(match.groups()[1])/100.0
            return "%g:%s" %(support, dist)
         
        if self.compute_alrt:
            if self.compute_alrt == "phyml":
                for fname in glob(self.alg_phylip_file+"_phyml*"):
                    shutil.move(fname, self.jobs[1].jobdir)
                shutils.copy(self.alrt_tree_file, self.tree_file)
            else:
                tree = open(self.alrt_tree_file).read().replace("\n", "")
                nw = re.subn(":(\d+\.\d+)\[(\d+)\]", parse_alrt, tree, re.MULTILINE)
                open(self.tree_file, "w").write(nw[0])
        else:
            shutil.copy(self.ml_tree_file, self.tree_file)

        TreeTask.finish(self)
        
