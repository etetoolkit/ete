import sys

from ete_dev import Tree, faces
from ete_dev.treeview.main import TreeImage, NodeStyleDict
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

def ly(node):
    node.img_style["size"] = 50
    node.img_style["shape"] = "square"


    node.img_style["bgcolor"] = random_color()

    #node.img_style["node_bgcolor"] = random_color()
    #node.img_style["faces_bgcolor"] = random_color()

    if node.is_leaf():
        #faces.add_face_to_node(faces.AttrFace("name"), node, 0, position="aligned")
        faces.add_face_to_node(faces.AttrFace("name", fsize=16, fstyle="italic"), node, 0)#), position="aligned")
        faces.add_face_to_node(faces.AttrFace("name", fsize=16, fstyle="oblique"), node, 0)#), position="aligned")

        #faces.add_face_to_node(faces.AttrFace("support", fsize=6), node, 0, position="branch-top")
        pass
    elif 0:
        FLOAT = faces.CircleFace(random.randint(5,40), random_color(), "sphere")
        FLOAT.opacity = 0.9
        faces.add_face_to_node(FLOAT, node, 0, position="float")

def tiny(node):
    node.img_style["size"] = 7
    node.img_style["shape"] = "circle"
    node.img_style["fgcolor"] = random_color()
    if node.is_leaf():
        faces.add_face_to_node(faces.AttrFace("name", fstyle="italic"), node, 0, position="branch-right")

n = int(sys.argv[1])

I = TreeImage()
I.mode = "rect"
I.orientation = 1
#I.scale = n/2
I.layout_fn = ly
I.margin_left = 50
I.margin_right = 100
I.margin_top = 100
I.margin_bottom = 50
I.draw_border = True

t2 = Tree()
t2.populate(10)
I2 = TreeImage()
#I2.scale=1
I2.mode = "circular"
I2.layout_fn = tiny
I2.arc_start = 45
I2.arc_span = 360

t = Tree()
#t.populate(n, "ABCDEFGHIjklmnopqrstuvwxyz", reuse_names=False)
t.populate(n, reuse_names=False)
#t = Tree("(a, b, c);")

print t.get_ascii(show_internal=True)

style = NodeStyleDict()
style.add_fixed_face(faces.TreeFace(t2, I2), "branch-right", 0)

t.img_style = NodeStyleDict()
for c in t.children:
    c.img_style = NodeStyleDict()

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

I.mode = "circular"
I2.mode = "rect"
treemap =  t.render("test.png", img_properties=I)
t.show(ly, img_properties=I)

