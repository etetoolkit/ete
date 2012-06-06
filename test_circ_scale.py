import sys
import random
sys.path.insert(0, "./")
from ete_dev import Tree, TreeStyle, faces
from ete_dev.treeview.main import random_color

def layout(node):
    #node.img_style["size"] = random.randint(5,100)
    node.img_style["hz_line_width"] = 0
    node.img_style["vt_line_width"] = 0
    if node.is_leaf():
        #node.img_style["size"] = random.randint(50, 50)
        f = faces.AttrFace("name", fsize=20)
        faces.add_face_to_node(f, node, 0, position="aligned")
        
        f = faces.AttrFace("name", fsize=20)
        faces.add_face_to_node(f, node, 0, position="branch-right")
        f.border.width = 1
    node.img_style["bgcolor"] = random_color()

ts = TreeStyle()
ts.mode = "c"
ts.layout_fn = layout 
ts.show_leaf_name = False
ts.draw_guiding_lines = False
t = Tree()
t.populate(100, random_branches=True)
t.dist = 0
t.write(outfile="test.nw")
t.show(tree_style=ts)


    
        