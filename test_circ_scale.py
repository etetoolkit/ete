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
        f = faces.AttrFace("name", fsize=random.randint(20,20))
        faces.add_face_to_node(f, node, 0, position="aligned")
        f.border.width = 0
        #f = faces.CircleFace(20, "red")
        f = faces.AttrFace("name", fsize=20)
        #faces.add_face_to_node(f, node, 0, position="branch-right")
        f.border.width = 0
    node.img_style["bgcolor"] = random_color()

ts = TreeStyle()
ts.mode = "c"
ts.layout_fn = layout 
ts.show_leaf_name = False
#ts.show_branch_length = True
ts.draw_guiding_lines = False
ts.optimal_scale_level = "mid"
ts.scale = None
t = Tree()
t.populate(50, random_branches=True, branch_range=(0, 0.7))
t.dist = 0
dists = [n.dist for n in t.traverse() if n.dist != 0]
print max(dists), min(dists)
t.write(outfile="test.nw")
t.show(tree_style=ts)


    
        