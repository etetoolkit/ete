import random
import sys
sys.path.insert(0, "../")
from ete_dev import Tree, TreeStyle, NodeStyle, PhyloTree
from ete_dev.treeview.faces import *
from ete_dev.treeview.main import random_color, _NODE_TYPE_CHECKER, FACE_POSITIONS

sys.path.insert(0, "../examples/treeview")
import face_grid, bubble_map, item_faces, node_style, node_background, face_positions

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

# Test orphan nodes and trees with 0 branch length
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
temp_tface = TreeFace(Tree(), ts)
n = main_tree.add_child()
n.add_face(temp_tface, 0, "aligned")

t, ts = Tree(), TreeStyle()
ts.mode = "c"
temp_tface = TreeFace(Tree(), ts)
n = main_tree.add_child()
n.add_face(temp_tface, 0, "aligned")


ms = TreeStyle()
ms.mode = "r"
ms.show_leaf_name = False
main_tree.show(tree_style=ms)
 

        