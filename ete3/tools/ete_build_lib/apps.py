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
from __future__ import print_function
import sys
import os
import re
import logging
import subprocess
import six

from .utils import colorify

log = logging.getLogger("main")

APPTYPES = {
    "aligners": set(["muscle", "mafft", "clustalo", "metaligner", "dialingtx", "tcoffee"]),
    "model testers": set(["prottest", "pmodeltest"]),
    "alg cleaners": set(["trimal"]),
    "tree builders": set(["fasttree", "phyml", "raxml"]),
    "COG selectors": set(["cogselector"]),
    "alg concatenators": set(["concatalg"]),
    }
  

OPTION2APPTYPE = {
    "_aa_aligner": APPTYPES["aligners"],
    "_nt_aligner": APPTYPES["aligners"],

    "_aa_alg_cleaner": APPTYPES["alg cleaners"],
    "_nt_alg_cleaner": APPTYPES["alg cleaners"],
    
    "_aa_tree_builder": APPTYPES["tree builders"],
    "_nt_tree_builder": APPTYPES["tree builders"], 
    
    "_aa_model_tester": APPTYPES["model testers"],
    "_nt_model_tester": APPTYPES["model testers"],

    "_cog_selector": APPTYPES["COG selectors"],
    "_alg_concatenator": APPTYPES["alg concatenators"], 
    
}

APP2CLASS = {
    "tcoffee"             : "TCoffee",
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
    "pmodeltest"          : "PModelTest",
#    "jmodeltest"          : "JModeltest",
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
    "TCoffee"       : "tcoffee",
    "Phyml"         : "phyml",
#    "JModeltest"    : "jmodeltest",
    "Dialigntx"     : "dialigntx",
    "FastTree"      : "fasttree",
    "PModelTest"    : "pmodeltest",
    }

builtin_apps = {
    'muscle'             : "%BIN%/muscle",
    'mafft'              : "MAFFT_BINARIES=%BIN%  %BIN%/mafft --thread %CORES%",
    'clustalo'           : "%BIN%/clustalo --threads %CORES%",
    'trimal'             : "%BIN%/trimal",
    'readal'             : "%BIN%/readal",
    'tcoffee'            : "export HOME=/tmp MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP% PLUGINS_4_TCOFFEE=%BIN%/ && %BIN%/t_coffee",
    'phyml'              : "%BIN%/phyml",
    'raxml-pthreads'     : "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%", # defaults to SSE3
    'raxml'              : "%BIN%/raxmlHPC-SSE3",                    # defaults to SSE3
    #'raxml-pthreads-sse3': "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%",
    #'raxml-sse3'         : "%BIN%/raxmlHPC-SSE3",
    #'raxml-pthreads-avx' : "%BIN%/raxmlHPC-PTHREADS-AVX -T%CORES%",
    #'raxml-avx'          : "%BIN%/raxmlHPC-AVX",
    #'raxml-pthreads-avx2': "%BIN%/raxmlHPC-PTHREADS-AVX2 -T%CORES%",
    #'raxml-avx2'         : "%BIN%/raxmlHPC-AVX2",
    'pmodeltest'         : "python %BIN%/pmodeltest.py --nprocs %CORES% --phyml %BIN%/phyml",
    'dialigntx'          : "%BIN%/dialign-tx %BIN%/dialigntx_conf",
    'fasttree'           : "export OMP_NUM_THREADS=%CORES%; %BIN%/FastTree",
    'statal'             : "%BIN%/statal",
    'prank'              : "%BIN%/prank",
    'probcons'           : "%BIN%/probcons",
    'kalign'             : "%BIN%/kalign",
    'codeml'             : "%BIN%/codeml",
    'slr'                : "%BIN%/Slr",
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
    #'raxml-pthreads-sse3' : "-help |grep -i stamatakis|wc -l",
    #'raxml-sse3'          : "-help |grep -i stamatakis|wc -l",
    #'raxml-pthreads-avx'  : "-help |grep -i stamatakis|wc -l",
    #'raxml-avx'           : "-help |grep -i stamatakis|wc -l",
    #'raxml-pthreads-avx2' : "-help |grep -i stamatakis|wc -l",
    #'raxml-avx2'          : "-help |grep -i stamatakis|wc -l",
    #'jmodeltest'          : "--help | grep -i posada |wc -l",
    'dialigntx'           : "| grep alignment |wc -l",
    'fasttree'            : "| grep -i 'FastTree ver'|wc -l",
    'statal'              : "-h | grep -i capella |wc -l ",
    'pmodeltest'          : "--version 2>&1|grep 'pmodeltest.py v'",
    'prank'              : "|grep 'prank v'", 
    'probcons'           : " 2>&1 |grep -i version",
    'kalign'             : " 2>&1 |grep -i version",
    'codeml'             : " /dev/null 2>&1 |grep -i version",
    'slr'                : " 2>&1 |grep -i version",   
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
    #'raxml-pthreads-sse3' : "-version| grep -i version",
    #'raxml-sse3'          : "-version| grep -i version",
    #'raxml-pthreads-avx'  : "-version| grep -i version",
    #'raxml-avx'           : "-version| grep -i version",
    #'raxml-pthreads-avx2' : "-version| grep -i version",
    #'raxml-avx2'          : "-version| grep -i version",
    'dialigntx'           : "/bin/sh |grep -i version",
    'fasttree'            : "2>&1 | grep -i version",
    'statal'              : "--version| grep -i statal",
    'pmodeltest'          : "--version 2>&1|grep 'pmodeltest.py v'",
    'prank'              : "|grep 'prank v'", 
    'probcons'           : "2>&1 |grep -i version",
    'kalign'             : "2>&1 |grep -i version",   
    'codeml'             : " /dev/null 2>&1 |grep -i version",
    'slr'                : " 2>&1 |grep -i version",   
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
    errors = 0
    for name, cmd in sorted(apps.items()):
        if name == "dialigntx" and sys.platform == "darwin":
            print(colorify('Dialign-tx not supported in OS X', "orange"), file=sys.stderr)
            continue
        if app2version.get(name):
            print(" %14s:" %name, end=' ')
            test_cmd = cmd + " " + app2version.get(name, "")

            process = subprocess.Popen(test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            out = bytes.decode(out)
            #print (process.returncode)
            #print (test_cmd)
            if out:
                print("%s - %s" %(colorify("OK", "green"), str(out).strip()))
            else:
                print(colorify("ERROR", "red"))
                errors += 1
                #print("** ", test_cmd)
                #log.debug(test_cmd)
                #log.debug(subprocess.check_output(test_cmd.rstrip("wc -l")), shell=True)
    if errors:
        print(colorify('\nWARNING: %d external tools seem to be missing or unfunctional' %errors, "yellow"), file=sys.stderr)
        print(colorify('Install using conda (recomended):', "lgreen"), file=sys.stderr)
        print(colorify(' conda install -c etetoolkit ete3_external_tools', "white"), file=sys.stderr)
        print(colorify('or manually compile by running:', "lgreen"), file=sys.stderr)
        print(colorify(' ete3 upgrade-external-tools', "white"), file=sys.stderr)
        print()
