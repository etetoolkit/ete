import os
import logging
log = logging.getLogger("main")

from nprlib.master_task import MsfTask
from nprlib.master_job import Job
from nprlib.utils import PhyloTree, SeqGroup, md5, generate_node_ids, hascontent, pjoin
from nprlib.errors import DataError

from nprlib import db

__all__ = ["Msf"]

class Msf(MsfTask):
    def __init__(self, target_seqs, out_seqs, seqtype):
        # Nodeid represents the whole group of sequences (used to
        # compute task unique ids). Cladeid represents target
        # sequences. Same cladeid with different outgroups would mean
        # an independent set of tasks.
        node_id, clade_id = generate_node_ids(target_seqs, out_seqs)
        # Initialize task
        MsfTask.__init__(self, node_id, "msf", "MSF")

        # taskid does not depend on jobs, so I set it manually
        self.taskid = node_id
        self.init()

        # Set basic information
        self.multiseq_file = os.path.join(self.taskdir, "msf.fasta")
        self.nodeid = node_id
        self.cladeid = clade_id
        self.seqtype = seqtype
        self.target_seqs = target_seqs
        self.out_seqs = out_seqs
        if out_seqs & target_seqs:
            log.error(out_seqs)
            log.error(target_seqs)
            raise DataError("Outgroup seqs included in target seqs.")
        all_seqs = self.target_seqs | self.out_seqs
        self.size = len(all_seqs)


    def finish(self):
        if hascontent(self.multiseq_file):
            log.log(24, "@@8:Reusing MSF file@@1:")
        else:
            # Dump sequences into MSF
            all_seqs = self.target_seqs | self.out_seqs
            fasta = '\n'.join([">%s\n%s" % (n, db.get_seq(n, self.seqtype))
                               for n in all_seqs])
            open(self.multiseq_file, "w").write(fasta)           
            
    def check(self):
        if os.path.exists(self.multiseq_file):
            return True
        return False
