import sys
import random
from ... import Tree, faces, TreeStyle, COLOR_SCHEMES

schema_names = COLOR_SCHEMES.keys()

def layout(node):
    if node.is_leaf():
        F= faces.PieChartFace([10,10,10,10,10,10,10,10,10,4,6],
                              colors=COLOR_SCHEMES["set3"],
                              width=50, height=50)
        F.border.width = None
        F.opacity = 0.8
        faces.add_face_to_node(F,node, 0, position="branch-right")

        F= faces.PieChartFace([10,20,5,5,60],
                              colors=COLOR_SCHEMES[random.sample(schema_names, 1)[0]],
                              width=100, height=40)
        F.border.width = None
        F.opacity = 0.8
        faces.add_face_to_node(F,node, 0, position="branch-right")
    else:
        F= faces.BarChartFace([40,20,70,100,30,40,50,40,70,-12], min_value=-12,
                              colors=COLOR_SCHEMES["spectral"],
                              labels = "aaa,bbb,cccccc,dd,eeee,ffff,gg,HHH,II,JJJ,KK".split(","))
        faces.add_face_to_node(F,node, 0, position="branch-top")
        F.background.color = "#eee"

def get_example_tree():
    t = Tree()
    ts = TreeStyle()
    ts.layout_fn = layout
    ts.mode = "r"
    ts.show_leaf_name = False
    t.populate(10)
    return t, ts

if __name__ == '__main__':
    t, ts = get_example_tree()
    t.show(tree_style=ts)
