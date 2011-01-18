#!/usr/bin/env python

import math
import sys
import random
import colorsys
from PyQt4 import QtCore, QtGui
from ete_dev import Tree, faces, treeview
from circular_render import ArcPartition, get_min_radius, rotate_and_displace, random_color
from main_render import NodeStyleDict, TreeImage, TreeFace, RandomFace, render



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
    distF = faces.AttrFace("dist", fsize=7)

    N = 6

    trees = []
    t2i = {}
    for i in xrange(N):
        I = TreeImage()
        I.mode =  random.sample(["rect", "circular"], 1)[0]
        I.scale = random.random()*40
        t = Tree()
        t.populate(random.randint(5, 60), names_library="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz", reuse_names=False)
        size = random.randint(4, 20)
        color = random_color(0.3)

        for n in t.traverse():
            n.img_style = NodeStyleDict()
            n.img_style["bgcolor"] = color
            n.img_style["fgcolor"] = color
            n.img_style["size"] = size
            n.img_style["vt_line_width"] = 0
            n.img_style["hz_line_width"] = 0
            if _leaf(n):
                n.img_style.add_fixed_face(nameF, "branch-right",  0)
                #n.img_style.add_fixed_face(distF, "branch-bottom",  1)

        t2i[t] = I
        trees.append(t)

    main_tree = t = trees.pop(0)
    while trees: 
        subt = trees.pop()
        n = random.sample(t.get_descendants(), 1)[0]
        face_position =  random.sample(["branch-top", "branch-right", "branch-bottom"], 1)[0]
        n.img_style.add_fixed_face(TreeFace(subt, t2i[subt]), face_position,  1)
        t = subt


    print t.get_ascii(show_internal=True)
    # Basic QtApplication
    app = QtGui.QApplication(sys.argv)
    scene = QtGui.QGraphicsScene()
    parent = QtGui.QGraphicsRectItem(0, 0, 1, 1)
    tree_item = render(main_tree, {}, {}, t2i[main_tree])


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
