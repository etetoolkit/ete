"""
Classes and functions for drawing a tree.
"""

from math import sin, cos, pi, sqrt, atan2
from collections import namedtuple, OrderedDict, defaultdict, deque
import random

from ete4.smartview.ete.walk import walk

Size = namedtuple('Size', 'dx dy')  # size of a 2D shape (sizes are always >= 0)
Box = namedtuple('Box', 'x y dx dy')  # corner and size of a 2D shape
SBox = namedtuple('SBox', 'x y dx_min dx_max dy')  # slanted box

FACE_POSITIONS = ["branch-top", "branch-bottom", "branch-right", "aligned"]

# They are all "generalized coordinates" (can be radius and angle, say).


# The convention for coordinates is:
#   x increases to the right, y increases to the bottom.
#
#  +-----> x          +------.
#  |                   \   a .
#  |                    \   .   (the angle thus increases clockwise too)
#  v y                 r \.
#
# This is the convention normally used in computer graphics, including SVGs,
# HTML Canvas, Qt, and PixiJS.
#
# The boxes (shapes) we use are:
#
# * Rectangle         w
#              x,y +-----+          so (x,y) is its (left,top) corner
#                  |     | h        and (x+w,y+h) its (right,bottom) one
#                  +-----+
#
# * Annular sector   r,a .----.
#                       .  dr .     so (r,a) is its (inner,smaller-angle) corner
#                       \   .       and (r+dr,a+da) its (outer,bigger-angle) one
#                        \. da

# Drawing.

class Drawer:
    "Base class (needs subclassing with extra functions to draw)"

    COLLAPSE_SIZE = 6  # anything that has less pixels will be outlined

    MIN_SIZE = 1  # anything that has less pixels will not be drawn

    TYPE = 'base'  # can be 'rect' or 'circ' for working drawers

    NPANELS = 1 # number of drawing panels (including the aligned ones)

    def __init__(self, tree, viewport=None, panel=0, zoom=(1, 1),
                 limits=None, collapsed_ids=None, searches=None,
                 tree_style=None):
        self.tree = tree
        self.viewport = Box(*viewport) if viewport else None
        self.panel = panel
        self.zoom = zoom
        self.xmin, self.xmax, self.ymin, self.ymax = limits or (0, 0, 0, 0)
        self.collapsed_ids = collapsed_ids or set()  # manually collapsed
        self.searches = searches or {}  # looks like {text: (results, parents)}
        self.tree_style = tree_style
        if not self.tree_style:
            from ete4.smartview.ete.layouts import TreeStyle
            self.tree_style = TreeStyle()

    def draw(self):
        "Yield graphic elements to draw the tree"
        self.outline = None  # sbox surrounding the current collapsed nodes
        self.collapsed = []  # nodes that are curretly collapsed together
        self.nodeboxes = []  # boxes surrounding all nodes and collapsed boxes
        self.node_dxs = [[]]  # lists of nodes dx (to find the max)
        self.bdy_dys = [[]]  # lists of branch dys and total dys

        if self.panel == 0:
            self.tree_style.aligned_grid_dxs = defaultdict(lambda: 0)

        point = self.xmin, self.ymin
        for it in walk(self.tree):
            graphics = []
            if it.first_visit:
                point = self.on_first_visit(point, it, graphics)
            else:
                point = self.on_last_visit(point, it, graphics)
            yield from graphics

        if self.outline:
            yield from self.get_outline()

        if self.panel == 0:  # draw in preorder the boxes we found in postorder
            yield from self.nodeboxes[::-1]  # (so they overlap nicely)

    def on_first_visit(self, point, it, graphics):
        "Update list of graphics to draw and return new position"
        box_node = make_box(point, self.node_size(it.node))
        x, y = point
        it.node.is_collapsed = False

        if not self.in_viewport(box_node):
            self.bdy_dys[-1].append( (box_node.dy / 2, box_node.dy) )
            it.descend = False  # skip children
            return x, y + box_node.dy

        is_manually_collapsed = it.node_id in self.collapsed_ids

        if is_manually_collapsed and self.outline:
            graphics += self.get_outline()  # so we won't stack with its outline

        if is_manually_collapsed or self.is_small(box_node):
            self.node_dxs[-1].append(box_node.dx)
            self.collapsed.append(it.node)
            self.outline = stack(self.outline, box_node)
            it.descend = False  # skip children
            return x, y + box_node.dy

        if self.outline:
            graphics += self.get_outline()

        self.bdy_dys.append([])

        dx, dy = self.content_size(it.node)
        if it.node.is_leaf():
            return self.on_last_visit((x + dx, y + dy), it, graphics)
        else:
            self.node_dxs.append([])
            return x + dx, y

    def on_last_visit(self, point, it, graphics):
        "Update list of graphics to draw and return new position"
        if self.outline:
            graphics += self.get_outline()

        x_after, y_after = point
        dx, dy = self.content_size(it.node)
        x_before, y_before = x_after - dx, y_after - dy

        content_graphics = list(self.draw_content(it.node, (x_before, y_before)))
        graphics += content_graphics

        ndx = (drawn_size(content_graphics, self.get_box).dx if it.node.is_leaf()
                else (dx + max(self.node_dxs.pop() or [0])))
        self.node_dxs[-1].append(ndx)

        box = Box(x_before, y_before, ndx, dy)
        result_of = [text for text,(results,_) in self.searches.items()
                        if it.node in results]
        self.nodeboxes += self.draw_nodebox(it.node, it.node_id, box,
                result_of, { 'fill': it.node.img_style.get('bgcolor') })

        return x_before, y_after

    def draw_content(self, node, point):
        "Yield the node content's graphic elements"
        x, y = point
        dx, dy = self.content_size(node)

        if not self.in_viewport(Box(x, y, dx, dy)):
            return

        # Find branch dy of first child (bdy0), last (bdy1), and self (bdy).
        bdy_dys = self.bdy_dys.pop()  # bdy_dys[i] == (bdy, dy)
        bdy0 = bdy1 = dy / 2  # branch dys of the first and last children
        if bdy_dys:
            bdy0 = bdy_dys[0][0]
            bdy1 = sum(bdy_dy[1] for bdy_dy in bdy_dys[:-1]) + bdy_dys[-1][0]
        bdy = (bdy0 + bdy1) / 2  # this node's branch dy
        self.bdy_dys[-1].append( (bdy, dy) )

        # Collapsed nodes will be drawn from self.draw_collapsed()
        if not node.is_collapsed:
            bdy0_, bdy1_ = (0, dy) if node.is_leaf() else (bdy0, bdy1)
            yield from self.draw_node(node, point, dx, bdy, bdy0_, bdy1_)

        # Draw the branch line ("lengthline") and a line spanning all children.
        if self.panel == 0:
            node_style = node.img_style
            if dx > 0:
                parent_of = [text for text,(_,parents) in self.searches.items()
                                if node in parents]
                hz_line_style = {
                        'type': node_style['hz_line_type'],
                        'width': node_style['hz_line_width'],
                        'color': node_style['hz_line_color'],
                }
                yield from self.draw_lengthline((x, y + bdy), (x + dx, y + bdy),
                                parent_of, hz_line_style)

                nodedot_style = {
                        'shape': node_style['shape'],
                        'size': node_style['size'],
                        'fill': node_style['fgcolor'],
                }
                yield from self.draw_nodedot((x + dx, y + bdy),
                        dy * self.zoom[1], nodedot_style)

            if bdy0 != bdy1:
                vt_line_style = {
                        'type': node_style['vt_line_type'],
                        'width': node_style['vt_line_width'],
                        'color': node_style['vt_line_color'],
                }
                yield from self.draw_childrenline((x + dx, y + bdy0),
                                                  (x + dx, y + bdy1),
                                                  style=vt_line_style)

    def get_outline(self):
        "Yield the outline representation"
        result_of = [text for text,(results,parents) in self.searches.items()
            if any(node in results or node in parents for node in self.collapsed)]

        graphics = []

        node0 = self.collapsed[0]
        uncollapse = len(self.collapsed) == 1 and node0.is_leaf()

        x, y, _, _, _ = self.outline

        if uncollapse:
            self.bdy_dys.append([])
            graphics += self.draw_content(node0, (x, y))
        else:
            self.bdy_dys[-1].append( (self.outline.dy / 2, self.outline.dy) )
            graphics += self.draw_collapsed()

        collapsed_node = self.get_collapsed_node()
        is_manually_collapsed = collapsed_node in self.collapsed
        is_small = self.is_small(make_box((x, y),
            self.node_size(collapsed_node)))

        ndx = drawn_size(graphics, self.get_box).dx

        # Draw collapsed node nodebox when necessary
        if is_manually_collapsed or is_small or collapsed_node.dist == 0:
            name, properties = collapsed_node.name, collapsed_node.properties

            box = draw_nodebox(self.flush_outline(ndx), name, 
                    properties, [], result_of, 
                    { 'fill': collapsed_node.img_style.get('bgcolor') })
            self.nodeboxes.append(box)
        else:
            self.flush_outline()

        self.collapsed = []
        self.node_dxs[-1].append(ndx)

        yield from graphics

    def flush_outline(self, minimum_dx=0):
        "Return box outlining the collapsed nodes and reset the current outline"
        x, y, dx_min, dx_max, dy = self.outline
        self.outline = None
        return Box(x, y, max(dx_max, minimum_dx), dy)

    def get_collapsed_node(self):
        """Get node that will be rendered as a collapsed node.
        Either the only node collapsed or the parent of all collapsed nodes."""

        node0 = self.collapsed[0]
        if len(self.collapsed) == 1:
            node0.is_collapsed = True
            return node0
        
        parent = node0.up
        if all(node.up == parent for node in self.collapsed[1:]) and\
           all(child in self.collapsed for child in parent.children):
            parent.is_collapsed = True
            return parent

        # No node inside the tree contains all the collapsed nodes
        # Create a fictional node whose children are the collapsed nodes
        try:
            node = Tree()
        except:
            from ete4 import Tree # avoid circular import
            node = Tree()

        node.is_collapsed = True
        node.is_initialized = False
        node.children = self.collapsed  # add avoiding parent override
        _, _, dx_min, _, dy = self.outline
        node.dist = 0 
        node.size = Size(0, dy)

        return node

    def is_fully_collapsed(self, collapsed_node):
        """Returns true if collapsed_node is utterly collapsed,
        i.e. has no branch width"""
        x, y, *_ = self.outline
        is_manually_collapsed = collapsed_node in self.collapsed
        box_node = make_box((x, y), self.node_size(collapsed_node))

        return is_manually_collapsed or self.is_small(box_node)


    # These are the 2 functions that the user overloads to choose what to draw
    # when representing a node and a group of collapsed nodes:

    def draw_node(self, node, point, bdx, bdy, bdy0, bdy1):
        "Yield graphic elements to draw the contents of the node"
        # bdx: branch dx (width)
        # bdy: branch dy (height)
        # bdy0: fist child branch dy (height)
        # bdy1: last child branch dy (height)
        yield from []  # only drawn if the node's content is visible

    def draw_collapsed(self):
        "Yield graphic elements to draw the list of nodes in self.collapsed"
        yield from []  # they are always drawn (only visible nodes can collapse)
        # Uses self.collapsed and self.outline to extract and place info.



class DrawerRect(Drawer):
    "Minimal functional drawer for a rectangular representation"

    TYPE = 'rect'

    def in_viewport(self, box):
        if not self.viewport:
            return True

        if self.panel == 0:
            return intersects_box(self.viewport, box)
        else:
            return intersects_segment(get_ys(self.viewport), get_ys(box))

    def node_size(self, node):
        "Return the size of a node (its content and its children)"
        return Size(node.size[0], node.size[1])

    def content_size(self, node):
        "Return the size of the node's content"
        return Size(abs(node.dist), node.size[1])

    def children_size(self, node):
        "Return the size of the node's children"
        return Size(node.size[0] - abs(node.dist), node.size[1])

    def is_small(self, box):
        zx, zy = self.zoom
        return box.dy * zy < self.COLLAPSE_SIZE

    def get_box(self, element):
        return get_rect(element, self.zoom)

    def draw_lengthline(self, p1, p2, parent_of, style):
        "Yield a line representing a length"
        line = draw_line(p1, p2, 'lengthline', parent_of, style)
        if not self.viewport or intersects_box(self.viewport, get_rect(line)):
            yield line

    def draw_childrenline(self, p1, p2, style):
        "Yield a line spanning children that starts at p1 and ends at p2"
        line = draw_line(p1, p2, 'childrenline', style=style)
        if not self.viewport or intersects_box(self.viewport, get_rect(line)):
            yield line

    def draw_nodedot(self, center, max_size, style):
        "Yield circle or square on node based on node.img_style"
        size = min(max_size, style['size'])
        if size > 0:
            fill = style['fill']
            nodedot_style={'fill':fill}
            if style['shape'] == 'circle':
                yield draw_circle(center, radius=size, 
                        circle_type='nodedot', style=nodedot_style)
            elif style['shape'] == 'square':
                x, y = center
                zx, zy = self.zoom
                dx, dy = 2 * size / zx, 2 * size / zy
                box = (x - dx/2, y - dy/2, dx, dy)
                yield draw_rect(box, rect_type='nodedot', style=nodedot_style)

    def draw_nodebox(self, node, node_id, box, result_of, style=None):
        yield draw_nodebox(box, node.name, node.properties,
                node_id, result_of, style)



class DrawerCirc(Drawer):
    "Minimal functional drawer for a circular representation"

    TYPE = 'circ'

    def __init__(self, tree, viewport=None, panel=0, zoom=(1, 1),
                 limits=None, collapsed_ids=None, searches=None,
                 tree_style=None):
        super().__init__(tree, viewport, panel, zoom,
                         limits, collapsed_ids, searches, tree_style)

        assert self.zoom[0] == self.zoom[1], 'zoom must be equal in x and y'

        if not limits:
            self.ymin, self.ymax = -pi, pi

        self.dy2da = (self.ymax - self.ymin) / self.tree.size[1]

    def in_viewport(self, box):
        if not self.viewport:
            return intersects_segment((-pi, +pi), get_ys(box))

        if self.panel == 0:
            return (intersects_box(self.viewport, circumrect(box)) and
                    intersects_segment((-pi, +pi), get_ys(box)))
        else:
            return intersects_angles(self.viewport, box)

    def flush_outline(self, minimum_dr=0):
        "Return box outlining the collapsed nodes"
        r, a, dr, da = super().flush_outline(minimum_dr)
        a1, a2 = clip_angles(a, a + da)
        return Box(r, a1, dr, a2 - a1)

    def node_size(self, node):
        "Return the size of a node (its content and its children)"
        return Size(node.size[0], node.size[1] * self.dy2da)

    def content_size(self, node):
        "Return the size of the node's content"
        return Size(abs(node.dist), node.size[1] * self.dy2da)

    def children_size(self, node):
        "Return the size of the node's children"
        return Size(node.size[0] - abs(node.dist), node.size[1] * self.dy2da)

    def is_small(self, box):
        z = self.zoom[0]  # zx == zy in this drawer
        r, a, dr, da = box
        return (r + dr) * da * z < self.COLLAPSE_SIZE

    def get_box(self, element):
        return get_asec(element, self.zoom)

    def draw_lengthline(self, p1, p2, parent_of, style):
        "Yield a line representing a length"
        if -pi <= p1[1] < pi:  # NOTE: the angles p1[1] and p2[1] are equal
            yield draw_line(cartesian(p1), cartesian(p2),
                            'lengthline', parent_of, style)

    def draw_childrenline(self, p1, p2, style):
        "Yield an arc spanning children that starts at p1 and ends at p2"
        (r1, a1), (r2, a2) = p1, p2
        a1, a2 = clip_angles(a1, a2)
        if a1 < a2:
            is_large = a2 - a1 > pi
            yield draw_arc(cartesian((r1, a1)), cartesian((r2, a2)), 
                           is_large, 'childrenline', style=style)

    def draw_nodedot(self, center, max_size, style):
        r, a = center
        size = min(max_size, style['size'])
        if -pi < a < pi and size > 0:
            fill = style['fill']
            nodedot_style={'fill':fill}
            if style['shape'] == 'circle':
                yield draw_circle(center, radius=size,
                          circle_type='nodedot', style=nodedot_style)
            elif style['shape'] == 'square':
                z = self.zoom[0] # same zoom in x and y
                dr, da = 2 * size / z, 2 * size / (z * r)
                box = Box(r - dr / 2, a - da / 2, dr, da)
                yield draw_rect(box, rect_type='nodedot', style=nodedot_style)

    def draw_nodebox(self, node, node_id, box, result_of, style=None):
        r, a, dr, da = box
        a1, a2 = clip_angles(a, a + da)
        if a1 < a2:
            yield draw_nodebox(Box(r, a1, dr, a2 - a1),
                       node.name, node.properties, node_id, result_of, style)


def clip_angles(a1, a2):
    "Return the angles such that a1 to a2 extend at maximum from -pi to pi"
    EPSILON = 1e-8  # without it, p1 can be == p2 and svg arcs are not drawn
    return max(-pi + EPSILON, a1), min(pi - EPSILON, a2)


def cartesian(point):
    r, a = point
    return r * cos(a), r * sin(a)


def is_good_angle_interval(a1, a2):
    EPSILON = 1e-8  # without it, rounding can fake a2 > pi
    return -pi <= a1 < a2 < pi + EPSILON


def dx_fitting_texts(texts, dy, zoom):
    "Return a dx wide enough on the screen to fit all texts in the given dy"
    zx, zy = zoom
    dy_char = zy * dy / len(texts)  # height of a char, in screen units
    dx_char = dy_char / 1.5  # approximate width of a char
    max_len = max(len(t) for t in texts)  # number of chars of the longest
    return max_len * dx_char / zx  # in tree units

# Drawing generators.

def draw_rect_leaf_name(drawer, node, point):
    "Yield name to the right of the leaf"
    if not node.is_leaf() or not node.name:
        return

    x, y = point
    dx, dy = drawer.content_size(node)

    x_text = (x + dx) if drawer.panel == 0 else drawer.xmin
    dx_fit = dx_fitting_texts([node.name], dy, drawer.zoom)
    box = Box(x_text, y, dx_fit, dy)

    yield draw_text(box, (0, 0.5), node.name, 'name',
            style={ 'fill': node.img_style.get('fgcolor') })


def draw_circ_leaf_name(drawer, node, point):
    "Yield name at the end of the leaf"
    if not node.is_leaf() or not node.name:
        return

    r, a = point
    dr, da = drawer.content_size(node)

    if is_good_angle_interval(a, a + da) and r + dr > 0:
        r_text = (r + dr) if drawer.panel == 0 else drawer.xmin
        dr_fit = dx_fitting_texts([node.name], (r + dr) * da, drawer.zoom)
        box = Box(r_text, a, dr_fit, da)
        yield draw_text(box, (0, 0.5), node.name, 'name',
                style={ 'fill': node.img_style.get('fgcolor') })


def draw_rect_collapsed_names(drawer):
    "Yield names of collapsed nodes after their outline"
    x, y, dx_min, dx_max, dy = drawer.outline

    names = summary(drawer.collapsed)
    if all(name == '' for name in names):
        return

    texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])

    x_text = (x + dx_max) if drawer.panel == 0 else drawer.xmin
    dx_fit = dx_fitting_texts(texts, dy, drawer.zoom)
    box = Box(x_text, y, dx_fit, dy)

    yield from draw_texts(box, (0, 0.5), texts, 'name')


def draw_circ_collapsed_names(drawer):
    "Yield names of collapsed nodes after their outline"
    r, a, dr_min, dr_max, da = drawer.outline
    if not (-pi <= a <= pi and -pi <= a + da <= pi):
        return

    names = summary(drawer.collapsed)
    if all(name == '' for name in names):
        return

    texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])

    r_text = (r + dr_max) if drawer.panel == 0 else drawer.xmin
    dr_fit = dx_fitting_texts(texts, (r + dr_max) * da, drawer.zoom)
    box = Box(r_text, a, dr_fit, da)

    yield from draw_texts(box, (0, 0.5), texts, 'name')


# The actual drawers.

class DrawerRectFaces(DrawerRect):

    def draw_node(self, node, point, bdx, bdy, bdy0, bdy1):
        size = self.content_size(node)
        # Space available for branch-right Face position
        dx_to_closest_child = min(child.dist for child in node.children)\
                if not node.is_leaf() else node.dist
        zx, zy = self.zoom

        def it_fits(box):
            _, _, dx, dy = box
            return dx * zx > self.MIN_SIZE\
                    and dy * zy > self.MIN_SIZE\
                    and self.in_viewport(box)

        def draw_face(face, pos, row, n_row, n_col, dx_before, dy_before):
            if face.get_content():
                box = face.compute_bounding_box(self, point, size, 
                            dx_to_closest_child,
                            bdx, bdy, bdy0, bdy1,
                            pos, row, n_row, n_col,
                            dx_before, dy_before)
                if it_fits(box) and face.fits():
                    yield from face.draw(self)

        def draw_faces_at_pos(node, pos):
            if node.is_collapsed:
                node_faces = node.collapsed_faces
            else:
                node_faces = node.faces
                
            faces = dict(getattr(node_faces, pos, {}))
            n_col = max(faces.keys(), default = -1) + 1

            dx_before = 0
            for col, face_list in sorted(faces.items()):
                dx_max = 0
                dy_before = 0
                n_row = len(face_list)
                for row, face in enumerate(face_list):
                    face.node = node
                    drawn_face = list(draw_face(face, pos, row, n_row, n_col,
                            dx_before, dy_before))
                    if drawn_face:
                        _, _, dx, dy = face.get_box()
                        hz_padding = 2 * face.padding_x / zx
                        vt_padding = 2 * face.padding_y / zy
                        dx_max = max(dx_max, (dx or 0) + hz_padding)
                        dy_before += dy + vt_padding
                        yield from drawn_face

                # Update dx_before
                if pos == 'aligned'\
                        and self.tree_style.aligned_grid\
                        and self.NPANELS > 1:
                    dx_grid = self.tree_style.aligned_grid_dxs[col]
                    if self.panel == 0:
                        # Compute aligned grid
                        dx_grid = max(dx_grid, dx_max)
                        self.tree_style.aligned_grid_dxs[col] = dx_grid
                    else:
                        dx_before += dx_grid
                else:
                    dx_before += dx_max

        if not node.is_initialized:
            node.is_initialized = True
            for layout_fn in self.tree_style.layout_fn:
                layout_fn(node)

        # Render Faces in different panels
        if self.NPANELS > 1:
            if self.panel == 0:
                for pos in FACE_POSITIONS[:3]:
                    yield from draw_faces_at_pos(node, pos)
                # Only run function to compute aligned grid
                if self.tree_style.aligned_grid: 
                    deque(draw_faces_at_pos(node, 'aligned'))
            else:
                yield from draw_faces_at_pos(node, 'aligned')
        else:
            for pos in FACE_POSITIONS:
                yield from draw_faces_at_pos(node, pos)

    def draw_collapsed(self):
        x, y, dx_min, dx_max, dy = self.outline

        collapsed_node = self.get_collapsed_node()

        if self.is_fully_collapsed(collapsed_node):
            bdx = 0
        else:
            x = x - collapsed_node.dist
            bdx = collapsed_node.dist

        x = x if self.panel == 0 else self.xmin

        yield from self.draw_node(collapsed_node, (x, y), bdx, dy/2, 0, dy)


class DrawerCircFaces(DrawerCirc):

    def draw_node(self, node, point, bdr, bda, bda0, bda1):
        size = self.content_size(node)
        # Space available for branch-right Face position
        dr_to_closest_child = min(child.dist for child in node.children)\
                if not node.is_leaf() else node.dist
        z = self.zoom[0]  # zx == zy
            
        r_node = point[0]
        if r_node == 0:
            return

        def it_fits(box):
            r, a, dr, da = box
            return r > 0 \
                    and dr * z > self.MIN_SIZE\
                    and (r + dr) * da * z > self.MIN_SIZE\
                    and self.in_viewport(box)

        def draw_face(face, pos, row, n_row, n_col, dr_before, da_before):
            if face.get_content():
                box = face.compute_bounding_box(self, point, size,
                        dr_to_closest_child,
                        bdr, bda, bda0, bda1,
                        pos, row, n_row, n_col,
                        dr_before, da_before)
                if it_fits(box) and face.fits():
                    yield from face.draw(self)

        def draw_faces_at_pos(node, pos):
            if node.is_collapsed:
                node_faces = node.collapsed_faces
            else:
                node_faces = node.faces
                
            faces = dict(getattr(node_faces, pos, {}))
            n_col = len(faces.keys())

            # Avoid drawing faces very close to center
            if pos.startswith('branch-') and abs(r_node) < 1e-5:
                n_col += 1
                dr_before = .7 * size[0] / n_col
            elif pos == 'aligned' and self.panel == 1:
                dr_before = self.tree_style.aligned_grid_dxs[-1]
            else:
                dr_before = 0

            for col, face_list in sorted(faces.items()):
                dr_max = 0
                da_before = 0
                n_row = len(face_list)
                for row, face in enumerate(face_list):
                    face.node = node
                    drawn_face = list(draw_face(face, pos, row, n_row, n_col,
                            dr_before, da_before))
                    if drawn_face:
                        r, a, dr, da = face.get_box()
                        hz_padding = 2 * face.padding_x / z
                        vt_padding = 2 * face.padding_y / (z * r)
                        dr_max = max(dr_max, dr + hz_padding)
                        da_before = da + vt_padding
                        yield from drawn_face
                
                # Update dr_before
                if pos == 'aligned'\
                        and self.tree_style.aligned_grid\
                        and self.NPANELS > 1:
                    dr_grid = self.tree_style.aligned_grid_dxs[col]
                    if self.panel == 0:
                        # Compute aligned grid
                        dr_grid = max(dr_grid, dr_max)
                        self.tree_style.aligned_grid_dxs[col] = dr_grid
                    else:
                        dr_before += dr_grid
                else:
                    dr_before += dr_max

            if pos == 'branch-right'\
                    and (node.is_leaf() or node.is_collapsed):
                dr_grid = self.tree_style.aligned_grid_dxs[-1]
                dr_grid = max(dr_grid, r_node + dr_before)
                self.tree_style.aligned_grid_dxs[-1] = dr_grid


        if not node.is_initialized:
            node.is_initialized = True
            for layout_fn in self.tree_style.layout_fn:
                layout_fn(node)

        # Render Faces in different panels
        if self.NPANELS > 1:
            if self.panel == 0:
                for pos in FACE_POSITIONS[:3]:
                    yield from draw_faces_at_pos(node, pos)
                # Only run function to compute aligned grid
                if self.tree_style.aligned_grid: 
                    deque(draw_faces_at_pos(node, 'aligned'))
            else:
                yield from draw_faces_at_pos(node, 'aligned')
        else:
            for pos in FACE_POSITIONS:
                yield from draw_faces_at_pos(node, pos)

    def draw_collapsed(self):
        r, a, dr_min, dr_max, da = self.outline

        collapsed_node = self.get_collapsed_node()

        if self.is_fully_collapsed(collapsed_node):
            bdr = 0
        else:
            r = r - collapsed_node.dist
            bdr = collapsed_node.dist

        r = r if self.panel == 0 else self.xmin

        yield from self.draw_node(collapsed_node, (r, a), bdr, da/2, 0, da)


class DrawerAlignRectFaces(DrawerRectFaces):
    NPANELS = 2

    def draw_node(self, node, point, bdx, bdy, bdy0, bdy1):
        node_graphics = list(super().draw_node(node, point, bdx, bdy, bdy0, bdy1))
        yield from node_graphics
        if self.panel == 0 and node.is_leaf() and self.viewport:
            x, y = point
            dx, dy = self.node_size(node)
            ndx = drawn_size(node_graphics, self.get_box).dx
            p1 = (x + dx + ndx, y + dy/2)
            p2 = (self.viewport.x + self.viewport.dx, y + dy/2)
            style = { 'type': 1, # dotted
                      'width': 0.5,
                      'color': 'gray' }
            yield draw_line(p1, p2, 'align-link', style=style)

    def draw_collapsed(self):
        collapsed_graphics = list(super().draw_collapsed())
        yield from collapsed_graphics
        if self.panel == 0 and self.viewport:
            x, y, dx_min, dx_max, dy = self.outline
            collapsed_node = self.get_collapsed_node()
            dx = collapsed_node.dist\
                    if not self.is_fully_collapsed(collapsed_node) else 0
            ndx = drawn_size(collapsed_graphics, self.get_box).dx
            p1 = (x + ndx, y + dy/2)
            p2 = (self.viewport.x + self.viewport.dx, y + dy/2)
            style = { 'type': 1, # dotted
                      'width': 0.5,
                      'color': 'gray'}
            yield draw_line(p1, p2, 'align-link', style=style)


class DrawerAlignCircFaces(DrawerCircFaces):
    NPANELS = 2


def get_drawers():
    return [ DrawerRect, DrawerCirc, 
            DrawerRectFaces, DrawerCircFaces,
            DrawerAlignRectFaces, DrawerAlignCircFaces,
            ]


def summary(nodes):
    "Return a list of names summarizing the given list of nodes"
    return list(OrderedDict((first_name(node), None) for node in nodes).keys())


def first_name(tree):
    "Return the name of the first node that has a name"
    return next((node.name for node in tree.traverse('preorder') if node.name), '')


def draw_texts(box, texts, text_type):
    "Yield texts so they fit in the box"
    dy = box.dy / len(texts)
    y = box.y
    for text in texts:
        yield draw_text(Box(box.x, y, box.dx, dy), text, text_type)
        y += dy


# Basic drawing elements.

def draw_nodebox(box, name='', properties=None, 
        node_id=None, result_of=None, style=None):
    return ['nodebox', box, name, 
            properties or {}, node_id or [], 
            result_of or [], style or {}]

def draw_outline(sbox, style=None):
    return ['outline', sbox, style or {}]

def draw_line(p1, p2, line_type='', parent_of=None, style=None):
    types = ['solid', 'dotted', 'dashed']
    if style and style.get('type'):
        style['type'] = types[int(style['type'])]
    else:
        style['type'] = types[0]

    return ['line', p1, p2, line_type, parent_of or [], style or {}]

def draw_arc(p1, p2, large=False, arc_type='', style=None):
    return ['arc', p1, p2, int(large), arc_type, style or {}]

def draw_circle(center, radius, circle_type='', style=None):
    return ['circle', center, radius, circle_type, style or {}]

def draw_ellipse(center, rx, ry, ellipse_type='', style=None):
    return ['ellipse', center, rx, ry, ellipse_type, style or {}]

def draw_triangle(box, tip, triangle_type='', style=None):
    """Returns array with all the information needed to draw a triangle
    in front end. 
    :box: bounds triangle
    :tip: defines tip orientation 'top', 'left' or 'right'.
    :triangle_type: will label triangle in front end (class)
    """
    return ['triangle', box, tip, triangle_type, style or {}]

def draw_text(box, text, text_type='', style=None):
    return ['text', box, text, text_type, style or {}]

def draw_rect(box, rect_type, style=None):
    return ['rect', box, rect_type, style or {}]

def draw_rhombus(box, rhombus_type='', style=None):
    """ Create rhombus provided a bounding box """
    # Rotate the box to provide a rhombus (points) to drawing engine
    x, y, dx, dy = box
    rhombus = ((x + dx / 2, y),      # top
               (x + dx, y + dy / 2), # right
               (x + dx / 2, y + dy), # bottom
               (x, y + dy / 2))      # left
    return ['rhombus', rhombus, rhombus_type, style or {}]


def draw_array(box, a):
    return ['array', box, a]


# Box-related functions.

def make_box(point, size):
    x, y = point
    dx, dy = size
    return Box(x, y, dx, dy)

def get_xs(box):
    x, _, dx, _ = box
    return x, x + dx

def get_ys(box):
    _, y, _, dy = box
    return y, y + dy


def get_rect(element, zoom=(0, 0)):
    "Return the rectangle that contains the given graphic element"
    eid = element[0]
    if eid in ['nodebox', 'rect', 'array', 'text', 'triangle']:
        return element[1]
    elif eid == 'outline':
        x, y, dx_min, dx_max, dy = element[1]
        return Box(x, y, dx_max, dy)
    elif eid == 'rhombus':
        points = element[1]
        x = points[3][0]
        y = points[0][1]
        dx = points[2][0] - x
        dy = points[2][0] - y
        return  Box(x, y, dx, dy)
    elif eid in ['line', 'arc']:  # not a great approximation for an arc...
        (x1, y1), (x2, y2) = element[1], element[2]
        return Box(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    elif eid == 'circle':
        (x, y), r = element[1], element[2]
        zx, zy = zoom
        rx, ry = r / zx, r / zy
        return Box(x - rx, y - ry, 2 * rx, 2 * ry)
    elif eid == 'ellipse':
        (x, y), rx, ry = element[1:4]
        zx, zy = zoom
        rx, ry = rx / zx, ry / zy
        rx, ry = 0, 0
        return Box(x - rx, y - ry, 2 * rx, 2 * ry)
    else:
        raise ValueError(f'unrecognized element: {element!r}')


def get_asec(element, zoom=(0, 0)):
    "Return the annular sector that contains the given graphic element"
    eid = element[0]
    if eid in ['nodebox', 'rect', 'array', 'text', 'triangle']:
        return element[1]
    elif eid == 'outline':
        r, a, dr_min, dr_max, da = element[1]
        return Box(r, a, dr_max, da)
    elif eid == 'rhombus':
        points = element[1]
        r = points[3][0]
        a = points[0][1]
        dr = points[2][0] - r
        da = points[2][0] - a
        return Box(r, a, dr , da)
    elif eid in ['line', 'arc']:
        (x1, y1), (x2, y2) = element[1], element[2]
        rect = Box(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        return circumasec(rect)
    elif eid == 'circle':
        z = zoom[0]
        (x, y), r = cartesian(element[1]), element[2] / z
        rect = Box(x - r, y - r, 2 * r, 2 * r)
        return circumasec(rect)
    elif eid == 'ellipse':
        x, y = cartesian(element[1])
        zx, zy = zoom
        rx, ry = element[2] / zx, element[3] / zy
        rect = Box(x - rx, y - ry, 2 * rx, 2 * ry)
        return circumasec(rect)
    else:
        raise ValueError(f'unrecognized element: {element!r}')


def drawn_size(elements, get_box):
    "Return the size of a box containing all the elements"
    # The type of size will depend on the kind of boxes that are returned by
    # get_box() for the elements. It is width and height for boxes that are
    # rectangles, and dr and da for boxes that are annular sectors.

    if not elements:
        return Size(0, 0)

    x, y, dx, dy = get_box(elements[0])
    x_min, x_max = x, x + dx
    y_min, y_max = y, y + dy

    for element in elements[1:]:
        x, y, dx, dy = get_box(element)
        x_min, x_max = min(x_min, x), max(x_max, x + dx)
        y_min, y_max = min(y_min, y), max(y_max, y + dy)

    return Size(x_max - x_min, y_max - y_min)


def intersects_box(b1, b2):
    "Return True if the boxes b1 and b2 (of the same kind) intersect"
    return (intersects_segment(get_xs(b1), get_xs(b2)) and
            intersects_segment(get_ys(b1), get_ys(b2)))


def intersects_segment(s1, s2):
    "Return True if the segments s1 and s2 intersect"
    s1min, s1max = s1
    s2min, s2max = s2
    return s1min <= s2max and s2min <= s1max


def intersects_angles(rect, asec):
    "Return True if any part of rect is contained within the angles of the asec"
    return any(intersects_segment(get_ys(circumasec(r)), get_ys(asec))
                   for r in split_thru_negative_xaxis(rect))
    # We divide rect in two if it passes thru the -x axis, because then its
    # circumbscribing asec goes from -pi to +pi and (wrongly) always intersects.


def split_thru_negative_xaxis(rect):
    "Return a list of rectangles resulting from cutting the given one"
    x, y, dx, dy = rect
    if x >= 0 or y > 0 or y + dy < 0:
        return [rect]
    else:
        EPSILON = 1e-8
        return [Box(x, y, dx, -y-EPSILON), Box(x, EPSILON, dx, dy + y)]


def stack(sbox, box):
    "Return the sbox resulting from stacking the given sbox and box"
    if not sbox:
        x, y, dx, dy = box
        return SBox(x, y, dx, dx, dy)
    else:
        x, y, dx_min, dx_max, dy = sbox
        _, _, dx_box, dy_box = box
        return SBox(x, y, min(dx_min, dx_box), max(dx_max, dx_box), dy + dy_box)


def circumrect(asec):
    "Return the rectangle that circumscribes the given annular sector"
    if asec is None:
        return None

    rmin, amin, dr, da = asec
    rmax, amax = rmin + dr, amin + da

    amin, amax = clip_angles(amin, amax)

    points = [(rmin, amin), (rmin, amax), (rmax, amin), (rmax, amax)]
    xs = [r * cos(a) for r,a in points]
    ys = [r * sin(a) for r,a in points]
    xmin, ymin = min(xs), min(ys)
    xmax, ymax = max(xs), max(ys)

    if amin < -pi/2 < amax:  # asec traverses the -y axis
        ymin = -rmax
    if amin < 0 < amax:  # asec traverses the +x axis
        xmax = rmax
    if amin < pi/2 < amax:  # asec traverses the +y axis
        ymax = rmax
    # NOTE: the annular sectors we consider never traverse the -x axis.

    return Box(xmin, ymin, xmax - xmin, ymax - ymin)


def circumasec(rect):
    "Return the annular sector that circumscribes the given rectangle"
    if rect is None:
        return None
    x, y, dx, dy = rect
    points = [(x, y), (x, y+dy), (x+dx, y), (x+dx, y+dy)]
    radius2 = [x*x + y*y for x,y in points]
    if x <= 0 and x+dx >= 0 and y <= 0 and y+dy >= 0:
        return Box(0, -pi, sqrt(max(radius2)), 2*pi)
    else:
        angles = [atan2(y, x) for x,y in points]
        rmin, amin = sqrt(min(radius2)), min(angles)
        return Box(rmin, amin, sqrt(max(radius2)) - rmin, max(angles) - amin)
