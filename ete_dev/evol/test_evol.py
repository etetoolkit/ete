#!/usr/bin/python
"""
11 Nov 2010

test module
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete_dev                  import EvolTree
from ete_dev.treeview.layouts import evol_clean_layout
from ete_dev                  import faces, TreeStyle
from random                   import random as rnd
from model                    import Model
from copy                     import deepcopy
from ete_dev                  import __path__ as ete_path
import sys, os
from cPickle                  import load, dump


WRKDIR = ete_path[0] + '/../examples/evol/data/protamine/PRM1/'

dumb_align = '''>seq1
ATGATG
>seq2
ATGATG
>seq3
ATGATG
'''

dumb_tree = '((seq1,seq2),seq3);'

def get_err():
    return '   # ' + sys.exc_info()[1].message.replace('\n', '\n   # ')

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
    
def main():
    errors = {}
    ############################################################################
    print '-> Testing paml alignment parser',
    try:
        test_paml_parser()
        print 'OK'
        errors['Alignement Parser'] = False
    except:
        print 'ERROR'
        errors['Alignement Parser'] = get_err()
    ############################################################################
    print '-> Loading EvolTree',
    try:
        tree = EvolTree (WRKDIR + 'tree.nw')
        tree.workdir = 'examples/data/protamine/PRM1/paml/'
        print 'OK'
        errors['Loading EvolTree'] = False
    except:
        print 'ERROR'
        errors['Loading EvolTree'] = get_err()
    ############################################################################
    print '-> Loading Models',
    try:
        tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
        tree.link_to_evol_model (WRKDIR + 'paml/M1/M1.out', 'M1')
        tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
        tree.link_to_evol_model (WRKDIR + 'paml/M7/M7.out', 'M7')
        tree.link_to_evol_model (WRKDIR + 'paml/M8/M8.out', 'M8')
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        print 'OK'
        errors['Loading Models'] = False
    except:
        print 'ERROR'
        errors['Loading Models'] = get_err()
    ############################################################################
    print '-> Get most likely',
    try:
        if tree.get_most_likely ('M2','M1') > 1e-09:
            raise Exception ('able to run, but not a good value')
        print 'OK'
        errors['Get most likely'] = False
    except:
        print 'ERROR'
        errors['Get most likely'] = get_err()
    ############################################################################
    print '-> Loading alignment',
    try:
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        print 'OK'
        errors['Loading alignment'] = False
    except:
        print 'ERROR'
        errors['Loading alignment'] = get_err()
    ############################################################################
    print '-> Labelling tree',
    try:
        random_swap(tree)
        tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
        check_annotation (tree)
        errors['Labelling tree'] = False
        print 'OK'
    except:
        print 'ERROR'
        errors['Labelling tree'] = get_err()
    ############################################################################
    print '-> Deepcopy',
    try:
        M2a = deepcopy (tree.get_evol_model('M2'))
        tree._models['M2.a'] = M2a
        print 'OK'
        errors['Deepcopy'] = False
    except:
        print 'ERROR'
        errors['Deepcopy'] = get_err()
    ############################################################################
    print '-> Histfaces',
    try:
        col =  {'NS' : 'grey', 'RX' : 'black',
                'RX+': 'grey', 'CN' : 'black',
                'CN+': 'grey', 'PS' : 'black', 'PS+': 'black'}
        col2 = {'NS' : 'white', 'RX' : 'white',
                'RX+': 'white', 'CN' : 'white',
                'CN+': 'white', 'PS' : 'white', 'PS+': 'white'}
        M2a.set_histface (up=False, typ='line', lines = [1.0,0.3], col_lines=['red','grey'], header='ugliest face')
        M2a.set_histface (up=False, typ='error', col=col2, lines = [2.5, 1.0, 4.0, 0.5], header = 'Many lines, error boxes, background black',
                          col_lines=['orange', 'yellow', 'red', 'cyan'])
        M2a.set_histface (up=False, typ='protamine', lines = [1.0,0.3], col_lines=['black','grey'],
                          extras=['+','-',' ',' ',' ',':P', ' ',' ']*2+[' ']*(len(tree.get_leaves()[0].sequence)-16))
        M2a.set_histface (up=False, typ='hist', col=col, lines = [1.0,0.3], col_lines=['black','grey'])
        print 'OK'
        errors['Histfaces'] = False
    except:
        print 'ERROR'
        errors['Histfaces'] = get_err()
    ############################################################################
    print '-> Running CodeML',
    try:
        TREE_PATH    = ete_path[0] + '/../examples/evol/data/S_example/measuring_S_tree.nw'
        ALG_PATH     = ete_path[0] + '/../examples/evol/data/S_example/alignment_S_measuring_evol.fasta'
        WORKING_PATH = "/tmp/ete2-codeml_example/"
        tree = EvolTree (TREE_PATH)
        tree.link_to_alignment (ALG_PATH)
        tree.workdir = (WORKING_PATH)
        tree.run_model ('M0.test')
        print 'OK'
        errors['Running CodeML'] = False
    except:
        print 'ERROR: certainly not installed'
        errors['Running CodeML'] = get_err()
    ############################################################################
    print '-> Running SLR',
    try:
        tree.run_model ('SLR')
        print 'OK'
        errors['Running SLR'] = False
    except:
        print 'ERROR: certainly not installed'
        errors['Running SLR'] = get_err()
    ############################################################################
    print '-> Marking trees',
    try:
        if tree.write() != '((Hylobates_lar,(Gorilla_gorilla,Pan_troglodytes)),Papio_cynocephalus);':
            raise Exception ('simple write failed')
        tree.mark_tree (map (lambda x: x._nid, tree.get_descendants()),
                        marks=[''] * len (tree.get_descendants()), verbose=True)
        if tree.write().replace(' ', '') != '((Hylobates_lar,(Gorilla_gorilla,Pan_troglodytes)),Papio_cynocephalus);':
            raise Exception ('clean marks failed')
        tree.mark_tree ([2, 3, 4] + [1, 5], marks=['#1']*3 + ['#2']*2)
        if tree.write().replace(' ', '') != '((Hylobates_lar#2,(Gorilla_gorilla#1,Pan_troglodytes#1)#1)#2,Papio_cynocephalus);':
            raise Exception ('complete marks failed')
        print 'OK'
        errors['Marking trees'] = False
    except:
        print 'ERROR'
        errors['Marking trees'] = get_err()
    ############################################################################
    print '-> Pickling',
    try:
        out = open('blip.pik', 'w')
        dump (tree, out)
        out.close()
        out = open('blip.pik')
        tree = load (out)
        out.close()
        os.remove('blip.pik')
        print 'OK'
        errors['Pickling'] = False
    except:
        print 'ERROR'
        errors['Pickling'] = get_err()
    ############################################################################
    print '-> ',
    try:
        tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
        print 'OK'
        errors[''] = False
    except:
        print 'ERROR'
        errors[''] = get_err()

    ############################################################################

    ############################################################################
        
    ############################################################################
        
    print '\n\n Errors found:' + (' None' if all (errors.values()) else '')
    print '############################################################################'
    for e in errors:
        if errors[e]:
            print '-> '+e + ':'
            print errors[e]
            print '############################################################################'
            
def test_paml_parser():
    alignments = ['''  3 6
seq1
ATGATG
seq2
ATGATG
seq3
ATGATG
''',
'''  3 6
>seq1
ATGATG
>seq2
ATGATG
>seq3
ATGATG

''',
'''>seq1
ATGATG
>seq2
ATGATG
>seq3
ATGATG
''']
    for ali in alignments:
        t = EvolTree('((seq1,seq2),seq3);')
        t.link_to_alignment(ali)

if __name__ == "__main__":
    exit(main())
