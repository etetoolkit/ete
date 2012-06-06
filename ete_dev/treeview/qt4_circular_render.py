import math
import colorsys
from PyQt4 import QtCore, QtGui
from main import _leaf
from qt4_gui import _NodeActions
from collections import deque
import time

class _LineItem(QtGui.QGraphicsLineItem):
    def paint(self, painter, option, widget):
        #painter.setClipRect( option.exposedRect )
        QtGui.QGraphicsLineItem.paint(self, painter, option, widget)

# Performance tests!!
TIME  = [0]
def etime(f):
    def a_wrapper_accepting_arguments(*args, **kargs):
        global TIME
        t1 = time.time()
        f(*args, **kargs)
        print ".",
        TIME[0] = TIME[0] + time.time() - t1 
    return a_wrapper_accepting_arguments
         
COUNTER = 0
def reset_counter():
    global COUNTER
    COUNTER = 0

def print_counter():
    global COUNTER
    print "Paintings:", COUNTER

def increase():
    global COUNTER
    COUNTER += 1

class ArcPartition(QtGui.QGraphicsPathItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        #self.setCacheMode(QtGui.QGraphicsItem.ItemCoordinateCache)
        
    def set_arc(self, cxdist, cydist, r1, r2, angle_start, angle_end):
        """ Draws a 2D arc with two arc lines of length r1 (inner) and
        r2 (outer) with center in cxdist,cydist. angle_start and
        angle_end are relative to the starting rotation point equal 0
        degrees """

        #self.data = [cxdist, cydist, r1, r2, angle_start, angle_end]
        d1 = r1 * 2
        d2 = r2 * 2 
        r1_xstart = -r1 - cxdist
        r1_ystart = -r1 + cydist
        r2_xstart = -r2 - cxdist
        r2_ystart = -r2 + cydist
        angle_start = angle_start
        angle_end = angle_end
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

    def paint(self, painter, option, index):
        return QtGui.QGraphicsPathItem.paint(self, painter, option, index)


class _ArcItem(QtGui.QGraphicsPathItem):
    def __init__(self):
        QtGui.QGraphicsPathItem.__init__(self)
       
    def set_arc(self, cxdist, cydist, r1, r2, angle_start, angle_end):
        """ Draws a 2D arc with two arc lines of length r1 (inner) and
        r2 (outer) with center in cxdist,cydist. angle_start and
        angle_end are relative to the starting rotation point equal 0
        degrees """

        def clockwise(a):
            if a<0: 
                return -1 * (a)
            else:
                return -a
            return a

        #self.data = [cxdist, cydist, r1, r2, angle_start, angle_end]
        d1 = r1 * 2
        d2 = r2 * 2 
        r1_xstart = -r1 - cxdist
        r1_ystart = -r1 + cydist
        r2_xstart = -r2 - cxdist
        r2_ystart = -r2 + cydist

        # ArcTo does not use clockwise angles
        angle_start = clockwise(angle_start)
        angle_end = clockwise(angle_end)
        angle_span = angle_end - angle_start

        path = QtGui.QPainterPath()
        # Calculate start and end points of inner arc
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, angle_start)
        i1 = path.currentPosition()
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, angle_end)
        i2 = path.currentPosition()
        # Moves to outer arc start position
        path.arcMoveTo(r2_xstart, r2_ystart , d2, d2, angle_start)
        o1 = path.currentPosition()
        # Draws outer arc
        path.arcTo(r2_xstart, r2_ystart, d2, d2, angle_start, angle_span)
        o2 = path.currentPosition()
        # Draws line to the end point in inner arc (straight line)
        path.lineTo(i2)
        # Draws inner arc from end point to to start 
        path.arcTo(r1_xstart, r1_ystart, d1, d1, angle_end, -angle_span)
        # Draws line to the start point of outer arc (straight line)
        #path.lineTo(o1)
        self.setPath(path)

    def paint(self, painter, option, index):
        return QtGui.QGraphicsPathItem.paint(self, painter, option, index)

def rotate_and_displace(item, rotation, height, offset):
    """ Rotates an item of a given height over its own left most edis and moves
    the item offset units in the rotated x axis """
    t = QtGui.QTransform()
    t.rotate(rotation)
    t.translate(0, - (height / 2))
    t.translate(offset, 0)
    item.setTransform(t)


def get_min_radius(w, h, a, xoffset):
    """ returns the radius and X-displacement required to render a
    rectangle (w,h) within and given angle (a)."""

    # converts to radians
    angle = (a * math.pi) / 180 
    b = xoffset + w
    a = h / 2
    off = 0
    if xoffset:
        effective_angle = math.atan(a / xoffset)
        if effective_angle > angle / 2 and angle / 2 < math.pi:
            off = a / math.tan(angle / 2) 
            bb = off + w 
            r = math.sqrt(a**2 + bb**2) 
            off = max (off, xoffset) - xoffset
        else:
            r = math.sqrt(a**2 + b**2) 
    else:
        # It happens on root nodes
        r1 = math.sqrt(a**2 + b**2) 
        #effective_angle = math.asin(a/r1)
        #r2 = w / math.cos(effective_angle)
        r = r1#+r2
        
    return r, off

def render_circular(root_node, n2i, rot_step):
    max_r = 0.0
    for node in root_node.traverse('preorder'):
        item = n2i[node]
        w = item.nodeRegion.width()
        h = item.effective_height

        parent_radius = n2i[node.up].radius if node.up else 0 
        angle = rot_step if _leaf(node) else item.angle_span

        if hasattr(item, "radius"):
            r = item.radius
            xoffset = 0
        else:
            r, xoffset = get_min_radius(w, h, angle, parent_radius)
            item.radius = r
            print "parent", parent_radius , "mio", item.radius, "branch", item.branch_length
        if xoffset:
            print "Offset detected in node", xoffset

        rotate_and_displace(item.content, item.rotation, h, parent_radius)
        
        max_r = max(max_r, r)

        if not _leaf(node) and len(node.children) > 1:
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            rot_span = abs(rot_end - rot_start)
            C = item.vt_line
            C.setParentItem(item)
            path = QtGui.QPainterPath()
            # Counter clock wise
            path.arcMoveTo(-r, -r, r * 2, r * 2, 360 - rot_start - rot_span)
            path.arcTo(-r, -r, r*2, r * 2, 360 - rot_start - rot_span, rot_span)
            # Faces
            C.setPath(path)
            item.static_items.append(C)


        if hasattr(item, "content"):
            # If applies, it sets the length of the extra branch length
            if item.extra_branch_line:
                xtra =  item.extra_branch_line.line().dx()
                if xtra > 0:
                    xtra = xoffset + xtra
                else:
                    xtra = xoffset
                item.extra_branch_line.setLine(item.branch_length, item.center,\
                                               item.branch_length + xtra , item.center)
                item.nodeRegion.setWidth(item.nodeRegion.width()+xtra)

            # And moves elements 
            if xoffset:
                print "SI"
                for i in item.movable_items:
                    i.moveBy(xoffset, 0)

            
            
    n2i[root_node].max_r = max_r
    return max_r

    
def render_circular_old(root_node, n2i, rot_step):
    #to_visit = deque()
    #to_visit.append(root_node)
    max_r = 0.0
    for node in root_node.traverse('preorder'):
    #while to_visit:
    #    node = to_visit.popleft()
    # 
    #    if not _leaf(node):
    #        to_visit.extend(node.children)
        item = n2i[node]
        w = item.nodeRegion.width()
        h = item.effective_height

        if node is not root_node:
            parent_radius = n2i[node.up].radius
        else:
            parent_radius = 0

        if _leaf(node):
            angle = rot_step
        else:
            angle = item.angle_span
            #full_angle = angle
            #full_angle = abs(item.full_end - item.full_start)

        r, xoffset = get_min_radius(w, h, angle, parent_radius)
        if xoffset:
            print "SI", xoffset

        rotate_and_displace(item.content, item.rotation, h, parent_radius)
        item.radius = r
        max_r = max(max_r, r)

        if not _leaf(node):
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation

            C = item.vt_line
            C.setParentItem(item)
            path = QtGui.QPainterPath()
            # Counter clock wise
            path.arcMoveTo(-r, -r, r * 2, r * 2, 360 - rot_start - angle)
            path.arcTo(-r, -r, r*2, r * 2, 360 - rot_start - angle, angle)
            # Faces
            C.setPath(path)
            item.static_items.append(C)

        if hasattr(item, "content"):

            # If applies, it sets the length of the extra branch length
            if item.extra_branch_line:
                xtra =  item.extra_branch_line.line().dx()
                if xtra > 0:
                    xtra = xoffset + xtra
                else:
                    xtra = xoffset
                item.extra_branch_line.setLine(item.branch_length, item.center,\
                                               item.branch_length + xtra , item.center)
                item.nodeRegion.setWidth(item.nodeRegion.width()+xtra)

            # And moves elements 
            if xoffset:
                for i in item.movable_items:
                    i.moveBy(xoffset, 0)
            
    n2i[root_node].max_r = max_r
    return max_r

def init_circular_leaf_item(node, n2i, n2f, last_rotation, rot_step):
    item = n2i[node]
    item.rotation = last_rotation
    item.full_start = last_rotation - (rot_step / 2)
    item.full_end = last_rotation + (rot_step / 2)
    item.angle_span = rot_step
    #item.center = item.nodeRegion.height() / 2
    item.effective_height = get_effective_height(node, n2i, n2f)
    item.center = item.effective_height/2
    #item.setParentItem(n2i[node.up])

def init_circular_node_item(node, n2i, n2f):
    item = n2i[node]
    if len(node.children) >1: 
        first_c = n2i[node.children[0]]
        last_c = n2i[node.children[-1]]
        rot_start = first_c.rotation
        rot_end = last_c.rotation 
        #item.angle_span = rot_end - rot_start
        item.rotation = rot_start + ((rot_end - rot_start) / 2)
        item.full_start = first_c.full_start
        item.full_end = last_c.full_end
        item.angle_span = item.full_end - item.full_start
        
    else:
        child = n2i[node.children[0]]
        rot_start = child.full_start
        rot_end = child.full_end
        item.angle_span = child.angle_span
        item.rotation = rot_start + ((rot_end - rot_start) / 2)
        item.full_start = child.full_start
        item.full_end = child.full_end
    
    #item.center = item.nodeRegion.height()/2
    item.effective_height = get_effective_height(node, n2i, n2f)
    item.center = item.effective_height/2
    #if node.up:
    #    item.setParentItem(n2i[node.up])

def get_effective_height(n, n2i, n2f):
    down_h = n2f[n]["branch-bottom"].h
    up_h = n2f[n]["branch-top"].h

    right_h = n2i[n].nodeRegion.height()/2
    up_h = max(right_h, up_h)
    down_h = max(right_h, down_h)
        
    fullR = n2i[n].fullRegion
    center = fullR.height()/2
    return max(up_h, down_h)*2

def get_optimal_tree_width(root_node, n2f, img, rot_step):
    most_distant = 0
    for lf in root_node.iter_leaves():
        _n = lf
        max_he = 0
        while _n.up:
            max_he = max([n2f[_n]["branch-right"].h,
                     n2f[_n]["aligned"].h,
                     _n.img_style["size"],
                     sum([n2f[_n]["branch-top"].h,
                         n2f[_n]["branch-bottom"].h,
                         _n.img_style["hz_line_width"]]),
                     max_he]
                     )
            _n = _n.up
     
        angle = (rot_step * math.pi)/180 # converts to radians
        rad = (max_he/2.0) / math.tan(angle/2)
        most_distant = max(most_distant, rad)
    fnode, dist = root_node.get_closest_leaf(topology_only=\
                                             img.force_topology)
    return most_distant



def calculate_optimal_scale(root_node, n2i, rot_step):
    n2minradius = {}
    n2offset = {}
    n2sumdist = {}
    n2sumwidth = {}
    visited_nodes = []
    # Calcula la posicion minima de los elementos
    for node in root_node.traverse('preorder'):
        visited_nodes.append(node)
        item = n2i[node]
        
        w = item.nodeRegion.width()
        h = item.effective_height

        if node is not root_node:
            parent_radius = n2minradius[node.up]
        else:
            parent_radius = 0

        if _leaf(node):
            angle = rot_step
        else:
            angle = item.angle_span
            
        r, xoffset = get_min_radius(w, h, angle, parent_radius)
        n2offset[node] = xoffset
        n2minradius[node] = r
        n2sumdist[node] = n2sumdist.get(node.up, 0) + node.dist
        c = r - (parent_radius + xoffset + w)
        n2sumwidth[node] = n2sumwidth.get(node.up, 0) + w + c
        #print len(node), node.name, n2minradius[node], n2sumwidth[node]
        
    best_scale = None
    n2realradius= {}
    for node in visited_nodes:
        item = n2i[node]
        w = item.nodeRegion.width()
        h = item.effective_height

        if best_scale is None:
            best_scale = n2offset[node] / node.dist if node.dist else 0.0
            print len(node), node.name, node.dist, best_scale
            print n2minradius[node], best_scale
            n2realradius[node] = n2minradius[node]
        else:
            #current_start = n2realradius[node.up] + (node.dist * best_scale)
            current_start = n2sumdist[node] * best_scale + n2sumwidth[node.up]
            min_start = n2minradius[node.up] + n2offset[node]
            if current_start < min_start:
                print "OOps adjusting scale"
                # Aqui la ecuacion. Esto es solo una aproximacion al
                # resultado que infravalora el resultado real.
                old_scale = best_scale
                best_scale = (min_start - n2sumwidth[node.up]) / n2sumdist[node]
                #for n in n2realradius:
                #    off = (n.dist * best_scale) - (n.dist * old_scale)
                #    #print off
                #    n2realradius[n] += off
                current_start = n2realradius[node.up] + (node.dist * best_scale)
                
            n2realradius[node] = math.sqrt((current_start + w)**2 + (h/2)**2)
            
    for node in visited_nodes:
        item = n2i[node]
        current_start = n2sumdist[node] * best_scale + n2sumwidth[node]
        item.radius = current_start
        
    return best_scale