# -*- coding: utf-8 -*-
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
from six.moves import map
log = logging.getLogger("main")

from ..master_task import AlgCleanerTask
from ..master_job import Job
from ..utils import SeqGroup, GLOBALS, hascontent, DATATYPES, pjoin
from .. import db

__all__ = ["PyTrimal"]

class PyTrimal(AlgCleanerTask):
    def __init__(self, nodeid, seqtype, alg_fasta_file, alg_phylip_file,
                 conf, confname):
        #GLOBALS["citator"].add('Trimal')

        self.confname = confname
        self.conf = conf
        self.seqtype = seqtype
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        base_args = {
            '-in': None,
            '-out': None,
            '-fasta': "",
            '-colnumbering': "",
            }
        # Initialize task
        AlgCleanerTask.__init__(self, nodeid, "acleaner", "PyTrimal",
                                base_args,
                                self.conf[confname])

        self.init()

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = self.args.copy()
        args["-i"] = pjoin(GLOBALS["input_dir"], self.alg_fasta_file)
        args["-o"] = "clean.alg.fasta"
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.alg_fasta_file)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format. Both files, fasta and phylip,
        # remain accessible.

        # Set Task specific attributes
        main_job = self.jobs[0]
        fasta_path = pjoin(main_job.jobdir, "clean.alg.fasta")
        columns_path = pjoin(main_job.jobdir, "clean.alg.fasta.kept_columns")
        alg = SeqGroup(fasta_path)
        with open(columns_path) as COLS:
            kept_columns = list(map(int, COLS.readline().split(",")))
        fasta = alg.write(format="fasta")
        phylip = alg.write(format="iphylip_relaxed")
        AlgCleanerTask.store_data(self, fasta, phylip, kept_columns)
