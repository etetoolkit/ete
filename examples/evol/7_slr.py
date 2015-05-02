#!/usr/bin/python
"""
06 Feb 2011

use slr to compute evolutionary rates
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete3 import EvolTree


tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ("data/S_example/alignment_S_measuring_evol.fasta")


tree.run_model ('SLR')

slr = tree.get_evol_model ('SLR')

slr.set_histface (up=False, kind='curve',errors=True,
                  hlines = [1.0,0.3], hlines_col=['black','grey'])

tree.show (histfaces=['SLR'])





