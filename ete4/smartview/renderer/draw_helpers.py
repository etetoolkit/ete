from collections import OrderedDict, namedtuple
from math import sin, cos, pi, sqrt, atan2

Box = namedtuple('Box', 'x y dx dy')  # corner and size of a 2D shape

Padding = namedtuple('Padding', 'x y')


def clip_angles(a1, a2):
    "Return the angles such that a1 to a2 extend at maximum from -pi to pi"
    EPSILON = 1e-8  # without it, p1 can be == p2 and svg arcs are not drawn
    return max(-pi + EPSILON, a1), min(pi - EPSILON, a2)


def cartesian(point):
    r, a = point
    return r * cos(a), r * sin(a)


def summary(nodes, prop="name"):
    "Return a list of names summarizing the given list of nodes"
    return list(OrderedDict((first_value(node, prop), None) for node in nodes).keys())


def first_value(tree, prop):
    "Return the value of the requested property for the first node that has it"
    return next((node.props.get(prop) for node in tree.traverse('preorder')
                 if node.props.get(prop)), '')


def get_xs(box):
    x, _, dx, _ = box
    return x, x + dx

def get_ys(box):
    _, y, _, dy = box
    return y, y + dy

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

# Basic drawing elements.
def draw_nodebox(box, name='', properties=None,
        node_id=None, searched_by=None, style=None):
    properties = { k:v for k,v in (properties or {}).items() \
            if not (k.startswith('_') or k == 'seq')}
    return ['nodebox', box, name,
            properties, node_id or [],
            searched_by or [], style or {}]

def draw_outline(box, style=None):
    return ['outline', box, style or {}]

def get_line_type(style):
    types = ['solid', 'dotted', 'dashed']
    if style.get('type'):
        style['type'] = types[int(style['type'])]
    else:
        style['type'] = types[0]
    return style

def draw_line(p1, p2, line_type='', parent_of=None, style=None):
    style = get_line_type(style or {})
    return ['line', p1, p2, line_type, parent_of or [], style]

def draw_arc(p1, p2, large=False, arc_type='', style=None):
    style = get_line_type(style or {})
    return ['arc', p1, p2, int(large), arc_type, style]

def draw_circle(center, radius, circle_type='', style=None, tooltip=None):
    return ['circle', center, radius, circle_type, style or {}, tooltip or '']

def draw_ellipse(center, rx, ry, ellipse_type='', style=None, tooltip=None):
    return ['ellipse', center, rx, ry, ellipse_type, style or {}, tooltip or '']

def draw_slice(center, r, a, da, slice_type='', style=None, tooltip=None):
    return ['slice', (center, r, a, da), slice_type, style or {}, tooltip or '']

def draw_triangle(box, tip, triangle_type='', style=None, tooltip=None):
    """Returns array with all the information needed to draw a triangle
    in front end.
    :box: bounds triangle
    :tip: defines tip orientation 'top', 'left' or 'right'.
    :triangle_type: will label triangle in front end (class)
    """
    return ['triangle', box, tip, triangle_type, style or {}, tooltip or '']

def draw_text(box, text, text_type='', rotation=0, anchor=None, style=None):
    return ['text', box, text, text_type, rotation, anchor or "",  style or {}]

def draw_rect(box, rect_type, style=None, tooltip=None):
    return ['rect', box, rect_type, style or {}, tooltip or '']

def draw_rhombus(box, rhombus_type='', style=None, tooltip=None):
    """ Create rhombus provided a bounding box """
    # Rotate the box to provide a rhombus (points) to drawing engine
    x, y, dx, dy = box
    rhombus = ((x + dx / 2, y),      # top
               (x + dx, y + dy / 2), # right
               (x + dx / 2, y + dy), # bottom
               (x, y + dy / 2))      # left
    return ['rhombus', rhombus, rhombus_type, style or {}, tooltip or '']

def draw_arrow(box, tip, orientation='right', arrow_type='',
        style=None, tooltip=None):
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
    return ['polygon', arrow, arrow_type, style or {}, tooltip or '']

def draw_array(box, a, tooltip=None):
    return ['array', box, a, tooltip or '']

def draw_html(box, html, html_type='', style=None):
    return ['html', box, html, html_type, style or {}]

def draw_img(box, img, img_type='', style=None):
    return ['img', box, img, img_type, style or {}]
