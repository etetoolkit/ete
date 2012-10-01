import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, OrderedDict, GLOBALS

__all__ = ["Dialigntx"]

class Dialigntx(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf):
        GLOBALS["citator"].add("Subramanian AR, Kaufmann M, Morgenstern B.",
                               "DIALIGN-TX: greedy and progressive approaches for segment-based multiple sequence alignment.",
                               "Algorithms Mol Biol. 2008 May 27;3:6. PubMed PMID: 18505568.")
        
        # fixed options for running this task
        base_args = OrderedDict({
                '': None,
                })
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "DialignTX", 
                      base_args, conf["dialigntx"])
        
        self.conf = conf
        self.seqtype = seqtype
        self.multiseq_file = multiseq_file

        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

    def load_jobs(self):
        # Only one Muscle job is necessary to run this task
        args = self.args.copy()
        args[''] = "%s %s" %(self.multiseq_file, "alg.fasta")
        job = Job(self.conf["app"]["dialigntx"], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        AlgTask.finish(self)
