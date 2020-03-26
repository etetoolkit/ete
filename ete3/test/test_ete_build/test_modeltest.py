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
    
class Test_ete_build_modeltest(unittest.TestCase):
    def test_01_aa_genetree_worflows_with_model_test(self):        
        aligners = "muscle_default", "clustalo_default", "mafft_default"
        trimmers = "none", "trimal01"
        testers = "none", "pmodeltest_full_fast"
        builders = "phyml_default", "raxml_default", "fasttree_default"
        for _aligner in aligners:
            for _trimmer in trimmers:
                for _tester in testers:
                    for _builder in builders:
                        wkname = "%s-%s-%s-%s" %(_aligner, _trimmer, _tester, _builder)
                        expected_nw = '(30611.ENSOGAP00000015106:0.0794915,(30608.ENSMICP00000013539:0.0917718,(9483.ENSCJAP00000027663:0.081188,(9544.ENSMMUP00000035274:0.0293646,(9601.ENSPPYP00000008923:0.017464,(61853.ENSNLEP00000011861:0.0460495,(9593.ENSGGOP00000009561:0.00324716,9606.ENSP00000269305:2.4e-07)0.99985:0.0108707)0.725327:0.0031931)0.99985:0.0125782)0.99985:0.0309675)0.99985:0.0348935)1:0.0794915);'
                        expected_tree = Tree(expected_nw)        
                        cmd = 'ete3 build -a %s/P53.fa -w %s -o ete_test_tmp/etebuild_test1  -t0.3 --launch 0.5 --clearall --cpu %d' %(DIR, wkname, CPUS)
                        args = cmd.split()
                        ete._main(args)                        
                        ctree, xtree, alg_used, alg, alg_trimmed, img, cmd = get_out_files("ete_test_tmp/etebuild_test1", wkname, "P53.fa")
                        t1 = Tree(ctree)
                        t2 = Tree(xtree)
                        a1 = SeqGroup(alg_used)
                        a2 = SeqGroup(alg)
                        self.assertEqual(t1.robinson_foulds(expected_tree)[:2], [0, 12])
                        self.assertEqual(t2.robinson_foulds(expected_tree)[:2], [0, 12])
                        if _tester != "none":
                            # This are the expected winner models given the corresponding algs (tested with the online version of prottest)
                            if wkname.startswith('mafft_default-'):
                                self.assertEqual(wkname+t2.modeltester_bestmodel, wkname+"pmodeltest-HIVb+I+F!G")
                            else:
                                self.assertEqual(wkname+t2.modeltester_bestmodel, wkname+"pmodeltest-HIVb+G+F!I")                            
                        if _trimmer:
                            SeqGroup(alg_trimmed)
                            
if __name__ == "__main__":
    unittest.main()
