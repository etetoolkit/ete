# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
import os
import sys
import re
import shutil

import logging
log = logging.getLogger("main")

from ete2.tools.phylobuild_lib.master_task import TreeTask
from ete2.tools.phylobuild_lib.master_job import Job
from ete2.tools.phylobuild_lib.utils import (basename, GLOBALS, DATATYPES)
from ete2.tools.phylobuild_lib import db

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
        node_info = self.conf["_nodeinfo"][self.nodeid]
        
        target_seqs = node_info.get("target_seqs", set())
        out_seqs = node_info.get("out_seqs", set())
        all_seqs = list(target_seqs | out_seqs)
        
        newick = "(%s, (%s));" %(all_seqs[0], ','.join(all_seqs[1:]))
        
        TreeTask.store_data(self, newick, {})

