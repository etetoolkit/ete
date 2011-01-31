import sys

from ete_dev import Tree, faces
from ete_dev.treeview.main import TreeImage, NodeStyleDict
import colorsys
import random

def random_color(base=None):
    if not base:
        base = random.random()
    s = 0.5
    v = 0.5+random.random()/2
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])

def ly(node):
    node.img_style["size"] = 10
    node.img_style["shape"] = "square"
    
    if node.is_leaf():
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="aligned")
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="branch-right")
        faces.add_face_to_node(faces.AttrFace("support"), node, 0, position="branch-top")

    else:
        FLOAT = faces.CircleFace(random.randint(5,40), random_color(), "sphere")
        FLOAT.opacity = 0.4
        faces.add_face_to_node(FLOAT, node, 0, position="float")

def tiny(node):
    node.img_style["size"] = 7
    node.img_style["shape"] = "circle"
    node.img_style["fgcolor"] = random_color()
    if node.is_leaf():
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="branch-right")

I = TreeImage()
I.mode = "rect"
I.scale = 40

n = int(sys.argv[1])

t2 = Tree()
t2.populate(10)
I2 = TreeImage()
I2.scale=1
I2.mode = "circular"
I2.layout_fn = tiny
I2.arc_start = 45
I2.arc_span = 360

t = Tree()
t.populate(n)

style = NodeStyleDict()
style.add_fixed_face(faces.TreeFace(t2, I2), "branch-right", 0)
t.children[1].children[0].img_style = style 


t.show(ly, img_properties=I)


I.mode = "circular"
I2.mode = "rect"
t.show(ly, img_properties=I)

