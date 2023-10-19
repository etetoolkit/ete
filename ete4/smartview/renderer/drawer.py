"""
Classes and functions for drawing a tree.
"""

from math import sin, cos, pi, sqrt, atan2
from collections import namedtuple, OrderedDict, defaultdict, deque
import random

from time import time

from ete4.core import operations as ops
from .. import TreeStyle
from .face_positions import FACE_POSITIONS, make_faces
from . import draw_helpers as dh
Box = dh.Box  # shortcut, because we use it a lot

Size = namedtuple('Size', 'dx dy')  # size of a 2D shape (sizes are always >= 0)
TreeActive = namedtuple('TreeActive', 'nodes clades')
Active = namedtuple('Active', 'results parents')

def get_empty_active():
    nodes = Active(set(), defaultdict(lambda: 0))
    clades = Active(set(), defaultdict(lambda: 0))
    return TreeActive(nodes, clades)


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

def safe_string(prop):
    if type(prop) in (int, float, str):
        return prop
    try:
        return str(prop)
    except:
        return ""


class Drawer:
    "Base class (needs subclassing with extra functions to draw)"

    COLLAPSE_SIZE = 6  # anything that has less pixels will be outlined

    MIN_SIZE = 1  # anything that has less pixels will not be drawn

    TYPE = 'base'  # can be 'rect' or 'circ' for working drawers

    NPANELS = 1 # number of drawing panels (including the aligned ones)

    def __init__(self, tree, viewport=None, panel=0, zoom=(1, 1),
                 limits=None, collapsed_ids=None,
                 active=None, selected=None, searches=None,
                 layouts=None, tree_style=None,
                 include_props=None, exclude_props=None):
        self.tree = tree
        self.viewport = Box(*viewport) if viewport else None
        self.panel = panel
        self.zoom = zoom
        self.xmin, self.xmax, self.ymin, self.ymax = limits or (0, 0, 0, 0)
        self.collapsed_ids = collapsed_ids or set()  # manually collapsed
        self.active = active or get_empty_active()  # looks like (results, parents)
        self.selected = selected or {}  # looks like {node_id: (node, parents)}
        self.searches = searches or {}  # looks like {text: (results, parents)}
        self.layouts = layouts or []
        self.include_props = include_props
        self.exclude_props = exclude_props
        self.tree_style = tree_style
        if not self.tree_style:
            self.tree_style = TreeStyle()

    def draw(self):
        "Yield graphic elements to draw the tree"
        self.outline = None  # box surrounding the current collapsed nodes
        self.collapsed = []  # nodes that are curretly collapsed together
        self.nodeboxes = []  # boxes surrounding all nodes and collapsed boxes
        self.node_dxs = [[]]  # lists of nodes dx (to find the max)
        self.bdy_dys = [[]]  # lists of branch dys and total dys

        if self.panel == 0:
            self.tree_style.aligned_grid_dxs = defaultdict(lambda: 0)

        if self.panel in (2, 3):
            yield from self.draw_aligned_headers()

        if self.panel == -1:
            yield from self.tree_style.get_legend()
        else:
            point = self.xmin, self.ymin
            for it in ops.walk(self.tree):
                graphics = []
                if it.first_visit:
                    point = self.on_first_visit(point, it, graphics)
                else:
                    point = self.on_last_visit(point, it, graphics)
                yield from graphics

            if self.outline:
                yield from self.get_outline()  # send last surrounding outline

            if self.panel == 0:
                max_dx = max([box[1].dx for box in self.nodeboxes] + [0])
                self.tree_style.aligned_grid_dxs[-1] = max_dx

                # To draw in preorder the boxes we found in postorder.
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

        if not it.node.sm_style['draw_descendants']:
            # Skip descendants => in collapsed_ids
            self.collapsed_ids.add(it.node_id)

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
        if it.node.is_leaf:
            return self.on_last_visit((x + dx, y + dy), it, graphics)
        else:
            self.node_dxs.append([])
            return x + dx, y

    def on_last_visit(self, point, it, graphics):
        "Update list of graphics to draw and return new position"

        # Searches
        searched_by = set( text for text,(results,_) in self.searches.items()
                if it.node in results )
        # Selection
        selected_by = [ text for text,(results,_) in self.selected.items()
                if it.node in results ]
        active_clade = [ "active_clades" ] if it.node in self.active.clades.results else []
        # Only if node is collapsed
        selected_children = []
        active_children = TreeActive(0, 0)
        if self.outline:
            if all(child in self.collapsed for child in it.node.children):
                searched_by.update( text for text,(results,parents) in self.searches.items()
                        if any(node in results or node in parents.keys() for node in self.collapsed) )
                active_children = self.get_active_children()
                selected_children = self.get_selected_children()

            graphics += self.get_outline()

        x_after, y_after = point
        dx, dy = self.content_size(it.node)
        x_before, y_before = x_after - dx, y_after - dy

        content_graphics = list(self.draw_content(it.node, (x_before, y_before),
            active_children, selected_children))
        graphics += content_graphics

        ndx = (drawn_size(content_graphics, self.get_box).dx if it.node.is_leaf
               else (dx + max(self.node_dxs.pop() or [0])))
        self.node_dxs[-1].append(ndx)

        box = Box(x_before, y_before, ndx, dy)
        self.nodeboxes += self.draw_nodebox(it.node, it.node_id, box,
                list(searched_by) + selected_by + active_clade,
                { 'fill': it.node.sm_style.get('bgcolor') })

        return x_before, y_after;

    def draw_content(self, node, point, active_children=TreeActive(0, 0), selected_children=[]):
        "Yield the node content's graphic elements"
        x, y = point
        dx, dy = self.content_size(node)

        # Find branch dy of first child (bdy0), last (bdy1), and self (bdy).
        bdy_dys = self.bdy_dys.pop()  # bdy_dys[i] == (bdy, dy)
        bdy0 = bdy1 = dy / 2  # branch dys of the first and last children
        if bdy_dys:
            bdy0 = bdy_dys[0][0]
            bdy1 = sum(bdy_dy[1] for bdy_dy in bdy_dys[:-1]) + bdy_dys[-1][0]
        bdy = (bdy0 + bdy1) / 2  # this node's branch dy
        self.bdy_dys[-1].append( (bdy, dy) )

        # Collapsed nodes will be drawn from self.draw_collapsed()
        if not node.is_collapsed or node.is_leaf:
            bdy0_, bdy1_ = (0, dy) if node.is_leaf else (bdy0, bdy1)
            yield from self.draw_node(node, point, dx, bdy, bdy0_, bdy1_,
                    active_children, selected_children)

        # Draw the branch line ("lengthline") and a line spanning all children.
        if self.panel == 0:
            node_style = node.sm_style
            if dx > 0:
                parent_of = set(text for text,(_,parents) in self.searches.items()
                                if node in parents.keys())
                parent_of.update(text for text,(_,parents) in self.selected.items()
                                if node in parents.keys())
                hz_line_style = {
                        'type': node_style['hz_line_type'],
                        'stroke-width': node_style['hz_line_width'],
                        'stroke': node_style['hz_line_color'],
                }
                yield from self.draw_lengthline((x, y + bdy), (x + dx, y + bdy),
                                list(parent_of), style=hz_line_style)

            if bdy0 != bdy1:
                vt_line_style = {
                        'type': node_style['vt_line_type'],
                        'stroke-width': node_style['vt_line_width'],
                        'stroke': node_style['vt_line_color'],
                }
                yield from self.draw_childrenline((x + dx, y + bdy0),
                                                  (x + dx, y + bdy1),
                                                  style=vt_line_style)

            active_node = "selected_results_active_nodes"\
                if node in self.active.nodes.results else ""
            nodedot_style = {
                    'shape': node_style['shape'],
                    'size': node_style['size'],
                    'fill': node_style['fgcolor'],
                    'opacity': node_style['fgopacity'],
            }

            yield from self.draw_nodedot((x + dx, y + bdy),
                    dy * self.zoom[1], active_node, nodedot_style)

    def draw_aligned_headers(self):
        # Draw aligned panel headers
        def it_fits(box, pos):
            _, _, dx, dy = box
            return dx * zx > self.MIN_SIZE and dy * zy > self.MIN_SIZE

        def draw_face(face, pos, row, n_row, n_col, dx_before, dy_before):
            if face.get_content():
                box = face.compute_bounding_box(self, (0, 0), size,
                            None, None, None, None, None,
                            pos, row, n_row, n_col,
                            dx_before, dy_before)
                if (it_fits(box, pos) and face.fits()) or face.always_drawn:
                    yield from face.draw(self)

        def draw_faces_at_pos(faces, pos, iteration):
            n_col = max(faces.keys(), default = -1) + 1

            dx_before = 0
            for col, face_list in sorted(faces.items()):
                if col > 0:
                    # Avoid changing-size error when zooming very quickly
                    dxs = list(faces._grid_dxs.items())
                    dx_before = sum(v for k, v in dxs if 0 <= k < col)
                dx_max = 0
                dy_before = 0
                n_row = len(face_list)
                for row, face in enumerate(face_list):
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
                dx_grid = faces._grid_dxs.get(col, 0)
                if iteration == 0:
                    # Compute aligned grid
                    dx_grid = max(dx_grid, dx_max)
                    faces._grid_dxs[col] = dx_grid
                else:
                    dx_before += dx_grid

        size = ( self.viewport.dx, self.viewport.dy )
        _, zy, zx = self.zoom
        graphics = []

        if self.panel == 2:
            deque(draw_faces_at_pos(self.tree_style.aligned_panel_header,
                    "aligned_bottom", 0))
            graphics += draw_faces_at_pos(self.tree_style.aligned_panel_header,
                    "aligned_bottom", 1)

        if self.panel == 3:
            deque(draw_faces_at_pos(self.tree_style.aligned_panel_footer,
                    "aligned_top", 0))
            graphics += draw_faces_at_pos(self.tree_style.aligned_panel_footer,
                    "aligned_top", 1)

        return graphics

    def get_outline(self):
        """Yield the outline representation."""
        graphics = []  # will contain the graphic elements to draw

        node0 = self.collapsed[0]
        uncollapse = len(self.collapsed) == 1 and node0.is_leaf

        x, y, _, _ = self.outline
        collapsed_node = self.get_collapsed_node()

        searched_by = [text for text,(results,parents) in self.searches.items()
                       if collapsed_node in results
                       or any(node in results or node in parents
                              for node in self.collapsed)]
        selected_by = [text for text,(results,parents) in self.selected.items()
                       if collapsed_node in results]
        active_clade = [ "active_clades" ] if collapsed_node in self.active.clades.results else []
        active_children = self.get_active_children()
        selected_children = self.get_selected_children()

        if uncollapse:
            self.bdy_dys.append([])
            graphics += self.draw_content(node0, (x, y))
        else:
            self.bdy_dys[-1].append( (self.outline.dy / 2, self.outline.dy) )
            graphics += self.draw_collapsed(collapsed_node, active_children, selected_children)

        is_manually_collapsed = collapsed_node in self.collapsed
        is_small = self.is_small(make_box((x, y),
                                          self.node_size(collapsed_node)))

        self.collapsed = []

        ndx = max(self.outline.dx, drawn_size(graphics, self.get_box).dx)
        self.node_dxs[-1].append(ndx)

        # Draw collapsed node nodebox when necessary
        if is_manually_collapsed or is_small or dist(collapsed_node) == 0:
            name = collapsed_node.name
            properties = self.get_popup_props(collapsed_node)

            node_id = tuple(collapsed_node.id) if is_manually_collapsed else []
            box = dh.draw_nodebox(self.flush_outline(ndx), name,
                    properties, node_id, searched_by + selected_by + active_clade,
                    { 'fill': collapsed_node.sm_style.get('bgcolor') })
            self.nodeboxes.append(box)
        else:
            self.flush_outline()

        yield from graphics

    def flush_outline(self, minimum_dx=0):
        "Return box outlining the collapsed nodes and reset the current outline"
        x, y, dx, dy = self.outline
        self.outline = None
        return Box(x, y, max(dx, minimum_dx), dy)

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
            from ... import Tree # avoid circular import
            node = Tree()

        node.is_collapsed = True
        node.is_initialized = False
        node._children = self.collapsed  # add avoiding parent override
        _, _, _, dy = self.outline
        node.dist = 0
        node.size = Size(0, dy)

        return node

    def is_fully_collapsed(self, collapsed_node):
        """Returns true if collapsed_node is utterly collapsed,
        i.e. has no branch width"""
        x, y, _, _ = self.outline
        is_manually_collapsed = collapsed_node in self.collapsed
        box_node = make_box((x, y), self.node_size(collapsed_node))

        return is_manually_collapsed or self.is_small(box_node)

    def get_active_children(self):
        nodes = sum(1 for node in self.collapsed if node in self.active.nodes.results)
        nodes += sum(self.active.nodes.parents.get(node, 0) for node in self.collapsed)
        clades = sum(len(node) for node in self.collapsed if node in self.active.clades.results)
        clades += sum(self.active.clades.parents.get(node, 0) for node in self.collapsed)
        return TreeActive(nodes, clades)

    def get_selected_children(self):
        selected_children = []
        for text,(results, parents) in self.selected.items():
            hits = sum(1 for node in self.collapsed if node in results)
            hits += sum(parents.get(node, 0) for node in self.collapsed)
            if hits:
                selected_children.append((text, hits))
        return selected_children

    def get_popup_props(self, node):
        """Return dictionary of web-safe node properties (to use in a popup)."""
        include_props = (self.include_props if self.include_props is not None
                         else node.props)

        return {k: safe_string(node.props[k]) for k in include_props
                    if k in node.props and k not in (self.exclude_props or [])}
        # NOTE: We do it this way so the properties appear in the
        # order given in include_props.


    # These are the 2 functions that the user overloads to choose what to draw
    # when representing a node and a group of collapsed nodes:

    def draw_node(self, node, point, bdx, bdy, bdy0, bdy1, active_children=TreeActive(0, 0), selected_children=[]):
        "Yield graphic elements to draw the contents of the node"
        # bdx: branch dx (width)
        # bdy: branch dy (height)
        # bdy0: fist child branch dy (height)
        # bdy1: last child branch dy (height)
        # selected_children: list of selected nodes (under this node if collapsed or
        #              this node if not collapsed) (to be tagged in front end)
        yield from []  # only drawn if the node's content is visible

    def draw_collapsed(self, collapsed_node, active_children=TreeActive(0, 0), selected_children=[]):
        "Yield graphic elements to draw the list of nodes in self.collapsed"
        # selected_children: list of selected nodes under this node
        yield from []  # they are always drawn (only visible nodes can collapse)
        # Uses self.collapsed and self.outline to extract and place info.


class DrawerRect(Drawer):
    "Minimal functional drawer for a rectangular representation"

    TYPE = 'rect'

    def in_viewport(self, box, pos=None):

        if not self.viewport:
            return True

        if self.panel == 0 and pos != 'aligned':
            return dh.intersects_box(self.viewport, box)
        else:
            return dh.intersects_segment(dh.get_ys(self.viewport), dh.get_ys(box))

    def node_size(self, node):
        "Return the size of a node (its content and its children)"
        return Size(node.size[0], node.size[1])

    def content_size(self, node):
        "Return the size of the node's content"
        return Size(dist(node), node.size[1])

    def is_small(self, box):
        zx, zy, _ = self.zoom
        return box.dy * zy < self.COLLAPSE_SIZE

    def get_box(self, element):
        zx, zy, za = self.zoom
        if self.panel == 0:
            zoom = (zx, zy)
        else:
            zoom = (za, zy)
        return get_rect(element, zoom)

    def draw_lengthline(self, p1, p2, parent_of, style):
        "Yield a line representing a length"
        line = dh.draw_line(p1, p2, 'lengthline', parent_of, style)
        if not self.viewport or dh.intersects_box(self.viewport, get_rect(line)):
            yield line

    def draw_childrenline(self, p1, p2, style):
        "Yield a line spanning children that starts at p1 and ends at p2"
        line = dh.draw_line(p1, p2, 'childrenline', style=style)
        if not self.viewport or dh.intersects_box(self.viewport, get_rect(line)):
            yield line

    def draw_nodedot(self, center, max_size, active_node, style):
        "Yield circle or square on node based on node.sm_style"
        size = min(max_size, style['size'])

        if active_node:
            size = max(min(max_size, 4), size)

        if size > 0:
            fill = style['fill']
            nodedot_style={'fill':fill, 'opacity': style['opacity']}
            if style['shape'] == 'circle':
                yield dh.draw_circle(center, radius=size,
                        circle_type='nodedot ' + active_node, style=nodedot_style)
            elif style['shape'] == 'square':
                x, y = center
                zx, zy, _ = self.zoom
                dx, dy = 2 * size / zx, 2 * size / zy
                box = (x - dx/2, y - dy/2, dx, dy)
                yield dh.draw_rect(box, rect_type='nodedot ' + active_node, style=nodedot_style)

    def draw_nodebox(self, node, node_id, box, searched_by, style=None):
        yield dh.draw_nodebox(box, node.name, self.get_popup_props(node),
                node_id, searched_by, style)

    def draw_collapsed(self, collapsed_node, active_children=TreeActive(0, 0), selected_children=[]):
        # Draw line to farthest leaf under collapsed node
        x, y, dx, dy = self.outline

        p1 = (x, y + dy / 2)
        p2 = (x + dx, y + dy / 2)

        yield dh.draw_line(p1, p2, 'lengthline')


class DrawerCirc(Drawer):
    "Minimal functional drawer for a circular representation"

    TYPE = 'circ'

    def __init__(self, tree, viewport=None, panel=0, zoom=(1, 1),
                 limits=None, collapsed_ids=None, active=None,
                 selected=None, searches=None,
                 layouts=None, tree_style=None,
                 include_props=None, exclude_props=None):
        super().__init__(tree, viewport, panel, zoom,
                         limits, collapsed_ids, active, selected, searches,
                         layouts, tree_style,
                         include_props=include_props,
                         exclude_props=exclude_props)

        assert self.zoom[0] == self.zoom[1], 'zoom must be equal in x and y'

        if not limits:
            self.ymin, self.ymax = -pi, pi

        self.dy2da = (self.ymax - self.ymin) / self.tree.size[1]

    def in_viewport(self, box, pos=None):
        if not self.viewport:
            return dh.intersects_segment((-pi, +pi), dh.get_ys(box))

        if self.panel == 0 and pos != 'aligned':
            return (dh.intersects_box(self.viewport, dh.circumrect(box)) and
                    dh.intersects_segment((-pi, +pi), dh.get_ys(box)))
        else:
            return dh.intersects_angles(self.viewport, box)

    def flush_outline(self, minimum_dr=0):
        "Return box outlining the collapsed nodes"
        r, a, dr, da = super().flush_outline(minimum_dr)
        a1, a2 = dh.clip_angles(a, a + da)
        return Box(r, a1, dr, a2 - a1)

    def node_size(self, node):
        "Return the size of a node (its content and its children)"
        return Size(node.size[0], node.size[1] * self.dy2da)

    def content_size(self, node):
        "Return the size of the node's content"
        return Size(dist(node), node.size[1] * self.dy2da)

    def is_small(self, box):
        z = self.zoom[0]  # zx == zy in this drawer
        r, a, dr, da = box
        return (r + dr) * da * z < self.COLLAPSE_SIZE

    def get_box(self, element):
        return get_asec(element, self.zoom)

    def draw_lengthline(self, p1, p2, parent_of, style):
        "Yield a line representing a length"
        if -pi <= p1[1] < pi:  # NOTE: the angles p1[1] and p2[1] are equal
            yield dh.draw_line(dh.cartesian(p1), dh.cartesian(p2),
                            'lengthline', parent_of, style)

    def draw_childrenline(self, p1, p2, style):
        "Yield an arc spanning children that starts at p1 and ends at p2"
        (r1, a1), (r2, a2) = p1, p2
        a1, a2 = dh.clip_angles(a1, a2)
        if a1 < a2:
            is_large = a2 - a1 > pi
            yield dh.draw_arc(dh.cartesian((r1, a1)), dh.cartesian((r2, a2)),
                             is_large, 'childrenline', style=style)

    def draw_nodedot(self, center, max_size, active_node, style):
        r, a = center
        size = min(max_size, style['size'])

        if active_node:
            size = max(min(max_size, 4), size)

        if -pi < a < pi and size > 0:
            fill = style['fill']
            nodedot_style={'fill':fill, 'opacity': style['opacity']}
            if style['shape'] == 'circle':
                yield dh.draw_circle(center, radius=size,
                          circle_type='nodedot ' + active_node, style=nodedot_style)
            elif style['shape'] == 'square':
                z = self.zoom[0] # same zoom in x and y
                dr, da = 2 * size / z, 2 * size / (z * r)
                box = Box(r - dr / 2, a - da / 2, dr, da)
                yield dh.draw_rect(box, rect_type='nodedot ' + active_node, style=nodedot_style)

    def draw_nodebox(self, node, node_id, box, searched_by, style=None):
        r, a, dr, da = box
        a1, a2 = dh.clip_angles(a, a + da)
        if a1 < a2:
            yield dh.draw_nodebox(Box(r, a1, dr, a2 - a1),
                       node.name, self.get_popup_props(node), node_id, searched_by, style)

    def draw_collapsed(self, collapsed_node, active_children=TreeActive(0, 0), selected_children=[]):
        # Draw line to farthest leaf under collapsed node
        r, a, dr, da = self.outline

        p1 = (r, a + da / 2)
        p2 = (r + dr, a + da / 2)

        yield dh.draw_line(dh.cartesian(p1), dh.cartesian(p2), 'lengthline')




# The actual drawers.

class DrawerRectFaces(DrawerRect):

    def draw_node(self, node, point, bdx, bdy, bdy0, bdy1,
                  active_children=TreeActive(0, 0), selected_children=[]):
        size = self.content_size(node)

        # Space available for branch-right Face position
        dx_to_closest_child = (dist(node) if node.is_leaf else
                               min(dist(child) for child in node.children))
        zx, zy, za = self.zoom

        def it_fits(box, pos):
            z = za if pos == 'aligned' else zx
            _, _, dx, dy = box
            return (dx * z > self.MIN_SIZE and
                    dy * zy > self.MIN_SIZE and
                    self.in_viewport(box, pos))

        def draw_face(face, pos, row, n_row, n_col, dx_before, dy_before):
            if face.get_content():
                box = face.compute_bounding_box(self, point, size,
                            dx_to_closest_child,
                            bdx, bdy, bdy0, bdy1,
                            pos, row, n_row, n_col,
                            dx_before, dy_before)
                if (it_fits(box, pos) and face.fits()) or face.always_drawn:
                    yield from face.draw(self)

        def draw_faces_at_pos(node, pos):
            if node.is_collapsed and not node.is_leaf:
                node_faces = node.collapsed_faces
            else:
                node_faces = node.faces

            faces = dict(getattr(node_faces, pos, {}))
            n_col = max(faces.keys(), default=-1) + 1

            z = za if pos == 'aligned' else zx

            # Add SelectedFace for each search this node is a result of
            if pos == self.tree_style.selected_face_pos and len(selected_children):
                faces[n_col] = [ self.tree_style.selected_face(s, text=v) for s,v in selected_children ]
                n_col += 1

            if pos == self.tree_style.active_face_pos:
                active_faces = []
                nodes = active_children.nodes
                if nodes > 0:
                    active_faces.append(self.tree_style.active_face("active_nodes", text=nodes))
                clades = active_children.clades
                if clades > 0:
                    active_faces.append(self.tree_style.active_face("active_clades", text=clades))
                if active_faces:
                    faces[n_col] = active_faces
                    n_col += 1

            dx_before = 0
            for col, face_list in sorted(faces.items()):
                if pos == 'aligned'\
                            and self.tree_style.aligned_grid\
                            and self.NPANELS > 1\
                            and self.panel > 0\
                            and col > 0:
                    # Avoid changing-size error when zooming very quickly
                    dxs = list(self.tree_style.aligned_grid_dxs.items())
                    dx_before = sum(v for k, v in dxs if k < col and k >= 0)

                dx_max = 0
                dy_before = 0
                n_row = len(face_list)

                for row, face in enumerate(face_list):
                    face.node = node

                    drawn_face = list(draw_face(face, pos, row, n_row, n_col,
                            dx_before, dy_before))
                    if drawn_face:
                        _, _, dx, dy = face.get_box()
                        hz_padding = 2 * face.padding_x / z
                        vt_padding = 2 * face.padding_y / zy

                        # NOTE: This is a hack to align nicely the headers in LayoutBarPlot.
                        hfaces = self.tree_style._aligned_panel_header.get(col)  # header faces

                        if col > 0 and hfaces:
                            dx_max = max((hface.width for hface in hfaces if hface.width), default=0) + hz_padding # it's possible width is none

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
            node.faces = make_faces()
            node.collapsed_faces = make_faces()
            for layout in self.layouts:
                layout.set_node_style(node)

        # Render Faces in different panels
        if self.NPANELS > 1:
            if self.panel == 0:
                for pos in FACE_POSITIONS[:3]:
                    yield from draw_faces_at_pos(node, pos)
                # Only run function to compute aligned grid
                if self.tree_style.aligned_grid:
                    deque(draw_faces_at_pos(node, 'aligned'))
            elif self.panel == 1:
                yield from draw_faces_at_pos(node, 'aligned')
        else:
            for pos in FACE_POSITIONS:
                yield from draw_faces_at_pos(node, pos)

    def draw_collapsed(self, collapsed_node, active_children=TreeActive(0, 0), selected_children=[]):
        x, y, dx, dy = self.outline

        if self.is_fully_collapsed(collapsed_node):
            bdx = 0
        else:
            x = x - dist(collapsed_node)
            bdx = dist(collapsed_node)

        x = x if self.panel == 0 else self.xmin

        yield from self.draw_node(collapsed_node,
                (x, y), bdx, dy/2, 0, dy, active_children, selected_children)


class DrawerCircFaces(DrawerCirc):

    def draw_node(self, node, point, bdr, bda, bda0, bda1, active_children=TreeActive(0, 0), selected_children=[]):
        size = self.content_size(node)
        # Space available for branch-right Face position
        dr_to_closest_child = min(dist(child) for child in node.children)\
                if not (node.is_leaf or node.is_collapsed) else dist(node)
        z = self.zoom[0]  # zx == zy

        def it_fits(box, pos):
            r, a, dr, da = box
            return r > 0 \
                    and dr * z > self.MIN_SIZE\
                    and (r + dr) * da * z > self.MIN_SIZE\
                    and self.in_viewport(box, pos)

        def draw_face(face, pos, row, n_row, n_col, dr_before, da_before):
            if face.get_content():
                box = face.compute_bounding_box(self, point, size,
                        dr_to_closest_child,
                        bdr, bda, bda0, bda1,
                        pos, row, n_row, n_col,
                        dr_before, da_before)
                if (it_fits(box, pos) and face.fits()) or face.always_drawn:
                    yield from face.draw(self)

        def draw_faces_at_pos(node, pos):
            if node.is_collapsed and not node.is_leaf:
                node_faces = node.collapsed_faces
            else:
                node_faces = node.faces

            faces = dict(getattr(node_faces, pos, {}))
            n_col = len(faces.keys())

            # Add SelectedFace for each search this node is a result of
            if pos == self.tree_style.selected_face_pos and len(selected_children):
                faces[n_col] = [ self.tree_style.selected_face(s) for s in selected_children ]
                n_col += 1

            if pos == self.tree_style.active_face_pos:
                active_faces = []
                nodes = active_children.nodes
                if nodes > 0:
                    active_faces.append(self.tree_style.active_face("active_nodes", text=nodes))
                clades = active_children.clades
                if clades > 0:
                    active_faces.append(self.tree_style.active_face("active_clades", text=clades))
                if active_faces:
                    faces[n_col] = active_faces
                    n_col += 1

            # Avoid drawing faces very close to center
            if pos.startswith('branch-') and abs(point[0]) < 1e-5:
                n_col += 1
                dr_before = .7 * size[0] / n_col
            else:
                dr_before = 0

            for col, face_list in sorted(faces.items()):
                if pos == 'aligned'\
                            and self.tree_style.aligned_grid\
                            and self.NPANELS > 1:
                    # Avoid changing-size error when zooming very quickly
                    drs = list(self.tree_style.aligned_grid_dxs.items())
                    dr_before = sum(v for k, v in drs if k < col)
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
                        vt_padding = 2 * face.padding_y / (z * (r or 1e-10))
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

        if not node.is_initialized:
            node.is_initialized = True
            for layout in self.layouts:
                layout.set_node_style(node)

        # Render Faces in different panels
        if self.NPANELS > 1:
            if self.panel == 0:
                for pos in FACE_POSITIONS[:3]:
                    yield from draw_faces_at_pos(node, pos)
                # Only run function to compute aligned grid
                if self.tree_style.aligned_grid:
                    deque(draw_faces_at_pos(node, 'aligned'))
            elif self.panel == 1:
                yield from draw_faces_at_pos(node, 'aligned')
        else:
            for pos in FACE_POSITIONS:
                yield from draw_faces_at_pos(node, pos)

    def draw_collapsed(self, collapsed_node, active_children=TreeActive(0, 0), selected_children=[]):
        r, a, dr, da = self.outline

        if self.is_fully_collapsed(collapsed_node):
            bdr = 0
        else:
            r = r - dist(collapsed_node)
            bdr = dist(collapsed_node)

        r = r if self.panel == 0 else self.xmin

        yield from self.draw_node(collapsed_node,
                (r, a), bdr, da/2, 0, da, active_children, selected_children)


class DrawerAlignRectFaces(DrawerRectFaces):
    NPANELS = 4


class DrawerAlignCircFaces(DrawerCircFaces):
    NPANELS = 2


def get_drawers():
    return [ DrawerRect, DrawerCirc,
            DrawerRectFaces, DrawerCircFaces,
            DrawerAlignRectFaces, DrawerAlignCircFaces, ]


# Box-related functions.

def make_box(point, size):
    x, y = point
    dx, dy = size
    return Box(x, y, dx, dy)


def get_rect(element, zoom=(0, 0)):
    "Return the rectangle that contains the given graphic element"
    eid = element[0]  # elements are tuples with element-id in the 1st place

    if eid in ['nodebox', 'rect', 'array', 'text', 'triangle', 'html', 'img']:
        return element[1]
    elif eid == 'outline':
        x, y, dx, dy = element[1]
        return Box(x, y, dx, dy)
    elif eid.startswith('pixi-'):
        x, y, dx, dy = element[1]
        return Box(x, y, dx, dy)
    elif eid == 'rhombus':
        points = element[1]
        x = points[3][0]
        y = points[0][1]
        dx = points[2][0] - x
        dy = points[2][0] - y
        return  Box(x, y, dx, dy)
    elif eid == 'polygon':
        min_x = min(p[0] for p in element[1])
        max_x = max(p[0] for p in element[1])
        min_y = min(p[1] for p in element[1])
        max_y = max(p[1] for p in element[1])
        return Box(min_x, min_y, max_x - min_x, max_y - min_y)
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
    elif eid == 'slice':
        (x, y), r = element[1][0], element[1][1]
        zx, zy = zoom
        rx, ry = r / zx, r / zy
        return Box(x - rx, y - ry, 2 * rx, 2 * ry)
    else:
        raise ValueError(f'unrecognized element: {element!r}')


def get_asec(element, zoom=(0, 0)):
    "Return the annular sector that contains the given graphic element"
    eid = element[0]  # elements are tuples with element-id in the 1st place

    if eid in ['nodebox', 'rect', 'array', 'text', 'triangle', 'html', 'img']:
        return element[1]
    elif eid == 'outline':
        r, a, dr, da = element[1]
        return Box(r, a, dr, da)
    elif eid.startswith('pixi-'):
        x, y, dx, dy = element[1]
        return Box(x, y, dx, dy)
    elif eid == 'rhombus':
        points = element[1]
        r = points[3][0]
        a = points[0][1]
        dr = points[2][0] - r
        da = points[2][0] - a
        return Box(r, a, dr , da)
    elif eid == 'polygon':
        min_x = min(p[0] for p in element[1])
        max_x = max(p[0] for p in element[1])
        min_y = min(p[1] for p in element[1])
        max_y = max(p[1] for p in element[1])
        return Box(min_x, min_y, max_x - min_x, max_y - min_y)
    elif eid in ['line', 'arc']:
        (x1, y1), (x2, y2) = element[1], element[2]
        rect = Box(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        return dh.circumasec(rect)
    elif eid == 'circle':
        z = zoom[0]
        (x, y), r = dh.cartesian(element[1]), element[2] / z
        rect = Box(x - r, y - r, 2 * r, 2 * r)
        return dh.circumasec(rect)
    elif eid == 'ellipse':
        x, y = dh.cartesian(element[1])
        z = zoom[0]
        rx, ry = element[2] / z, element[3] / z
        rect = Box(x - rx, y - ry, 2 * rx, 2 * ry)
        return dh.circumasec(rect)
    elif eid == 'slice':
        z = zoom[0]
        (x, y), r = dh.cartesian(element[1][0]), element[1][1] / z
        rect = Box(x - r, y - r, 2 * r, 2 * r)
        return dh.circumasec(rect)
    else:
        raise ValueError(f'unrecognized element: {element!r}')


def drawn_size(elements, get_box, min_x=None):
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

    # Constrains x_min
    # Necessary for collapsed nodes with branch-top/bottom faces
    if min_x:
        x_min = max(x_min, min_x)

    return Size(x_max - x_min, y_max - y_min)


def dist(node):
    """Return the distance of a node, with default values if not set."""
    return float(node.props.get('dist', 0 if node.up is None else 1))


def stack(box1, box2):
    """Return the box resulting from stacking the given boxes."""
    if not box1:
        return box2
    else:
        x, y, dx1, dy1 = box1
        _, _, dx2, dy2 = box2
        return Box(x, y, max(dx1, dx2), dy1 + dy2)
