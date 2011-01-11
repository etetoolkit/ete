import math
import random
import colorsys
from PyQt4 import QtCore, QtGui
from main_render import render_node_content

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

        color = "#DDE8C4"
        color = random_color()
        self.setPen(QtGui.QPen(QtGui.QColor("green")))
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))

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
    # optimal_angle = angle fitting provided offset and item
    # dimensions
    if xoffset:
        optimal_angle = math.atan((h/2) / xoffset) 
    else:
        optimal_angle = 0

    # If available angle is >=180, I don't need to calculate extra
    # offset. Any item will fit
    if a/2>=180: #don't fully understand why a/2 ??
        min_offset = xoffset
    else:
        min_offset = (h/2) / math.tan(angle / 2)
   
    # Returns the optimal angle and x_offset 
    if optimal_angle < angle and xoffset>min_offset:
        off = xoffset
        r = (w + off) / math.cos(optimal_angle) 
        an = optimal_angle * 2
    elif optimal_angle < angle:
        off = min_offset
        r = (w + off) / math.cos(optimal_angle) 
        an = optimal_angle * 2
    else:
        off = min_offset
        r = (w + off) / math.cos(angle / 2) 
        an = angle
    return r, off, (an * 180) / math.pi

def render_circular(root_node, n2i, rot_step):
    print "PINTANDO ", root_node.name
    to_visit = []
    to_visit.append(root_node)
    max_r = 0
    while to_visit:
        node = to_visit.pop(0)
        hybrid_node = (node is not root_node) and hasattr(node, "mode") 

        if not _leaf(node) and not hybrid_node:
            to_visit.extend(node.children)

        item = n2i[node]

        w = item.nodeRegion.width()
        h = item.nodeRegion.height()
        if node is not root_node:
            parent_radius = n2i[node.up].radius
        else:
            parent_radius = 0

        if _leaf(node) or hybrid_node:
            angle = rot_step
        else:
            angle = item.angle_span
            
        print ".",
        r, xoffset, best_a = get_min_radius(w, h, angle, parent_radius)
        rotate_and_displace(item, item.rotation, h, parent_radius)
        item.radius = r
        max_r = max(max_r, r)
        if hybrid_node:
            print w, h, "HYBRID SIZE", item.radius

        if not _leaf(node) and not hybrid_node:
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # BG
            # full_angle = last_c.full_end - first_c.full_start
            # angle_start = last_c.full_end - item.rotation
            # angle_end = item.rotation - first_c.full_start
            # item.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            # item.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            C = QtGui.QGraphicsPathItem(item.parentItem())
            path = QtGui.QPainterPath()
            # Counter clock wise
            path.arcMoveTo(-r, -r, r * 2, r * 2, 360 - rot_start - angle)
            path.arcTo(-r, -r, r*2, r * 2, 360 - rot_start - angle, angle)
            # Faces
            C.setPath(path)
        #QtGui.QGraphicsRectItem(xoffset - parent_radius, 0, 10, 10, item)
        #faces.moveBy(xoffset - parent_radius + node.dist_xoffset, 0)
    n2i[root_node].max_r = max_r



def init_circular_leaf_item(node, n2i, last_rotation, rot_step):
    item = n2i[node]
    item.rotation = last_rotation
    item.full_start = last_rotation - (rot_step / 2)
    item.full_end = last_rotation + (rot_step / 2)
    item.center = item.nodeRegion.height() / 2

def init_circular_node_item(node, n2i):
    item = n2i[node]
    first_c = n2i[node.children[0]]
    last_c = n2i[node.children[-1]]
    rot_start = first_c.rotation
    rot_end = last_c.rotation
    item.angle_span = rot_end - rot_start
    item.rotation = rot_start + ((rot_end - rot_start) / 2)
    item.full_start = first_c.full_start
    item.full_end = last_c.full_end
    item.center = item.nodeRegion.height()/2


def random_color(base=0.25):
    s = 0.5#random.random()
    v = 0.5+random.random()/2
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])

def _leaf(node):
    return node.is_leaf()
