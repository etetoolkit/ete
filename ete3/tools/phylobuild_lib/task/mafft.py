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
import logging
log = logging.getLogger("main")

from ..master_task import AlgTask
from ..master_job import Job
from ..utils import SeqGroup, OrderedDict, GLOBALS, pjoin
from .. import db

__all__ = ["Mafft"]

class Mafft(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, conf, confname):
        GLOBALS["citator"].add('mafft')

        self.confname = confname
        self.conf = conf
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Mafft",
                      OrderedDict(), self.conf[confname])

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.init()

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        # Mafft redirects resulting alg to std.output. The order of
        # arguments is important, input file must be the last
        # one.
        args[""] = pjoin(GLOBALS["input_dir"], self.multiseq_file)
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.multiseq_file)
        job.cores = self.conf["threading"][appname]
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(self.jobs[0].stdout_file)
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgTask.store_data(self, fasta, phylip)
