import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, OrderedDict, GLOBALS, MAFFT_CITE
from nprlib import db

__all__ = ["Mafft"]

class Mafft(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add(MAFFT_CITE)
        
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Mafft", 
                      OrderedDict(), self.conf[confname])

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file     
        self.init()

        # Expected outputs
        self.alg_fasta_file = None
        self.alg_phylip_file = None
 
    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        # Mafft redirects resulting alg to std.output. The order of
        # arguments is important, input file must be the last
        # one.
        args[""] = pjoin(GLOBALS["input_dir"], self.multiseq_file)
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.input_files.add(self.multiseq_file)
        job.cores = self.conf["threading"][appname]
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. 
        alg = SeqGroup(self.jobs[0].stdout_file)
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
       
        AlgTask.store_data(self, fasta, phylip)
