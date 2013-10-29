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
    def __init__(self, nodeid, alg_phylip_file, constrain_id, model,
                 seqtype, conf, confname, parts_id=None):

        GLOBALS["citator"].add(PHYML_CITE)
        
        base_args = OrderedDict({
                "--model": "", 
                "--no_memory_check": "", 
                "--quiet": "",
                "--constraint_tree": ""})
        
        self.confname = confname
        self.conf = conf
        self.constrain_tree = None
        if constrain_id:
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_tree)
        self.alg_phylip_file = alg_phylip_file
        
        TreeTask.__init__(self, nodeid, "tree", "Phyml", 
                          base_args, conf[confname])

        if seqtype == "aa":
            self.model = model or conf[confname]["_aa_model"]
        elif seqtype == "nt":
            self.model = model or conf[confname]["_nt_model"]
        self.seqtype = seqtype
        self.lk = None

        self.init()
            
    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args["--model"] = self.model
        args["--datatype"] = self.seqtype
        args["--input"] = self.alg_phylip_file
        if self.constrain_tree:
            args["--constraint_tree"] = self.constrain_tree
            args["-u"] = self.constrain_tree
        else:
            del args["--constraint_tree"]
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.alg_phylip_file, job.jobdir)
        if self.constrain_tree:
            job.add_input_file(self.constrain_tree, job.jobdir)
        job.jobname += "-"+self.model
        self.jobs.append(job)

    def finish(self):
        lks = []
        j = self.jobs[0]
        tree_file = os.path.join(j.jobdir,
                                 self.alg_phylip_file+"_phyml_tree.txt")
        stats_file = os.path.join(j.jobdir,
                                  self.alg_phylip_file+"_phyml_stats.txt")

        m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                      open(stats_file).read())
        lk = float(m.groups()[0])
        stats = {"lk": lk}
        tree = PhyloTree(tree_file)        
        TreeTask.store_data(self, tree.write(), stats)
 
