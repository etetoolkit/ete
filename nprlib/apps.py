import os
import re
import commands
import logging
log = logging.getLogger("main")


builtin_apps = {
    'muscle'         : "%BIN%/muscle",
    'mafft'          : "MAFFT_BINARIES=%BIN%  %BIN%/mafft --thread %CORES%",
    'clustalo'       : "%BIN%/clustalo",
    'trimal'         : "%BIN%/trimal",
    'readal'         : "%BIN%/readal",
    'tcoffee'        : "export HOME=%TMP% DIR_4_TCOFFEE=%BASE%/t_coffee_9_01 MAFFT_BINARIES=%BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP%  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && %BIN%/t_coffee",
    'phyml'          : "%BIN%/phyml",
    'raxml-pthreads' : "%BIN%/raxmlHPC-PTHREADS-SSE3 -T%CORES%",
    'raxml'          : "%BIN%/raxmlHPC-SSE3",
    'jmodeltest'     : "JMODELTEST_HOME=%BASE%/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'      : "%BIN%/dialign-tx %BASE%/DIALIGN-TX_1.0.2/conf",
    'usearch'        : "%BIN%/usearch",
    'fasttree'       : "export OMP_NUM_THREADS=%CORES%; %BIN%/FastTree",   
    'statal'         : "%BIN%/statal",
    }

app2check = {
    'muscle'         : "| grep -i Edgar|wc -l",
    'mafft'          : "--help | grep -i bioinformatics |wc -l",
    'clustalo'       : "--help | grep -i omega|wc -l",
    'trimal'         : "-h | grep -i capella |wc -l",
    'readal'         : "-h | grep -i capella |wc -l",
    'tcoffee'        : "| grep -i notredame |wc -l",
    'phyml'          : "--help |grep -i Guindon|wc -l",
    'raxml-pthreads' : "-help |grep -i stamatakis|wc -l",
    'raxml'          : "-help |grep -i stamatakis|wc -l",
    'jmodeltest'     : "--help | grep -i posada |wc -l",
    'dialigntx'      : "| grep alignment |wc -l",
    'usearch'        : "| grep -i Edgar|wc -l",
    'fasttree'       : "| grep 'FastTree ver'|wc -l",
    'statal'         : "-h | grep -i capella |wc -l ",
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
