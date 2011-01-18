import math
import random
import colorsys
from PyQt4 import QtCore, QtGui
from main_render import _leaf

class ArcPartition(QtGui.QGraphicsPathItem):
    def set_arc(self, cxdist, cydist, r1, r2, angle_start, angle_end):
        """ Draws a 2D arc with two arc lines of length r1 (inner) and
        r2 (outer) with center in cxdist,cydist. angle_start and
        angle_end are relative to the starting rotation point equal 0
        degrees """

        # Precalculate values
        d1 = r1 * 2
        d2 = r2 * 2
        r1_xstart = -r1 - cxdist
        r1_ystart = -r1 + cydist
        r2_xstart = -r2 - cxdist
        r2_ystart = -r2 + cydist
        angle_span = angle_end + angle_start

        path = QtGui.QPainterPath()
        # Calculate start and end points of inner arc
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, -angle_start)
        i1 = path.currentPosition()
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, angle_end)
        i2 = path.currentPosition()
        # Moves to outer arc start position
        path.arcMoveTo(r2_xstart, r2_ystart , d2, d2, -angle_start)
        o1 = path.currentPosition()
        # Draws outer arc
        path.arcTo(r2_xstart, r2_ystart, d2, d2, -angle_start, angle_span)
        o2 = path.currentPosition()
        # Draws line to the end point in inner arc (straight line)
        path.lineTo(i2)
        # Draws inner arc from end point to to start 
        path.arcTo(r1_xstart, r1_ystart, d1, d1, angle_end, -angle_span)
        # Draws line to the start point of outer arc (straight line)
        path.lineTo(o1)
        self.setPath(path)

def rotate_and_displace(item, rotation, height, offset):
    """ Rotates and item of a given height over its own axis and moves
    the item offset units in the rotated x axis """
    t = QtGui.QTransform()
    t.rotate(rotation)
    t.translate(0, - (height / 2))
    t.translate(offset, 0)
    item.setTransform(t)

def get_min_radius(w, h, a, xoffset):
    """ returns the radius and X-displacement required to render a
    rectangle (w,h) within and given angle (a)."""

    angle = (a * math.pi)/180 # converts to radians
    b = (xoffset+w) 
    a = h/2
    off = 0
    if xoffset:
        effective_angle = math.atan(a/xoffset)
        if effective_angle > angle/2 and angle/2 < math.pi:
            off = a / math.tan(angle/2)
            bb = off + w 
            r = math.sqrt(a**2 + bb**2) 
            off = max (off, xoffset) - xoffset
        else:
            r = math.sqrt(a**2 + b**2) 
    else:
        # It happens on root nodes
        r1 = math.sqrt(a**2 + b**2) 
        effective_angle = math.asin(a/r1)
        r2 = w / math.cos(effective_angle)
        r = r1+r2
    return r, off

def render_circular(root_node, n2i, rot_step):
    to_visit = []
    to_visit.append(root_node)
    max_r = 0
    while to_visit:
        node = to_visit.pop(0)

        if not _leaf(node):
            to_visit.extend(node.children)

        item = n2i[node]
        w = item.nodeRegion.width()
        #h = item.nodeRegion.height()
        h = item.effective_height


        if node is not root_node:
            parent_radius = n2i[node.up].radius
        else:
            parent_radius = 0

        if _leaf(node):
            angle = rot_step
        else:
            angle = item.angle_span
            #full_angle = abs(item.full_end - item.full_start)

        r, xoffset = get_min_radius(w, h, angle, parent_radius)
        rotate_and_displace(item, item.rotation, h, parent_radius)
        item.radius = r
        max_r = max(max_r, r)

        if not _leaf(node):
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # BG
            full_angle = last_c.full_end - first_c.full_start
            angle_start = last_c.full_end - item.rotation
            angle_end = item.rotation - first_c.full_start
            #item.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            #item.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            # C = item.vt_line
            C = QtGui.QGraphicsPathItem()
            C.setParentItem(item.parentItem())
            path = QtGui.QPainterPath()
            # Counter clock wise
            path.arcMoveTo(-r, -r, r * 2, r * 2, 360 - rot_start - angle)
            path.arcTo(-r, -r, r*2, r * 2, 360 - rot_start - angle, angle)
            # Faces
            C.setPath(path)

        if hasattr(item, "content"):
            item.content.moveBy(xoffset, 0)
            extra = QtGui.QGraphicsLineItem(0, item.center, xoffset, item.center, item)
            extra.setPen(QtGui.QPen(QtGui.QColor("orange")))
            
            
    return max_r

def init_circular_leaf_item(node, n2i, n2f, last_rotation, rot_step):
    item = n2i[node]
    item.rotation = last_rotation
    item.full_start = last_rotation - (rot_step / 2)
    item.full_end = last_rotation + (rot_step / 2)
    #item.center = item.nodeRegion.height() / 2
    item.effective_height = get_effective_height(node, n2i, n2f)
    item.center = item.effective_height/2

def init_circular_node_item(node, n2i, n2f):
    item = n2i[node]
    first_c = n2i[node.children[0]]
    last_c = n2i[node.children[-1]]
    rot_start = first_c.rotation
    rot_end = last_c.rotation
    item.angle_span = rot_end - rot_start
    item.rotation = rot_start + ((rot_end - rot_start) / 2)
    item.full_start = first_c.full_start
    item.full_end = last_c.full_end
    #item.center = item.nodeRegion.height()/2
    item.effective_height = get_effective_height(node, n2i, n2f)
    item.center = item.effective_height/2

def random_color(base=0.25):
    s = 0.5#random.random()
    v = 0.5+random.random()/2
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])


def get_effective_height(n, n2i, n2f):
        down_h = n2f[n]["branch-bottom"].h
        up_h = n2f[n]["branch-top"].h

        right_h = n2i[n].nodeRegion.height()/2
        up_h = max(right_h, up_h)
        down_h = max(right_h, down_h)
        
        fullR = n2i[n].fullRegion
        center = fullR.height()/2

        return max(up_h, down_h)*2

