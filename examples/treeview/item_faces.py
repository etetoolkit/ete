# To play with random colors.
import colorsys
import random

# We will need to create Qt items.
from PyQt6 import QtCore
from PyQt6.QtGui import QColor, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem, QGraphicsEllipseItem

from ete4 import Tree
from ete4.treeview import faces, TreeStyle, NodeStyle


class InteractiveItem(QGraphicsRectItem):
    def __init__(self, *arg, **karg):
        super().__init__(*arg, **karg)
        self.node = None
        self.label = None
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAcceptsHoverEvents(True)

    def hoverEnterEvent(self, e):
        # There are many ways of adding interactive elements. With the
        # following code, I show/hide a text item over my custom
        # DynamicItemFace
        if not self.label:
            self.label = QGraphicsRectItem()
            self.label.setParentItem(self)
            # This is to ensure that the label is rendered over the
            # rest of item children (default ZValue for items is 0)
            self.label.setZValue(1)
            self.label.setBrush(QBrush(QColor('white')))
            self.label.text = QGraphicsSimpleTextItem()
            self.label.text.setParentItem(self.label)

        self.label.text.setText(self.node.name)
        self.label.setRect(self.label.text.boundingRect())
        self.label.setVisible(True)

    def hoverLeaveEvent(self, e):
        if self.label:
            self.label.setVisible(False)


def random_color(hue=None):
    """Return a random color in RGB format."""
    hue = hue if hue is not None else random.random()

    luminosity = 0.5
    saturation = 0.5

    rgb = colorsys.hls_to_rgb(hue, luminosity, saturation)

    return '#%02x%02x%02x' % tuple([int(x * 255) for x in rgb])


def ugly_name_face(node, *args, **kargs):
    """Item generator. It must receive a node object, and return a Qt
    graphics item that can be used as a node face.
    """

    # receive an arbitrary number of arguments, in this case width and
    # height of the faces
    width = args[0][0]
    height = args[0][1]

    ## Creates a main master Item that will contain all other elements
    ## Items can be standard QGraphicsItem
    # masterItem = QGraphicsRectItem(0, 0, width, height)

    # Or your custom Items, in which you can re-implement interactive
    # functions, etc. Check QGraphicsItem doc for details.
    masterItem = InteractiveItem(0, 0, width, height)

    # Keep a link within the item to access node info.
    masterItem.node = node

    # No border around the masterItem.
    masterItem.setPen(QPen(QtCore.Qt.NoPen))

    # Add ellipse around text.
    ellipse = QGraphicsEllipseItem(masterItem.rect())
    ellipse.setParentItem(masterItem)
    # Change ellipse color.
    ellipse.setBrush(QBrush(QColor( random_color())))

    # Add node name within the ellipse.
    text = QGraphicsSimpleTextItem(node.name)
    text.setParentItem(ellipse)
    text.setPen(QPen(QPen(QColor('white'))))

    # Center text according to masterItem size.
    tw = text.boundingRect().width()
    th = text.boundingRect().height()
    center = masterItem.boundingRect().center()
    text.setPos(center.x()-tw/2, center.y()-th/2)

    return masterItem


def master_ly(node):
    if node.is_leaf:
        # Create an ItemFAce. First argument must be the pointer to
        # the constructor function that returns a QGraphicsItem. It
        # will be used to draw the Face. Next arguments are arbitrary,
        # and they will be forwarded to the constructor Face function.
        F = faces.DynamicItemFace(ugly_name_face, 100, 50)
        faces.add_face_to_node(F, node, 0, position='aligned')


def get_example_tree():
    t = Tree()
    t.populate(8)

    ts = TreeStyle()
    ts.layout_fn = master_ly
    ts.title.add_face(faces.TextFace('Drawing your own Qt Faces', fsize=15), 0)

    return t, ts


if __name__ == '__main__':
    t, ts = get_example_tree()

    # The interactive features are only available using the GUI.
    t.show(tree_style=ts)
