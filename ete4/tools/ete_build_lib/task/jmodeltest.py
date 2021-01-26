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
import logging
log = logging.getLogger("main")

from ..master_task import ModelTesterTask
from ..master_job import Job
from ..utils import basename, PhyloTree

__all__ = ["JModeltest"]

class JModeltest(ModelTesterTask):
    def __init__(self, nodeid, alg_fasta_file, alg_phylip_file, conf):
        GLOBALS["citator"].add('jmodeltest')

        self.conf = conf
        base_args = {
            '-d': alg_fasta_file,
            }
        args = self.conf["jmodeltest"]
        if args.get("-t", "ML") == "ML":
            task_type = "tree"
        else:
            task_type = "mchooser"

        ModelTesterTask.__init__(self, nodeid, task_type, "Jmodeltest",
                                 base_args, self.conf[confname])

        # set app arguments and options
        self.alg_fasta_file = alg_fasta_file
        self.alg_phylip_file = alg_phylip_file
        self.seqtype = "nt"
        self.models = "see jmodeltest params"

        self.init()
        self.best_model_file = os.path.join(self.taskdir, "best_model.txt")
        if task_type == "tree":
            self.tree_file = os.path.join(self.taskdir, "final_tree.nw")
        else:
            self.tree_file = None


    def load_jobs(self):
        tree_job = Job(self.conf["app"]["jmodeltest"], self.args, parent_ids=[self.nodeid])
        self.jobs.append(tree_job)

    def finish(self):
        # first job is the raxml tree
        best_model = None
        best_model_in_next_line = False
        t = None
        for line in open(self.jobs[-1].stdout_file, "r"):
            line = line.strip()
            if best_model_in_next_line and line.startswith("Model"):
                pass#best_model = line.split("=")[1].strip()
            elif best_model_in_next_line and line.startswith("partition"):
                best_model = line.split("=")[1].strip()
                best_model_in_next_line = False
            elif line.startswith("Model selected:"):
                best_model_in_next_line = True
            elif line.startswith("ML tree (NNI) for the best AIC model ="):
                nw = line.replace("ML tree (NNI) for the best AIC model =", "")
                t = PhyloTree(nw)

        open(self.best_model_file, "w").write(best_model)
        log.log(26, "Best model: %s" %best_model)
        if self.ttype == "tree":
            tree_job = self.jobs[-1]
            tree_file =  os.path.join(tree_job.jobdir,
                                      "jModelTest_tree."+self.nodeid)
            t.write(outfile=self.tree_file)
            self.model = best_model


        ModelTesterTask.finish(self)
