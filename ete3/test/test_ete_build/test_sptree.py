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
    

class Test_ete_build_sptree(unittest.TestCase):
    def test_01_sptree_worflow(self):
        gene_wkname = 'clustalo_default-trimal01-none-none'
        for wkname in "cog_all-alg_concat_default-raxml_default", "cog_all-alg_concat_default-fasttree":
            wkname = "cog_all-alg_concat_default-raxml_default"
            cmd = 'ete3 build -a %s/cog_seqs.fa --cogs %s/fake_cogs.tsv -w %s -m %s -o ete_test_tmp/etebuild_test2  -t0.5 --launch 0.5 --clearall --cpu %d' %(DIR, DIR, gene_wkname, wkname, CPUS)
            args = cmd.split()
            ete._main(args)                        
            ctree, xtree, alg_used, alg, alg_trimmed, img, cmd = get_out_files("ete_test_tmp/etebuild_test2", wkname, "cog_seqs.fa")
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
                            
if __name__ == "__main__":
    unittest.main()
