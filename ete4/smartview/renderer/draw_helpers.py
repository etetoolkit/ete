from collections import OrderedDict, namedtuple
from math import sin, cos, pi, sqrt, atan2

Box = namedtuple('Box', 'x y dx dy')  # corner and size of a 2D shape
SBox = namedtuple('SBox', 'x y dx_min dx_max dy')  # slanted box


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


def summary(nodes):
    "Return a list of names summarizing the given list of nodes"
    return list(OrderedDict((first_name(node), None) for node in nodes).keys())


def first_name(tree):
    "Return the name of the first node that has a name"
    return next((node.name for node in tree.traverse('preorder') if node.name), '')

# Basic drawing elements.

def draw_nodebox(box, name='', properties=None, 
        node_id=None, searched_by=None, style=None):
    properties = { k:v for k,v in (properties or {}).items() if not k.startswith('_') }
    return ['nodebox', box, name, 
            properties, node_id or [], 
            searched_by or [], style or {}]

def draw_outline(sbox, style=None):
    return ['outline', sbox, style or {}]

def draw_line(p1, p2, line_type='', parent_of=None, style=None):
    types = ['solid', 'dotted', 'dashed']
    style = style or {}
    if style.get('type'):
        style['stroke-dasharray'] = types[int(style['type'])]
    else:
        style['stroke-dasharray'] = types[0]

    return ['line', p1, p2, line_type, parent_of or [], style]

def draw_arc(p1, p2, large=False, arc_type='', style=None):
    return ['arc', p1, p2, int(large), arc_type, style or {}]

def draw_circle(center, radius, circle_type='', style=None):
    return ['circle', center, radius, circle_type, style or {}]

def draw_ellipse(center, rx, ry, ellipse_type='', style=None):
    return ['ellipse', center, rx, ry, ellipse_type, style or {}]

def draw_slice(center, r, a, da, slice_type='', style=None):
    return ['slice', (center, r, a, da), slice_type, style or {}]

def draw_triangle(box, tip, triangle_type='', style=None):
    """Returns array with all the information needed to draw a triangle
    in front end. 
    :box: bounds triangle
    :tip: defines tip orientation 'top', 'left' or 'right'.
    :triangle_type: will label triangle in front end (class)
    """
    return ['triangle', box, tip, triangle_type, style or {}]

def draw_text(box, text, text_type='', rotation=0, anchor=None, style=None):
    return ['text', box, text, text_type, rotation, anchor or "",  style or {}]

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

def draw_arrow(box, tip, orientation='right', arrow_type='', 
        style=None, props=None):
    """ Create arrow provided a bounding box """
    x, y, dx, dy = box

    if orientation == 'right':
        arrow = ((x, y),
                 (x + dx - tip, y),
                 (x + dx, y + dy / 2),
                 (x + dx - tip, y + dy),
                 (x, y + dy))
    elif orientation == 'left':
        arrow = ((x, y + dy / 2),
                 (x + tip, y),
                 (x + dx, y),
                 (x + dx, y + dy),
                 (x + tip, y + dy))
    return ['polygon', arrow, arrow_type, style or {}, props or {}]

def draw_array(box, a):
    return ['array', box, a]

def draw_html(box, html, html_type='', style=None):
    return ['html', box, html, html_type, style or {}]
