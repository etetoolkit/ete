import sys

from ete_dev import Tree, PhyloTree, faces, TreeStyle, add_face_to_node, orthoxml, SVG_COLORS, faces, treeview, NodeStyle
from utils import print_table, color, timeit
from ete_dev.ncbi_taxonomy import ncbiquery as ncbi

try:
    import argparse
except ImportError:
    from ete_dev import argparse

__CITATION__ = '''#       ** If you use this software for a published work, please cite: **
#  
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. ETE: a python Environment
# for Tree Exploration. BMC Bioinformatics 2010, 11:24. doi: 10.1186/1471-2105-11-24.'''




def add_common_arguments(parser, f):
    if f == 'target_trees':
        parser.add_argument("-t", dest='target_trees',
                            type=str, nargs="+",
                            help='a list of target trees (newick files)' )
    elif f == 'target_tree':
        parser.add_argument("-t", dest='target_tree',
                            type=str,
                            help='a target tree')
    elif f == 'ref_tree':
        parser.add_argument("-r", dest='reftree',
                            type=str, 
                            help='A reference tree')
    elif f == 'target_trees_file':
        parser.add_argument("-tf", dest='target_trees_file',
                            type=str, nargs="+",
                            help='a file containing a list of target trees')
    elif f == 'ref_attr':
        parser.add_argument("--ref_attr", dest="ref_attr",
                            default = "name", 
                            help=("The node attribute in the reference tree that should be used as node's name"))
    elif f == 'target_attr':
        parser.add_argument("--target_attr", dest="target_attr",
                            default = "name",
                            help=("The node attribute the target tree(s) that should be used as node's name"))
    elif f == 'target_outgroup':
        parser.add_argument("--target_out", dest="target_outgroup", 
                            nargs = "+",
                            help="""outgroup used to root the target tree(s) prior to any analysis""")
    elif f == 'target_ref':
        parser.add_argument("--ref_out", dest="ref_outgroup", 
                            nargs = "+",
                            help="""outgroup used to root the reference tree prior to any analysis""")
    elif f == 'ref_sp_attr':
        parser.add_argument("--ref_sp_attr", dest="ref_sp_attr", 
                            type=str,
                            help="""attribute in the reference tree that contains the species name or code""")
    elif f == 'ref_sp_attr_parser':
        parser.add_argument("--ref_taxid_sp_parser", dest="ref_sp_attr_parser", 
                            type=str, 
                            help="""A regular expression matching the species name or code from ref_sp_attr""")
    elif f == 'ref_sp_delimiter':
        parser.add_argument("--ref_sp_delimiter", dest="ref_sp_delimiter", 
                            type=str, 
                            help="""A single character delimiter that allows to extract the species name from node names ( i.e. "_" for node names like HUMAN_p53)""")
    elif f == 'ref_sp_field':
        parser.add_argument("--ref_sp_field", dest="ref_sp_field", 
                            type=str, 
                            help="""The position of the species code after splitting node names using ref_sp_delimiter (i.e. 0 for node names like HUMAN_p53 and 1 for names like p53_HUMAN)""")
    elif f == 'target_sp_attr':
        parser.add_argument("--target_sp_attr", dest="target_sp_attr", 
                            type=str,
                            help="""attribute in the target tree(s) that contains the species name or code""")
    elif f == 'target_sp_attr_parser':
        parser.add_argument("--target_taxid_sp_parser", dest="target_sp_attr_parser", 
                            type=str, 
                            help="""A regular expression matching the species name or code from target_sp_attr""")
    elif f == 'target_sp_delimiter':
        parser.add_argument("--target_sp_delimiter", dest="target_sp_delimiter", 
                            type=str, 
                            help="""A single character delimiter that allows to extract the species name from node names ( i.e. "_" for node names like HUMAN_p53)""")
    elif f == 'target_sp_field':
        parser.add_argument("--target_sp_field", dest="target_sp_field", 
                            type=str, 
                            help="""The position of the species code after splitting node names using target_sp_delimiter (i.e. 0 for node names like HUMAN_p53 and 1 for names like p53_HUMAN)""")
