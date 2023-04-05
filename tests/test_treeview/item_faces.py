# To play with random colors
import colorsys
import random

from ... import Tree, faces, TreeStyle, NodeStyle, Face

# We will need to create Qt4 items
from ...treeview.qt import QtCore, Qt
from ...treeview.qt import QGraphicsRectItem, QGraphicsSimpleTextItem, \
    QGraphicsEllipseItem, QColor, QPen, QBrush

class InteractiveItem(QGraphicsRectItem):
    def __init__(self, *arg, **karg):
        QGraphicsRectItem.__init__(self, *arg, **karg)
        self.node = None
        self.label = None
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def hoverEnterEvent (self, e):
        # There are many ways of adding interactive elements. With the
        # following code, I show/hide a text item over my custom
        # DynamicItemFace
        if not self.label:
            self.label = QGraphicsRectItem()
            self.label.setParentItem(self)
            # This is to ensure that the label is rendered over the
            # rest of item children (default ZValue for items is 0)
            self.label.setZValue(1)
            self.label.setBrush(QBrush(QColor("white")))
            self.label.text = QGraphicsSimpleTextItem()
            self.label.text.setParentItem(self.label)

        self.label.text.setText(self.node.name)
        self.label.setRect(self.label.text.boundingRect())
        self.label.setVisible(True)

    def hoverLeaveEvent(self, e):
        if self.label:
            self.label.setVisible(False)


def random_color(h=None):
    """Generates a random color in RGB format."""
    if not h:
        h = random.random()
    s = 0.5
    l = 0.5
    return _hls2hex(h, l, s)

def _hls2hex(h, l, s):
    return '#%02x%02x%02x' %tuple(map(lambda x: int(x*255),
                                      colorsys.hls_to_rgb(h, l, s)))

def ugly_name_face(node, *args, **kargs):
    """ This is my item generator. It must receive a node object, and
    returns a Qt4 graphics item that can be used as a node face.
    """

    # receive an arbitrary number of arguments, in this case width and
    # height of the faces
    width = args[0]
    height = args[1]

    ## Creates a main master Item that will contain all other elements
    ## Items can be standard QGraphicsItem
    # masterItem = QGraphicsRectItem(0, 0, width, height)

    # Or your custom Items, in which you can re-implement interactive
    # functions, etc. Check QGraphicsItem doc for details.

    masterItem = InteractiveItem(0, 0, width, height)
    masterItem.setAcceptHoverEvents(True)
    
    # Keep a link within the item to access node info
    masterItem.node = node

    # I dont want a border around the masterItem
    masterItem.setPen(QPen(QtCore.Qt.NoPen))

    # Add ellipse around text
    ellipse = QGraphicsEllipseItem(masterItem.rect())
    ellipse.setParentItem(masterItem)
    # Change ellipse color
    ellipse.setBrush(QBrush(QColor( random_color())))

    # Add node name within the ellipse
    text = QGraphicsSimpleTextItem(node.name)
    text.setParentItem(ellipse)
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
        F = faces.DynamicItemFace(ugly_name_face, 100, 50)
        faces.add_face_to_node(F, node, 0, position="aligned")

def get_example_tree():

    t = Tree()
    t.populate(8, reuse_names=False)

    ts = TreeStyle()
    ts.layout_fn = master_ly
    ts.title.add_face(faces.TextFace("Drawing your own Qt Faces", fsize=15), 0)
    return t, ts

if __name__ == "__main__":
    t, ts = get_example_tree()

    #t.render("item_faces.png", h=400, tree_style=ts)
    # The interactive features are only available using the GUI
    t.show(tree_style=ts)
