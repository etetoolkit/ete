#!/usr/bin/python
"""
10 Nov 2010

example to test, extrernal runs of codeml
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete3 import EvolTree, faces
from random import random as rnd

WRKDIR = 'data/protamine/PRM1/'

def main():
    """
    main function
    """
    tree = EvolTree (WRKDIR + 'tree.nw')
    tree.workdir = 'data/protamine/PRM1/paml/'

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


    tree.show (histfaces=['M2'])

    print 'The End.'


def random_swap(tree):
    for node in tree.iter_descendants():
        if int (rnd()*100)%3:
            node.swap_children()

def check_annotation (tree):
    for node in tree.iter_descendants():
        if not hasattr (node, 'paml_id'):
            print 'Error, unable to label with paml ids'
            break
    print 'Labelling ok!'


if __name__ == "__main__":
    exit(main())
