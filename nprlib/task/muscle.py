import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import (SeqGroup, OrderedDict, GLOBALS, MUSCLE_CITE,
                          hascontent, pjoin)

__all__ = ["Muscle"]

class Muscle(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add(MUSCLE_CITE)

        # fixed Muscle options
        base_args = OrderedDict({
                '-in': None,
                '-out': None,
                })
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Muscle", 
                      base_args,  self.conf[confname])

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file

        self.init()

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args["-in"] = pjoin(GLOBALS["input_dir"], self.multiseq_file)
        args["-out"] = "alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.input_files.add(self.multiseq_file)
        self.jobs.append(job)

    def finish(self):
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)

