"""
A "face" is a piece of drawn information.

Different faces can represent different kinds of information in
different forms. Faces have a drawing function that returns the
graphic elements that will show the information, and the size they
occupy (in tree coordinates).

They know how to represent node(s) information, confined to an area of
a given size. They do it with a method face.draw(nodes, size, ...)
which returns the graphic elements and the actual size they use
(which may be smaller than the allocated size).

The sizes are always given in "tree units". The size in pixels is
always that size multiplied by the zoom.
"""

# Other names that may be better than "face": glyph, chip, infobox,
# ibox, ichip, infochip.

import os
from base64 import b64encode
from math import pi, cos, sin
import re  # so it can be used when evaluating expressions

from ete4.core.eval import eval_on_node
from .coordinates import Size, Box, make_box
from . import graphics as gr


# Default anchors. The x, y go between -1 to +1, with 0 the center.
default_anchors = {'top':     (-1, 1),   # left, bottom
                   'bottom':  (-1, -1),  # left, top
                   'right':   (-1, 0),   # left, middle
                   'left':    ( 1, 0),   # right, middle
                   'aligned': (-1, 0),   # left, middle
                   'header':  (-1, 1)}   # left, bottom


class Face:
    """Base class.

    It contains a position ("top", "bottom", "right", "left",
    "aligned", "header"), a column (an integer used for relative order
    with other faces in the same position), and an anchor point (to
    fine-tune the position of things like texts within them).
    """

    def __init__(self, position='top', column=0, anchor=None):
        """Save all the parameters that we may want to use."""
        self.position = position  # 'top', 'bottom', 'right', etc.
        self.column = column  # integer >= 0
        self.anchor = anchor or default_anchors[position]  # tuple

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        """Return a list of graphic elements and the actual size they use.

        The retuned graphic elements normally depend on the node(s).
        They have to fit inside the given size (dx, dy) in tree
        coordinates (dx==0 means no limit for dx, and same for dy==0).

        If collapsed==[], nodes contains only one node (and is not collapsed).
        Otherwise, nodes (== collapsed) is a list of the collapsed nodes.

        The zoom is passed in case the face wants to represent
        things differently according to its size on the screen.

        ax_ay is the anchor point within the box of the given size
        (from 0 for left/up, to 1 for right/down).

        r * size[1] * zoom[1] is the size in pixels of the left
        border, whether we are in rectangular or circular mode.
        """
        graphic_elements = []  # like [draw_text(...), draw_line(...), ...]

        size_used = Size(0, 0)

        return graphic_elements, size_used


class EvalTextFace(Face):
    """A text that results from evaluating an expression on the node.

    The style can be a string which refers to the style the gui is
    going to assign it, or a dictionary with svg attributes for text.
    """

    def __init__(self, expression, fs_min=2, fs_max=16, rotation=0, style='',
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.code = (expression if type(expression) != str else
                     compile(expression, '<string>', 'eval'))
        self.style = style or ('text_' + expression)
        self.fs_min = fs_min
        self.fs_max = fs_max
        self.rotation = rotation

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        # Get text(s) from applying expression to nodes.
        if collapsed:
            texts_dirty, all_accounted = make_nodes_summary(nodes, self.code)
            texts = text_repr([a for a in texts_dirty if a], all_accounted)
        else:
            text = eval_as_str(self.code, nodes[0])
            texts = [text] if text else []

        if not texts:  # no texts?
            return [], Size(0, 0)  # nothing to draw

        # FIXME: Little hack to make all the texts appear with the same size.
        len_max = max(len(text) for text in texts)
        texts = [text + ' ' * (len_max - len(text)) for text in texts]

        # Find the size that we will use to draw everything.
        size_used = texts_size(texts, size, self.fs_max, self.rotation, zoom, r)

        # Only draw if  font size > fs_min.
        if not r * zoom[1] * size_used.dy > self.fs_min * len(texts):
            return [], Size(0, 0)  # nothing to draw

        # Place x according to the anchor point. It must be:
        #   ax * size.dx == x + ax * size_used.dx
        ax, ay = ax_ay
        x = ax * (size.dx - size_used.dx)

        # Get the graphic elements to draw.
        elements = list(draw_texts(make_box((x, 0), size_used), (ax, ay), texts,
                                   self.fs_max, self.rotation, self.style))

        return elements, size_used


class TextFace(EvalTextFace):
    """A fixed text."""

    def __init__(self, text, fs_min=2, fs_max=16, rotation=0,
                 style='', position='top', column=0, anchor=None):
        expression = '""' if not text else '"%s"' % text.replace('"', r'\"')
        super().__init__(expression, fs_min, fs_max, rotation, style,
                         position, column, anchor)


class PropFace(EvalTextFace):
    """A text showing the given property, and optionally a special format."""

    def __init__(self, prop, fmt='%s', fs_min=2, fs_max=16, rotation=0,
                 style='', position='top', column=0, anchor=None):
        pexp = prop if prop in ['name', 'dist', 'support'] else f'p["{prop}"]'
        expression = f'"{fmt}" % {pexp} if "{prop}" in p else ""'
        super().__init__(expression, fs_min, fs_max, rotation, style,
                         position, column, anchor)


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


def texts_size(texts, size_max, fs_max, rotation, zoom, r=1):
    """Return the (dx, dy) dimensions of the texts so they fit in size_max."""
    zx, zy = zoom
    dx_max, dy_max = size_max  # NOTE: "0" means "no limit"

    # Find a font size that makes the text fit in size_max.
    a = rotation * pi / 180  # rotation angle in radians
    c, s = abs(cos(a)), abs(sin(a))
    nrows = len(texts)  # number of rows of text (normally just 1)
    len_text_max = max((len(text) for text in texts), default=0)

    # The font size has to be <= fs_max and has to fit in the given space.
    fs = fs_max
    if dx_max > 0:
        fs = min(fs, dx_max * zx / (c * len_text_max / 1.5 + s * nrows))
    if dy_max > 0:
        fs = min(fs, dy_max * zy / (s * len_text_max / 1.5 + c * nrows))

    # The size used by (rotated) text with font size fs.
    dx = fs * (c * len_text_max / 1.5 + s * nrows) / zx
    dy = fs * (s * len_text_max / 1.5 + c * nrows) / zy

    # TODO: Check how to use r to do it properly in circular mode.

    return Size(dx, dy)


def text_repr(texts, all_have):
    """Return a summarized representation of the given texts."""
    texts = list(dict.fromkeys(texts))  # remove duplicates
    if all_have:  # texts are all the texts that we want to summarize
        return texts if len(texts) < 6 else (texts[:3] + ['[...]'] + texts[-2:])
    else:  # there may be more texts that our representation is not including
        return texts[:6] + ['[...]']


def draw_texts(box, ax_ay, texts, fs_max, rotation, style):
    """Yield texts so they fit in the box."""
    x = box.x
    y = box.y  # will advance for each text
    dx = box.dx
    dy = box.dy / len(texts)
    for text in texts:
        yield gr.draw_text(Box(x, y, dx, dy), ax_ay, text,
                           fs_max, rotation, style)
        y += dy


def eval_as_str(code, node):
    """Return the given code evaluated on values related to the given node."""
    result = eval_on_node(code, node)
    return str(result) if result is not None else ''


class CircleFace(Face):
    """A circle."""

    def __init__(self, rmax=None, style='',
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.rmax = rmax  # maximum radius in pixels
        self.style = style

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        # Find the circle radius (cr) in pixels.
        assert dx > 0 or dy > 0 or self.rmax is not None, 'rmax needed'
        cr = self.rmax
        if dx > 0:
            cr_x = zx * dx / 2
            cr = min(cr, cr_x) if cr is not None else cr_x
        if dy > 0:
            cr_y = zy * r * dy / 2
            cr = min(cr, cr_y) if cr is not None else cr_y

        # Return the circle graphic and its size.
        center = (cr / zx, cr / (r * zy))  # in tree coordinates
        circle = gr.draw_circle(center, cr, self.style)

        return [circle], Size(2*cr/zx, 2*cr/(r*zy))
        # NOTE: For small r (in circular mode), that size is just approximate.


class PolygonFace(Face):
    """A polygon."""

    def __init__(self, rmax=None, shape=3, style='',
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.shape = shape  # name of the shape or number of edges
        self.rmax = rmax  # maximum "radius" in pixels
        self.style = style

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        # Find the (approx.) radius (cr) of circumscribing circle in pixels.
        assert dx > 0 or dy > 0 or self.rmax is not None, 'rmax needed'
        cr = self.rmax
        if dx > 0:
            cr_x = zx * dx / 2
            cr = min(cr, cr_x) if cr is not None else cr_x
        if dy > 0:
            cr_y = zy * r * dy / 2
            cr = min(cr, cr_y) if cr is not None else cr_y

        # Return the graphic and its size.
        center = (cr / zx, cr / (r * zy))  # in tree coordinates
        polygon = gr.draw_polygon(center, cr, self.shape, self.style)

        return [polygon], Size(2*cr/zx, 2*cr/(r*zy))
        # NOTE: For small r (in circular mode), that size is just approximate.


class BoxedFace(Face):
    """A shape defined by a box (with optionally a text inside)."""
    # Base class for BoxFace and RectFace.

    def __init__(self, wmax=None, hmax=None, text=None,
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.wmax = wmax  # maximum width in pixels
        self.hmax = hmax  # maximum height in pixels
        self.text = TextFace(text) if type(text) is str else text

        self.drawing_fn = None  # will be set by its subclasses

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        # Find the width and height so they are never bigger than the max.
        assert dx > 0 or self.wmax is not None, 'wmax needed'
        assert dy > 0 or self.hmax is not None, 'hmax needed'
        w, h = self.wmax, self.hmax
        if dx > 0:
            w = min(w, zx * dx)     if w is not None else zx * dx
        if dy > 0:
            h = min(h, zy * r * dy) if h is not None else zy * r * dy

        # Keep the ratio h/w if we had hmax in addition to wmax.
        if self.hmax:
            h_over_w = self.hmax / self.wmax

            if h / w > h_over_w:
                h = h_over_w * w
            else:
                w = h / h_over_w

        # Return the graphics and their size.
        size = Size(w/zx, h/(r*zy))
        box = make_box((0, 0), size)
        graphics = [self.drawing_fn(box)]

        if self.text:
            # Draw the text centered in x (0.5). But we have to shift the y
            # "by hand" because faces let the caller anchor in y afterwards
            # (so several faces can be vertically stacked and then anchored).
            graphics_text, size_text = self.text.draw(nodes, size, collapsed,
                                                      zoom, (0.5, 0.5), r)
            circular = False
            shift = (0, (size.dy - size_text.dy) / 2)  # shift the y
            graphics += gr.draw_group(graphics_text, circular, shift)

        return graphics, size


class BoxFace(BoxedFace):
    """A box (with optionally a text inside)."""

    def __init__(self, wmax=None, hmax=None, style='', text=None,
                 position='top', column=0, anchor=None):
        super().__init__(wmax, hmax, text, position, column, anchor)

        self.drawing_fn = lambda box: gr.draw_box(box, style)


class RectFace(BoxedFace):
    """A rectangle (with optionally a text inside)."""

    def __init__(self, wmax=None, hmax=None, style='', text=None,
                 position='top', column=0, anchor=None):
        super().__init__(wmax, hmax, text, position, column, anchor)

        self.drawing_fn = lambda box: gr.draw_rect(box, style)


class ImageFace(BoxedFace):
    """An image (with optionally a text inside)."""

    def __init__(self, path, wmax=None, hmax=None, style='', text=None,
                 position='top', column=0, anchor=None):
        super().__init__(wmax, hmax, text, position, column, anchor)

        assert os.path.exists(path), f'missing image at {path}'
        ext = os.path.splitext(path)[1][1:].lower()  # extension

        assert ext in ['png', 'jpeg', 'jpg', 'svg'], f'invalid type: {path}'
        href = ('data:image/' + ext + ';base64,' +
                b64encode(open(path, 'rb').read()).decode('utf8'))

        self.drawing_fn = lambda box: gr.draw_image(box, href, style);


class SeqFace(Face):
    """A sequence of nucleotides or amino acids."""

    def __init__(self, seq, seqtype='aa', poswidth=15, draw_text=True,
                 hmax=None, fs_max=15, style='', render='auto',
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.seq = ''.join(x for x in seq)  # in case it was a list
        self.seqtype = seqtype
        self.poswidth = poswidth  # width in pixels of each nucleotide/aa
        self.draw_text = draw_text
        self.hmax = hmax  # maximum height in pixels
        self.fs_max = fs_max
        self.style = style
        self.render = render

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        if dx <= 0:  # no limit on dx? make it as big as possible
            dx = self.poswidth * len(self.seq) / zx

        assert dy > 0 or self.hmax is not None, 'hmax needed'
        if dy <= 0:  # no limit on y? there better be hmax then
            dy = self.hmax / zy
        elif self.hmax is not None:  # if dy > 0, but hmax defined, take the min
            dy = min(dy, self.hmax / zy)  # make dy so pixel height < hmax

        size = Size(dx, dy)
        box = make_box((0, 0), size)
        graphics = [gr.draw_seq(box, self.seq, self.seqtype, self.draw_text,
                                self.fs_max, self.style, self.render)]

        return graphics, size


class HeatmapFace(Face):
    """An array of colored squares according to a value and color range."""

    def __init__(self, values, value_range, color_range,
                 poswidth=15, hmax=None,
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.values = values
        self.value_range = value_range  # (min, max)
        self.color_range = [gr.hex2rgba(x) for x in color_range]  # (min, max)
        self.poswidth = poswidth  # width in pixels of each position (square)
        self.hmax = hmax  # maximum height in pixels

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        if dx <= 0:  # no limit on dx? make it as big as possible
            dx = self.poswidth * len(self.values) / zx

        assert dy > 0 or self.hmax is not None, 'hmax needed'
        if dy <= 0:  # no limit on y? there better be hmax then
            dy = self.hmax / zy
        elif self.hmax is not None:  # if dy > 0, but hmax defined, take the min
            dy = min(dy, self.hmax / zy)  # make dy so pixel height < hmax

        size = Size(dx, dy)
        box = make_box((0, 0), size)
        graphics = [gr.draw_heatmap(box, self.values,
                                    self.value_range, self.color_range)]

        return graphics, size


class TextArrayFace(Face):
    """An array of texts."""

    def __init__(self, texts, fs_max=16, rotation=0,
                 poswidth=15, hmax=None, style='',
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        self.texts = texts
        self.fs_max = fs_max
        self.rotation = rotation
        self.poswidth = poswidth  # width in pixels of each position
        self.hmax = hmax  # maximum height in pixels
        self.style = style

    def draw(self, nodes, size, collapsed, zoom=(1, 1), ax_ay=(0, 0), r=1):
        dx, dy = size
        zx, zy = zoom

        if dx <= 0:  # no limit on dx? make it as big as possible
            dx = self.poswidth * len(self.texts) / zx

        assert dy > 0 or self.hmax is not None, 'hmax needed'
        if dy <= 0:  # no limit on y? there better be hmax then
            dy = self.hmax / zy
        elif self.hmax is not None:  # if dy > 0, but hmax defined, take the min
            dy = min(dy, self.hmax / zy)  # make dy so pixel height < hmax
        # FIXME: The dy that we get from hmax seems not to be used correctly
        # later (probably related to draw.js:get_text_placement_rect()).

        size = Size(dx, dy)
        box = make_box((0, 0), size)
        graphics = [gr.draw_textarray(box, ax_ay, self.texts, self.fs_max,
                                      self.rotation, self.style)]

        return graphics, size


class LegendFace(Face):
    """A legend with information about the data we are visualizing."""

    def __init__(self, title, variable,
                 colormap=None, value_range=None, color_range=None,
                 position='top', column=0, anchor=None):
        super().__init__(position, column, anchor)

        # Do some very basic consistency checks first.
        if variable == 'discrete':
            assert colormap and value_range is None and color_range is None, \
                'discrete variable needs a colormap (and no more)'
        elif variable == 'continuous':
            assert value_range and color_range and colormap is None, \
                'continuous variable needs value and color ranges (and no more)'
        else:
            raise ValueError(f'invalid variable value: {variable}')

        self.title = title
        self.variable = variable  # can be "discrete" or "continuous"
        self.colormap = colormap  # dict {name: color}
        self.value_range = value_range  # (min, max)
        self.color_range = color_range  # (min, max)

    # NOTE: We don't need a special draw() function, we use the info directly.
