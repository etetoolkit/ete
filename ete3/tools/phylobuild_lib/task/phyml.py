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
import shutil
import sys
import re

import logging
log = logging.getLogger("main")

from ..master_task import TreeTask
from ..master_job import Job
from ..utils import basename, PhyloTree, OrderedDict, GLOBALS,  DATATYPES
from .. import db

__all__ = ["Phyml"]


modelcodes = {
 'JC'   :'000000',  
 'K80'   :'010010' ,
 'TrNef' :'010020' ,
 'TPM1'  :'012210' ,
 'TPM2'  :'010212' ,
 'TPM3'  :'012012' ,
 'TIM1ef':'012230' ,
 'TIM2ef':'010232' ,
 'TIM3ef':'012032' ,
 'TVMef' :'012314' ,
 'SYM'   :'012345' ,
 'F81'   :'000000' ,
 'HKY'   :'010010' ,
 'TrN'   :'010020' ,
 'TPM1uf':'012210' ,
 'TPM2uf':'010212' ,
 'TPM3uf':'012012' ,
 'TIM1'  :'012230' ,
 'TIM2'  :'010232' ,
 'TIM3'  :'012032' ,
 'TVM'   :'012314' ,
 'GTR'   :'012345',
}


class Phyml(TreeTask):
    def __init__(self, nodeid, alg_phylip_file, constrain_id, model,
                 seqtype, conf, confname, parts_id=None):

        GLOBALS["citator"].add('phyml')
            
        base_args = OrderedDict({
                "--model": "",
                "--no_memory_check": "",
                "--quiet": "",
                "--constraint_tree": ""})


        if model and model.startswith('pmodeltest-'):
            model = model.replace('pmodeltest-', '')
            self.fullmodel = model

            # overwrites default options if model selection says so            
            if "+I" in model:
                conf[confname]["-v"]=" e"
            elif "!I" in model:
                conf[confname]["-v"]=" 0"
                            
            if "+G" in model:
                #conf[confname]["-c"]=" 4"
                conf[confname]["-a"]="e"
            elif "!G" in model:
                conf[confname]["-c"]=" 1"
                conf[confname].pop("-a", None)
                
            if "+F" in model:
                conf[confname]["-f"] = "m" if seqtype == "nt" else "e"
            elif "!F" in model:
                conf[confname]["-f"] = '0.25,0.25,0.25,0.25' if seqtype == "nt" else "m"
                
            model = model.split("+")[0].split("!")[0]
            if seqtype == "nt":
                model = modelcodes[model]

        elif not model:
            model = conf[confname]["_aa_model"] if seqtype == "aa" else conf[confname]["_nt_model"]
            self.fullmodel = ""
        else:
            self.fullmodel = model+"-prottest"
            model= model # use the model as provided by prottest (older, simpler approach)  

        self.model = model
        self.confname = confname
        self.conf = conf
        self.constrain_tree = None
        if constrain_id:
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_tree)
            
        self.alg_phylip_file = alg_phylip_file
        TreeTask.__init__(self, nodeid, "tree", "Phyml",
                          base_args, conf[confname])
            
        self.seqtype = seqtype
        self.lk = None

        self.init()

    def load_jobs(self):
        appname = self.conf[self.confname]["_app"]
        args = OrderedDict(self.args)
        args["--datatype"] = self.seqtype
        args["--model"] = self.model
        args["--input"] = self.alg_phylip_file
        if self.constrain_tree:
            args["--constraint_tree"] = self.constrain_tree
            args["-u"] = self.constrain_tree
        else:
            del args["--constraint_tree"]
        job = Job(self.conf["app"][appname], args, parent_ids=[self.nodeid])
        job.add_input_file(self.alg_phylip_file, job.jobdir)
        if self.constrain_tree:
            job.add_input_file(self.constrain_tree, job.jobdir)
        job.jobname += "-"+self.fullmodel
        self.jobs.append(job)

    def finish(self):
        lks = []
        j = self.jobs[0]
        tree_file = os.path.join(j.jobdir,
                                 self.alg_phylip_file+"_phyml_tree.txt")
        stats_file = os.path.join(j.jobdir,
                                  self.alg_phylip_file+"_phyml_stats.txt")

        m = re.search('Log-likelihood:\s+(-?\d+\.\d+)',
                      open(stats_file).read())
        lk = float(m.groups()[0])
        stats = {"lk": lk}
        tree = PhyloTree(tree_file)
        TreeTask.store_data(self, tree.write(), stats)

