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
import logging
log = logging.getLogger("main")

from ete2.tools.phylobuild_lib.master_task import MsfTask
from ete2.tools.phylobuild_lib.master_job import Job
from ete2.tools.phylobuild_lib.utils import (PhyloTree, SeqGroup, md5, generate_node_ids,
                          hascontent, pjoin, DATATYPES)
from ete2.tools.phylobuild_lib.errors import DataError

from ete2.tools.phylobuild_lib import db

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
        # Dump sequences into MSF
        all_seqs = self.target_seqs | self.out_seqs
        fasta = '\n'.join([">%s\n%s" % (n, db.get_seq(n, self.seqtype))
                               for n in all_seqs])
        MsfTask.store_data(self, fasta)
  
        
