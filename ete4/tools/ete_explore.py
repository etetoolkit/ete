import random
import re
import colorsys
from collections import defaultdict

from .common import log, POSNAMES, node_matcher, src_tree_iterator
# from .. import (Tree, PhyloTree, TextFace, RectFace, faces, TreeStyle, CircleFace, AttrFace,
#                 add_face_to_node, random_color)
from .. import PhyloTree
from ..smartview import TreeStyle
from ..smartview.gui.server import run_smartview

DESC = "Launches an instance of the ETE smartview tree explorer server."

def populate_args(explore_args_p):
    explore_args_p.add_argument("--face", action="append",
                             help="adds a face to the selected nodes. In example --face 'value:@dist, pos:b-top, color:red, size:10, if:@dist>0.9' ")
    return



def run(args):

    # VISUALIZATION
    # Basic tree style
    ts = TreeStyle()
    ts.show_leaf_name = True
    try:
        tfile = next(src_tree_iterator(args))
    except StopIteration:
        run_smartview()
    else:
        t = PhyloTree(tfile, format=args.src_newick_format)
        t.explore(tree_name=tfile)
