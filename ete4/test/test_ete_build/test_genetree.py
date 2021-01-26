from __future__ import absolute_import
from __future__ import print_function

import os
import multiprocessing
CPUS = min(20, max(1, multiprocessing.cpu_count()-1))
import unittest

from ...tools import ete
from ... import Tree, SeqGroup

DIR = os.path.split(os.path.abspath(__file__))[0]

def get_out_files(outdir, workflow, fasta):
    clean_tree = "%s/%s/%s.final_tree.nw" %(outdir, workflow, fasta)
    extended_tree = "%s/%s/%s.final_tree.nwx" %(outdir, workflow, fasta)
    alg_used = "%s/%s/%s.final_tree.used_alg.fa" %(outdir, workflow, fasta)
    alg = "%s/%s/%s.final_tree.fa" %(outdir, workflow, fasta)
    alg_trimmed = "%s/%s/%s.final_tree.fa" %(outdir, workflow, fasta)
    img = "%s/%s/%s.final_tree.png" %(outdir, workflow, fasta)
    cmd = "%s/%s/commands.log" %(outdir, workflow)
    return clean_tree, extended_tree, alg_used, alg, alg_trimmed, img, cmd

class Test_ete_build_genetree(unittest.TestCase):
    def test_01_aa_genetree_worflow(self):
        aligners = "muscle_default", "clustalo_default", "mafft_default"
        trimmers = "none", "trimal01"
        testers = "none", "pmodeltest_full_fast"
        builders = "phyml_default", "raxml_default", "fasttree_default", "iqtree_default"
        for _aligner in aligners:
            for _trimmer in trimmers:
                for _tester in testers:
                    for _builder in builders:
                        pass
if __name__ == "__main__":
    unittest.main()
