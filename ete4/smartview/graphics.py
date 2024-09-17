"""
Basic graphical elements.

They are all lists whose first element is a string saying which kind
of element it is (like "line"), and the rest are its parameters.

They are sent as json to the javascript viewer, which interprets them
(in draw.js) and draws the corresponding graphics.

Whenever a box is used, it is in "tree coordinates" (that is, not
multiplied by the zoom or the radius, so not in pixels).
"""

from math import pi


# A nodebox is a high-level representations of a node (or a group of
# collapsed nodes). It can have the name of the node, other
# properties, and a list of texts (searches for which the node is a
# result of).
def draw_nodebox(box, name='', props=None, node_id=None, result_of=None):
    return ['nodebox', box, name, props or {}, node_id or [], result_of or []]

# An outline has the information to draw an approximate representation
# of the interior of collapsed nodes.
def draw_outline(points):
    return ['outline', points]

# In the following elements, "style" can be a string (referencing a
# css class), a dictionary (with css fields), or a list containing
# strings and dictionaries (to be combined); and "kwargs" is a
# dictionary with any extra information that we may want to pass (for
# example, if a line is a distline of a node that is parent to the
# result of a search, so we can draw it highlighted or something).

def draw_line(p1, p2, style='', kwargs=None):
    return ['line', p1, p2, style, kwargs or {}]

def draw_arc(p1, p2, large=False, style='', kwargs=None):
    return ['arc', p1, p2, int(large), style, kwargs or {}]

def draw_circle(center, radius=1, style=''):
    return ['circle', center, radius, style]

def draw_rect(box, style=''):
    return ['rect', box, style]

def draw_text(box, anchor, text, fs_max=None, style=''):
    return ['text', box, anchor, text, fs_max, style]
# NOTE: We include  fs_max  in addition to just  box  because in circular mode
# we translate the boxes for the aligned items, changing their pixel size.

def draw_array(box, a):
    return ['array', box, a]


# Other (non-drawing) commands.

def set_panel(panel=0):  # panel that we will use to draw from now on
    return ['panel', panel]

def set_xmax(xmax):  # maximum reached x (so we can align to it)
    return ['xmax', xmax]


# Related functions.

def draw_group(elements, circular, shift):
    """Yield the given drawing elements with their coordinates shifted."""
    x0, y0 = shift

    if x0 == y0 == 0:
        yield from elements  # no need to shift anything
        return

    for element in elements:
        eid = element[0]  # "element identifier" (name of drawing element)
        if eid in ['nodebox', 'array', 'text']:
            # The position for these elements is given by a box.
            x, y, dx, dy = element[1]
            box = x0 + x, y0 + y, dx, dy
            if not circular or are_valid_angles(y0 + y, y0 + y + dy):
                yield [eid, box] + element[2:]
        elif eid == 'outline':
            # The points given in the outline can be (x,y) or (r,a).
            points = [(x0 + x, y0 + y) for x, y in element[1]
                      if not circular or are_valid_angles(y0 + y)]
            yield [eid, points]
        elif eid in ['line', 'arc']:
            # The points in these elements are always in rectanglar coords.
            (x1, y1), (x2, y2) = element[1], element[2]
            yield [eid, (x0 + x1, y0 + y1), (x0 + x2, y0 + y2)] + element[3:]
        elif eid == 'circle':
            # The center of the circle is always in rectangular coords.
            x, y = element[1]
            yield [eid, (x0 + x, y0 + y)] + element[2:]
        elif eid == 'rect':
            x, y, w, h = element[1]
            yield [eid, (x0 + x, y0 + y, w, h)] + element[2:]
        else:
            raise ValueError(f'unrecognized element: {element!r}')


def are_valid_angles(*angles):
    EPSILON = 1e-8  # without it, rounding can fake an angle a > pi
    return all(-pi <= a < pi+EPSILON for a in angles)
