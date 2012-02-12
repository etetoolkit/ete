import os
import re
import commands
import logging
log = logging.getLogger("main")


builtin_apps = {
    'muscle'         : "%BIN%/muscle",
    'mafft'          : "MAFFT_BINARIES=%BIN%  %BIN%/mafft",
    'clustalo'       : "%BIN%/clustalo",
    'trimal'         : "%BIN%/trimal",
    'readal'         : "%BIN%/readal",
    'tcoffee'        : "export DIR_4_TCOFFEE=%BASE%/t_coffee_9_01 MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP%  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && %BIN%/t_coffee",
    'phyml'          : "%BIN%/phyml",
    'raxml-pthreads' : "%BIN%/raxmlHPC-PTHREADS-SSE3",
    'raxml'          : "%BIN%/raxmlHPC-SSE3",
    'jmodeltest'     : "JMODELTEST_HOME=%BASE%/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'      : "%BIN%/dialign-tx %BASE%/DIALIGN-TX_1.0.2/conf",
    'usearch'        : "%BIN%/usearch",
    'fasttree'       : "%BIN%/FastTree",
    'statal'         : "%BIN%/statal",
    }

app2check = {
    'muscle'         : "|grep -i muscle|wc -l",
    'mafft'          : "--help|grep -i mafft|wc -l",
    'clustalo'       : "--help|grep -i Omega|wc -l",
    'trimal'         : "--version |grep -i trimal|wc -l",
    'readal'         : "--version |grep -i readal|wc -l",
    'tcoffee'        : "-version|grep t_coffee|wc -l",
    'phyml'          : "--help|grep -i phyml|wc -l",
    'raxml-pthreads' : "-help|grep -i raxml|wc -l",
    'raxml'          : "-help|grep -i raxml|wc -l",
    'jmodeltest'     : "--help|grep -i jmodeltest|wc -l",
    'dialigntx'      : "--help|grep -i dialign|wc -l",
    'usearch'        : "|grep -i usearch|wc -l",
    'fasttree'       : "|grep -i fasttree|wc -l",
    'statal'         : "--version |grep -i statal|wc -l ",
    }


def get_call(appname, apps_path, exec_path):
    try:
        cmd = builtin_apps[appname]
    except KeyError:
        return None
    bin_path = os.path.join(apps_path, "bin")
    tmp_path = os.path.join(exec_path, "tmp")
    apps_base = apps_path.rstrip("/x86-64").rstrip("/x86-32")
    cmd = re.sub("%BIN%", bin_path, cmd)
    cmd = re.sub("%BASE%", apps_base, cmd)
    cmd = re.sub("%TMP%", tmp_path, cmd)
    cmd = "export NPR_APP_PATH=%s; %s" %(apps_path, cmd) 
    return cmd
  
def test_apps(apps):
    for name, cmd in apps.iteritems():
        print "Checking %20s..." %name,
        test_cmd = cmd+" 2>&1 "+app2check.get(name, "")
        response = int(commands.getoutput(test_cmd))
        if response:
            print "OK."
        else:
            print "Missing or nonfunctional."