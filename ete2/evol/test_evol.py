#!/usr/bin/python
"""
11 Nov 2010

test module
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"



from ete_dev.evol import EvolTree, faces
from random import random as rnd


WRKDIR = 'examples/data/protamine/PRM1/'

def main():
    """
    main function
    """
    tree = EvolTree (WRKDIR + 'tree.nw')
    tree.workdir = 'examples/data/protamine/PRM1/paml/'

    random_swap(tree)
    tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
    check_annotation (tree)
    tree.link_to_evol_model (WRKDIR + 'paml/M1/M1.out', 'M1')
    tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
    tree.link_to_evol_model (WRKDIR + 'paml/M7/M7.out', 'M7')
    tree.link_to_evol_model (WRKDIR + 'paml/M8/M8.out', 'M8')
    tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
    print 'pv of LRT M2 vs M1: ',
    print tree.get_most_likely ('M2','M1')
    print 'pv of LRT M8 vs M7: ',
    print tree.get_most_likely ('M8','M7')
    tree.get_evol_model('M2').set_histface (up=True, typ='error',
                                            lines = [1.0,0.3],
                                            col_lines=['black','grey'])
    tree.show (histfaces=['M2'])

    # run codeml
    TREE_PATH    = "examples/data/S_example/measuring_S_tree.nw"
    ALG_PATH     = "examples/data/S_example/alignment_S_measuring_evol.fasta"
    WORKING_PATH = "/tmp/ete2-codeml_example/"
    
    tree = EvolTree (TREE_PATH)
    tree.link_to_alignment (ALG_PATH)
    tree.workdir = (WORKING_PATH)
    tree.run_model ('fb')
    tree.run_model ('M1')
    tree.run_model ('M2')
    tree.run_model ('M7')
    tree.run_model ('M8')
    print 'pv of LRT M2 vs M1: ',
    print tree.get_most_likely ('M2','M1')
    print 'pv of LRT M8 vs M7: ',
    print tree.get_most_likely ('M8','M7')
    tree.get_evol_model('M8').set_histface (up=False, typ='protamine',
                                            lines = [1.0,0.3],
                                            col_lines=['black','grey'])
    tree.show(histfaces=['M2', 'M8'])
    tree.mark_tree ([2])
    print tree.write()
    tree.run_model ('bsA.2')
    tree.run_model ('bsA1.2')
    print 'pv of LRT bsA vs bsA1: ',
    print tree.get_most_likely ('bsA.2','bsA1.2')
    # clean marks:
    print tree.write()
    tree.mark_tree (map (lambda x: x._nid, tree.get_descendants()),
                    marks=[''] * len (tree.get_descendants()), verbose=True)
    print tree.write()
    tree.mark_tree ([2, 3, 4] + [1, 5], marks=['#1']*3 + ['#2']*2)
    print tree.write()
    tree.run_model ('bsC.2-3-4_1-5')
    tree.run_model ('bsA1.2')
    print 'pv of LRT bsC vs M1, marking 2 3 4 versus 1 5: ',
    print tree.get_most_likely ('bsC.2-3-4_1-5','M1')
    tree.run_model ('b_free.2-3-4_1-5')
    tree.run_model ('b_neut.2-3-4_1-5')
    print 'pv of LRT b_free 2 3 4, 1 5 amd outgroup vs 1 5 with omega = 1: ',
    print tree.get_most_likely ('b_free.2-3-4_1-5','b_neut.2-3-4_1-5')

    print "The End."


def random_swap(tree):
    for node in tree.iter_descendants():
        if int (rnd()*100)%3:
            node.swap_childs()
    
def check_annotation (tree):
    for node in tree.iter_descendants():
        if not hasattr (node, 'paml_id'):
            print 'Error, unable to label with paml ids'
            break
    print 'Labelling ok!'


if __name__ == "__main__":
    exit(main())
