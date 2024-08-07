from math import pi
import re  # so it can be used when evaluating expressions

from .coordinates import Size, Box, make_box
from . import graphics as gr


# A "face" (glyph, chip, infobox, ibox, ichip, infochip) is a piece of
# drawn information. It has a drawing function which is a function of
# a node that returns the graphic elements that will show the
# information. It also has a drawing function for collapsed elements.

class Face:
    """Base class (mostly an example of the expected interface)."""

    def __init__(self):
        """Save all the parameters that we may want to use."""
        pass  # in this example, we don't save any

    def draw(self, nodes, size, collapsed=False, zoom=None, anchor=None, r=1):
        """Return a list of graphic elements and the actual size they use."""
        # The retuned graphic elements normally depend on the node(s).
        # They have to fit inside the given size (dx, dy) in tree
        # coordinates (dx==0 means no limit for dx).

        # If collapsed=False, nodes contain only one node (and is not
        # collapsed). Otherwise, nodes is a list of the collapsed nodes.

        # The zoom is passed in case the face wants to represent
        # things differently according to its size on the screen. But
        # zoom=None should work too. Same thing for the anchor point.

        # r * size[1] * zoom[1] is the size in pixels of the left
        # border, whether we are in rectangular or circular mode.

        graphic_elements = []  # like [draw_text(...), draw_line(...), ...]

        size_used = Size(0, 0)

        return graphic_elements, size_used


class TextFace:  # no need to inherit like  TextFace(Face)  (faster?)
    """A text that results from executing an expression on the node."""

    def __init__(self, expression, fs_max=16, style=None):
        self.code = (expression if type(expression) != str else
                     compile(expression, '<string>', 'eval'))
        self.style = style or ('text_' + expression)
        self.fs_max = fs_max

    def draw(self, nodes, size, collapsed=False, zoom=None, anchor=None, r=1):
        # Get text(s) from applying expression to nodes.
        if collapsed:
            texts_dirty, all_accounted = make_nodes_summary(nodes, self.code)
            texts = text_repr([a for a in texts_dirty if a], all_accounted)
        else:
            text = eval_as_str(self.code, nodes[0])
            texts = [text] if text else []

        if not texts:  # no texts, nothing to draw
            return [], Size(0, 0)

        # Find the size that we will use to draw everything.
        shrink_x = size.dx > 0  # dx == 0 is a special value, "no shrink"
        size_used = texts_size(texts, size, self.fs_max, zoom, shrink_x, r)

        if size_used.dx <= 0 or size_used.dy <= 0:
            return [], size_used

        # Place x according to the anchor point. It must be:
        #   ax * dx_col == x + ax * size_used.dx
        ax, ay = anchor or (0, 0)
        x = ax * (size.dx - size_used.dx)

        # Get the graphic elements to draw.
        elements = list(draw_texts(make_box((x, 0), size_used),
                                   (ax, ay), texts, self.fs_max, self.style))

        return elements, size_used


def make_nodes_summary(nodes, code=None):
    """Return values summarizing the nodes, and if all are accounted for."""
    all_accounted = True  # did we get the value from all the given nodes?
    values = []  # will have the (summary of the) values
    for node in nodes:
        value = node.name if code is None else eval_as_str(code, node)
        if value:
            values.append(value)
        else:
            value_in_descendant = first_value(node, code)
            if value_in_descendant:
                values.append(value_in_descendant)
                # There could be more values to add, that we ignore:
                all_accounted = False

    return values, all_accounted


def first_value(tree, code=None):
    """Return value of evaluating the given code, on the first possible node."""
    if code is None:  # special (and common!) case: get the first name
        return next((node.name for node in tree.traverse() if node.name), '')
    else:
        for node in tree.traverse():
            value = eval_as_str(code, node)
            if value:
                return value
        return ''


def texts_size(texts, size_max, fs_max, zoom, shrink_x=True, r=1):
    """Return the (dx, dy) dimensions of the texts so they fit in size_max."""
    zx, zy = zoom
    dx_max, dy_max = size_max

    if r <= 0 or zx <= 0 or zy <= 0 or dy_max <= 0:
        return Size(0, 0)

    # Find its dimensions so its font size on screen is fs_max.
    len_text_max = max((len(text) for text in texts), default=0)
    dy_text = fs_max * len(texts) / (r * zy)
    dx_text = fs_max * len_text_max / (1.5 * zx)

    # Shrink its dimensions so it fits inside dx_max, dy_max.
    if dy_text > dy_max:
        sf = dy_max / dy_text  # shrink factor
        dx_text *= sf
        dy_text *= sf

    if shrink_x and dx_text > dx_max:
        sf = dx_max / dx_text
        dx_text *= sf
        dy_text *= sf

    return Size(dx_text, dy_text)


def text_repr(texts, all_have):
    """Return a summarized representation of the given texts."""
    texts = list(dict.fromkeys(texts))  # remove duplicates
    if all_have:  # texts are all the texts that we want to summarize
        return texts if len(texts) < 6 else (texts[:3] + ['[...]'] + texts[-2:])
    else:  # there may be more texts that our representation is not including
        return texts[:6] + ['[...]']


def draw_texts(box, anchor, texts, fs_max, style):
    """Yield texts so they fit in the box."""
    x = box.x
    y = box.y  # will advance for each text
    dx = box.dx
    dy = box.dy / len(texts)
    for text in texts:
        yield gr.draw_text(Box(x, y, dx, dy), anchor, text, fs_max, style)
        y += dy


def eval_as_str(code, node):
    """Return the given code evaluated on values related to the given node."""
    result = safer_eval(code, {
        'node': node, 'name': node.name, 'is_leaf': node.is_leaf,
        'length': node.dist, 'dist': node.dist, 'd': node.dist,
        'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
        'support': node.props.get('support', ''),
        'properties': node.props, 'props': node.props, 'p': node.props,
        'get': dict.get, 'split': str.split,
        'children': node.children, 'ch': node.children,
        'regex': re.search,
        'len': len, 'sum': sum, 'abs': abs, 'float': float, 'pi': pi})
    return str(result) if result is not None else ''


def safer_eval(code, context):
    """Return a safer version of eval(code, context)."""
    for name in code.co_names:
        if name not in context:
            raise SyntaxError('invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)


class CircleFace:
    """A circle."""

    def __init__(self, rmax=None, style=None):
        self.rmax = rmax  # maximum radius in pixels
        self.style = style or ''

    def draw(self, nodes, size, collapsed=False, zoom=None, anchor=None, r=1):
        dx, dy = size
        zx, zy = zoom if zoom else (1, 1)

        # Find the circle radius in pixels.
        cr = zy * r * dy / 2
        if dx > 0:
            cr = min(cr, zx * dx / 2)
        if self.rmax:
            cr = min(cr, self.rmax)

        # Return the circle graphic and its size.
        center = (cr / zx, cr / (r * zy))  # in tree coordinates
        circle = gr.draw_circle(center, cr, self.style)

        return [circle], Size(2*cr/zx, 2*cr/(r*zy))
        # NOTE: For small r (in circular mode), that size is just approximate.


class RectFace:
    """A rectangle."""

    def __init__(self, wmax, hmax=None, style=None):
        self.wmax = wmax  # maximum width in pixels
        self.hmax = hmax  # maximum height in pixels
        self.style = style or ''

    def draw(self, nodes, size, collapsed=False, zoom=None, anchor=None, r=1):
        dx, dy = size
        zx, zy = zoom if zoom else (1, 1)

        # Find the width and height so they are never bigger than the max.
        w = min(zx * dx, self.wmax) if dx > 0 else self.wmax
        h = min(zy * r * dy, self.hmax)

        # Keep the ratio h/w if we had hmax in addition to wmax.
        if self.hmax:
            h_over_w = self.hmax / self.wmax

            if h / w > h_over_w:
                h = h_over_w * w
            else:
                w = h / h_over_w

        # Return the rectangle graphic and its size.
        rect = gr.draw_rect((0, 0, w/zx, h/(r*zy)), self.style)

        return [rect], Size(w/zx, h/(r*zy))
