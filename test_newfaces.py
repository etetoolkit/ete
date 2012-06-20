import sys
from ete_dev import Tree, faces, TreeStyle, COLOR_SCHEMES

sys.path.insert(0, "./")
def layout(node):
    if node.is_leaf():
        F= faces.PieChartFace([10,10,10,10,10,10,10,10,10,4,6], colors=COLOR_SCHEMES["set3"], width=100, height=100)
        F.border.width = None
        F.opacity = 0.8
        faces.add_face_to_node(F,node, 0, position="branch-right")
    else:
        F= faces.BarChartFace([40,20,70,100,30,40,50,40,70,12], min_value=0, colors=COLOR_SCHEMES["spectral"])
        faces.add_face_to_node(F,node, 0, position="branch-top")
        
t = Tree()
ts = TreeStyle()
ts.layout_fn = layout
ts.mode = "c"
ts.show_leaf_name = False

t.populate(10)
t.show(tree_style=ts)
