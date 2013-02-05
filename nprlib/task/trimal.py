# -*- coding: utf-8 -*-
import os
import sys
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgCleanerTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, GLOBALS, TRIMAL_CITE
from nprlib.errors import RetryException

__all__ = ["Trimal"]

class Trimal(AlgCleanerTask):
    def __init__(self, nodeid, seqtype, alg_fasta_file, alg_phylip_file, confname):
        GLOBALS["citator"].add(TRIMAL_CITE)
                               
        self.confname = confname
        self.seqtype = seqtype
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.kept_columns = []
        base_args = {
            '-in': None,
            '-out': None,
            '-fasta': "", 
            '-colnumbering': "", 
            }
        # Initialize task
        AlgCleanerTask.__init__(self, nodeid, "acleaner", "Trimal",
                                base_args,
                                GLOBALS["config"][confname])

        self.init()
        
        # Set Task specific attributes
        main_job = self.jobs[0]
        self.clean_alg_fasta_file = os.path.join(main_job.jobdir, "clean.alg.fasta")
        self.clean_alg_phylip_file = os.path.join(main_job.jobdir, "clean.alg.iphylip")

    def load_jobs(self):
        conf = GLOBALS["config"]
        appname = conf[self.confname]["_app"]
        args = self.args.copy()
        args["-in"] = self.alg_fasta_file
        args["-out"] = "clean.alg.fasta"
        job = Job(conf["app"][appname], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.clean_alg_fasta_file)
        if len(alg) != self.size:
            log.warning("Trimming is to aggressive and it tried"
                        " to remove one or more sequences."
                        " Alignment trimming will be disabled for this dataset."
                        )
            alg = SeqGroup(self.alg_fasta_file)
            alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")
            alg.write(outfile=self.clean_alg_fasta_file, format="fasta")
        else:
            for line in open(self.jobs[0].stdout_file):
                line = line.strip()
                if line.startswith("#ColumnsMap"):
                    self.kept_columns = map(int, line.split("\t")[1].split(","))
            alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")
            
        AlgCleanerTask.finish(self)
