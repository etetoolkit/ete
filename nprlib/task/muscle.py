import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, OrderedDict, GLOBALS

__all__ = ["Muscle"]

class Muscle(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf):
        GLOBALS["citator"].add("Edgar RC.",
                               "MUSCLE: multiple sequence alignment with high accuracy and high throughput.",
                               "Nucleic Acids Res. 2004 Mar 19;32(5):1792-7.")

        # fixed Muscle options
        base_args = OrderedDict({
                '-in': None,
                '-out': None,
                })
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Muscle", 
                      base_args, conf["muscle"])

        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file

        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args["-in"] = self.multiseq_file
        args["-out"] = "alg.fasta"
        job = Job(self.conf["app"]["muscle"], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        AlgTask.finish(self)

