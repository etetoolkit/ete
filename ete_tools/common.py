import sys

from ete_dev import Tree, PhyloTree, faces, TreeStyle, add_face_to_node, orthoxml, SVG_COLORS, faces, treeview, NodeStyle
from jhc_utils import print_table, color, timeit
from ncbi_taxonomy import ncbi_query

try:
    import argparse
except ImportError:
    from ete_dev import argparse

__CITATION__ = '''#       ** If you use this software for a published work, please cite: **
#  
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. ETE: a python Environment
# for Tree Exploration. BMC Bioinformatics 2010, 11:24. doi: 10.1186/1471-2105-11-24.'''
