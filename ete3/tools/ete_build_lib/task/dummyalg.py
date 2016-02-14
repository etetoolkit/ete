from __future__ import absolute_import
import os
import sys
import logging
log = logging.getLogger("main")

from ..master_task import AlgTask
from ..master_job import Job
from .. import db
from ..utils import (read_fasta, OrderedDict, GLOBALS, pjoin, SeqGroup)
from ..errors import TaskError

__all__ = ["ManualAlg"]

class ManualAlg(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        base_args = {}
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "ManualAlg",
                         base_args, {})

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.init()

    def load_jobs(self):
        pass
    
    def finish(self):
        # Uses the original MSF file as alignment
        alg_file = os.path.join(self.multiseq_file)
        try:
            _tid, _did = alg_file.split(".")
            _did = int(_did)
        except (IndexError, ValueError):
            dataid = alg_file
        else:
            dataid = db.get_dataid(_tid, _did)
        alg = SeqGroup(db.get_data(dataid))

        lengths = set([len(seq) for seq in alg.id2seq.values()])
        if len(lengths) > 1:
            raise TaskError("Original sequences are not aligned!")            
        
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)
