import os

from ... import Tree, faces
from ...treeview.main import TreeStyle, NodeStyle, random_color
import colorsys
import random

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

def leaf_name(node):
    if node.is_leaf():
        nameF = faces.AttrFace("name")
        nameF.border.width = 1
        faces.add_face_to_node(nameF, node, 0, position="branch-right")


def aligned_faces(node):
    if node.is_leaf():
        for i in range(3):
            F = faces.TextFace("ABCDEFGHIJK"[0:random.randint(1,11)])
            F.border.width = 1
            F.border.line_style = 1
            F.inner_background.color = "lightgreen"
            F.border.width = 1
            F.inner_border.width = 1
            F.background.color = "darkgreen"
            F.border.width = 2
            F.vt_align = random.randint(0,4)
            F.hz_align = random.randint(0,4)
            F.margin_bottom = random.randint(1, 20)
            F.margin_right  = random.randint(1, 20)
            F.margin_left = random.randint(1, 20)
            F.margin_top = random.randint(1, 20)

            faces.add_face_to_node(F, node, i, position="aligned")
            if random.randint(0, 1):
                faces.add_face_to_node(F, node, i, position="aligned")


def master_ly(node):
    random_background(node)
    sphere_map(node)
    leaf_name(node)
    aligned_faces(node)

def tiny_ly(node):
    node.img_style["size"] = 2
    node.img_style["shape"] = "square"

size = 15
t = Tree()
t.populate(size, reuse_names=False)

I = TreeStyle()
I.mode = "r"

I.orientation = 0
I.layout_fn = master_ly
I.margin_left = 100
I.margin_right = 50
I.margin_top = 100
I.arc_start = 45
I.arc_span = 360
I.margin_bottom = 50
I.show_border = True
I.legend_position = 4
I.title.add_face(faces.TextFace("HOLA MUNDO", fsize=30), 0)
I.draw_aligned_faces_as_table = True

def test(node):
    if node.is_leaf():
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="aligned")

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

# Creates a fixed NodeStyle object containing a TreeFace (A tree image
# as a face within another tree image)
# t.add_face(faces.TreeFace(t2, I), "branch-right", 0)

# Attach the fixed style to the first child of the root node
# t.children[0].img_style = style
I.rotation = 90
I.mode = "c"
t.show(tree_style=I)
#t.render("/home/jhuerta/test.svg", img_properties=I)
#t.render("/home/jhuerta/test.pdf", img_properties=I)
#t.render("/home/jhuerta/test.png", img_properties=I)
#t.render("/home/jhuerta/test.ps", img_properties=I)
#os.system("inkscape /home/jhuerta/test.svg")
#I.mode = "c"
#t.show(img_properties=I)

