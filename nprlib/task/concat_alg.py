import os
import re
import logging
log = logging.getLogger("main")

from nprlib.task import Msf
from nprlib.master_task import ConcatAlgTask
from nprlib.master_job import Job
from nprlib.utils import basename, PhyloTree, GLOBALS, generate_runid


__all__ = ["ConcatAlg"]

class ConcatAlg(ConcatAlgTask):
    def __init__(self, nodeid, cogs, ourgroups, seqtype, source):
        base_args = {}
        ConcatAlgTask.__init__(self, nodeid, "concat_alg", "ConcatAlg", 
                      base_args)
        self.cogs = cogs
        self.cladeid = "UNSET"
        self.seqtype = seqtype
        self.source = source
        self.alg_fasta_file = ""
        self.alg_phylip_file = ""
        self.init()

    def load_jobs(self):
        from nprlib.template.genetree import pipeline
        for co in self.cogs:
            # get sequences
            #db.get_sequences(co)
            pass
            
            # write fasta for each co
            pass
            
            # register each msf task
            job = Msf(co, set(),
                      seqtype = self.seqtype,
                      source = self.source)

            # This converts the job in a workflow job. AS soon as task
            # is done, it will be processed and new tasks will be
            # registered as new jobs.
            job.main_tree = None
            job.task_processor = pipeline
            job.threadid = generate_runid()
            self.jobs.append(job) 

    def finish(self):
        log.info("finishing CONCAT ALG....")
        # concat all single alignments into one file
        pass

        
        
