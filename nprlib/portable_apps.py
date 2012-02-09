import os
import re
apps = {
    'muscle'         : "%BIN%/muscle",
    'mafft'          : "MAFFT_BINARIES=%BIN%  %BIN%/mafft",
    'clustalo'       : "%BIN%/clustalo",
    'trimal'         : "%BIN%/trimal",
    'readal'         : "%BIN%/readal",
    'tcoffee'        : "export DIR_4_TCOFFEE=%BASE%/t_coffee_9_01 MAFFT_BINARIES=$BIN% TMP_4_TCOFFEE=%TMP% LOCKDIR_4_TCOFFEE=%TMP%  PERL5LIB=$PERL5LIB:$DIR_4_TCOFFEE/perl  && $DIR_4_TCOFFEE/bin/t_coffee",
    'phyml'          : "%BIN%/phyml",
    'raxml-pthreads' : "%BIN%/raxmlHPC-PTHREADS-SSE3",
    'raxml'          : "%BIN%/raxmlHPC-SSE3",
    'jmodeltest'     : "JMODELTEST_HOME=%BASE%/jmodeltest2; cd $JMODELTEST_HOME; java -jar $JMODELTEST_HOME/jModelTest.jar",
    'dialigntx'      : "%BIN%/dialign-tx %BASE%/DIALIGN-TX_1.0.2/conf",
    'usearch'        : "%BIN%/usearch",
    'fasttree'       : "%BIN%/FastTree",
    'statal'         : "%BIN%/statal",
    }

def get_call(appname, apps_path, exec_path):
    try:
        cmd = apps[appname]
    except KeyError:
        return None
    #libpath = os.path.join(apps_path, "lib")
    #linker_path = os.path.join(libpath, "ld-linux")
    bin_path = os.path.join(apps_path, "bin")
    tmp_path = os.path.join(exec_path, "tmp")
    
    cmd = re.sub("%BIN%", bin_path, cmd)
    cmd = re.sub("%BASE%", apps_path, cmd)
    cmd = re.sub("%TMP%", tmp_path, cmd)
    cmd = "export NPR_APP_PATH=%s; %s" %(apps_path, cmd) 
    return cmd
  
    