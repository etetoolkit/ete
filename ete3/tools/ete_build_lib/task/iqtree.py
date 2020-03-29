from __future__ import absolute_import
import os
import shutil
import sys
import re

import logging
log = logging.getLogger("main")

from ..master_task import TreeTask
from ..errors import TaskError,ConfigError
from ..master_job import Job
from ..utils import basename, PhyloTree, OrderedDict, GLOBALS,  DATATYPES
from .. import db

__all__ = ["IQTree"]

class IQTree(TreeTask):
    def __init__(self, nodeid, alg_phylip_file, constrain_id, model,
                 seqtype, conf, confname, parts_id=None):

        GLOBALS["citator"].add('iqtree')

        if constrain_id:
            raise ConfigError("IQTree does not support topology constraints")
        
        base_args = {}
        if "-st" not in conf[confname]:
            base_args["-st"] = "AA" if seqtype == "aa" else "DNA"            
        else:
            if conf[confname]["-st"].startswith("CODON"):
                if seqtype == "aa" or "aa" not in GLOBALS["seqtypes"]: 
                    raise ConfigError("IQTREE CODON models require a codon alignment.\nProvide nucleotide sequences with '-n' and set '--nt-switch-thr 0.0' to ensure codon alignments.")
            
        if model:
            raise TaskError('External model selection not yet supported for IQTree')
        else:
            if "-m" in conf[confname]:
                model = conf[confname]["-m"]
            elif conf[confname].get("-st", "").startswith("CODON"):
                model = "defaultCODON"
            elif seqtype == "aa":
                model = "WAG"
            elif seqtype == "nt":
                model = "HKY"
                
        self.model = model
        self.confname = confname
        self.conf = conf
        self.constrain_tree = None
        self.alg_phylip_file = alg_phylip_file
        self.seqtype = seqtype
        self.lk = None
        
        TreeTask.__init__(self, nodeid, "tree", "IQTree",
                          base_args, conf[confname])  
                  
        self.init()

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args['-s'] = self.alg_phylip_file            
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.alg_phylip_file, job.jobdir)
        
        job.jobname += "-"+self.model.replace(' ', '')
        self.jobs.append(job)

    def finish(self):
        j = self.jobs[0]
        tree_file = os.path.join(j.jobdir,
                                 self.alg_phylip_file+".treefile")
        stats_file = os.path.join(j.jobdir,
                                  self.alg_phylip_file+".iqtree")

        m = re.search('Log-likelihood of the tree:\s+(-?\d+\.\d+)',
                      open(stats_file).read())
        lk = float(m.groups()[0])
        stats = {"lk": lk}
        tree = PhyloTree(tree_file)
        self.store_data(tree.write(), stats)

