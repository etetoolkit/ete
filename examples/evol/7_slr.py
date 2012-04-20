#!/usr/bin/python
"""
06 Feb 2011

use slr to compuet evilutionnary rates
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete_dev import EvolTree
import os

#os.chdir ('examples')

#tree = EvolTree ("data/bglobin/bglobin.trees")
#tree.link_to_alignment ("data/bglobin/bglobin.paml")



tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ("data/S_example/alignment_S_measuring_evol.fasta")


tree.run_model ('SLR')

slr = tree.get_evol_model ('SLR')

slr.set_histface (up=False, typ='protamine',
                  lines = [1.0,0.3], col_lines=['black','grey'])

tree.show (histfaces=['SLR'])





