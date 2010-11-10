#!/usr/bin/python
"""
10 Nov 2010

example to test, extrernal runs of codeml
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete_dev.evol import EvolTree
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
    tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
    tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
    tree.show ()
    tree.add_histface ('M2')
    tree.show ()

    print 'The End.'


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
