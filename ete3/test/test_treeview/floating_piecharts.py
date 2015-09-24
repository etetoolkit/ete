import sys
import random
from ... import Tree, faces, TreeStyle, COLOR_SCHEMES

schema_names = COLOR_SCHEMES.keys()

def layout(node):
    if not node.is_leaf():
        size = random.randint(20,50)
        F= faces.PieChartFace([10,20,60,10],
                              colors=COLOR_SCHEMES[random.sample(schema_names, 1)[0]],
                              width=size, height=size)
        F.border.width = None
        F.opacity = 0.6
        faces.add_face_to_node(F,node, 0, position="float")

def get_example_tree():
    t = Tree()
    ts = TreeStyle()
    ts.layout_fn = layout
    ts.mode = "c"
    ts.show_leaf_name = True
    ts.min_leaf_separation = 15
    t.populate(100)
    return t, ts

if __name__ == '__main__':
    t, ts = get_example_tree()
    t.show(tree_style=ts)
    #t.render("float_piechart.png", tree_style=ts)
