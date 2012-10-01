import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, OrderedDict, GLOBALS

__all__ = ["Mafft"]

class Mafft(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf):
        GLOBALS["citator"].add("Katoh K, Kuma K, Toh H, Miyata T.",
                               "MAFFT version 5: improvement in accuracy of multiple sequence alignment.",
                               "Nucleic Acids Res. 2005 Jan 20;33(2):511-8.")
        
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Mafft", 
                      OrderedDict(), conf["mafft"])

        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file     
        self.init()

        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")
 
    def load_jobs(self):
        args = self.args.copy()
        # Mafft redirects resulting alg to std.output. The order of
        # arguments is important, input file must be the last
        # one.
        args[""] = self.multiseq_file
        job = Job(self.conf["app"]["mafft"], args, parent_ids=[self.nodeid])
        job.cores = self.conf["threading"]["mafft"]
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. 
        alg = SeqGroup(self.jobs[0].stdout_file)
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        AlgTask.finish(self)
