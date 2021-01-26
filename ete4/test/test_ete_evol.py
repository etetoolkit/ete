from __future__ import absolute_import
from __future__ import print_function

import os
import multiprocessing
CPUS = min(20, max(1, multiprocessing.cpu_count()))
import unittest

from ..tools import ete
from ..evol.control import AVAIL

BASEPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
DATAPATH = os.path.join(BASEPATH, "ete_evol_data", "S_example")
SDATAPATH = os.path.join(BASEPATH,"ete_evol_data", "XS_example")
OUTPATH = 'ete_test_tmp/ete3_evol-test/'

class Test_ete_evol(unittest.TestCase):
    def test_01_all_models(self):
        models = [k for k in AVAIL.keys() if not k.startswith('XX.')]

        cmd = 'ete3 evol --mark Pan_troglodytes --noimg --alg %s/ali.fasta -t %s/tree.nw --clear_all -o %s --cpu %d --model ' %(
            SDATAPATH, SDATAPATH, OUTPATH, CPUS)
        args = cmd.split()
        args.extend([model for model in models if not 'XX' in model])
        print(' '.join(args))
        ete._main(args)

    def test_02_web_examples(self):
        commands = [
            'ete3 evol -t ECP_EDN_15.nw --alg ECP_EDN_15.fasta -o ete_test_tmp/results1/ --models fb M2 SLR --cpu $$CPU',
            'ete3 evol -t ECP_EDN_15.nw --alg ECP_EDN_15.fasta --models b_neut b_free --mark Papio_EDN,,,Orang_EDN -o ete_test_tmp/results2/ --cpu $$CPU',
            'ete3 evol -t ECP_EDN_15.nw --alg ECP_EDN_15.fasta --models b_neut b_free --mark Human_EDN,,,Hylobates_EDN,Macaq_EDN,,,Papio_EDN Macaq_ECP,,Macaq2_ECP,Human_ECP,,Goril_ECP -o ete_test_tmp/results3/ --cpu $$CPU',
            'ete3 evol -t ECP_EDN_15.nw --alg ECP_EDN_15.fasta --models b_neut b_free --mark Papio_EDN,,,Orang_EDN -o ete_test_tmp/results3/ --cpu $$CPU',
            'ete3 evol -t ECP_EDN_15.nw --alg ECP_EDN_15.fasta --models M2 M1 b_free b_neut --leaves --tests b_free,b_neut -o ete_test_tmp/results4/ --cpu $$CPU',
            ]
        for cmd in commands:
            cmd = cmd.replace("ECP_EDN_15", "%s/ete_evol_data/CladeModelCD/ECP_EDN_15" %BASEPATH)
            cmd = cmd.replace("$$CPU", str(CPUS))
            print(cmd)
            args = cmd.split()
            ete._main(args)
        os.system('rm -rf ete_test_tmp')
        
if __name__ == "__main__":
    unittest.main()
