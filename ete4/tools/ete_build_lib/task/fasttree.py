from __future__ import absolute_import
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

from ..master_task import TreeTask
from ..master_job import Job
from ..utils import (basename, Tree, OrderedDict, GLOBALS, DATATYPES, pjoin)
from .. import db
__all__ = ["FastTree"]

class FastTree(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_id, model, seqtype,
                 conf, confname, parts_id=None):
        GLOBALS["citator"].add('fasttree')

        self.confname = confname
        self.conf = conf
        self.alg_phylip_file = alg_file
        self.constrain_tree = None
        if constrain_id:
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_alg)
        self.alg_basename = basename(self.alg_phylip_file)
        self.seqtype = seqtype
        self.tree_file = ""
        if model:
            log.warning("FastTree does not support model selection")

        self.model = None
        self.lk = None

        base_args = OrderedDict()
        base_args["-nopr"] = ""
        if self.seqtype == "nt":
            base_args["-gtr -nt"] = ""
        elif self.seqtype == "aa":
            pass
        else:
            raise ValueError("Unknown seqtype %s" %self.seqtype)

        TreeTask.__init__(self, nodeid, "tree", "FastTree", base_args,
                          self.conf[confname])

        self.init()

    def load_jobs(self):
        args = self.args.copy()

        try:
            del args["-wag"]
        except KeyError:
            pass

        if self.constrain_tree:
            args["-constraints"] = pjoin(GLOBALS["input_dir"], self.constrain_tree)

        args[pjoin(GLOBALS["input_dir"], self.alg_phylip_file)] = ""
        appname = self.conf[self.confname]["_app"]

        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.cores = self.conf["threading"][appname]
        if self.constrain_tree:
            job.add_input_file(self.constrain_tree)
        job.add_input_file(self.alg_phylip_file)
        self.jobs.append(job)

    def finish(self):
        job = self.jobs[-1]
        t = Tree(job.stdout_file)
        TreeTask.store_data(self, t.write(), {})

