import sys

sys.path.insert(0, "/home/huerta/_Devel/ete_master")
from ete_dev import Tree, PhyloTree, faces, TreeStyle, add_face_to_node, orthoxml
sys.path.insert(0, "/home/huerta/_Devel/jhc-utils")
from jhc_utils import print_table

try:
    import argparse
except ImportError:
    from ete_dev import argparse
