# -*- coding: utf-8 -*-
import os
import sys
import logging
log = logging.getLogger("main")

from nprlib.master_task import AlgCleanerTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, GLOBALS
from nprlib.errors import RetryException

__all__ = ["Trimal"]

class Trimal(AlgCleanerTask):
    def __init__(self, nodeid, seqtype, alg_fasta_file, alg_phylip_file, conf):
        GLOBALS["citator"].add(u"Capella-Gutiérrez S, Silla-Martínez JM, Gabaldón T.",
                               "trimAl: a tool for automated alignment trimming in large-scale phylogenetic analyses.",
                               "Bioinformatics. 2009 Aug 1;25(15):1972-3. Epub 2009 Jun 8. PubMed PMID: 19505945;")
                               
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
                      base_args, conf["trimal"])

        self.init()
        
        # Set Task specific attributes
        main_job = self.jobs[0]
        self.clean_alg_fasta_file = os.path.join(main_job.jobdir, "clean.alg.fasta")
        self.clean_alg_phylip_file = os.path.join(main_job.jobdir, "clean.alg.iphylip")

    def load_jobs(self):
        args = self.args.copy()
        args["-in"] = self.alg_fasta_file
        args["-out"] = "clean.alg.fasta"
        job = Job(self.conf["app"]["trimal"], args, parent_ids=[self.nodeid])
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.
        alg = SeqGroup(self.clean_alg_fasta_file)
        if len(alg) != self.size:
            log.warning("Trimming was to aggressive and some"
                        " sequences were removed. Params will"
                        " be changed to keep at least 50% of the alg")
            self.jobs[0].args["-cons"]="50"
            self.jobs[0].status="W"
            self.status = "W"
            raise RetryException("")
        else:
            for line in open(self.jobs[0].stdout_file):
                line = line.strip()
                if line.startswith("#ColumnsMap"):
                    self.kept_columns = map(int, line.split("\t")[1].split(","))
            alg.write(outfile=self.clean_alg_phylip_file, format="iphylip_relaxed")
            AlgCleanerTask.finish(self)
