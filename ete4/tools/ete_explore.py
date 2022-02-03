# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
#
#                     ABOUT THE ETE PACKAGE
#                     =====================
#
# ETE is distributed under the GPL copyleft license (2008-2015).
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in
# the toolkit may be available in the documentation.
#
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
#
# #END_LICENSE#############################################################
from __future__ import absolute_import
from __future__ import print_function

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
 
        
