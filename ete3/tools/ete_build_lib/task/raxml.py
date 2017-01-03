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
import re
import shutil
from glob import glob

log = logging.getLogger("main")

from ..master_task import TreeTask
from ..master_job import Job
from ..utils import (basename, Tree, OrderedDict, GLOBALS, pjoin, DATATYPES,
                     md5)
from .. import db

__all__ = ["Raxml"]

class Raxml(TreeTask):
    def __init__(self, nodeid, alg_file, constrain_id, model,
                 seqtype, conf, confname, parts_id=None):
        GLOBALS["citator"].add('raxml')

        model_string = "PROT" if seqtype == "aa" else "GTR" 
        if model and model.startswith('pmodeltest-'):
            fullmodel = model.replace('pmodeltest-', '')
            basemodel = fullmodel.split("+")[0].split("!")[0]
            if seqtype == "nt" and basemodel != "GTR":
                log.warning("Raxml supports only the GTR model, but model selection returned %s. Consider using Phyml if this is important." %basemodel)
                
            # overwrites default options if model selection says so
            
            if "+G" in fullmodel:
                model_string += "GAMMA"
            elif "!G" in fullmodel:
                model_string += "CAT"
                #conf[confname]['-c'] = 1
            else:
                if seqtype == "aa":
                    model_string += conf[confname]["_method"]
                
            if seqtype == "aa":
                model_string += basemodel.upper()
                
            if "+I" in fullmodel and "GAMMA" in model_string:
                model_string += "I"
            elif "!I" in fullmodel:
                pass
            else:
                if "I" in conf[confname]["_model_suffix"] and "GAMMA" in model_string:
                    model_string += "I" 

            if "+F" in fullmodel:
                if seqtype == "aa":
                    model_string += "F"
            if "!F" in fullmodel:                
                pass
            else:
                if "F" in conf[confname]["_model_suffix"] and seqtype == "aa":
                    model_string += "F"
        else:
            # in case of using older, simpler prottest or no model selection step
            model_string += conf[confname]["_method"]
            if seqtype == "aa":
                model_string += model if model else conf[confname]["_aa_model"]
            model_string += conf[confname]["_model_suffix"]                        

        self.model_string = model_string
        self.model = model_string
        
        base_args = OrderedDict()
        self.bootstrap = conf[confname].get("_bootstrap", None)

        self.confname = confname
        self.conf = conf
        self.alg_phylip_file = alg_file

        try:
            self.constrain_tree = db.get_dataid(constrain_id, DATATYPES.constrain_tree)
        except ValueError:
            self.constrain_tree = None

        self.partitions_file = parts_id

        TreeTask.__init__(self, nodeid, "tree", "RaxML",
                          base_args, conf[confname])

        max_cores = GLOBALS["_max_cores"]
        appname = conf[confname]["_app"]
        if max_cores > 1:
            threads = conf["threading"].get("raxml-pthreads")
            if threads > 1:
                appname = appname.replace("raxml", "raxml-pthreads")
                raxml_bin = conf["app"][appname]
        else:
            appname = appname.replace("raxml-pthreads", "raxml")
            threads = 1
            raxml_bin = conf["app"][appname]

        self.raxml_bin = raxml_bin
        self.threads = threads
        self.seqtype = seqtype

        self.init()

    def load_jobs(self):
        args = OrderedDict(self.args)
        args["-s"] = pjoin(GLOBALS["input_dir"], self.alg_phylip_file)
        args["-m"] = self.model_string
        args["-n"] = self.alg_phylip_file
        if self.constrain_tree:
            log.log(24, "Using constrain tree %s" %self.constrain_tree)
            args["-g"] = pjoin(GLOBALS["input_dir"], self.constrain_tree)
        if self.partitions_file:
            log.log(24, "Using alg partitions %s" %self.partitions_file)
            args['-q'] = pjoin(GLOBALS["input_dir"], self.partitions_file)

        tree_job = Job(self.raxml_bin, args, parent_ids=[self.nodeid])
        tree_job.jobname += "-"+self.model_string
        tree_job.cores = self.threads
        # Register input files necessary to run the job
        tree_job.add_input_file(self.alg_phylip_file)
        if self.constrain_tree:
            tree_job.add_input_file(self.constrain_tree)
        if self.partitions_file:
            tree_job.add_input_file(self.partitions_file)

        self.jobs.append(tree_job)
        self.out_tree_file = os.path.join(tree_job.jobdir,
                                     "RAxML_bestTree." + self.alg_phylip_file)

        if self.bootstrap == "alrt":
            alrt_args = tree_job.args.copy()
            if self.constrain_tree:
                del alrt_args["-g"]
            if self.partitions_file:
                alrt_args["-q"] = args['-q']

            alrt_args["-f"] =  "J"
            alrt_args["-t"] = self.out_tree_file
            alrt_job = Job(self.raxml_bin, alrt_args,
                           parent_ids=[tree_job.jobid])
            alrt_job.jobname += "-alrt"
            alrt_job.dependencies.add(tree_job)
            alrt_job.cores = self.threads

            # Register necessary input files
            alrt_job.add_input_file(self.alg_phylip_file)
            if self.partitions_file:
                alrt_job.add_input_file(self.partitions_file)

            self.jobs.append(alrt_job)
            self.alrt_job = alrt_job

        elif self.bootstrap == "alrt_phyml":
            alrt_args = {
                "-o": "n",
                "-i": self.alg_phylip_file,
                "--bootstrap": "-2",
                "-d": self.seqtype,
                "-u": self.out_tree_file,
                "--model": self.model,
                "--quiet": "",
                "--no_memory_check": "",
                }
            #if self.constrain_tree:
            #    alrt_args["--constraint_tree"] = self.constrain_tree

            alrt_job = Job(self.conf["app"]["phyml"],
                           alrt_args, parent_ids=[tree_job.jobid])
            alrt_job.add_input_file(self.alg_phylip_file, alrt_job.jobdir)
            alrt_job.jobname += "-alrt"
            alrt_job.dependencies.add(tree_job)
            alrt_job.add_input_file(self.alg_phylip_file)
            self.jobs.append(alrt_job)
            self.alrt_job = alrt_job

        else:
            # Bootstrap calculation
            boot_args = tree_job.args.copy()
            boot_args["-n"] = "bootstraps."+boot_args["-n"]
            boot_args["-N"] = int(self.bootstrap)
            boot_args["-b"] = 31416
            boot_job = Job(self.raxml_bin, boot_args,
                           parent_ids=[tree_job.jobid])
            boot_job.jobname += "-%d-bootstraps" %(boot_args['-N'])
            boot_job.dependencies.add(tree_job)
            boot_job.cores = self.threads

            # Register necessary input files
            boot_job.add_input_file(self.alg_phylip_file)
            if self.constrain_tree:
                boot_job.add_input_file(self.constrain_tree)
            if self.partitions_file:
                boot_job.add_input_file(self.partitions_file)

            self.jobs.append(boot_job)

            # Bootstrap drawing on top of best tree
            bootd_args = tree_job.args.copy()
            if self.constrain_tree:
                del bootd_args["-g"]
            if self.partitions_file:
                del bootd_args["-q"]

            bootd_args["-n"] = "bootstrapped."+ tree_job.args["-n"]
            bootd_args["-f"] = "b"
            bootd_args["-t"] = self.out_tree_file
            bootd_args["-z"] = pjoin(boot_job.jobdir, "RAxML_bootstrap." + boot_job.args["-n"])

            bootd_job = Job(self.raxml_bin, bootd_args,
                            parent_ids=[tree_job.jobid])
            bootd_job.jobname += "-bootstrapped"
            bootd_job.dependencies.add(boot_job)
            bootd_job.cores = self.threads
            self.jobs.append(bootd_job)

            self.boot_job = boot_job
            self.bootd_job = bootd_job

    def finish(self):
        #first job is the raxml tree
        def parse_alrt(match):
            dist = match.groups()[0]
            support = float(match.groups()[1])/100.0
            return "%g:%s" %(support, dist)

        if self.bootstrap == "alrt":
            alrt_tree_file = os.path.join(self.alrt_job.jobdir,
                                               "RAxML_fastTreeSH_Support." + self.alrt_job.args["-n"])
            raw_nw = open(alrt_tree_file).read()
            try:
                nw, nsubs = re.subn(":(\d+\.\d+)\[(\d+)\]", parse_alrt, raw_nw, flags=re.MULTILINE)
            except TypeError:
                raw_nw = raw_nw.replace("\n","")
                nw, nsubs = re.subn(":(\d+\.\d+)\[(\d+)\]", parse_alrt, raw_nw)
            if nsubs == 0:
                log.warning("alrt values were not detected in raxml tree!")
            tree = Tree(nw)

        elif self.bootstrap == "alrt_phyml":
            alrt_tree_file = os.path.join(self.alrt_job.jobdir,
                                          self.alg_phylip_file +"_phyml_tree.txt")
            tree = Tree(alrt_tree_file)

        else:
            alrt_tree_file = os.path.join(self.bootd_job.jobdir,
                                               "RAxML_bipartitions." + self.bootd_job.args["-n"])
            nw = open(alrt_tree_file).read()
            tree = Tree(nw)
            tree.support = 100
            for n in tree.traverse():
                if n.support >1:
                    n.support /= 100.
                else:
                    n.support = 0

        TreeTask.store_data(self, tree.write(), {})




