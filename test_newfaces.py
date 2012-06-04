import sys
from ete_dev import Tree, faces, TreeStyle

sys.path.insert(0, "./")
def layout(node):
    if node.is_leaf():
        F= faces.PieChartFace([10,20,70], 100, 100)
        F.border.width = 1
        faces.add_face_to_node(F,node, 0)
    else:
        F= faces.BarChartFace([40,20,70,100], [0,0,0,0], 200, 100, min_value = 0)
        faces.add_face_to_node(F,node, 0, position="branch-top")
        
t = Tree()
ts = TreeStyle()
ts.layout_fn = layout
ts.mode = "r"
ts.show_leaf_name = False

t.populate(10)
t.show(tree_style=ts)
