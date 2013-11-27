import os
import sys
import re
import shutil

import logging
log = logging.getLogger("main")

from nprlib.master_task import TreeTask
from nprlib.master_job import Job
from nprlib.utils import (basename, GLOBALS, DATATYPES)
from nprlib import db

__all__ = ["DummyTree"]

class DummyTree(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_id, model, seqtype,
                 conf, confname, parts_id=None):
        self.confname = confname
        self.conf = conf
        self.alg_phylip_file = alg_file
        self.constrain_tree = None
        if constrain_id:
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_alg)
        self.alg_basename = basename(self.alg_phylip_file)
        self.seqtype = seqtype
        self.tree_file = ""
        self.model = None
        self.lk = None

        TreeTask.__init__(self, nodeid, "tree", "DummyTree", {}, {})
        self.init()
        
    def load_jobs(self):
        pass
    
    def finish(self):
        node_info = GLOBALS["nodeinfo"][self.nodeid]
        target_seqs = node_info.get("target_seqs", set())
        out_seqs = node_info.get("out_seqs", set())
        all_seqs = list(target_seqs | out_seqs)
        newick = "(%s, (%s));" %(all_seqs[0], ','.join(all_seqs[1:]))
        print newick
        TreeTask.store_data(self, newick, {})

