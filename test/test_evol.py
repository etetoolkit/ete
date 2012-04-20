#!/usr/bin/python
"""
11 Nov 2010

test module
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


import unittest
from ete_dev.evol             import EvolTree
from random                   import random as rnd
from copy                     import deepcopy
from ete_dev                  import __path__ as ete_path
from cPickle                  import load, dump
import os

def random_swap(tree):
    '''
    swap randomly tree, to make sure labelling as paml is well done
    '''
    for node in tree.iter_descendants():
        if int (rnd()*100)%3:
            node.swap_children()
    
def check_annotation (tree):
    '''
    check each node is labelled with a paml_id
    '''
    for node in tree.iter_descendants():
        if not hasattr (node, 'paml_id'):
            raise Exception ('Error, unable to label with paml ids')
    return True


class TestEvolEvolTree(unittest.TestCase):
    """Tests EvolTree basics"""

    def test_paml_parser(self):
        alignments = ['  3 6\nseq1\tyo\nATGATG\nseq2\nCTGATG\nseq3\nATGTTT\n',
                      '  3 6\n>seq1\nATGATG\n>seq2\t|prout\nCTGATG\n>seq3\nATGTTT\n',
                      '>seq1 \nATGATG\n>seq2\nCTGATG\n>seq3\nATGTTT\n']
        for ali in alignments:
            t = EvolTree('((seq1,seq2),seq3);')
            t.link_to_alignment(ali)
            self.assertEqual((t & 'seq1').nt_sequence, 'ATGATG')
            self.assertEqual((t & 'seq2').nt_sequence, 'CTGATG')
            self.assertEqual((t & 'seq3').nt_sequence, 'ATGTTT')

    def test_load_model(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
        tree.link_to_evol_model (WRKDIR + 'paml/M1/M1.out', 'M1')
        tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
        tree.link_to_evol_model (WRKDIR + 'paml/M7/M7.out', 'M7')
        tree.link_to_evol_model (WRKDIR + 'paml/M8/M8.out', 'M8')
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        self.assertEqual(sorted(tree._models.keys()),
                         sorted(['fb', 'M1', 'M2', 'M7', 'M8']))
        self.assertEqual(len (tree.get_evol_model('M2').branches), 193)
        self.assertEqual(tree.get_evol_model('fb').lnL, -3265.316569)
        self.assert_('proportions' in str(tree.get_evol_model('M2')))
        self.assert_('p2=' in str(tree.get_evol_model('M2')))
        self.assert_('proportions' not in str(tree.get_evol_model('fb')))
        self.assert_(' #194' in str(tree.get_evol_model('fb')))

    def test_get_most_likely(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        tree.link_to_evol_model (WRKDIR + 'paml/M1/M1.out', 'M1')
        tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
        self.assertEqual(tree.get_most_likely ('M2','M1'),
                         6.3280740347111373e-10)

    def test_labelling_tree(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        random_swap(tree)
        tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
        self.assert_(check_annotation (tree))
        
    def test_deep_copy(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
        fba = deepcopy (tree.get_evol_model('fb'))
        tree._models['fb.a'] = fba
        self.assertEqual(str(tree.get_evol_model('fb.a')),
                         str(tree.get_evol_model('fb'))
                     )
    def test_call_histface(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2.a')
        col =  {'NS' : 'grey', 'RX' : 'black',
                'RX+': 'grey', 'CN' : 'black',
                'CN+': 'grey', 'PS' : 'black', 'PS+': 'black'}
        col2 = {'NS' : 'white', 'RX' : 'white',
                'RX+': 'white', 'CN' : 'white',
                'CN+': 'white', 'PS' : 'white', 'PS+': 'white'}
        M2a = tree.get_evol_model('M2.a')
        M2a.set_histface (up=False, typ='line', lines=[1.0, 0.3],
                          col_lines=['red','grey'], header='ugliest face')
        M2a.set_histface (up=False, typ='error', col=col2,
                          lines = [2.5, 1.0, 4.0, 0.5],
                          header = 'Many lines, error boxes, background black',
                          col_lines=['orange', 'yellow', 'red', 'cyan'])
        M2a.set_histface (up=False, typ='protamine', lines = [1.0, 0.3],
                          col_lines=['black','grey'],
                          extras=['+','-',' ',' ',' ',':P', ' ',' ']*2 + \
                          [' ']*(len(tree.get_leaves()[0].sequence)-16))
        M2a.set_histface (up=False, typ='hist', col=col, lines = [1.0, 0.3],
                          col_lines=['black','grey'])
        self.assertEqual(str(type(M2a.properties['histface'])),
                         "<class 'ete_dev.evol.treeview.histface.HistFace'>")

    def test_run_codeml(self):
        tree = EvolTree('((seq1,seq2),seq3);')
        tree.link_to_alignment('>seq1\nATGCTG\n>seq2\nATGCTG\n>seq3\nTTGATG\n')
        tree.run_model('fb')
        self.assert_('CODONML' in tree.get_evol_model('fb').run)
        self.assert_('Time used:' in tree.get_evol_model('fb').run)
        self.assert_('end of tree file' in tree.get_evol_model('fb').run)
        self.assert_('lnL' in tree.get_evol_model('fb').run)

    def test_run_slr(self):
        tree = EvolTree('((seq1,seq2),seq3);')
        tree.link_to_alignment('>seq1\nCTGATTCTT\n>seq2\nCTGATTCTT\n>seq3\nATGATTCTT\n')
        tree.run_model('SLR')
        self.assert_('Sitewise Likelihood R' in tree.get_evol_model('SLR').run)
        self.assert_('Positively selected s' in tree.get_evol_model('SLR').run)
        self.assert_('Conserved sites' in tree.get_evol_model('SLR').run)
        self.assert_('lnL' in tree.get_evol_model('SLR').run)

    def test_marking_trees(self):
        TREE_PATH = ete_path[0] + '/../examples/evol/data/S_example/'
        tree = EvolTree (TREE_PATH + 'measuring_S_tree.nw')
        self.assertEqual(tree.write(),
                         '((Hylobates_lar,(Gorilla_gorilla,Pan_troglodytes)),Papio_cynocephalus);')
        tree.mark_tree ([2, 3, 4] + [1, 5], marks=['#1']*3 + ['#2']*2, verbose=True)
        self.assertEqual(tree.write().replace(' ', ''),
                         '((Hylobates_lar#2,(Gorilla_gorilla#1,Pan_troglodytes#1)#1)#2,Papio_cynocephalus);')
        tree.mark_tree (map (lambda x: x._nid, tree.get_descendants()),
                        marks=[''] * len (tree.get_descendants()), verbose=False)
        self.assertEqual(tree.write().replace(' ', ''),
                         '((Hylobates_lar,(Gorilla_gorilla,Pan_troglodytes)),Papio_cynocephalus);')

    def test_pickling(self):
        WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2.a')
        out = open('blip.pik', 'w')
        dump (tree, out)
        out.close()
        out = open('blip.pik')
        tree2 = load (out)
        out.close()
        os.remove('blip.pik')
        self.assertEqual(str(tree2.get_evol_model('M2.a')),
                         str(tree.get_evol_model('M2.a'))
        )

        
if __name__ == '__main__':
    unittest.main()
