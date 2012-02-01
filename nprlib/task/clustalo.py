import os
import sys
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job

from nprlib.utils import read_fasta, OrderedDict

__all__ = ["Clustalo"]

class Clustalo(AlgTask):
    def __init__(self, cladeid, multiseq_file, seqtype, conf):
        if seqtype != "aa":
            raise ValueError("Clustal Omega does only support aa seqtype")
        
        base_args = OrderedDict({
                '-i': None,
                '-o': None,
                '--outfmt': "fa",
                })
        # Initialize task
        AlgTask.__init__(self, cladeid, "alg", "Clustal-Omega", 
                      base_args, conf["clustalo"])

        self.conf = conf
        self.seqtype = "aa" # only aa supported
        self.multiseq_file = multiseq_file

        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args["-i"] = self.multiseq_file
        args["-o"] = "alg.fasta"
        job = Job(self.conf["app"]["clustalo"], args, parent_ids=[self.cladeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg_file = os.path.join(self.jobs[0].jobdir, "alg.fasta")
        # ClustalO returns a tricky fasta file
        alg = read_fasta(alg_file, header_delimiter=" ")
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        AlgTask.finish(self)
