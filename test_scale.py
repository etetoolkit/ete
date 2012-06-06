import random
import sys
sys.path.insert(0, "./")
from ete_dev import Tree, TreeStyle, faces
from ete_dev.treeview.main import random_color

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

def layout2(node):
    #node.img_style["size"] = random.randint(40, 200)
    if hasattr(node, "size"):
        f = faces.PieChartFace([100], 50, node.size, ["blue"])
        faces.add_face_to_node(f, node, 0, position="branch-right")
        
        #node.img_style["size"] = node.size
        
    node.img_style["bgcolor"] = random_color()
    node.img_style["hz_line_width"] = 0
    node.img_style["vt_line_width"] = 0
    #if node.is_leaf():
    #    f = faces.CircleFace(50, "red")
    #    faces.add_face_to_node(f, node, 0, position="aligned")
        

ts = TreeStyle()
ts.mode = "c"
ts.layout_fn = layout 
ts.show_leaf_name = False
ts.show_border = True
ts.draw_guiding_lines = False
ts.show_scale = True
#ts.scale = 60
t = Tree()
t.dist = 0

t.size = 0
for x in xrange(100):
    n = t.add_child()
    n2 = n.add_child()
    #n3 = n.add_child()
    n3 = n2.add_child()
    n5 = n3.add_child()
    n.size = 50
    n2.size = 50
    n3.size = 50
    n5.size = 50
    #n2.dist = 0.1
    #n2.size = 1
    #n3.size = 1
    #n2.dist = 0.5
    
#t.populate(100)#, random_branches=True)
#t.write(outfile="test.nw")
ts.layout_fn = layout2
t.show(tree_style=ts)
ts.scale = 1
sys.exit()
t.show(tree_style=ts)

for x in xrange(30):
    t = Tree()
    t.dist = 0
    t.populate(100, random_branches=True)
    t.render("/tmp/kk.png", tree_style=ts)
sys.exit()
ts.layout_fn = layout
t.show(tree_style=ts)
ts.mode = "r"
t.show(tree_style=ts)


    
        