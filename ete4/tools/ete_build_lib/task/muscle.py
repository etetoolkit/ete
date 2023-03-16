import os
import logging
log = logging.getLogger("main")

from ..master_task import AlgTask
from ..master_job import Job
from ..utils import (SeqGroup, OrderedDict, GLOBALS, hascontent, pjoin)

__all__ = ["Muscle"]

class Muscle(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add('muscle')

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
        args["-out"] = "muscle_alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.multiseq_file)
        self.jobs.append(job)

    def finish(self):
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "muscle_alg.fasta"))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)
