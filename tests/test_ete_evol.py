import os
import multiprocessing
CPUS = min(20, max(1, multiprocessing.cpu_count()))

import unittest

from ete4.tools import ete
from ete4.evol.control import AVAIL

BASEPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
DATAPATH = os.path.join(BASEPATH, "ete_evol_data", "S_example")
SDATAPATH = os.path.join(BASEPATH,"ete_evol_data", "XS_example")
OUTPATH = 'ete_test_tmp/ete4_evol-test/'


class Test_ete_evol(unittest.TestCase):
    def test_01_all_models(self):
        cmd = (f'ete4 evol'
               f'    --mark Pan_troglodytes --noimg'
               f'    --alg {SDATAPATH}/ali.fasta -t {SDATAPATH}/tree.nw'
               f'    --clear_all -o {OUTPATH} --cpu {CPUS}'
               f'    --model ') + ' '.join(model for model in AVAIL if not 'XX' in model)

        print(cmd)
        args = cmd.split()
        ete._main(args)

    def test_02_web_examples(self):
        # TODO: Download the data from the ete-data repository to a
        # temporary directory (with tempfile module?).

        dpath = BASEPATH + '/ete_evol_data/CladeModelCD'
        prefix = f'ete4 evol -t {dpath}/ECP_EDN_15.nw --alg {dpath}/ECP_EDN_15.fasta --cpu {CPUS} '

        params = [
            '--models fb M2 SLR -o ete_test_tmp/results1/',
            '--models b_neut b_free --mark Papio_EDN,,,Orang_EDN -o ete_test_tmp/results2/',
            '--models b_neut b_free --mark Human_EDN,,,Hylobates_EDN,Macaq_EDN,,,Papio_EDN Macaq_ECP,,Macaq2_ECP,Human_ECP,,Goril_ECP -o ete_test_tmp/results3/',
            '--models b_neut b_free --mark Papio_EDN,,,Orang_EDN -o ete_test_tmp/results3/',
            '--models M2 M1 b_free b_neut --leaves --tests b_free,b_neut -o ete_test_tmp/results4/']

        for param in params:
            cmd = prefix + param
            print(cmd)
            args = cmd.split()
            ete._main(args)

        os.system('rm -rf ete_test_tmp')


if __name__ == "__main__":
    unittest.main()
