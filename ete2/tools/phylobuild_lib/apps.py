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
import commands
import logging
import subprocess
log = logging.getLogger("main")

APP2CLASS = {
    "muscle"              : "Muscle",
    "mafft"               : "Mafft",
    "clustalo"            : "Clustalo",
    "metaligner"          : "MetaAligner",
    "phyml"               : "Phyml",
    "raxml-pthreads"      : "Raxml",
    "raxml"               : "Raxml",
    # "raxml-pthreads-sse3" : "Raxml",
    # "raxml-sse3"          : "Raxml",
    # "raxml-pthreads-avx"  : "Raxml",
    # "raxml-avx"           : "Raxml",
    # "raxml-pthreads-avx2" : "Raxml",
    # "raxml-avx2"          : "Raxml",
    "jmodeltest"          : "JModeltest",
    "dialigntx"           : "Dialigntx",
    "fasttree"            : "FastTree",
    "trimal"              : "Trimal",
    "prottest"            : "Prottest",
    "jmodeltest"          : "JModeltest",
    "treesplitter"        : "TreeMerger",
    "concatalg"           : "ConcatAlg",
    "cogselector"         : "CogSelector",
    }

CLASS2MODULE = {
    "Muscle"        : "muscle",
    "Trimal"        : "trimal",
    "Mafft"         : "mafft",
    "Clustalo"      : "clustalo",
    "MetaAligner"   : "meta_aligner",
    "Phyml"         : "phyml",
    "JModeltest"    : "jmodeltest",
    "Dialigntx"     : "dialigntx",
    "FastTree"      : "fasttree",
    }

builtin_apps = {
    'muscle'             : "%BIN%/muscle",
    'mafft'              : "MAFFT_BINARIES=%BIN%  %BIN%/mafft --thread %CORES%",
    'clustalo'           : "%BIN%/clustalo --threads %CORES%",
    'trimal'             : "%BIN%/trimal",
    'readal'             : "%BIN%/readal",
    'tcoffee'            : "export HOME=/tmp MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP%  && %BIN%/t_coffee",
    'phyml'              : "%BIN%/phyml",
    'raxml-pthreads'     : "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%", # defaults to SSE3
    'raxml'              : "%BIN%/raxmlHPC-SSE3",                    # defaults to SSE3
    'raxml-pthreads-sse3': "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%",
    'raxml-sse3'         : "%BIN%/raxmlHPC-SSE3",
    'raxml-pthreads-avx' : "%BIN%/raxmlHPC-PTHREADS-AVX -T%CORES%",
    'raxml-avx'          : "%BIN%/raxmlHPC-AVX",
    'raxml-pthreads-avx2': "%BIN%/raxmlHPC-PTHREADS-AVX2 -T%CORES%",
    'raxml-avx2'         : "%BIN%/raxmlHPC-AVX2",
    'jmodeltest'         : "JMODELTEST_HOME=%BASE%/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'          : "%BIN%/dialign-tx %BASE%/DIALIGN-TX_1.0.2/conf",
    'usearch'            : "%BIN%/usearch",
    'fasttree'           : "export OMP_NUM_THREADS=%CORES%; %BIN%/FastTree",   
    'statal'             : "%BIN%/statal",
    }

app2check = {
    'muscle'              : "| grep -i Edgar|wc -l",
    'mafft'               : "--help | grep -i bioinformatics |wc -l",
    'clustalo'            : "--help | grep -i omega|wc -l",
    'trimal'              : "-h | grep -i capella |wc -l",
    'readal'              : "-h | grep -i capella |wc -l",
    'tcoffee'             : "| grep -i notredame |wc -l",
    'phyml'               : "--help |grep -i Guindon|wc -l",
    'raxml-pthreads'      : "-help |grep -i stamatakis|wc -l",
    'raxml'               : "-help |grep -i stamatakis|wc -l",
    'raxml-pthreads-sse3' : "-help |grep -i stamatakis|wc -l",
    'raxml-sse3'          : "-help |grep -i stamatakis|wc -l",
    'raxml-pthreads-avx'  : "-help |grep -i stamatakis|wc -l",
    'raxml-avx'           : "-help |grep -i stamatakis|wc -l",
    'raxml-pthreads-avx2' : "-help |grep -i stamatakis|wc -l",
    'raxml-avx2'          : "-help |grep -i stamatakis|wc -l",
    'jmodeltest'          : "--help | grep -i posada |wc -l",
    'dialigntx'           : "| grep alignment |wc -l",
    'usearch'             : "| grep -i Edgar|wc -l",
    'fasttree'            : "| grep 'FastTree ver'|wc -l",
    'statal'              : "-h | grep -i capella |wc -l ",
    }

app2version = {
    'muscle'              : "-version|grep MUSCLE",
    'mafft'               : "--noflagavailable 2>&1 |grep MAFFT",
    'clustalo'            : "--version",
    'trimal'              : "--version|grep -i trimal",
    'readal'              : "--version| grep -i readal",
    'tcoffee'             : "-version|grep -i version",
    'phyml'               : "--version | grep -i version",
    'raxml-pthreads'      : "-version| grep -i version",
    'raxml'               : "-version| grep -i version",
    'raxml-pthreads-sse3' : "-version| grep -i version",
    'raxml-sse3'          : "-version| grep -i version",
    'raxml-pthreads-avx'  : "-version| grep -i version",
    'raxml-avx'           : "-version| grep -i version",
    'raxml-pthreads-avx2' : "-version| grep -i version",
    'raxml-avx2'          : "-version| grep -i version",
#    'jmodeltest'          : "--help | grep -i posada ",
    'dialigntx'           : "/bin/sh |grep -i version",
#    'usearch'             : "",
    'fasttree'            : "2>&1 | grep version",
    'statal'              : "--version| grep -i statal",
    }


def get_call(appname, apps_path, exec_path, cores):
    try:
        cmd = builtin_apps[appname]
    except KeyError:
        return None
       
    bin_path = os.path.join(apps_path, "bin")
    tmp_path = os.path.join(exec_path, "tmp")
    #apps_base = apps_path.rstrip("/x86-64").rstrip("/x86-32")
    cmd = re.sub("%BIN%", bin_path, cmd)
    cmd = re.sub("%BASE%", os.path.join(apps_path, "src"), cmd)
    cmd = re.sub("%TMP%", tmp_path, cmd)
    cmd = re.sub("%CORES%", cores, cmd)
    #cmd = "export NPR_APP_PATH=%s; %s" %(apps_path, cmd)
    return cmd
  
def test_apps(apps):
    for name, cmd in sorted(apps.items()):
        if app2version.get(name):
            print "Checking %20s..." %name,
            test_cmd = cmd + " " + app2version.get(name, "")

            process = subprocess.Popen(test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
        
            if out:
                print "OK.\t%s" %out.strip()
            else:
                print "Missing or not functional."
                #print "** ", test_cmd
                #log.debug(test_cmd)
                #log.debug(commands.getoutput(test_cmd.rstrip("wc -l")))
