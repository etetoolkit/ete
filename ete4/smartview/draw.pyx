"""
Functions for drawing a tree.
"""

from collections import namedtuple
from utils import timeit 

Size = namedtuple('Size', ['w', 'h'])  # width and height
Rect = namedtuple('Rect', ['x', 'y', 'w', 'h'])  # top-left corner and size

# The convention for coordinates is:
#   x increases to the right, y increases to the bottom.
#
#  +-----> x
#  |
#  |
#  v y
#
# This is the one normally used in computer graphics, including HTML Canvas,
# SVGs, Qt, and PixiJS.
#
# For a rectangle:           w
#                     x,y +-----+          so x,y is its top-left corner
#                         |     | h        and x+w,y+h its bottom-right one
#                         +-----+

# Drawing.

class Drawer:
    MIN_HEIGHT = 6  # anything that has less pixels will be a rectangle

    def __init__(self, viewport=None, zoom=(1, 1)):
        self.viewport = viewport
        self.zoom = zoom
        self.outline_shape = None

    def in_viewport(self, rect):
        return intersects(self.viewport, rect)

    def update_outline(self, shape):
        "Update the current outline and yield a graphic shape if appropriate"
        if not self.outline_shape:
            self.outline_shape = shape
        else:
            stacked_shape = stack_vertical_rect(self.outline_shape, shape)  # TODO: shape
            if stacked_shape:
                self.outline_shape = stacked_shape
            else:
                yield draw_outlinerect(self.outline_shape)  # TODO: outlineshape
                self.outline_shape = shape

    # These are the functions that the user would supply to decide how to
    # represent a node.
    def draw_content_inline(self, node, point=(0, 0)):
        "Yield graphic elements to draw the inline contents of the node"
        yield from []

    def draw_content_float(self, node, point=(0, 0)):
        "Yield graphic elements to draw the floated contents of the node"
        yield from []

    def draw_content_align(self, node, point=(0, 0)):
        "Yield graphic elements to draw the aligned contents of the node"
        yield from []


class DrawerRect(Drawer):
    @timeit
    def draw(self, tree_img, point=(0, 0)):
        "Yield graphic elements to draw the tree"
        tree = tree_img.tree

        x, y = point

        visiting_nodes = [tree]  # root -> child2 -> child20 -> child201 (leaf)
        visited_childs = [0]     #   2  ->    0   ->    1    ->    0
        drawn = 0
        while visiting_nodes:
            node = visiting_nodes[-1]  # current node
            nch = visited_childs[-1]   # number of childs visited for this node
            w, h = content_size(node)

            if nch == 0:  # first time we visit this node
                elements, draw_childs = self.get_content(node, (x, y))
                drawn += 1
                yield from elements
                if draw_childs:
                    x += w  # move our pointer to the right of the content
                else:
                    y += h
                    pop(visiting_nodes, visited_childs)
                    continue

            if len(node.children) > nch:  # add next child to the list to visit
                visiting_nodes.append(node.children[nch])
                visited_childs.append(0)
            else:                       # go back to parent node
                x -= w  # move our pointer back
                if node.is_leaf():
                    y += h
                pop(visiting_nodes, visited_childs)

        if self.outline_shape:
            yield draw_outlinerect(self.outline_shape)
        print("drawn", drawn)
        
    def get_content(self, node, point):
        "Return list of content's graphic elements, and if childs need drawing"
        # Both the node's rect and its content's rect start at the given point.
        r_node = make_rect(point, node_size(node))

        if not self.in_viewport(r_node):               # skip
            return [], False

        if r_node.h * self.zoom[1] < self.MIN_HEIGHT:  # outline & skip
            return list(self.update_outline(r_node)), False

        x, y = point
        w, h = content_size(node)

        elements = []
        if self.in_viewport(Rect(x, y, w, h)):
            elements.append(draw_line((x, y + node.d1), (x + w, y + node.d1)))
            # horizontal line representing the node's length ------

            if len(node.children) > 1:
                c0, c1 = node.children[0], node.children[-1]
                elements.append(            # vertical line spanning childs  |
                    draw_line((x + w, y + c0.d1),                         #  |
                              (x + w, y + h - node_size(c1).h + c1.d1)))  #  |

            elements += self.draw_content_inline(node, (x, y))
            elements.append(draw_noderect(r_node, node.name, None)) #node.properties))

        elements += self.draw_content_float(node, (x, y))
        elements += self.draw_content_align(node, (x, y))

        return elements, True


def pop(visiting_nodes, visited_childs):
    visiting_nodes.pop()
    visited_childs.pop()
    if visited_childs:
        visited_childs[-1] += 1


class DrawerSimple(DrawerRect):
    "Skeleton of the tree"
    pass


class DrawerLeafNames(DrawerRect):
    "With names on leaf nodes"

    def draw_content_float(self, node, point=(0, 0)):
        if node.is_leaf():
            x, y = point
            w, h = content_size(node)
            zx, zy = self.zoom
            p_after_content = (x + w + 2 / zx, y + h / 1.5)
            yield draw_name(make_rect(p_after_content, Size(-1, h/2)), node.name)


class DrawerLengths(DrawerRect):
    "With labels on the lengths"

    def draw_content_inline(self, node, point=(0, 0)):
        if node.dist >= 0:
            x, y = point
            w, h = content_size(node)
            zx, zy = self.zoom
            text = '%.2g' % node.dist
            g_text = draw_label(Rect(x, y + node.d1, w, node.d1), text)

            if zy * h > 1:  # NOTE: we may want to change this, but it's tricky
                yield g_text
            else:
                yield draw_rect(get_rect(g_text))


class DrawerFull(DrawerLeafNames, DrawerLengths):
    "With names on leaf nodes and labels on the lengths"
    pass


class DrawerTooltips(DrawerFull):
    "With tooltips with the names and properties of all nodes"

    def draw_content_inline(self, node, point=(0, 0)):
        yield from super().draw_content_inline(node, point)

        if node.name:# or node.features:
            x, y = point
            w, h = content_size(node)
            zx, zy = self.zoom
            #ptext = ', '.join(f'{k}: {v}' for k in node.features)
            ptext = ', '.join([k for k in node.features])
            text = node.name + (' - ' if node.name and ptext else '')  + ptext
            fs = min(node.d1, 15/zy)
            yield draw_tooltip(Rect(x + w/2, y + node.d1, w/2, fs), text)


class DrawerAlign(DrawerFull):
    "With aligned content"

    def draw_content_align(self, node, point=(0, 0)):
        if node.is_leaf():
            x, y = point
            w, h = content_size(node)
            yield align(draw_name(Rect(0, y+h/1.5, 0, h/2), node.name))



def get_drawers():
    return [DrawerSimple, DrawerLengths, DrawerLeafNames, DrawerFull,
        DrawerTooltips, DrawerAlign]


# Basic drawing elements.

def draw_rect(r, name='', properties=None, rect_type=''):
    return ['r' + rect_type, r.x, r.y, r.w, r.h, name, properties or {}]

draw_noderect = lambda *args: draw_rect(*args, rect_type='n')
draw_outlinerect = lambda *args: draw_rect(*args, rect_type='o')

def draw_line(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ['l', x1, y1, x2, y2]

def draw_text(rect, text, text_type=''):
    x, y, w, h = rect
    return ['t' + text_type, x, y, w, h, text]

draw_name = lambda *args: draw_text(*args, text_type='n')
draw_label = lambda *args: draw_text(*args, text_type='l')
draw_tooltip = lambda *args: draw_text(*args, text_type='t')

def align(element):
    return ['a'] + element


# Size-related functions.

def node_size(node):
    "Return the size of a node (its content and its childs)"
    return Size(node.size[0], node.size[1])

def content_size(node):
    return Size(abs(node.dist), node.size[1])

def childs_size(node):
    return Size(node.size[0] - abs(node.dist), node.size[1])


# Rectangle-related functions.

def make_rect(p, size):
    x, y = p
    w, h = size
    return Rect(x, y, w, h)


def get_rect(element):
    "Return the rectangle that contains the given element"
    if type(element) == Rect:
        return element
    elif element[0] == 'r':
        _, x, y, w, h = element
        return Rect(x, y, w, h)
    elif element[0] == 'l':
        _, x1, y1, x2, y2 = element
        return Rect(min(x1, x2), min(y1, y2),
                    abs(x2 - x1), abs(y2 - y1))
    elif element[0].startswith('t'):
        _, x, y, w, h, text = element
        return Rect(x, y - h, w, h)
    else:
        raise ValueError('unrecognized element: ' + repr(element))


def intersects(r1, r2):
    "Return True if the rectangles r1 and r2 intersect"
    cdef double x1min, x1max, x2min, x2max

    if r1 is None or r2 is None:
        return True  # the rectangle "None" represents the full plane

    x1min, y1min, w1, h1 = r1
    x1max, y1max = x1min + w1, y1min + h1
    x2min, y2min, w2, h2 = r2
    x2max, y2max = x2min + w2, y2min + h2
    return ((x1min < x2max and x2min < x1max) and
            (y1min < y2max and y2min < y1max))


def stack_vertical_rect(r1, r2):
    "Return the rectangle containing rectangles r1 and r2 vertically stacked"
    if r1.x == r2.x and r1.y + r1.h == r2.y:
        return Rect(r1.x, r1.y, max(r1.w, r2.w), r1.h + r2.h)
    else:
        return None
