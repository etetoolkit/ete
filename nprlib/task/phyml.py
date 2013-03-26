import os
import shutil
import sys
import re

import logging
log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, OrderedDict, GLOBALS, PHYML_CITE

__all__ = ["Phyml"]

class Phyml(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_tree, model,
                 seqtype, conf, confname):

        GLOBALS["citator"].add(PHYML_CITE)
        
        base_args = OrderedDict({
                "--model": "", 
                "--no_memory_check": "", 
                "--quiet": "",
                "--constraint_tree": ""})
        
        self.confname = confname
        self.conf = conf
        self.constrain_tree = constrain_tree
        self.alg_phylip_file = alg_file
        TreeTask.__init__(self, nodeid, "tree", "Phyml", 
                          base_args, conf[confname])
        self.alg_basename = basename(self.alg_phylip_file)
        if seqtype == "aa":
            self.model = model or conf[confname]["_aa_model"]
        elif seqtype == "nt":
            self.model = model or conf[confname]["_nt_model"]
        self.seqtype = seqtype
        self.lk = None

        self.init()
     
        # Phyml cannot write the output in a different directory that
        # the original alg file. So I use relative path to alg file
        # for processes and I create a symlink for each of the
        # instances.
        j = self.jobs[0]
        fake_alg_file = os.path.join(j.jobdir, self.alg_basename)
        try:
            os.remove(fake_alg_file)
        except OSError:
            pass
        try: # symlink does not work on windows 
            os.symlink(self.alg_phylip_file, fake_alg_file)
        except OSError:
            log.warning("Unable to create symbolic links. Duplicating files instead")
            shutil.copy(self.alg_phylip_file, fake_alg_file)
            
    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args["--model"] = self.model
        args["--datatype"] = self.seqtype
        args["--input"] = self.alg_basename
        if self.constrain_tree:
            args["--constraint_tree"] = self.constrain_tree
            args["-u"] = self.constrain_tree
        else:
            del args["--constraint_tree"]
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.jobname += "-"+self.model
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
        tree.write(outfile=tree_file)
        TreeTask.finish(self)
 
    
