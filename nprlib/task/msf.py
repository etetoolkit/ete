import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import Task
from nprlib.master_job import Job
from nprlib.utils import get_cladeid, PhyloTree, SeqGroup

__all__ = ["Msf"]

class Msf(Task):
    def __init__(self, cladeid, seed_file, seqtype, format="fasta"):
        # Set basic information
        self.seqtype = seqtype
        self.seed_file = seed_file
        self.seed_file_format = format
        self.msf = SeqGroup(self.seed_file, format=self.seed_file_format)
        self.nseqs = len(self.msf)
        msf_id = get_cladeid(self.msf.id2name.values())

        # Cladeid is created ignoring outgroup seqs. In contrast,
        # msf_id is calculated using all IDs present in the MSF. If no
        # cladeid is supplied, we can assume that MSF represents the
        # first iteration, so no outgroups must be ignored. Therefore,
        # cladeid=msfid
        if not cladeid:
            self.cladeid = msf_id
        else:
            self.cladeid = cladeid

        # Initialize task
        Task.__init__(self, self.cladeid, "msf", "MSF")

        # taskid does not depend on jobs, so I set it manually
        self.taskid = msf_id
        self.init()
        self.multiseq_file = os.path.join(self.taskdir, "msf.fasta")

    def finish(self):
        # Dump msf file to the correct path
        self.msf.write(outfile=self.multiseq_file)
        self.dump_inkey_file(self.seed_file)

    def check(self):
        if os.path.exists(self.multiseq_file):
            return True
        return False
