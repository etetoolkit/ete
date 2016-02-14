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
from __future__ import absolute_import
import os
import sys
import logging
log = logging.getLogger("main")

from ..master_task import AlgTask
from ..master_job import Job

from ..utils import (read_fasta, OrderedDict, GLOBALS, pjoin)

__all__ = ["Clustalo"]

class Clustalo(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add('clustalo')

        base_args = OrderedDict({
                '-i': None,
                '-o': None,
                '--outfmt': "fa",
                })
        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Clustal-Omega",
                      base_args, self.conf[self.confname])


        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.init()

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        # Only one Muscle job is necessary to run this task
        args = OrderedDict(self.args)
        args["-i"] = pjoin(GLOBALS["input_dir"], self.multiseq_file)
        args["-o"] = "clustalo_alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.cores = self.conf["threading"].get(appname, 1)
        job.add_input_file(self.multiseq_file)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg_file = os.path.join(self.jobs[0].jobdir, "clustalo_alg.fasta")
        # ClustalO returns a tricky fasta file
        alg = read_fasta(alg_file, header_delimiter=" ")
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)

