import sys
from PyQt4 import QtCore
from PyQt4.QtGui import QGraphicsRectItem, QGraphicsSimpleTextItem, \
    QGraphicsEllipseItem, QColor, QPen, QBrush
from ete_dev import Tree, faces, TreeStyle, NodeStyle

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


def ugly_name_face(node, *args):
    # receive an arbitrary number of arguments, in this case width and
    # height of the faces
    width = args[0][0]
    height = args[0][1]
    # Creates a main master Item that will contain all other elements
    masterItem = QGraphicsRectItem(0, 0, width, height)
    # I dont want a border around the masterItem
    masterItem.setPen(QPen(QtCore.Qt.NoPen))

    # Add ellipse around text
    ellipse = QGraphicsEllipseItem(masterItem.rect(), parent=masterItem)
    # Change ellipse color
    ellipse.setBrush(QBrush(QColor("darkred")))

    # Add text
    text = QGraphicsSimpleTextItem(node.name, parent=masterItem)
    text.setPen(QPen(QPen(QColor("white"))))

    # Center text according to masterItem size
    tw = text.boundingRect().width()
    th = text.boundingRect().height()
    center = masterItem.boundingRect().center()
    text.setPos(center.x()-tw/2, center.y()-th/2)
    
    return masterItem

def master_ly(node):
    if node.is_leaf():
        # Create an ItemFAce. First argument must be the pointer to
        # the constructor function that returns a QGraphicsItem. It
        # will be used to draw the Face. Next arguments are arbitrary,
        # and they will be forwarded to the constructor Face function.
        F = faces.ItemFace(ugly_name_face, 100, 50)
        faces.add_face_to_node(F, node, 0, position="aligned")
  
size = int(sys.argv[1])
t = Tree()
t.populate(size, reuse_names=False)

I = TreeStyle()
I.layout_fn = master_ly
I.title.add_face(faces.TextFace("Drawing your own Qt Faces", fsize=15), 0)

t.show(None, img_properties=I)

