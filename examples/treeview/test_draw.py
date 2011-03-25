import sys
import os

from ete_dev import Tree, faces
from ete_dev.treeview.main import TreeStyle, NodeStyle
import colorsys
import random

def random_color(h=None):
    if not h:
        h = random.random()
    s = 0.5
    l = 0.5
    return hls2hex(h, l, s)

def rgb2hex(rgb):
    return '#%02x%02x%02x' % rgb

def hls2hex(h, l, s):
    return rgb2hex( tuple(map(lambda x: int(x*255), colorsys.hls_to_rgb(h, l, s))))

# ::::::::::::::
# Layout actions
# ::::::::::::::

def sphere_map(node):
    # Creates a random color sphere face that will be floating over nodes
    bubble = faces.CircleFace(random.randint(5,40), random_color(), "sphere")
    bubble.opacity = 0.7
    faces.add_face_to_node(bubble, node, 0, position="float")
    
def random_background(node):
    # Set a random background color for each node partition
    node.img_style["bgcolor"] = random_color()
    #node.img_style["node_bgcolor"] = random_color()
    #node.img_style["faces_bgcolor"] = random_color()

def leaf_name(node):
    if node.is_leaf():
        nameF = faces.AttrFace("name")
        nameF.border=True
        faces.add_face_to_node(nameF, node, 0, position="branch-right")


def aligned_faces(node):
    if node.is_leaf():
        for i in xrange(3):
            F = faces.TextFace("ABCDEFGHIJK"[0:random.randint(1,11)] )
            F.border = True
            faces.add_face_to_node(F, node, i, position="aligned")

def master_ly(node):
    random_background(node)
    sphere_map(node)
    leaf_name(node)
    aligned_faces(node)

def tiny_ly(node):
    node.img_style["size"] = 2
    node.img_style["shape"] = "square"
    
size = int(sys.argv[1])
t = Tree()
t.populate(size, reuse_names=False)

I = TreeStyle()
I.mode = "rect"
I.orientation = 1
I.layout_fn = master_ly
I.margin_left = 100
I.margin_right = 50
I.margin_top = 100
I.margin_bottom = 50
I.show_border = True
I.legend_position = 4
I.title.add_face(faces.TextFace("HOLA MUNDO", fsize=30), 0)

I.aligned_header.add_face( faces.TextFace("H1"), 0 )
I.aligned_header.add_face( faces.TextFace("H1"), 1 )
I.aligned_header.add_face( faces.TextFace("H1"), 2 )
I.aligned_header.add_face( faces.TextFace("H1111111111111"), 3 )
I.aligned_header.add_face( faces.TextFace("H1"), 4 )

I.aligned_foot.add_face( faces.TextFace("FO1"), 0 )
I.aligned_foot.add_face( faces.TextFace("FO1"), 1 )
I.aligned_foot.add_face( faces.TextFace("FO1"), 2 )
I.aligned_foot.add_face( faces.TextFace("F1"), 3 )
I.aligned_foot.add_face( faces.TextFace("FO1"), 4 )

I.legend.add_face(faces.CircleFace(30, random_color(), "sphere"), 0)
I.legend.add_face(faces.CircleFace(30, random_color(), "sphere"), 0)
I.legend.add_face(faces.TextFace("HOLA"), 1)
I.legend.add_face(faces.TextFace("HOLA"), 1)

# Creates a random tree with 10 leaves
t2 = Tree()
t2.populate(10)

# Creates an alternative Tree Image set of properties
I2 = TreeStyle()
I2.mode = "circular"
I2.layout_fn = tiny_ly
I2.arc_start = 45
I2.arc_span = 360

# Creates a fixed NodeStyle object containing a TreeFace (A tree image
# as a face within another tree image)
style = NodeStyle()
style.add_fixed_face(faces.TreeFace(t2, I2), "branch-right", 0)

# Attach the fixed style to the first child of the root node
# t.children[0].img_style = style

t.show(img_properties=I)
#t.render("/home/jhuerta/test.svg", img_properties=I)
#os.system("inkscape /home/jhuerta/test.svg")
I.mode = "circular"
t.show(img_properties=I)

sys.exit(1)




t = Tree()
#t.populate(n, "ABCDEFGHIjklmnopqrstuvwxyz", reuse_names=False)

#t = Tree("(a, b, c);")

print t.get_ascii(show_internal=True)

style = NodeStyle()
style.add_fixed_face(faces.TreeFace(t2, I2), "branch-right", 0)

t.img_style = NodeStyle()
for c in t.children:
    c.img_style = NodeStyle()

#t.children[1].children[0].img_style = style 

#t.img_style["bgcolor"] = "#ff0000"
# t.children[1].img_style["bgcolor"] = "#00ff00"
# t.children[0].img_style["bgcolor"] = "#0000ff"

# I3 = TreeImage()
# I3.scale = n/2 
# I3.layout_fn = tiny
# t.show(img_properties = I3)
# sys.exit()

t.show(img_properties=I)
t.render("/home/jhuerta/test.svg", img_properties=I)
os.system("inkscape /home/jhuerta/test.svg")
t.show(img_properties=I)

I.mode = "circular"
I2.mode = "rect"
print t.render("test.svg", img_properties=I)

t.show(ly, img_properties=I)

