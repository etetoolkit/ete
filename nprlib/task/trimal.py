# -*- coding: utf-8 -*-
import os
import sys
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgCleanerTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, GLOBALS, TRIMAL_CITE, hascontent, DATATYPES, pjoin
from nprlib.errors import RetryException

__all__ = ["Trimal"]

class Trimal(AlgCleanerTask):
    def __init__(self, nodeid, seqtype, alg_fasta_file, alg_phylip_file,
                 conf, confname):
        GLOBALS["citator"].add(TRIMAL_CITE)
                               
        self.confname = confname
        self.conf = conf
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
                                self.conf[confname])

        self.init()
        

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = self.args.copy()
        args["-in"] = pjoin(GLOBALS["input_dir"], self.alg_fasta_file)
        args["-out"] = "clean.alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.alg_fasta_file)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.

        # Set Task specific attributes
        main_job = self.jobs[0]
        fasta_path = pjoin(main_job.jobdir, "clean.alg.fasta")
        alg = SeqGroup(fasta_path)
        if len(alg) != self.size:
            log.warning("Trimming was to aggressive and it tried"
                        " to remove one or more sequences."
                        " Alignment trimming will be disabled for this dataset."
                        )
            db.register_task_data(self.taskid, DATATYPES.clean_alg_fasta, self.alg_fasta_file)
            db.register_task_data(self.taskid, DATATYPES.clean_alg_phylip, self.alg_phylip_file)
        else:
            for line in open(self.jobs[0].stdout_file):
                line = line.strip()
                if line.startswith("#ColumnsMap"):
                    kept_columns = map(int, line.split("\t")[1].split(","))
            fasta = alg.write(format="fasta")
            phylip = alg.write(format="iphylip_relaxed")
            AlgCleanerTask.store_data(self, fasta, phylip, kept_columns)
