from __future__ import absolute_import
from __future__ import print_function
import unittest

from .. import PhyloTree, SeqGroup
from .datasets import *

class Test_phylo_module(unittest.TestCase):

    # ALL TESTS USE THIS EXAMPLE TREE
    #
    #                    /-Dme_001
    #          /--------|
    #         |          \-Dme_002
    #         |
    #         |                              /-Cfa_001
    #         |                    /--------|
    #         |                   |          \-Mms_001
    #         |                   |
    #---------|                   |                                        /-Hsa_001
    #         |                   |                              /--------|
    #         |          /--------|                    /--------|          \-Hsa_003
    #         |         |         |                   |         |
    #         |         |         |          /--------|          \-Ptr_001
    #         |         |         |         |         |
    #         |         |         |         |          \-Mmu_001
    #         |         |          \--------|
    #          \--------|                   |                    /-Hsa_004
    #                   |                   |          /--------|
    #                   |                    \--------|          \-Ptr_004
    #                   |                             |
    #                   |                              \-Mmu_004
    #                   |
    #                   |          /-Ptr_002
    #                    \--------|
    #                             |          /-Hsa_002
    #                              \--------|
    #                                        \-Mmu_002


    def test_link_alignmets(self):
        """ Phylotree can be linked to SeqGroup objects"""
        fasta = """
         >seqA
         MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
         >seqB
         MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
         >seqC
         MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
         >seqD
         MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
        """
        # Caution with iphylip string. blank spaces in the beginning are important
        iphylip = """
         4 76
      seqA   MAEIPDETIQ QFMALT---H NIAVQYLSEF GDLNEALNSY YASQTDDIKD RREEAHQFMA
      seqB   MAEIPDATIQ QFMALTNVSH NIAVQY--EF GDLNEALNSY YAYQTDDQKD RREEAHQFMA
      seqC   MAEIPDATIQ ---ALTNVSH NIAVQYLSEF GDLNEALNSY YASQTDDQPD RREEAHQFMA
      seqD   MAEAPDETIQ QFMALTNVSH NIAVQYLSEF GDLNEAL--- ---------- -REEAHQ---

             LTNVSHQFMA LTNVSH
             LTNVSH---- ------
             LTNVSH---- ------
             -------FMA LTNVSH
        """

        # Loads a tree and link it to an alignment. As usual, 'alignment' can be
        # the path to a file or the data themselves in text string format

        alg1 = SeqGroup(fasta)
        alg2 = SeqGroup(iphylip, format="iphylip")

        t = PhyloTree("(((seqA,seqB),seqC),seqD);", alignment=fasta, alg_format="fasta")

        for l in t.get_leaves():
            self.assertEqual(l.sequence, alg1.get_seq(l.name))

        # The associated alignment can be changed at any time
        t.link_to_alignment(alignment=alg2, alg_format="iphylip")

        for l in t.get_leaves():
            self.assertEqual(l.sequence, alg2.get_seq(l.name))

    def test_get_sp_overlap_on_all_descendants(self):
        """ Tests ortholgy prediction using the sp overlap"""
        # Creates a gene phylogeny with several duplication events at
        # different levels.
        t = PhyloTree('((Dme_001,Dme_002),(((Cfa_001,Mms_001),((((Hsa_001,Hsa_003),Ptr_001),Mmu_001),((Hsa_004,Ptr_004),Mmu_004))),(Ptr_002,(Hsa_002,Mmu_002))));')

        # Scans the tree using the species overlap algorithm and detect all
        # speciation and duplication events
        events = t.get_descendant_evol_events()

        # Check that all duplications are detected
        dup1 = t.get_common_ancestor("Hsa_001", "Hsa_004")
        self.assertEqual(dup1.evoltype, "D")

        dup2 = t.get_common_ancestor("Dme_001", "Dme_002")
        self.assertEqual(dup2.evoltype, "D")

        dup3 = t.get_common_ancestor("Hsa_001", "Hsa_002")
        self.assertEqual(dup3.evoltype, "D")

        dup4 = t.get_common_ancestor("Hsa_001", "Hsa_003")
        self.assertEqual(dup4.evoltype, "D")


        # All other nodes should be speciation
        for node in t.traverse():
            if not node.is_leaf() and \
                   node not in set([dup1, dup2, dup3, dup4]):
                self.assertEqual(node.evoltype, "S")

        # Check events
        for e in events:
            self.assertEqual(e.node.evoltype, e.etype)

        # Check orthology/paralogy prediction
        orthologs = set()
        for e in events:
            if e.node == dup1:
                self.assertEqual(e.inparalogs, set(['Ptr_001', 'Hsa_001', 'Mmu_001', 'Hsa_003']))
                self.assertEqual(e.outparalogs, set(['Mmu_004', 'Ptr_004', 'Hsa_004']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.outparalogs, e.out_seqs)
                self.assertEqual(e.inparalogs, e.in_seqs)
            elif e.node == dup2:
                self.assertEqual(e.inparalogs, set(['Dme_001']))
                self.assertEqual(e.outparalogs, set(['Dme_002']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.outparalogs, e.out_seqs)
                self.assertEqual(e.inparalogs, e.in_seqs)
            elif e.node == dup3:
                self.assertEqual(e.inparalogs, set(['Hsa_003', 'Cfa_001', 'Ptr_001', 'Hsa_001', 'Ptr_004', 'Hsa_004', 'Mmu_004', 'Mmu_001', 'Mms_001']))
                self.assertEqual(e.outparalogs, set(['Hsa_002', 'Ptr_002', 'Mmu_002']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.outparalogs, e.out_seqs)
                self.assertEqual(e.inparalogs, e.in_seqs)
            elif e.node == dup4:
                self.assertEqual(e.inparalogs, set(['Hsa_001']))
                self.assertEqual(e.outparalogs, set(['Hsa_003']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.outparalogs, e.out_seqs)
                self.assertEqual(e.inparalogs, e.in_seqs)
            else:

                key1 = list(e.inparalogs)
                key2 = list(e.orthologs)
                key1.sort()
                key2.sort()
                orthologs.add(tuple(sorted([tuple(key1), tuple(key2)])))

        orthologies = [
            [set(['Dme_001', 'Dme_002']), set(['Ptr_001', 'Cfa_001', 'Hsa_002', 'Hsa_003', 'Ptr_002', 'Hsa_001', 'Ptr_004', 'Hsa_004', 'Mmu_004', 'Mmu_001', 'Mms_001', 'Mmu_002'])],
            [set(['Mms_001', 'Cfa_001']), set(['Hsa_003', 'Ptr_001', 'Hsa_001', 'Ptr_004', 'Hsa_004', 'Mmu_004', 'Mmu_001'])],
            [set(['Ptr_002']), set(['Hsa_002', 'Mmu_002'])],
            [set(['Cfa_001']), set(['Mms_001'])],
            [set(['Hsa_002']), set(['Mmu_002'])],
            [set(['Hsa_003', 'Hsa_001', 'Ptr_001']), set(['Mmu_001'])],
            [set(['Ptr_004', 'Hsa_004']), set(['Mmu_004'])],
            [set(['Hsa_003', 'Hsa_001']), set(['Ptr_001'])],
            [set(['Hsa_004']), set(['Ptr_004'])]
            ]
        expected_orthologs = set()
        for l1,l2 in orthologies:
            key1 = list(l1)
            key2 = list(l2)
            key1.sort()
            key2.sort()
            expected_orthologs.add(tuple(sorted([tuple(key1), tuple(key2)])))

        # Are all orthologies as expected
        self.assertEqual(expected_orthologs, orthologs)

        # Test different sos_thr
        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = t.get_descendant_evol_events(0.1)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'D')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'D')

        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = t.get_descendant_evol_events(0.5)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'S')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'D')

        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = seed.get_my_evol_events(0.75)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'S')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'S')

    def test_get_sp_overlap_on_a_seed(self):
        """ Tests ortholgy prediction using sp overlap"""
        # Creates a gene phylogeny with several duplication events at
        # different levels.
        t = PhyloTree('((Dme_001,Dme_002),(((Cfa_001,Mms_001),((((Hsa_001,Hsa_003),Ptr_001),Mmu_001),((Hsa_004,Ptr_004),Mmu_004))),(Ptr_002,(Hsa_002,Mmu_002))));')

        # Scans the tree using the species overlap algorithm
        seed = t.search_nodes(name="Hsa_001")[0]
        events = seed.get_my_evol_events()

        # Check that duplications are detected
        dup1 = t.get_common_ancestor("Hsa_001", "Hsa_004")
        #print(dup1)
        self.assertEqual(dup1.evoltype, "D")

        # This duplication is not in the seed path
        dup2 = t.get_common_ancestor("Dme_001", "Dme_002")
        self.assertTrue(not hasattr(dup2, "evoltype"))

        dup3 = t.get_common_ancestor("Hsa_001", "Hsa_002")
        self.assertEqual(dup3.evoltype, "D")

        dup4 = t.get_common_ancestor("Hsa_001", "Hsa_003")
        self.assertEqual(dup4.evoltype, "D")

        # All other nodes should be speciation
        node = seed
        while node:
            if not node.is_leaf() and \
                   node not in set([dup1, dup2, dup3, dup4]):
                self.assertEqual(node.evoltype, "S")
            node = node.up

        # Check events
        for e in events:
            self.assertEqual(e.node.evoltype, e.etype)

        # Check orthology/paralogy prediction
        orthologs = set()
        for e in events:
            if e.node == dup1:
                self.assertEqual(e.inparalogs, set(['Hsa_001', 'Hsa_003']))
                self.assertEqual(e.outparalogs, set(['Hsa_004']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.in_seqs, set(['Ptr_001', 'Hsa_001', 'Mmu_001', 'Hsa_003']))
                self.assertEqual(e.out_seqs, set(['Mmu_004', 'Ptr_004', 'Hsa_004']))
            elif e.node == dup3:
                self.assertEqual(e.inparalogs, set(['Hsa_003', 'Hsa_001',  'Hsa_004' ]))
                self.assertEqual(e.outparalogs, set(['Hsa_002']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.in_seqs, set(['Hsa_003', 'Cfa_001', 'Ptr_001', 'Hsa_001', 'Ptr_004', 'Hsa_004', 'Mmu_004', 'Mmu_001', 'Mms_001']))
                self.assertEqual(e.out_seqs, set(['Hsa_002', 'Ptr_002', 'Mmu_002']))
            elif e.node == dup4:
                self.assertEqual(e.inparalogs, set(['Hsa_001']))
                self.assertEqual(e.outparalogs, set(['Hsa_003']))
                self.assertEqual(e.orthologs, set())
                self.assertEqual(e.in_seqs, set(['Hsa_001']))
                self.assertEqual(e.out_seqs, set(['Hsa_003']))
            else:

                key1 = list(e.inparalogs)
                key2 = list(e.orthologs)
                key1.sort()
                key2.sort()
                orthologs.add(tuple(sorted([tuple(key1), tuple(key2)])))


        orthologies = [
            [set(['Dme_001', 'Dme_002']), set([ 'Hsa_002', 'Hsa_003', 'Hsa_001',  'Hsa_004' ])],
            [set(['Mms_001', 'Cfa_001']), set(['Hsa_003',  'Hsa_001', 'Hsa_004'])],
            [set(['Hsa_003', 'Hsa_001']), set(['Mmu_001'])],
            [set(['Hsa_003', 'Hsa_001']), set(['Ptr_001'])],
            ]
        expected_orthologs = set()
        for l1,l2 in orthologies:
            key1 = list(l1)
            key2 = list(l2)
            key1.sort()
            key2.sort()
            expected_orthologs.add(tuple(sorted([tuple(key1), tuple(key2)])))

        # Are all orthologies as expected
        self.assertEqual(expected_orthologs, orthologs)

        # Test different sos_thr
        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = seed.get_my_evol_events(0.1)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'D')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'D')

        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = seed.get_my_evol_events(0.50)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'S')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'D')

        t = PhyloTree('(((SP1_a, SP2_a), (SP3_a, SP1_b)), (SP1_c, SP2_c));')
        seed = (t & 'SP1_a')
        events = seed.get_my_evol_events(0.75)
        self.assertEqual(t.get_common_ancestor(seed, 'SP3_a').evoltype, 'S')
        self.assertEqual(t.get_common_ancestor(seed, 'SP1_c').evoltype, 'S')

    def test_reconciliation(self):
        """ Tests ortholgy prediction based on the species reconciliation method"""
        gene_tree_nw = '((Dme_001,Dme_002),(((Cfa_001,Mms_001),((Hsa_001,Ptr_001),Mmu_001)),(Ptr_002,(Hsa_002,Mmu_002))));'
        species_tree_nw = "((((Hsa, Ptr), Mmu), (Mms, Cfa)), Dme);"

        genetree = PhyloTree(gene_tree_nw)
        sptree = PhyloTree(species_tree_nw)

        recon_tree, events = genetree.reconcile(sptree)

        # Check that reconcilied tree nodes have the correct lables:
        # gene loss, duplication, etc.
        expected_recon = "((Dme_001:1,Dme_002:1)1:1[&&NHX:evoltype=D],(((Cfa_001:1,Mms_001:1)1:1[&&NHX:evoltype=S],((Hsa_001:1,Ptr_001:1)1:1[&&NHX:evoltype=S],Mmu_001:1)1:1[&&NHX:evoltype=S])1:1[&&NHX:evoltype=S],((Mms:1[&&NHX:evoltype=L],Cfa:1[&&NHX:evoltype=L])1:1[&&NHX:evoltype=L],(((Hsa:1[&&NHX:evoltype=L],Ptr_002:1)1:1[&&NHX:evoltype=L],Mmu:1[&&NHX:evoltype=L])1:1[&&NHX:evoltype=L],((Ptr:1[&&NHX:evoltype=L],Hsa_002:1)1:1[&&NHX:evoltype=L],Mmu_002:1)1:1[&&NHX:evoltype=S])1:1[&&NHX:evoltype=D])1:1[&&NHX:evoltype=L])1:1[&&NHX:evoltype=D])[&&NHX:evoltype=S];"

        self.assertEqual(recon_tree.write(["evoltype"], format=9), PhyloTree(expected_recon).write(features=["evoltype"],format=9))

    def test_miscelaneus(self):
        """ Test several things """
        # Creates a gene phylogeny with several duplication events at
        # different levels.
        t = PhyloTree('((Dme_001,Dme_002),(((Cfa_001,Mms_001),((((Hsa_001,Hsa_003),Ptr_001),Mmu_001),((Hsa_004,Ptr_004),Mmu_004))),(Ptr_002,(Hsa_002,Mmu_002))));')

        # Create a dictionary with relative ages for the species present in
        # the phylogenetic tree.  Note that ages are only relative numbers to
        # define which species are older, and that different species can
        # belong to the same age.
        sp2age = {
          'Hsa': 1, # Homo sapiens (Hominids)
          'Ptr': 2, # P. troglodytes (primates)
          'Mmu': 2, # Macaca mulata (primates)
          'Mms': 3, # Mus musculus (mammals)
          'Cfa': 3, # Canis familiaris (mammals)
          'Dme': 4  # Drosophila melanogaster (metazoa)
        }


        # Check that dup ages are correct
        dup1 = t.get_common_ancestor("Hsa_001", "Hsa_004")
        self.assertEqual(dup1.get_age(sp2age), 2)
        dup2 = t.get_common_ancestor("Dme_001", "Dme_002")
        self.assertEqual(dup2.get_age(sp2age), 4)
        dup3 = t.get_common_ancestor("Hsa_001", "Hsa_002")
        self.assertEqual(dup3.get_age(sp2age), 3)
        dup4 = t.get_common_ancestor("Hsa_001", "Hsa_003")
        self.assertEqual(dup4.get_age(sp2age), 1)

        # Check rooting options
        expected_root = t.search_nodes(name="Dme_002")[0]
        expected_root.dist += 2.3
        self.assertEqual(t.get_farthest_oldest_leaf(sp2age), expected_root)
        #print t
        #print t.get_farthest_oldest_node(sp2age)


        # Check get species functions
        self.assertEqual(t.get_species(), set(sp2age.keys()))
        self.assertEqual(set([sp for sp in t.iter_species()]), set(sp2age.keys()))

    def test_colappse(self):
        t = PhyloTree('((Dme_001,Dme_002),(((Cfa_001,Mms_001),((((Hsa_001,Hsa_001),Ptr_001),Mmu_001),((Hsa_004,Ptr_004),Mmu_004))),(Ptr_002,(Hsa_002,Mmu_002))));')
        collapsed_hsa = '((Dme_001:1,Dme_002:1)1:1,(((Cfa_001:1,Mms_001:1)1:1,(((Ptr_001:1,Hsa_001:1)1:1,Mmu_001:1)1:1,((Hsa_004:1,Ptr_004:1)1:1,Mmu_004:1)1:1)1:1)1:1,(Ptr_002:1,(Hsa_002:1,Mmu_002:1)1:1)1:1)1:1);'
        t2 = t.collapse_lineage_specific_expansions(['Hsa'])
        self.assertEqual(str(collapsed_hsa), str(t2.write()))
        with self.assertRaises(TypeError):
            print(t.collapse_lineage_specific_expansions('Hsa'))


if __name__ == '__main__':
    unittest.main()
