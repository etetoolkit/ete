import random
import sys
sys.path.insert(0, "./")
from ete_dev import Tree, TreeStyle, faces

def layout(node):
    node.img_style["size"] = 5
    node.img_style["hz_line_width"] = 0
    node.img_style["vt_line_width"] = 0
    if node.is_leaf():
        f = faces.AttrFace("name", fgcolor="steelblue", fsize=20)
        faces.add_face_to_node(f, node, 0, position="aligned")
        
        f = faces.AttrFace("name", fsize=15)
        faces.add_face_to_node(f, node, 0, position="branch-right")
    else:
        f = faces.TextFace("uno", fsize=8)
        for x in xrange(random.randint(1, 5)):
            faces.add_face_to_node(f, node, 0, position="branch-top")

        f = faces.TextFace("otromassssssssssss", fsize=8)
        for x in xrange(random.randint(1, 5)):
            faces.add_face_to_node(f, node, 0, position="branch-bottom")
        
    f = faces.CircleFace(20, "red")
    f.opacity = 0.3
    faces.add_face_to_node(f, node, 0, position="float")
    f = faces.CircleFace(23, "blue")
    f.opacity = 0.3
    faces.add_face_to_node(f, node, 0, position="float-behind")
        

ts = TreeStyle()
ts.mode = "c"
ts.layout_fn = layout 
ts.show_leaf_name = False
ts.show_border = True
ts.draw_guiding_lines = False
ts.scale = 60
t = Tree()
t.dist = 0
t.populate(4, random_branches=True)
t.write(outfile="test.nw")
t.show(tree_style=ts)
ts.mode = "r"
t.show(tree_style=ts)


    
        