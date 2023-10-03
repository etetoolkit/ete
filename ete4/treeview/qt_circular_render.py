import math
import colorsys
import itertools

from .qt import *
from .main import _leaf, tracktime
from .node_gui_actions import _NodeActions

class _LineItem(QGraphicsLineItem):
    def paint(self, painter, option, widget):
        #painter.setClipRect( option.exposedRect )
        QGraphicsLineItem.paint(self, painter, option, widget)


class ArcPartition(QGraphicsPathItem):
    def __init__(self, parent=None):
        QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

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

        path = QPainterPath()
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
        return QGraphicsPathItem.paint(self, painter, option, index)


class _ArcItem(QGraphicsPathItem):
    def __init__(self):
        QGraphicsPathItem.__init__(self)

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

        path = QPainterPath()
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
        return QGraphicsPathItem.paint(self, painter, option, index)


def pack_nodes(n2i):
    """Shorten extra branch length to bring nodes closer to center."""
    max_r = max_x = min_x = max_y = min_y = 0.0
    for node in sorted(n2i, key=lambda x: n2i[x].radius):  # Move closer items first
        item = n2i[node]
        # QGraphicsRectItem(item.nodeRegion,  item.content)
        if node.is_leaf and item.extra_branch_line and item.extra_branch_line.line().dx() > 0:
            itemBoundingPoly = item.content.mapToScene(item.nodeRegion)

            intersecting_polys = []
            for other_item in n2i.values():
                if item != other_item:
                    otherItemBoundingPoly = other_item.content.mapToScene(other_item.nodeRegion)
                    if itemBoundingPoly.intersects(otherItemBoundingPoly):
                        for part in itertools.chain(other_item.static_items, other_item.movable_items):
                            intersecting_poly = part.mapToScene(part.boundingRect())
                            intersecting_polys.append(intersecting_poly)

            def has_intersecting_poly():
                for movable in item.movable_items:
                    mpoly = movable.mapToScene(movable.boundingRect())
                    for intersector in intersecting_polys:
                        if mpoly.intersects(intersector):
                            return True
                return False

            def move_node_towards_center(amount: int):
                # Update extra branch length
                old_line = item.extra_branch_line.line()
                item.extra_branch_line.setLine(old_line.x1(), old_line.y1(), math.floor(old_line.x2() - amount), old_line.y1())

                # Move items closer
                for movable in item.movable_items:
                    movable.moveBy(-amount, 0)
                item.nodeRegion.setWidth(item.nodeRegion.width() - amount)
                item.radius -= amount

            def binary_search_for_position(low: int, high: int):
                if high <= low:
                    return

                mid = (high + low) // 2
                move_by = math.ceil(item.extra_branch_line.line().dx()) - mid
                move_node_towards_center(move_by)

                if has_intersecting_poly():
                    move_node_towards_center(-move_by)
                    binary_search_for_position(mid+1, high)
                else:
                    binary_search_for_position(low, mid)

            binary_search_for_position(0, math.floor(item.extra_branch_line.line().dx()))

        # Update bounding values
        if max_r < item.radius:
            max_r = item.radius
        for movable in item.movable_items:
            b_rect = movable.sceneBoundingRect()
            if b_rect.top() < min_y:
                min_y = b_rect.top()
            if b_rect.bottom() > max_y:
                max_y = b_rect.bottom()
            if b_rect.left() < min_x:
                min_x = b_rect.left()
            if b_rect.right() > max_x:
                max_x = b_rect.right()

    return max_r, min_y, max_y, min_x, max_x


def rotate_and_displace(item, rotation, height, offset):
    """ Rotates an item of a given height over its own left most edis and moves
    the item offset units in the rotated x axis """
    t = QTransform()
    t.rotate(rotation)
    t.translate(0, - (height / 2))
    t.translate(offset, 0)
    item.setTransform(t)


def get_min_radius(w, h, angle, xoffset):
    """ returns the radius and X-displacement required to render a
    rectangle (w,h) within and given angle (a)."""

    # converts to radians
    angle = (angle * math.pi) / 180
    b = xoffset + w
    a = h / 2
    off = 0
    if xoffset:
        effective_angle = math.atan(a / xoffset)
        if effective_angle > angle / 2 and angle / 2 < math.pi:
            off = a / math.tan(angle / 2)
            bb = off + w
            #r = math.sqrt(a**2 + bb**2)
            r = math.hypot(a, bb)
            off = max (off, xoffset) - xoffset
        else:
            #r = math.sqrt(a**2 + b**2)
            r = math.hypot(a, b)
    else:
        # It happens on root nodes
        #r1 = math.sqrt(a**2 + b**2)
        r1 = math.hypot(a, b)
        #effective_angle = math.asin(a/r1)
        #r2 = w / math.cos(effective_angle)
        #print r1, r2
        r = r1#+r2

    return r, off

def render_circular(root_node, n2i, rot_step, pack_leaves):
    max_r = max_x = min_x = max_y = min_y = 0.0
    for node in root_node.traverse('preorder', is_leaf_fn=_leaf):
        item = n2i[node]
        w = sum(item.widths[1:5])
        h = item.effective_height

        parent_radius = n2i[node.up].radius if node.up and node.up in n2i else item.xoff
        angle = rot_step if _leaf(node) else item.angle_span

        if hasattr(item, "radius"):
            r = item.radius
            xoffset = 0
        else:
            r, xoffset = get_min_radius(w, h, angle, parent_radius + item.widths[0])
            item.radius = r
            node.add_props(rad=item.radius)

        #if xoffset: # DEBUG ONLY. IF Scale is correct, this should not be printed
        #    print "Offset detected in node", xoffset

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
            path = QPainterPath()
            # Counter clock wise
            start = r - node.img_style["vt_line_width"]/2
            path.arcMoveTo(-start, -start, start * 2, start * 2, 360 - rot_start - rot_span)
            path.arcTo(-start, -start, start * 2, start * 2, 360 - rot_start - rot_span, rot_span)
            # Faces
            C.setPath(path)
            item.static_items.append(C)


        if hasattr(item, "content"):

            # If applies, it sets the length of the extra branch length
            if item.extra_branch_line:
                xtra = item.extra_branch_line.line().dx()
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

        if not pack_leaves:
            for qt_item in itertools.chain(item.static_items, item.movable_items):
                b_rect = qt_item.sceneBoundingRect()
                if b_rect.top() < min_y:
                    min_y = b_rect.top()
                if b_rect.bottom() > max_y:
                    max_y = b_rect.bottom()
                if b_rect.left() < min_x:
                    min_x = b_rect.left()
                if b_rect.right() > max_x:
                    max_x = b_rect.right()

    if pack_leaves:
        max_r, min_y, max_y, min_x, max_x = pack_nodes(n2i)

    n2i[root_node].max_r = max_r

    return max_r, min_y, max_y, min_x, max_x

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
    if len(node.children) > 1:
        first_c = n2i[node.children[0]]
        last_c = n2i[node.children[-1]]
        rot_start = first_c.rotation
        rot_end = last_c.rotation
        item.rotation = rot_start + ((rot_end - rot_start) / 2)
        item.full_start = first_c.full_start
        item.full_end = last_c.full_end
        item.angle_span = item.full_end - item.full_start
    else:
        child = n2i[node.children[0]]
        rot_start = child.full_start
        rot_end = child.full_end
        item.angle_span = child.angle_span
        item.rotation = child.rotation
        #item.rotation = rot_start + ((rot_end - rot_start) / 2)
        item.full_start = child.full_start
        item.full_end = child.full_end

    item.effective_height = get_effective_height(node, n2i, n2f)
    item.center = item.effective_height/2

def get_effective_height(n, n2i, n2f):
    """Returns the height needed to calculated the adjustment
    of node to its available angle.
    """
    down_h = n2f[n]["branch-bottom"].h
    up_h = n2f[n]["branch-top"].h

    right_h = n2i[n].nodeRegion.height()/2
    up_h = max(right_h, up_h)
    down_h = max(right_h, down_h)

    fullR = n2i[n].fullRegion
    center = fullR.height()/2
    return max(up_h, down_h)*2


def calculate_optimal_scale(root_node, n2i, rot_step, img):
    """ Note: Seems to be fast. 0.5s from a tree of 10.000 leaves"""

    n2minradius = {}
    n2sumdist = {}
    n2sumwidth = {}
    visited_nodes = []
    # Calcula la posicion minima de los elementos (con scale=0, es
    # decir, sin tener en cuenta branch lengths.
    for node in root_node.traverse('preorder', is_leaf_fn=_leaf):
        visited_nodes.append(node)
        ndist = (node.dist or 1) if not img.force_topology else 1.0
        item = n2i[node]
        # Uses size of all node parts, except branch length
        w = sum(item.widths[1:5])
        h = item.effective_height
        parent_radius = n2minradius.get(node.up, 0)
        angle = rot_step if _leaf(node) else item.angle_span

        r, xoffset = get_min_radius(w, h, angle, parent_radius)
        n2minradius[node] = r
        n2sumdist[node] = n2sumdist.get(node.up, 0) + ndist
        # versed sine: the little extra line needed to complete the
        # radius.
        #vs = r - (parent_radius + xoffset + w)
        n2sumwidth[node] = n2sumwidth.get(node.up, 0) + sum(item.widths[2:5]) #+ vs

    root_opening = 0.0
    most_distant = max(n2sumdist.values())
    if most_distant == 0: return 0.0

    best_scale = None
    for node in visited_nodes:
        item = n2i[node]
        ndist = (node.dist or 1) if not img.force_topology else 1.0
        if best_scale is None:
            best_scale = (n2minradius[node] - n2sumwidth[node]) / ndist if ndist else 0.0
        else:
            #Whats the expected radius of this node?
            current_rad = n2sumdist[node] * best_scale + (n2sumwidth[node] + root_opening)

            # If still too small, it means we need to increase scale.
            if current_rad < n2minradius[node]:
                # This is a simplification of the real ecuacion needed
                # to calculate the best scale. Given that I'm not
                # taking into account the versed sine of each parent
                # node, the equation is actually very simple.
                if img.root_opening_factor:
                    best_scale = (n2minradius[node] - (n2sumwidth[node])) / (n2sumdist[node] + (most_distant * img.root_opening_factor))
                    root_opening = most_distant * best_scale * img.root_opening_factor
                else:
                    best_scale = (n2minradius[node] - (n2sumwidth[node]) + root_opening) / n2sumdist[node]
                #print "OOps adjusting scale", ndist, best_scale, n2minradius[node], current_rad, item.heights[5], node.name

            # If the width of branch top/bottom faces is not covered,
            # we can also increase the scale to adjust it. This may
            # produce huge scales, so let's keep it optional
            if img.optimal_scale_level == "full" and \
               item.widths[1] > ndist * best_scale:
                best_scale = item.widths[1] / ndist
                #print "OOps adjusting scale because  branch-faces", ndist, best_scale, item.widths[1]

    # Adjust scale for aligned faces
    if not img.allow_face_overlap:
        aligned_h = [(n2i[node].heights[5], node) for node in visited_nodes]
        aligned_h.sort(reverse=True, key=lambda x: x[0])
        maxh, maxh_node = aligned_h[0]
        angle = n2i[maxh_node].angle_span
        rad, off = get_min_radius(1, maxh, angle, 0.0001)
        min_alg_scale = None
        for node in visited_nodes:
            if n2i[node].heights[5]:
                new_scale = (rad - (n2sumwidth[node] + root_opening)) / n2sumdist[node]
                min_alg_scale = min(new_scale, min_alg_scale) if min_alg_scale is not None else new_scale
        if min_alg_scale is not None and min_alg_scale > best_scale:
            best_scale = min_alg_scale

    if root_opening:
        n2i[root_node].nodeRegion.adjust(root_opening, 0, root_opening, 0)
        n2i[root_node].fullRegion.adjust(root_opening, 0, root_opening, 0)
        n2i[root_node].xoff = root_opening

    return best_scale
