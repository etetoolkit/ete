from __future__ import absolute_import
from __future__ import print_function

import os
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
    

class Test_ete_build(unittest.TestCase):
    def test_01_sptree_worflow(self):
        gene_wkname = 'clustalo_default-trimal01-none-none'
        for wkname in "brh_cog_all-alg_concat_default-raxml_default", "brh_cog_all-alg_concat_default-fasttree":
            wkname = "brh_cog_all-alg_concat_default-raxml_default"
            cmd = 'ete3 build -a %s/cog_seqs.fa --cogs %s/fake_cogs.tsv -w %s -m %s -o /tmp/etebuild_test2  -t0.5 --launch 0.5 --clearall' %(DIR, DIR, gene_wkname, wkname)
            args = cmd.split()
            ete._main(args)                        
            ctree, xtree, alg_used, alg, alg_trimmed, img, cmd = get_out_files("/tmp/etebuild_test2", wkname, "cog_seqs.fa")
            t1 = Tree(ctree)
            t2 = Tree(xtree)
        
            expected_tree = Tree("(sp5:18.0858,((sp3:1.04727e-06,sp4:0.124439)0.49:3.18184,(sp2:1.04727e-06,sp1:1.04727e-06)0:1.04727e-06)1:18.0858);")
            self.assertEqual(t1.robinson_foulds(expected_tree)[:2], [0, 6])
            self.assertEqual(t2.robinson_foulds(expected_tree)[:2], [0, 6])
            self.assertEqual(int(t2.concatalg_cogs), 3)
            
            a2 = SeqGroup(alg)
            expected_seqs = SeqGroup("""
>sp1
AAAAAAAAABBBBBBBBBEEEEEEEEFFFFFFFFFFFFIIIIIIIIIIKKKKKKKKKK
>sp2
AAAAAAAAABBBBBBBBBEEEEEEEEFFFFFFFFFFFFIIIIIIIIIIKKKKKKKK
>sp3
AAAAAAAAACCCCDDDDDEEEEEEEEGGGGGGGGGGGGIIIIIIIIIILLLLLLLLLLLL
>sp4
AAAAAAAAACCCCCDDDDEEEEEEEEGGGGGGGGGGHHIIIIIIIIIILLLLLLLLLMMMM
>sp5
AAAAAAAAAPPPPPPPPPEEEEEEEEPPPPPPPPPPPP
""")
            for name, seq, _ in a2:
                self.assertEqual(seq.replace('-',''), expected_seqs.get_seq(name))

            
                                         
    def test_02_aa_genetree_worflow(self):        
        aligners = "muscle_default", "clustalo_default", "mafft_default"
        trimmers = "none", "trimal01"
        testers = "none", "pmodeltest_full_fast"
        builders = "phyml_default", "raxml_default", "fasttree_default"
        for _aligner in aligners:
            for _trimmer in trimmers:
                for _tester in testers:
                    for _builder in builders:
                        wkname = "%s-%s-%s-%s" %(_aligner, _trimmer, _tester, _builder)
                        expected_nw = '(30611.ENSOGAP00000015106:0.083369,(30608.ENSMICP00000013539:0.106942,(9483.ENSCJAP00000027663:0.085039,(9544.ENSMMUP00000035274:0.0303988,(9601.ENSPPYP00000008923:0.0177729,(61853.ENSNLEP00000011861:0.0492628,(9593.ENSGGOP00000009561:0.00332396,(9598.ENSPTRP00000014836:1e-08,9606.ENSP00000269305:1e-08)0:3.9e-07)0.99985:0.0110212)0.762815:0.00326138)0.99985:0.0130264)0.99985:0.0323286)0.99985:0.0373752)1:0.083369);'
                        expected_tree = Tree(expected_nw)        
                        cmd = 'ete3 build -a %s/P53.fa -w %s -o /tmp/etebuild_test1  -t0.3 --launch 0.5 --clearall' %(DIR, wkname)
                        args = cmd.split()
                        ete._main(args)                        
                        ctree, xtree, alg_used, alg, alg_trimmed, img, cmd = get_out_files("/tmp/etebuild_test1", wkname, "P53.fa")
                        t1 = Tree(ctree)
                        t2 = Tree(xtree)
                        a1 = SeqGroup(alg_used)
                        a2 = SeqGroup(alg)
                        self.assertEqual(t1.robinson_foulds(expected_tree)[:2], [0, 14])
                        self.assertEqual(t2.robinson_foulds(expected_tree)[:2], [0, 14])
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
