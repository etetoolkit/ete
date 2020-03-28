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

# ####################################################################
# REGISTER New application in the following global dictionries:

APPTYPES = {
    "aligners": set(["muscle", "mafft", "clustalo", "metaligner", "dialingtx", "tcoffee"]),
    "model testers": set(["prottest", "pmodeltest"]),
    "alg cleaners": set(["trimal"]),
    "tree builders": set(["fasttree", "phyml", "raxml", "iqtree"]),
    "COG selectors": set(["cogselector"]),
    "alg concatenators": set(["concatalg"]),
    }

# App name (as referred in config files) to Class name
APP2CLASS = {
    "tcoffee"             : "TCoffee",
    "muscle"              : "Muscle",
    "mafft"               : "Mafft",
    "clustalo"            : "Clustalo",
    "metaligner"          : "MetaAligner",
    "phyml"               : "Phyml",
    "iqtree"              : "IQTree",
    "raxml-pthreads"      : "Raxml",
    "raxml"               : "Raxml",
    "dialigntx"           : "Dialigntx",
    "fasttree"            : "FastTree",
    "trimal"              : "Trimal",
    "prottest"            : "Prottest",
    "pmodeltest"          : "PModelTest",
    "treesplitter"        : "TreeMerger",
    "concatalg"           : "ConcatAlg",
    "cogselector"         : "CogSelector",
    }

# Class name converted into source module name
CLASS2MODULE = {
    "Muscle"        : "muscle",
    "Trimal"        : "trimal",
    "Mafft"         : "mafft",
    "Clustalo"      : "clustalo",
    "MetaAligner"   : "meta_aligner",
    "TCoffee"       : "tcoffee",
    "Phyml"         : "phyml",
    "IQTree"        : "iqtree",
    "Dialigntx"     : "dialigntx",
    "FastTree"      : "fasttree",
    "PModelTest"    : "pmodeltest",
    }

# How to call applications
builtin_apps = {
    'muscle'             : "%BIN%/muscle",
    'mafft'              : "MAFFT_BINARIES=%BIN%  %BIN%/mafft --thread %CORES%",
    #'mafft'              : "%BIN%/mafft --thread %CORES%",
    'clustalo'           : "%BIN%/clustalo --threads %CORES%",
    'trimal'             : "%BIN%/trimal",
    'readal'             : "%BIN%/readal",
    'tcoffee'            : "export HOME=/tmp MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP% PLUGINS_4_TCOFFEE=%BIN%/ && %BIN%/t_coffee",
    'phyml'              : "%BIN%/phyml",
    'iqtree'             : "%BIN%/iqtree -nt %CORES%",
    'raxml-pthreads'     : "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%",
    'raxml'              : "%BIN%/raxmlHPC-SSE3",
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

# options and arguments necessary to run each program and return one line
# containing information about its version
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
    'dialigntx'           : "/bin/sh |grep -i version",
    'fasttree'            : "2>&1 | grep -i version",
    'statal'              : "--version| grep -i statal",
    'pmodeltest'          : "--version 2>&1|grep 'pmodeltest.py v'",
#    'prank'               : "|grep 'prank v'",
#    'probcons'            : "2>&1 |grep -i version",
    'kalign'              : "2>&1 |grep -i version",
    'codeml'              : " /dev/null 2>&1|grep -i version && rm rub rst rst1",
    'slr'                 : " 2>&1 |grep -i version",
    'iqtree'              : " -h |grep -i version|grep IQ",
}

# REGISTER New application in the above global dictionries
# ####################################################################



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

def get_call(appname, apps_path, exec_path, cores):
    try:
        cmd = builtin_apps[appname]
    except KeyError:
        return None

    bin_path = apps_path 
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
            if out:
                print("%s - %s" %(colorify("OK", "green"), str(out).strip()))
            else:
                print(colorify("MISSING", "red"))
                # print("** ", test_cmd)
                # print (process.returncode)
                # print (test_cmd)
                # print (out)
                # print (err)
                errors += 1
                
                #log.debug(test_cmd)
                #log.debug(subprocess.check_output(test_cmd.rstrip("wc -l")), shell=True)
    if errors:
        print(colorify('\nWARNING: %d external tools seem to be missing or unfunctional' %errors, "yellow"), file=sys.stderr)
        print(colorify('Install using conda (recomended):', "lgreen"), file=sys.stderr)
        print(colorify(' conda install -c etetoolkit ete3_external_apps', "white"), file=sys.stderr)
        print(colorify('or manually compile by running:', "lgreen"), file=sys.stderr)
        print(colorify(' ete3 upgrade-external-tools', "white"), file=sys.stderr)
        print()
