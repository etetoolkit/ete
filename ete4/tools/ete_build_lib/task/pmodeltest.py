from __future__ import absolute_import
import os
import re
import logging
import shutil
from six.moves import map
log = logging.getLogger("main")

from ..master_task import ModelTesterTask
from ..master_job import Job
from ..utils import basename, PhyloTree, GLOBALS, pjoin

__all__ = ["PModelTest"]

class PModelTest(ModelTesterTask):
    def __init__(self, nodeid, alg_fasta_file, alg_phylip_file,
                 constrain_tree, seqtype, conf, confname):
        GLOBALS["citator"].add('phyml')

        self.alg_phylip_file = alg_phylip_file
        self.alg_fasta_file = alg_fasta_file
        self.confname = confname
        self.conf = conf
        self.seqtype = seqtype
        base_args = {}
        if seqtype == "aa":
            base_args["--protein"] = ""
            base_args["-m"] = conf[confname]["_aa_models"]
            self.models = conf[confname]["_aa_models"]
        else:
            base_args["-m"] = conf[confname]["_nt_models"]
            self.models = conf[confname]["_nt_models"]
        task_name = "PModelTest-[%s]" %self.models
        
        ModelTesterTask.__init__(self, nodeid, "mchooser", task_name,
                                 base_args, conf[confname])

        self.best_model = None
        self.init()

    def load_jobs(self):
        args = self.args.copy()
        args["-i"] = pjoin(GLOBALS["input_dir"], self.alg_phylip_file)
        args["--outtable"] = "pmodeltest.txt"
        appname = self.conf[self.confname]["_app"]
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.cores = self.conf["threading"][appname]
        job.add_input_file(self.alg_phylip_file)
        self.jobs.append(job)

    def finish(self):
        main_job = self.jobs[0]
        aic_table = pjoin(main_job.jobdir, "pmodeltest.txt")        
        best = open(aic_table).readline().split('\t')        
        best_model = "pmodeltest-%s" %(best[0].strip())
        if "--nogam" not in self.args and "+G" not in best_model:
            best_model += "!G"
        if "--nofrq" not in self.args and "+F" not in best_model:
            best_model += "!F"            
        if "--noinv" not in self.args and "+I" not in best_model:
            best_model += "!I"
                
        log.log(22, "%s model selection output:\n%s" %(best_model, open(aic_table).read()))
        ModelTesterTask.store_data(self, best_model, aic_table)





