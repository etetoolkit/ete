#!/usr/bin/env python

import math
import sys
import random
import colorsys
from PyQt4 import QtCore, QtGui
from ete_dev import Tree, faces, treeview
from circular_render import ArcPartition, get_min_radius, rotate_and_displace, random_color
import main_render


def init_rect_leaf_item(node, n2i):
    item = n2i[node]
    item.ycenter = item.boundingRect.height()/2

def init_rect_node_item(node, n2i):
    item = n2i[node]
    item.ycenter = item.boundingRect.height()/2

# TEST AND TRASH

def new_node(w, h, parent, color="red", label=1):
    rect = QtGui.QGraphicsRectItem(0, 0, w, h)
    rect.setParentItem(parent)
    rect.setPen(QtGui.QPen(QtGui.QColor(color)))
    #e = QtGui.QGraphicsEllipseItem()
    #e.setParentItem(rect)
    #e.setRect(0,0, w, h)
    t = QtGui.QGraphicsSimpleTextItem(str(label))
    t.moveBy(5,0)
    t.setParentItem(rect)
    return rect

def rotate_and_translate(item, rotation, a, length):
    radian = (a * math.pi)/180
    height = item.rect().height()
    min_length = (height/2) / math.tan(radian/2)
    if min_length > length:
        length = min_length

    t = QtGui.QTransform()
    t.rotate(rotation)
    t.translate(0, -(item.rect().height()/2))        
    item.setTransform(t)
    t.translate(length, 0)
    item.setTransform(t)
    return length

def distribute(n, parent):
    # Distribute n items along a circumference 
    angle_start = 0
    angle_end = 360.0
    current_rotation = angle_start
    angle_step = angle_end/n
    offset = 0
    while current_rotation < angle_end:
        w = int(random.random()*100)
        h = int(random.random()*100)
        item = new_node(w, h, parent, "red")
        r, min_offset = get_min_radius(w, h, angle_step, offset)
        rotate(item, current_rotation, min_offset)
        current_rotation += angle_step

def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)

def distribute_tree(root_node, parent, scale, arc_span):
    n2i = node2item = {}
    last_rotation = -90 # starts rotation from 12 o'clock
    rot_step = float(arc_span) / len(root_node)
    max_r = 0
    # :::: Precalculate rotations and node regions. Creates QGitems ::::
    for node in root_node.traverse("postorder"): # Children first. This will be blind to draw descendents
        # Creates a semi-ring partition that will contain all node's
        # related QItems
        item = n2i[node] = ArcPartition(parent)
        if _leaf(node):
            item.rotation = last_rotation
            item.full_start = last_rotation - (rot_step / 2)
            item.full_end = last_rotation + (rot_step / 2)
            last_rotation += rot_step
        else:
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            rot_end = last_c.rotation
            rot_start = first_c.rotation
            item.angle_span = (rot_end - rot_start)
            item.rotation = rot_start + ((rot_end - rot_start) / 2)

            item.full_start = first_c.full_start
            item.full_end = last_c.full_end

    # :::: RENDER :::::
    for node in root_node.traverse("preorder"):
        item = n2i[node]

        # Branch length converted to pixels
        node.dist_xoffset = float(node.dist * scale)
        # Creates items (faces, node, etc.)
        if _leaf(node):
            iw = 10#int(random.random()*20)
            ih = 20#int(random.random()*20)
        else:
            iw = 1
            ih = 1
        #iw = int(random.random()*20)
        #ih = int(random.random()*20)

        w = node.dist_xoffset + iw
        h = ih 

        # Node region 
        node.nodeRegion = QtCore.QRectF(0, 0, w, h)
        # This is the node total region covered by the node
        node.fullRegion = QtCore.QRectF(0, 0, w, h)

        if node.up:
            parent_radius = n2i[node.up].radius
        else:
            parent_radius = 0

        if _leaf(node):
            angle = rot_step
        else:
            angle = item.angle_span

        r, xoffset, best_a = get_min_radius(w, h, angle, parent_radius)
        rotate_and_displace(item, item.rotation, h, parent_radius)
        item.radius = r

        if r > max_r:
            max_r = r

        if not _leaf(node):
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # BG
            full_angle = last_c.full_end - first_c.full_start
            angle_start = last_c.full_end - item.rotation
            angle_end = item.rotation - first_c.full_start
            item.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            C = QtGui.QGraphicsPathItem(parent)
            path = QtGui.QPainterPath()
            path.arcMoveTo(-r,-r, r * 2, r * 2, 360-rot_start-angle)
            path.arcTo(-r,-r, r*2, r * 2, 360 - rot_start - angle, angle)
            # Faces
            C.setPath(path)
            faces = new_node(w-node.dist_xoffset, h, item, "red", "" )
        else:
            faces = new_node(w-node.dist_xoffset, h, item, "blue", "" )
        faces.moveBy(xoffset - parent_radius+node.dist_xoffset, 0)

        # horizontal line
        branch = QtGui.QGraphicsLineItem(0, h/2, node.dist_xoffset, h/2)
        branch.setParentItem(item)
        if parent_radius < xoffset:
            branch_guide = QtGui.QGraphicsLineItem(node.dist_xoffset, h/2, xoffset-parent_radius+node.dist_xoffset, h/2)
            branch_guide.setPen(QtGui.QPen(QtGui.QColor("orange")))
            branch_guide.setParentItem(item)        
        #rrr = QtGui.QGraphicsRectItem(item.boundingRect())
        #rrr.setParentItem(item)
    return max_r

def _leaf(node):
    return node.is_leaf()


if __name__ == '__main__':
    n = float(sys.argv[1])
    try:
        scale = float(sys.argv[2])
    except Exception:
        print "Default scale"
        scale = 40
    try:
        arc_span = float(sys.argv[3])
    except Exception:
        print "Default scale"
        arc_span = 360

    nameF = faces.AttrFace("name", fsize=15)

    t = Tree()
    node = t
    #for i in xrange(n):
    #    node.add_child(Tree())
    #    x = Tree()
    #    node.add_child(x)
    #    node = x
    t.populate(n, names_library="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz", reuse_names=False)
    # Random node distances 
    x = t.children[0]
    x.populate(10, names_library="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz", reuse_names=False)
    for counter, n in enumerate(t.traverse()):
        n.dist = 1#random.random()
        n.img_style = main_render.NodeStyleDict()
        n.img_style["bgcolor"] = random_color(0.3)
        n.img_style["size"] = 20
        #n.img_style["vt_line_width"] = 0
        #n.img_style["hz_line_width"] = 0
        if _leaf(n):
            faces.add_face_to_node(nameF, n,  0)

            #x.img_style["draw_descendants"] = False

    t2 = Tree()
    t2.populate(30, names_library="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz", reuse_names=False)
    x.img_style.add_fixed_face(main_render.TreeFace(t2), "branch-right",  0)
    x.img_style["size"] = 40

    #faces.add_face_to_node(faces.TextFace("hola"), x, 0, position="branch-top")

    for n in x.traverse():
        n.img_style["fgcolor"] = "#FF0000"

    # faces.add_face_to_node(main_render.TreeFace(x.children[0]), x, 0)

    print t.get_ascii(show_internal=True)
    # Basic QtApplication
    app = QtGui.QApplication(sys.argv)
    scene = QtGui.QGraphicsScene()

    parent = QtGui.QGraphicsRectItem(0, 0, 1, 1)
    tree_item = main_render.render(t, {}, {}, "rect", scale)
    print tree_item
    #distribute(n, parent)
    #r = distribute_tree(t, parent, scale, arc_span) + 50
    tree_item.setParentItem(parent)
    # c1 = QtGui.QGraphicsEllipseItem(0,0,10,10)
    # c1.moveBy(15, 15)
    # c1.setParentItem(parent)
    #  
    # c2 = QtGui.QGraphicsEllipseItem(15,15,5,5)
    # c2.setPos( c1.mapFromScene(c2.pos()))
    #  
    # c2.setParentItem(c1)
    r = tree_item.rect().height()/2

    scene.setSceneRect(-r, -r,  r*4, r*4)
    scene.addItem(parent)
    view = QtGui.QGraphicsView(scene)
    view.setRenderHints(QtGui.QPainter.Antialiasing or QtGui.QPainter.SmoothPixmapTransform )
    view.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)

    view.show()
    sys.exit(app.exec_())
