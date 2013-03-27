import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, OrderedDict, GLOBALS, DIALIGN_CITE, pjoin

__all__ = ["Dialigntx"]

class Dialigntx(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add(DIALIGN_CITE)
        
        # fixed options for running this task
        base_args = OrderedDict({
                '': None,
                })
        # Initialize task
        self.confname = confname
        self.conf = conf
        AlgTask.__init__(self, nodeid, "alg", "DialignTX", 
                      base_args, self.conf[self.confname])
        

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.init()

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args[''] = "%s %s" %(pjoin(GLOBALS["input_dir"], self.multiseq_file),
                             "alg.fasta")
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.multiseq_file)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)
