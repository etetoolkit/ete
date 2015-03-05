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
import re
import logging
import shutil
log = logging.getLogger("main")

from ete2.tools.phylobuild_lib.master_task import ModelTesterTask
from ete2.tools.phylobuild_lib.master_job import Job
from ete2.tools.phylobuild_lib.utils import basename, PhyloTree, GLOBALS, PHYML_CITE, pjoin

__all__ = ["Prottest"]

class Prottest(ModelTesterTask):
    def __init__(self, nodeid, alg_fasta_file, alg_phylip_file,
                 constrain_tree, conf, confname):
        GLOBALS["citator"].add(PHYML_CITE)
        
        self.alg_phylip_file = alg_phylip_file
        self.alg_fasta_file = alg_fasta_file
        self.confname = confname
        self.conf = conf
        self.lk_mode = conf[confname]["_lk_mode"]
        if self.lk_mode == "raxml":
            phyml_optimization = "n"
        elif self.lk_mode == "phyml":
            phyml_optimization = "lr"
        else:
            raise ValueError("Choose a valid lk_mode value (raxml or phyml)")
        
        base_args = {
            "--datatype": "aa",
            "--input": self.alg_phylip_file,
            "--bootstrap": "0",
            "-o": phyml_optimization,
            "--model": None, # I will iterate over this value when
                             # creating jobs
            "--quiet": ""
            }
        self.models = conf[confname]["_models"]
        task_name = "Prottest-[%s]" %','.join(self.models)
        ModelTesterTask.__init__(self, nodeid, "mchooser", task_name, 
                      base_args, conf[confname])
        
        self.best_model = None
        self.seqtype = "aa"
        self.init()
                
    def load_jobs(self):
        conf = self.conf
        for m in self.models:
            args = self.args.copy()
            args["--model"] = m
            bionj_job = Job(conf["app"]["phyml"], args,
                      parent_ids=[self.nodeid])
            bionj_job.jobname += "-bionj-" + m
            bionj_job.jobcat = "bionj"
            bionj_job.add_input_file(self.alg_phylip_file, bionj_job.jobdir)
            self.jobs.append(bionj_job)

            if self.lk_mode == "raxml":
                raxml_args = {
                    "-f": "e", 
                    "-s": pjoin(bionj_job.jobdir, self.alg_phylip_file),
                    "-m": "PROTGAMMA%s" % m,
                    "-n": self.alg_phylip_file+"."+m,
                    "-t": pjoin(bionj_job.jobdir,
                                       self.alg_phylip_file+"_phyml_tree.txt")
                    }
                raxml_job = Job(conf["app"]["raxml"], raxml_args,
                                parent_ids=[bionj_job.jobid])
                raxml_job.jobname += "-lk-optimize"
                raxml_job.dependencies.add(bionj_job)
                raxml_job.model = m
                raxml_job.jobcat = "raxml"
                self.jobs.append(raxml_job)

    def finish(self):
        lks = []
        if self.lk_mode == "phyml":
            for job in self.jobs:
                if job.jobcat != "bionj": continue
                phyml_job = job
                tree_file = pjoin(phyml_job.jobdir,
                                  self.alg_phylip_file+"_phyml_tree.txt")
                stats_file = pjoin(phyml_job.jobdir,
                                   self.alg_phylip_file+"_phyml_stats.txt")
                tree = PhyloTree(tree_file)
                m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                              open(stats_file).read())
                lk = float(m.groups()[0])
                tree.add_feature("lk", lk)
                tree.add_feature("model", phyml_job.args["--model"])
                lks.append([float(tree.lk), tree.model, tree])
        elif self.lk_mode == "raxml":
            for job in self.jobs:
                if job.jobcat != "raxml": continue
                raxml_job = job
                lk = open(pjoin(raxml_job.jobdir, "RAxML_log.%s"
                                %raxml_job.args["-n"])).readline().split()[1]
                tree = PhyloTree(raxml_job.args["-t"])
                tree.add_feature("lk", lk)
                tree.add_feature("model", raxml_job.model)
                lks.append([float(tree.lk), tree.model, tree])

        # sort lks in ASC order
        lks.sort()
        # choose the model with higher likelihood, the lastone in the list
        best_model = lks[-1][1]
        best_tree = lks[-1][2]
        log.log(22, "%s model selected from the following lk values:\n%s" %(best_model, '\n'.join(map(str, lks))))
        ModelTesterTask.store_data(self, best_model, lks)
        
