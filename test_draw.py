import sys

from ete_dev import Tree, faces
from ete_dev.treeview.main import TreeImage
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
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="aligned")
        faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="aligned")
        faces.add_face_to_node(faces.AttrFace("name"), node, 1, position="aligned")

    else:
        FLOAT = faces.CircleFace(random.randint(5,40), random_color(), "sphere")
        FLOAT.opacity = 0.4
        faces.add_face_to_node(FLOAT, node, 0, position="float")


I = TreeImage()
I.mode = "rect"
I.scale = 40

n = int(sys.argv[1])

t = Tree()
t.populate(n)
t.show(ly, img_properties=I)
I.mode = "circular"
t.show(ly, img_properties=I)
