"""
Basic graphical elements.

They are all lists whose first element is a string saying which kind
of element it is (like "line"), and the rest are its parameters.

They are sent as json to the javascript viewer, which interprets them
(in draw.js) and draws the corresponding graphics.

Whenever a box is used, it is in "tree coordinates" (that is, not
multiplied by the zoom or the radius, so not in pixels).
"""


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

def draw_text(box, anchor, text, fs_max=None, style=''):
    return ['text', box, anchor, text, fs_max, style]
# NOTE: We include  fs_max  in addition to just  box  because in circular mode
# we translate the boxes for the aligned items, changing their pixel size.

def draw_array(box, a):
    return ['array', box, a]


# Other (non-drawing) commands.

def set_panel(panel=0):
    return ['panel', panel]
