from __future__ import absolute_import
import os
import logging
log = logging.getLogger("main")

from ..master_task import AlgTask
from ..master_job import Job
from ..utils import (SeqGroup, OrderedDict, pjoin,
                     GLOBALS, DATATYPES)
from .. import db

__all__ = ["TCoffee"]

class TCoffee(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        self.confname = confname
        self.conf = conf
        # Initialize task
        task_name =   "TCoffee(-%s)" %conf["-mode"] if "-mode" in conf else "TCoffee"
        AlgTask.__init__(self, nodeid, "alg", task_name,
                         OrderedDict(), self.conf[self.confname])
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.size = conf["_nodeinfo"][nodeid].get("size", 0)
        self.init()

    def load_jobs(self):
        args = OrderedDict()
        args[""] = pjoin(GLOBALS["input_dir"], self.multiseq_file)
        for k, v in self.args.items():
            args[k] = v
        args["-outfile"] = "mcoffee.fasta" 
        job = Job(self.conf["app"]["tcoffee"], args, parent_ids=[self.nodeid])
        job.add_input_file(self.multiseq_file)
        job.cores = self.conf["threading"]["tcoffee"]
        self.jobs.append(job)
        
    def finish(self):
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "mcoffee.fasta"))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)
