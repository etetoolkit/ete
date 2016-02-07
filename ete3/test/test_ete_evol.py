from __future__ import absolute_import
from __future__ import print_function

import os
import multiprocessing
CPUS = min(20, max(1, multiprocessing.cpu_count()))
import unittest

from ..tools import ete
from ..evol.control import AVAIL

DATAPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])+"/ete_evol_data/S_example/"
SDATAPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])+"/ete_evol_data/XS_example/"
OUTPATH = '/tmp/ete3_evol-test/'

class Test_ete_evol(unittest.TestCase):
    def test_01_all_models(self):
        models = [k for k in AVAIL.keys() if not k.startswith('XX.') and not k == 'SLR']

        cmd = 'ete3 evol --mark Pan_troglodytes --noimg --alg %s/ali.fasta -t %s/tree.nw --clear_all -o %s --cpu %d --model ' %(
            SDATAPATH, SDATAPATH, OUTPATH, CPUS)
        args = cmd.split()
        args.extend([model for model in models if not 'XX' in model])
        ete._main(args)

    def test_02_next_test_to_be_defined(self):
        pass

if __name__ == "__main__":
    unittest.main()
