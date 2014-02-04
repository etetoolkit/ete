import os
import re
import commands
import logging
log = logging.getLogger("main")

APP2CLASS = {
    "muscle"              : "Muscle",
    "mafft"               : "Mafft",
    "clustalo"            : "Clustalo",
    "metaligner"          : "MetaAligner",
    "phyml"               : "Phyml",
    "raxml-pthreads"      : "Raxml",
    "raxml"               : "Raxml",
    "raxml-pthreads-sse3" : "Raxml",
    "raxml-sse3"          : "Raxml",
    "raxml-pthreads-avx"  : "Raxml",
    "raxml-avx"           : "Raxml",
    "raxml-pthreads-avx2" : "Raxml",
    "raxml-avx2"          : "Raxml",
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
    'tcoffee'            : "export HOME=/tmp DIR_4_TCOFFEE=%BASE%/t_coffee_9_01 MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP%  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && %BIN%/t_coffee",
    'phyml'              : "%BIN%/phyml",
    'raxml-pthreads'     : "%BIN%/raxmlHPC-PTHREADS -T%CORES%",
    'raxml'              : "%BIN%/raxmlHPC",
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
    for name, cmd in apps.iteritems():
        print "Checking %20s..." %name,
        test_cmd = cmd+" 2>&1 "+app2check.get(name, "")
        out = commands.getoutput(test_cmd)
        try:
            response = int(out)
        except ValueError:
            response = 0
        
        if response:
            print "OK."
        else:
            print "Missing or not functional."
            #log.debug(test_cmd)
            #log.debug(commands.getoutput(test_cmd.rstrip("wc -l")))
