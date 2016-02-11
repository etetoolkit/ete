from __future__ import absolute_import
import unittest
import random
import sys
import os

ETEPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0]+'/../')
sys.path.insert(0, ETEPATH)

from ... import Tree, TreeStyle, NodeStyle, PhyloTree, faces, random_color
from ...treeview.faces import *
from ...treeview.main import _NODE_TYPE_CHECKER, FACE_POSITIONS

from . import (face_grid, bubble_map, item_faces, node_style, node_background,
               face_positions, face_rotation, seq_motif_faces,
               barchart_and_piechart_faces, phylotree_visualization)

CONT = 0
class Test_Coretype_Treeview(unittest.TestCase):
    """ Tests tree basics. """
    def test_renderer(self):

        main_tree = Tree()
        main_tree.dist = 0

        t, ts = face_grid.get_example_tree()
        t_grid = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_grid, 0, "aligned")

        t, ts = bubble_map.get_example_tree()
        t_bubble = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_bubble, 0, "aligned")

        t, ts = item_faces.get_example_tree()
        t_items = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_items, 0, "aligned")

        t, ts = node_style.get_example_tree()
        t_nodest = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_nodest, 0, "aligned")

        t, ts = node_background.get_example_tree()
        t_bg = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_bg, 0, "aligned")

        t, ts = face_positions.get_example_tree()
        t_fpos = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_fpos, 0, "aligned")

        t, ts = phylotree_visualization.get_example_tree()
        t_phylo = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(t_phylo, 0, "aligned")

        t, ts = face_rotation.get_example_tree()
        temp_facet = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_facet, 0, "aligned")

        t, ts = seq_motif_faces.get_example_tree()
        temp_facet = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_facet, 0, "aligned")

        t, ts = barchart_and_piechart_faces.get_example_tree()
        temp_facet = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_facet, 0, "aligned")

        #Test orphan nodes and trees with 0 branch length
        t, ts = Tree(), TreeStyle()
        t.populate(5)
        for n in t.traverse():
            n.dist = 0
        temp_tface = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        ts.optimal_scale_level = "full"
        temp_tface = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        ts = TreeStyle()
        t.populate(5)
        ts.mode = "c"
        temp_tface = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        ts.optimal_scale_level = "full"
        temp_tface = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        t, ts = Tree(), TreeStyle()
        temp_tface = TreeFace(Tree('node;'), ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        t, ts = Tree(), TreeStyle()
        ts.mode = "c"
        temp_tface = TreeFace(Tree('node;'), ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        t, ts = Tree(), TreeStyle()
        ts.mode = "c"
        temp_tface = TreeFace(Tree(), ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        t, ts = Tree(), TreeStyle()
        temp_tface = TreeFace(Tree(), ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        # TEST TIGHT TEST WRAPPING
        chars = ["." "p", "j", "jJ"]
        def layout(node):
            global CONT
            if CONT >= len(chars):
                CONT = 0
            if node.is_leaf():
                node.img_style["size"] = 0
                F2= AttrFace("name", tight_text=True)
                F= TextFace(chars[CONT], tight_text=True)
                F.inner_border.width = 0
                F2.inner_border.width = 0
                #faces.add_face_to_node(F ,node, 0, position="branch-right")
                faces.add_face_to_node(F2 ,node, 1, position="branch-right")
                CONT += 1
        t = Tree()
        t.populate(20, random_branches=True)
        ts = TreeStyle()
        ts.layout_fn = layout
        ts.mode = "c"
        ts.show_leaf_name = False

        temp_tface = TreeFace(t, ts)
        n = main_tree.add_child()
        n.add_face(temp_tface, 0, "aligned")

        # MAIN TREE

        ms = TreeStyle()
        ms.mode = "r"
        ms.show_leaf_name = False
        main_tree.render('test.png', tree_style=ms)
        main_tree.render('test.svg', tree_style=ms)
        main_tree.render('test.pdf', tree_style=ms)


if __name__ == '__main__':
    unittest.main()
