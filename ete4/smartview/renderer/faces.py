import base64
from collections.abc import Iterable
import pathlib
import re
from math import pi

from ..utils import InvalidUsage, get_random_string
from .draw_helpers import *
from copy import deepcopy

CHAR_HEIGHT = 1.4 # char's height to width ratio

ALLOWED_IMG_EXTENSIONS = [ "png", "svg", "jpeg" ]

_aacolors = {
    'A':"#C8C8C8" ,
    'R':"#145AFF" ,
    'N':"#00DCDC" ,
    'D':"#E60A0A" ,
    'C':"#E6E600" ,
    'Q':"#00DCDC" ,
    'E':"#E60A0A" ,
    'G':"#EBEBEB" ,
    'H':"#8282D2" ,
    'I':"#0F820F" ,
    'L':"#0F820F" ,
    'K':"#145AFF" ,
    'M':"#E6E600" ,
    'F':"#3232AA" ,
    'P':"#DC9682" ,
    'S':"#FA9600" ,
    'T':"#FA9600" ,
    'W':"#B45AB4" ,
    'Y':"#3232AA" ,
    'V':"#0F820F" ,
    'B':"#FF69B4" ,
    'Z':"#FF69B4" ,
    'X':"#BEA06E",
    '.':"#FFFFFF",
    '-':"#FFFFFF",
    }

_ntcolors = {
    'A':'#A0A0FF',
    'G':'#FF7070',
    'I':'#80FFFF',
    'C':'#FF8C4B',
    'T':'#A0FFA0',
    'U':'#FF8080',
    '.':"#FFFFFF",
    '-':"#FFFFFF",
    ' ':"#FFFFFF"
    }


def clean_text(text):
    return re.sub(r'[^A-Za-z0-9_-]', '',  text)


def swap_pos(pos, angle):
    if abs(angle) >= pi / 2:
        if pos == 'branch_top':
            pos = 'branch_bottom'
        elif pos == 'branch_bottom':
            pos = 'branch_top'
    return pos


def stringify(content):
    if type(content) in (str, float, int):
        return str(content)
    if isinstance(content, Iterable):
        return ",".join(map(str, content))
    return str(content)


class Face(object):

    def __init__(self, name="", padding_x=0, padding_y=0):
        self.node = None
        self.name = name
        self._content = "Empty"
        self._box = None
        self.padding_x = padding_x
        self.padding_y = padding_y

        self.always_drawn = False # Use carefully to avoid overheading...

        self.zoom = (0, 0)
        self.stretch = False  # Stretch width independently of height
        self.viewport = None  # Aligned panel viewport (x1, x2)
        self.viewport_margin = 100

    def __name__(self):
        return "Face"

    def in_aligned_viewport(self, segment):
        if self.viewport:
            return intersects_segment(self.viewport, segment)
        return True

    def get_content(self):
        return self._content

    def get_box(self):
        self._check_own_variables()
        return self._box

    def compute_fsize(self, dx, dy, zx, zy, max_fsize=None):
        self._fsize = min([dx * zx * CHAR_HEIGHT, abs(dy * zy), max_fsize or self.max_fsize])

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        self._check_own_content()
        x, y = point
        dx, dy = size

        zx, zy, za = drawer.zoom
        if pos.startswith("aligned"):
            zx = za
        self.zoom = (zx, zy)

        if pos == 'branch_top':  # above the branch
            avail_dx = dx / n_col
            avail_dy = bdy / n_row
            x = x + dx_before
            y = y + bdy - avail_dy - dy_before

        elif pos == 'branch_bottom':  # below the branch
            avail_dx = dx / n_col
            avail_dy = (dy - bdy) / n_row
            x = x + dx_before
            y = y + bdy + dy_before

        elif pos == 'branch_right':  # right of node
            avail_dx = dx_to_closest_child / n_col\
                    if not (self.node.is_leaf() or self.node.is_collapsed)\
                    else None
            avail_dy = min([bdy, dy - bdy, bdy - bdy0, bdy1 - bdy]) * 2 / n_row
            x = x + bdx + dx_before
            y = y + bdy + (row - n_row / 2) * avail_dy

        elif pos.startswith('aligned'): # right of tree
            avail_dx = None # should be overriden
            avail_dy = dy / n_row
            aligned_x = drawer.node_size(drawer.tree)[0]\
                    if drawer.panel == 0 else drawer.xmin
            x = aligned_x + dx_before

            if pos == 'aligned_bottom':
                y = y + dy - avail_dy - dy_before
            elif pos == 'aligned_top':
                y = y + dy_before
            else:
                y = y + dy / 2 + (row - n_row / 2) * avail_dy

        else:
            raise InvalidUsage(f'unkown position {pos}')

        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        padding_x = self.padding_x / zx
        padding_y = self.padding_y / (zy * r)

        self._box = Box(
            x + padding_x,
            y + padding_y,
            # avail_dx may not be initialized for branch_right and aligned
            max(avail_dx - 2 * padding_x, 0) if avail_dx else None,
            max(avail_dy - 2 * padding_y, 0))

        return self._box

    def fits(self):
        """
        Return True if Face fits in computed box.
        Method overriden by inheriting classes.
        """
        return True

    def _check_own_content(self):
        if not self._content:
            raise Exception(f'**Content** has not been computed yet.')

    def _check_own_variables(self):
        if not self._box:
            raise Exception(f'**Box** has not been computed yet.\
                    \nPlease run `compute_bounding_box()` first')
        self._check_own_content()
        return


class TextFace(Face):

    def __init__(self, text, name='', color='black',
            min_fsize=6, max_fsize=15, ftype='sans-serif',
            padding_x=0, padding_y=0, width=None, height=None, rotation=None):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

        self._content = stringify(text)
        self.color = color
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self._fsize = max_fsize
        self.rotation = rotation
        self.width = width
        self.height = height
        self.ftype = ftype

    def __name__(self):
        return "TextFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        zx, zy = self.zoom

        x, y , dx, dy = box
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

        def fit_fontsize(text, dx, dy):
            dchar = dx / len(text) if dx != None else float('inf')
            self.compute_fsize(dchar, dy, zx, zy)
            dxchar = self._fsize / (zx * CHAR_HEIGHT)
            dychar = self._fsize / (zy * r)
            return dxchar * len(text), dychar

        if self.width: 
            width = self.width
            _, height = fit_fontsize(self._content, dx, dy * r)
        else:
            width, height = fit_fontsize(self._content, dx, dy * r)
        

        if pos == 'branch_top':
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch_bottom':
            box = (x, y, width, height) # container top

        elif pos == 'aligned_bottom':
            box = (x, y + dy - height, width, height)

        elif pos == 'aligned_top':
            box = (x, y, width, height)

        else: # branch_right and aligned
            box = (x, y + (dy - height) / 2, width, height)

        self._box = Box(*box)
        return self._box

    def fits(self):
        return self._content != "None" and self._fsize >= self.min_fsize

    def draw(self, drawer):
        self._check_own_variables()
        style = {
                'fill': self.color,
                'max_fsize': self._fsize,
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
        yield draw_text(self._box, 
                self._content, self.name, rotation=self.rotation, style=style)


class AttrFace(TextFace):

    def __init__(self, attr,
            formatter=None,
            name=None,
            color="black",
            min_fsize=6, max_fsize=15,
            ftype="sans-serif",
            padding_x=0, padding_y=0):

        TextFace.__init__(self, text="",
                name=name, color=color,
                min_fsize=min_fsize, max_fsize=max_fsize,
                ftype=ftype,
                padding_x=padding_x, padding_y=padding_y)

        self._attr = attr
        self.formatter = formatter

    def __name__(self):
        return "AttrFace"

    def _check_own_node(self):
        if not self.node:
            raise Exception(f'An associated **node** must be provided to compute **content**.')

    def get_content(self):
        content = str(getattr(self.node, self._attr, None)\
                or self.node.props.get(self._attr))
        self._content = self.formatter % content if self.formatter else content
        return self._content


class CircleFace(Face):

    def __init__(self, radius, color, name="", tooltip=None,
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

        self.radius = radius
        self.color = color
        # Drawing private properties
        self._max_radius = 0
        self._center = (0, 0)

        self.tooltip = tooltip

    def __name__(self):
        return "CircleFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, dx, dy = box
        zx, zy = self.zoom

        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        padding_x, padding_y = self.padding_x / zx, self.padding_y / (zy * r)

        max_dy = dy * zy * r
        max_diameter = min(dx * zx, max_dy) if dx != None else max_dy
        self._max_radius = min(max_diameter / 2, self.radius)

        cx = x + self._max_radius / zx - padding_x

        if pos == 'branch_top':
            cy = y + dy - self._max_radius / (zy * r) # container bottom

        elif pos == 'branch_bottom':
            cy = y + self._max_radius / (zy * r) # container top

        else: # branch_right and aligned
            if pos == 'aligned':
                self._max_radius = min(dy * zy * r / 2, self.radius)

            cx = x + self._max_radius / zx - padding_x # centered

            if pos == 'aligned_bottom':
                cy = y + dy - self._max_radius / zy

            elif pos == 'aligned_top':
                cy = y + self._max_radius / zy

            else:
                cy = y + dy / 2 # centered

        self._center = (cx, cy)
        self._box = Box(cx, cy,
                2 * (self._max_radius / zx - padding_x),
                2 * (self._max_radius) / (zy * r) - padding_y)

        return self._box

    def draw(self, drawer):
        self._check_own_variables()
        style = {'fill': self.color} if self.color else {}
        
        yield draw_circle(self._center, self._max_radius,
                self.name, style=style, tooltip=self.tooltip)


class RectFace(Face):
    def __init__(self, width, height, color='gray',
            opacity=0.7,
            text=None, fgcolor='black', # text color
            min_fsize=6, max_fsize=15,
            ftype='sans-serif',
            tooltip=None,
            name="",
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name, padding_x=padding_x, padding_y=padding_y)

        self.width = width
        self.height = height
        self.stretch = True
        self.color = color
        self.opacity = opacity
        # Text related
        self.text = str(text) if text is not None else None
        self.rotate_text = False
        self.fgcolor = fgcolor
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize

        self.tooltip = tooltip

    def __name__(self):
        return "RectFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, dx, dy = box
        zx, zy = self.zoom
        zx = 1 if self.stretch\
                and pos.startswith('aligned')\
                and drawer.TYPE != 'circ'\
                else zx

        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

        def get_dimensions(max_width, max_height):
            if not (max_width or max_height):
                return 0, 0
            if (type(max_width) in (int, float) and max_width <= 0) or\
               (type(max_height) in (int, float) and max_height <= 0):
                return 0, 0

            width = self.width / zx if self.width is not None else None
            height = self.height / zy if self.height is not None else None

            if width is None:
                return max_width or 0, min(height or float('inf'), max_height)
            if height is None:
                return min(width, max_width or float('inf')), max_height

            hw_ratio = height / width

            if max_width and width > max_width:
                width = max_width
                height = width * hw_ratio
            if max_height and height > max_height:
                height = max_height
                if not self.stretch or drawer.TYPE == 'circ':
                    width = height / hw_ratio

            height /= r  # in circular drawer
            return width, height

        max_dy = dy * r  # take into account circular mode

        if pos == 'branch_top':
            width, height = get_dimensions(dx, max_dy)
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch_bottom':
            width, height = get_dimensions(dx, max_dy)
            box = (x, y, width, height) # container top

        elif pos == 'branch_right':
            width, height = get_dimensions(dx, max_dy)
            box = (x, y + (dy - height) / 2, width, height)

        elif pos.startswith('aligned'):
            width, height = get_dimensions(None, dy)
            # height = min(dy, (self.height - 2 * self.padding_y) / zy)
            # width = min(self.width - 2 * self.padding_x) / zx

            if pos == 'aligned_bottom':
                y = y + dy - height
            elif pos == 'aligned_top':
                y = y
            else:
                y = y + (dy - height) / 2

            box = (x, y, width, height)

        self._box = Box(*box)
        return self._box

    def draw(self, drawer):
        self._check_own_variables()

        circ_drawer = drawer.TYPE == 'circ'
        style = {'fill': self.color, 'opacity': self.opacity}
        if self.text and circ_drawer:
            rect_id = get_random_string(10)
            style['id'] = rect_id

        yield draw_rect(self._box,
                self.name,
                style=style,
                tooltip=self.tooltip)

        if self.text:
            x, y, dx, dy = self._box
            zx, zy = self.zoom

            r = (x or 1e-10) if circ_drawer else 1
            if self.rotate_text:
                rotation = 90
                self.compute_fsize(dy * zy / (len(self.text) * zx) * r,
                                   dx * zx / zy, zx, zy)

                text_box = Box(x + (dx - self._fsize / (2 * zx)) / 2,
                        y + dy / 2,
                        dx, dy)
            else:
                rotation = 0
                self.compute_fsize(dx / len(self.text), dy, zx, zy)
                text_box = Box(x + dx / 2,
                        y + (dy - self._fsize / (zy * r)) / 2,
                        dx, dy)
            text_style = {
                'max_fsize': self._fsize,
                'text_anchor': 'middle',
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }

            if circ_drawer:
                offset = dx * zx + dy * zy * r / 2
                # Turn text upside down on bottom
                if y + dy / 2 > 0:
                    offset += dx * zx + dy * zy * r
                text_style['offset'] = offset

            yield draw_text(text_box,
                    self.text,
                    rotation=rotation,
                    anchor=('#' + str(rect_id)) if circ_drawer else None,
                    style=text_style)


class ArrowFace(RectFace):
    def __init__(self, width, height, orientation='right',
            color='gray',
            stroke_color='gray', stroke_width='1.5px',
            tooltip=None,
            text=None, fgcolor='black', # text color
            min_fsize=6, max_fsize=15,
            ftype='sans-serif',
            name="",
            padding_x=0, padding_y=0):

        RectFace.__init__(self, width=width, height=height,
                color=color, text=text, fgcolor=fgcolor,
                min_fsize=min_fsize, max_fsize=max_fsize, ftype=ftype,
                tooltip=tooltip,
                name=name, padding_x=padding_x, padding_y=padding_y)

        self.orientation = orientation
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

    def __name__(self):
        return "ArrowFace"

    @property
    def orientation(self):
        return self._orientation
    @orientation.setter
    def orientation(self, value):
        if value not in ('right', 'left'):
            raise InvalidUsage('Wrong ArrowFace orientation {value}. Set value to "right" or "left"')
        else:
            self._orientation = value

    def draw(self, drawer):
        self._check_own_variables()

        circ_drawer = drawer.TYPE == 'circ'
        style = {
            'fill': self.color,
            'opacity': 0.7,
            'stroke': self.stroke_color,
            'stroke-width': self.stroke_width,
            }
        if self.text and circ_drawer:
            rect_id = get_random_string(10)
            style['id'] = rect_id

        x, y, dx, dy = self._box
        zx, zy = self.zoom

        tip = min(5, dx * zx * 0.9) / zx
        yield draw_arrow(self._box,
                tip, self.orientation,
                self.name,
                style=style,
                tooltip=self.tooltip)

        if self.text:
            r = (x or 1e-10) if circ_drawer else 1
            if self.rotate_text:
                rotation = 90
                self.compute_fsize(dy * zy / (len(self.text) * zx) * r,
                                   dx * zx / zy, zx, zy)

                text_box = Box(x + (dx - self._fsize / (2 * zx)) / 2,
                        y + dy / 2,
                        dx, dy)
            else:
                rotation = 0
                self.compute_fsize(dx / len(self.text), dy, zx, zy)
                text_box = Box(x + dx / 2,
                        y + (dy - self._fsize / (zy * r)) / 2,
                        dx, dy)
            text_style = {
                'max_fsize': self._fsize,
                'text_anchor': 'middle',
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                'pointer-events': 'none',
                }

            if circ_drawer:
                offset = dx * zx + dy * zy * r / 2
                # Turn text upside down on bottom
                if y + dy / 2 > 0:
                    offset += dx * zx + dy * zy * r
                text_style['offset'] = offset

            yield draw_text(text_box,
                    self.text,
                    rotation=rotation,
                    anchor=('#' + str(rect_id)) if circ_drawer else None,
                    style=text_style)



# Selected faces
class SelectedFace(Face):
    def __init__(self, name):
        self.name = clean_text(name)
        self.name = f'selected_results_{self.name}'

    def __name__(self):
        return "SelectedFace"

class SelectedCircleFace(SelectedFace, CircleFace):
    def __init__(self, name, radius=15,
            padding_x=0, padding_y=0):

        SelectedFace.__init__(self, name)

        CircleFace.__init__(self, radius=radius, color=None,
                name=self.name,
                padding_x=padding_x, padding_y=padding_y)

    def __name__(self):
        return "SelectedCircleFace"

class SelectedRectFace(SelectedFace, RectFace):
    def __init__(self, name, width=15, height=15,
            text=None,
            padding_x=1, padding_y=0):

        SelectedFace.__init__(self, name);

        RectFace.__init__(self, width=width, height=height, color=None,
                name=self.name, text=text,
                padding_x=padding_x, padding_y=padding_y)

    def __name__(self):
        return "SelectedRectFace"


class OutlineFace(Face):
    def __init__(self,
            stroke_color=None, stroke_width=None,
            color=None, opacity=0.3,
            collapsing_height=5, # height in px at which outline becomes a line
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.outline = None
        self.collapsing_height = collapsing_height

        self.always_drawn = True

    def __name__(self):
        return "OutlineFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        self.outline = drawer.outline if drawer.outline \
            and len(drawer.outline) == 5 else SBox(0, 0, 0, 0, 0)

        self.zoom = drawer.zoom[0], drawer.zoom[1]

        if drawer.TYPE == 'circ':
            r, a, dr_min, dr_max, da = self.outline
            a1, a2 = clip_angles(a, a + da)
            self.outline = SBox(r, a1, dr_min, dr_max, a2 - a1)

        return self.get_box()

    def get_box(self):
        if self.outline and len(self.outline) == 5:
            x, y, dx_min, dx_max, dy = self.outline
            return Box(x, y, dx_max, dy)
        return Box(0, 0, 0, 0)

    def fits(self):
        return True

    def draw(self, drawer):
        nodestyle = self.node.sm_style
        style = {
                'stroke': nodestyle["outline_line_color"],
                'stroke-width': nodestyle["outline_line_width"],
                'fill': nodestyle["outline_color"],
                'fill-opacity': nodestyle["outline_opacity"],
                }
        x, y, dx_min, dx_max, dy = self.outline
        zx, zy = self.zoom
        circ_drawer = drawer.TYPE == 'circ'
        r = (x or 1e-10) if circ_drawer else 1
        if dy * zy * r < self.collapsing_height:
            # Convert to line if height less than one pixel
            p1 = (x, y + dy / 2)
            p2 = (x + dx_max, y + dy / 2)
            if circ_drawer:
                p1 = cartesian(p1)
                p2 = cartesian(p2)
            yield draw_line(p1, p2, style=style)
        else:
            yield draw_outline(self.outline, style=style)


class AlignLinkFace(Face):
    def __init__(self,
            stroke_color='gray', stroke_width=0.5,
            line_type=1, opacity=0.8):
        """Line types: 0 solid, 1 dotted, 2 dashed"""

        Face.__init__(self, padding_x=0, padding_y=0)

        self.line = None

        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.type = line_type;
        self.opacity = opacity

        self.always_drawn = True

    def __name__(self):
        return "AlignLinkFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.NPANELS > 1 and drawer.viewport and pos == 'branch_right':
            x, y = point
            dx, dy = size
            p1 = (x + bdx + dx_before, y + dy/2)
            if drawer.TYPE == 'rect':
                p2 = (drawer.viewport.x + drawer.viewport.dx, y + dy/2)
            else:
                aligned = sorted(drawer.tree_style.aligned_grid_dxs.items())
                # p2 = (drawer.node_size(drawer.tree)[0], y + dy/2)
                if not len(aligned):
                    return Box(0, 0, 0, 0)
                p2 = (aligned[0][1] - bdx, y + dy/2)
                if p1[0] > p2[0]:
                    return Box(0, 0, 0, 0)
                p1, p2 = cartesian(p1), cartesian(p2)

            self.line = (p1, p2)

        return Box(0, 0, 0, 0) # Should not take space

    def get_box(self):
        return Box(0, 0, 0, 0) # Should not take space

    def fits(self):
        return True

    def draw(self, drawer):

        if drawer.NPANELS < 2:
            return None

        style = {
                'type': self.type,
                'stroke': self.stroke_color,
                'stroke-width': self.stroke_width,
                'opacity': self.opacity,
                }
        if drawer.panel == 0 and drawer.viewport and\
          (self.node.is_leaf() or self.node.is_collapsed)\
          and self.line:
            p1, p2 = self.line
            yield draw_line(p1, p2, 'align-link', style=style)


class SeqFace(Face):
    def __init__(self, seq, seqtype='aa', poswidth=15,
            draw_text=True, max_fsize=15, ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.seq = seq
        self.seqtype = seqtype
        self.colors = _aacolors if self.seqtype == 'aa' else _ntcolors
        self.poswidth = poswidth  # width of each nucleotide/aa

        # Text
        self.draw_text = draw_text
        self.ftype = ftype
        self.max_fsize = max_fsize
        self._fsize = None

    def __name__(self):
        return "SeqFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos not in ('branch_right', 'aligned'):
            raise InvalidUsage(f'Position {pos} not allowed for SeqFace')

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box
        zx, zy = self.zoom
        dx = self.poswidth * len(self.seq) / zx

        if self.draw_text:
            self.compute_fsize(self.poswidth / zx, dy, zx, zy)

        self._box = Box(x, y, dx, dy)

        return self._box

    def draw(self, drawer):
        x0, y, _, dy = self._box
        zx, zy = self.zoom

        dx = self.poswidth / zx
        # Send sequences as a whole to be rendered by PIXIjs
        if self.draw_text:
            aa_type = "text"
        else:
            aa_type = "notext"

        yield [ f'pixi-aa_{aa_type}', Box(x0, y, dx * len(self.seq), dy), self.seq ]

        # Rende text if necessary
        # if self.draw_text:
            # text_style = {
                # 'max_fsize': self._fsize,
                # 'text_anchor': 'middle',
                # 'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                # }
            # for idx, pos in enumerate(self.seq):
                # x = x0 + idx * dx
                # r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
                # # Draw rect
                # if pos != '-':
                    # text_box = Box(x + dx / 2,
                            # y + (dy - self._fsize / (zy * r)) / 2,
                            # dx, dy)
                    # yield draw_text(text_box,
                            # pos,
                            # style=text_style)


class SeqMotifFace(Face):
    def __init__(self, seq=None, motifs=None, seqtype='aa',
            gap_format='line', seq_format='[]',
            width=None, height=None, # max height
            fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
            gap_linewidth=0.2,
            max_fsize=12, ftype='sans-serif',
            padding_x=0, padding_y=0):

        if not motifs and not seq:
            raise ValueError(
                    "At least one argument (seq or motifs) should be provided.")

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.seq = seq or '-' * max([m[1] for m in motifs])
        self.seqtype = seqtype

        self.autoformat = True  # block if 1px contains > 1 tile

        self.motifs = motifs
        self.overlaping_motif_opacity = 0.5

        self.seq_format = seq_format
        self.gap_format = gap_format
        self.gap_linewidth = gap_linewidth
        self.compress_gaps = False

        self.poswidth = 0.5
        self.w_scale = 1
        self.width = width    # sum of all regions' width if not provided
        self.height = height  # dynamically computed if not provided

        self.fg = '#000'
        self.bg = _aacolors if self.seqtype == 'aa' else _ntcolors
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.gapcolor = gapcolor

        self.triangles = {'^': 'top', '>': 'right', 'v': 'bottom', '<': 'left'}

        # Text
        self.ftype = ftype
        self._min_fsize = 8
        self.max_fsize = max_fsize
        self._fsize = None

        self.regions = []
        self.build_regions()

    def __name__(self):
        return "SeqMotifFace"

    def build_regions(self):
        """Build and sort sequence regions: seq representation and motifs"""
        seq = self.seq
        motifs = deepcopy(self.motifs)

        # if only sequence is provided, build regions out of gap spaces
        if not motifs:
            if self.seq_format == "seq":
                motifs = [[0, len(seq), "seq",
                    15, self.height, None, None, None]]
            else:
                motifs = []
                pos = 0
                for reg in re.split('([^-]+)', seq):
                    if reg:
                        if not reg.startswith("-"):
                            motifs.append([pos, pos+len(reg)-1,
                                self.seq_format,
                                self.poswidth, self.height,
                                self.fgcolor, self.bgcolor, None])
                        pos += len(reg)

        motifs.sort()

        # complete missing regions
        current_seq_pos = 0
        for index, mf in enumerate(motifs):
            start, end, typ, w, h, fg, bg, name = mf
            if start > current_seq_pos:
                pos = current_seq_pos
                for reg in re.split('([^-]+)', seq[current_seq_pos:start]):
                    if reg:
                        if reg.startswith("-") and self.seq_format != "seq":
                            self.regions.append([pos, pos+len(reg)-1,
                                "gap_"+self.gap_format, self.poswidth, self.height,
                                self.gapcolor, None, None])
                        else:
                            self.regions.append([pos, pos+len(reg)-1,
                                self.seq_format, self.poswidth, self.height,
                                self.fgcolor, self.bgcolor, None])
                    pos += len(reg)
                current_seq_pos = start

            self.regions.append(mf)
            current_seq_pos = end + 1

        if len(seq) > current_seq_pos:
            pos = current_seq_pos
            for reg in re.split('([^-]+)', seq[current_seq_pos:]):
                if reg:
                    if reg.startswith("-") and self.seq_format != "seq":
                        self.regions.append([pos, pos+len(reg)-1,
                            "gap_"+self.gap_format,
                            self.poswidth, 1,
                            self.gapcolor, None, None])
                    else:
                        self.regions.append([pos, pos+len(reg)-1,
                            self.seq_format,
                            self.poswidth, self.height,
                            self.fgcolor, self.bgcolor, None])
                    pos += len(reg)

        # Compute total width and
        # Detect overlapping, reducing opacity in overlapping elements
        total_width = 0
        prev_end = -1
        for idx, (start, end, shape, w, *_) in enumerate(self.regions):
            overlapping = abs(min(start - 1 - prev_end, 0))
            w = self.poswidth if shape.startswith("gap_") and self.compress_gaps else w
            total_width += (w or self.poswidth) * (end + 1 - start - overlapping)
            prev_end = end
            opacity = self.overlaping_motif_opacity if overlapping else 1
            self.regions[idx].append(opacity)
            if overlapping:
                self.regions[idx - 1][-1] = opacity

        if self.width:
            self.w_scale = self.width / total_width
        else:
            self.width = total_width

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos != 'branch_right' and not pos.startswith('aligned'):
            raise InvalidUsage(f'Position {pos} not allowed for SeqMotifFace')

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box
        zx, zy = self.zoom

        self.viewport = (drawer.viewport.x, drawer.viewport.x + drawer.viewport.dx)

        self._box = Box(x, y, self.width / zx, dy)
        return self._box

    def fits(self):
        return True

    def draw(self, drawer):
        # Only leaf/collapsed branch_right or aligned
        x0, y, _, dy = self._box
        zx, zy = self.zoom

        if self.viewport and len(self.seq):
            vx0, vx1 = self.viewport
            too_small = ((vx1 - vx0) * zx) / (len(self.seq) / zx) < 3
            if self.seq_format in [ "seq", "compactseq" ] and too_small:
                self.seq_format = "[]"
                self.regions = []
                self.build_regions()
            if self.seq_format == "[]" and not too_small:
                self.seq_format = "seq"
                self.regions = []
                self.build_regions()


        x = x0
        prev_end = -1

        if self.gap_format in ["line", "-"]:
            p1 = (x0, y + dy / 2)
            p2 = (x0 + self.width, y + dy / 2)
            if drawer.TYPE == 'circ':
                p1 = cartesian(p1)
                p2 = cartesian(p2)
            yield draw_line(p1, p2, style={'stroke-width': self.gap_linewidth,
                                           'stroke': self.gapcolor})

        for item in self.regions:
            if len(item) == 9:
                start, end, shape, posw, h, fg, bg, text, opacity = item
            else:
                continue

            # if not self.in_aligned_viewport((start / zx, end / zx)):
                # continue

            posw = (posw or self.poswidth) * self.w_scale
            w = posw * (end + 1 - start)
            style = { 'fill': bg, 'opacity': opacity }

            # Overlapping
            overlapping = abs(min(start - 1 - prev_end, 0))
            if overlapping:
                x -= posw * overlapping
            prev_end = end

            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            default_h = dy * zy * r
            h = min([h or default_h, self.height or default_h, default_h]) / zy
            box = Box(x, y + (dy - h / r) / 2, w, h / r)

            if shape.startswith("gap_"):
                if self.compress_gaps:
                    w = posw
                x += w
                continue

            # Line
            if shape in ['line', '-']:
                p1 = (x, y + dy / 2)
                p2 = (x + w, y + dy / 2)
                if drawer.TYPE == 'circ':
                    p1 = cartesian(p1)
                    p2 = cartesian(p2)
                yield draw_line(p1, p2, style={'stroke-width': 0.5, 'stroke': fg})

            # Rectangle
            elif shape == '[]':
                yield [ "pixi-block", box ]

            elif shape == '()':
                style['rounded'] = 1;
                yield draw_rect(box, '', style=style)

            # Rhombus
            elif shape == '<>':
                yield draw_rhombus(box, style=style)

            # Triangle
            elif shape in self.triangles.keys():
                box = Box(x, y + (dy - h / r) / 2, w, h / r)
                yield draw_triangle(box, self.triangles[shape], style=style)

            # Circle/ellipse
            elif shape == 'o':
                center = (x + w / 2, y + dy / 2)
                rx = w * zx / 2
                ry = h * zy / 2
                if rx == ry:
                    yield draw_circle(center, rx, style=style)
                else:
                    yield draw_ellipse(center, rx, ry, style=style)

            # Sequence and compact sequence
            elif shape in ['seq', 'compactseq']:
                seq = self.seq[start : end + 1]
                if self.viewport:
                    sx, sy, sw, sh = box
                    sposw = sw / len(seq)
                    viewport_start = self.viewport[0] - self.viewport_margin / zx
                    viewport_end = self.viewport[1] + self.viewport_margin / zx
                    sm_x = max(viewport_start - sx, 0)
                    sm_start = round(sm_x / sposw)
                    sm_end = len(seq) - round(max(sx + sw - viewport_end, 0) / sposw)
                    seq = seq[sm_start:sm_end]
                    sm_box = (sm_x, sy, sposw * len(seq), sh)
                if shape == 'compactseq' or posw * zx < self._min_fsize:
                    aa_type = "notext"
                else:
                    aa_type = "text"
                yield [ f'pixi-aa_{aa_type}', sm_box, seq ]


            # Text on top of shape
            if text:
                try:
                    ftype, fsize, color, text = text.split("|")
                    fsize = int(fsize)
                except:
                    ftype, fsize, color = self.ftype, self.max_fsize, (fg or self.fcolor)
                self.compute_fsize(w / len(text), h, zx, zy, fsize)
                text_box = Box(x + w / 2,
                        y + (dy - self._fsize / (zy * r)) / 2,
                        self._fsize / (zx * CHAR_HEIGHT),
                        self._fsize / zy)
                text_style = {
                    'max_fsize': self._fsize,
                    'text_anchor': 'middle',
                    'ftype': f'{ftype}, sans-serif',
                    'fill': color,
                    }
                yield draw_text(text_box, text, style=text_style)

            # Update x to draw consecutive motifs
            x += w


class AlignmentFace(Face):
    def __init__(self, seq, seqtype='aa',
            gap_format='line', seq_format='[]',
            width=None, height=None, # max height
            fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
            gap_linewidth=0.2,
            max_fsize=12, ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.seq = seq
        self.seqlength = len(self.seq)
        self.seqtype = seqtype

        self.autoformat = True  # block if 1px contains > 1 tile

        self.seq_format = seq_format
        self.gap_format = gap_format
        self.gap_linewidth = gap_linewidth
        self.compress_gaps = False

        self.poswidth = 5
        self.w_scale = 1
        self.width = width    # sum of all regions' width if not provided
        self.height = height  # dynamically computed if not provided

        total_width = self.seqlength * self.poswidth
        if self.width:
            self.w_scale = self.width / total_width
        else:
            self.width = total_width

        self.bg = _aacolors if self.seqtype == 'aa' else _ntcolors
        # self.fgcolor = fgcolor
        # self.bgcolor = bgcolor
        self.gapcolor = gapcolor

        # Text
        self.ftype = ftype
        self._min_fsize = 8
        self.max_fsize = max_fsize
        self._fsize = None

        self.blocks = []
        self.build_blocks()

    def __name__(self):
        return "AlignmentFace"

    def get_seq(self, start, end):
        """Retrieves sequence given start, end"""
        return self.seq[start:end]

    def build_blocks(self):
        pos = 0
        for reg in re.split('([^-]+)', self.seq):
            if reg:
                if not reg.startswith("-"):
                    self.blocks.append([pos, pos + len(reg) - 1])
                pos += len(reg)

        self.blocks.sort()

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos != 'branch_right' and not pos.startswith('aligned'):
            raise InvalidUsage(f'Position {pos} not allowed for SeqMotifFace')

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box

        zx, zy = self.zoom
        zx = 1 if drawer.TYPE != 'circ' else zx

            # zx = drawer.zoom[0]
            # self.zoom = (zx, zy)

        if drawer.TYPE == "circ":
            self.viewport = (0, drawer.viewport.dx)
        else:
            self.viewport = (drawer.viewport.x, drawer.viewport.x + drawer.viewport.dx)

        self._box = Box(x, y, self.width / zx, dy)
        return self._box

    def draw(self, drawer):
        def get_height(x, y):
            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            default_h = dy * zy * r
            h = min([self.height or default_h, default_h]) / zy
            # h /= r
            return y + (dy - h) / 2, h

        # Only leaf/collapsed branch_right or aligned
        x0, y, dx, dy = self._box
        zx, zy = self.zoom
        zx = drawer.zoom[0] if drawer.TYPE == 'circ' else zx


        if self.gap_format in ["line", "-"]:
            p1 = (x0, y + dy / 2)
            p2 = (x0 + self.width, y + dy / 2)
            if drawer.TYPE == 'circ':
                p1 = cartesian(p1)
                p2 = cartesian(p2)
            yield draw_line(p1, p2, style={'stroke-width': self.gap_linewidth,
                                           'stroke': self.gapcolor})
        vx0, vx1 = self.viewport
        too_small = (self.width * zx) / (self.seqlength) < 1

        posw = self.poswidth * self.w_scale
        viewport_start = vx0 - self.viewport_margin / zx
        viewport_end = vx1 + self.viewport_margin / zx
        sm_x = max(viewport_start - x0, 0)
        sm_start = round(sm_x / posw)
        w = self.seqlength * posw
        sm_x0 = x0 if drawer.TYPE == "rect" else 0
        sm_end = self.seqlength - round(max(sm_x0 + w - viewport_end, 0) / posw)

        if too_small or self.seq_format == "[]":
            for start, end in self.blocks:
                if end >= sm_start and start <= sm_end:
                    bstart = max(sm_start, start)
                    bend = min(sm_end, end)
                    bx = x0 + bstart * posw
                    by, bh = get_height(bx, y)
                    box = Box(bx, by, (bend + 1 - bstart) * posw, bh)
                    yield [ "pixi-block", box ]

        else:
            seq = self.get_seq(sm_start, sm_end)
            sm_x = sm_x if drawer.TYPE == 'rect' else x0
            y, h = get_height(sm_x, y)
            sm_box = Box(sm_x, y, posw * len(seq), h)

            if self.seq_format == 'compactseq' or posw * zx < self._min_fsize:
                aa_type = "notext"
            else:
                aa_type = "text"
            yield [ f'pixi-aa_{aa_type}', sm_box, seq ]



class ScaleFace(Face):
    def __init__(self, name='', width=None, color='black',
            scale_range=(0, 0), tick_width=80, line_width=1,
            formatter='%.0f',
            min_fsize=6, max_fsize=12, ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

        self.width = width
        self.height = None
        self.range = scale_range

        self.color = color
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self._fsize = max_fsize
        self.ftype = ftype
        self.formatter = formatter

        self.tick_width = tick_width
        self.line_width = line_width

        self.vt_line_height = 10

    def __name__(self):
        return "ScaleFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box
        zx, zy = self.zoom

        self.viewport = (drawer.viewport.x, drawer.viewport.x + drawer.viewport.dx)

        self.height = (self.line_width + 10 + self.max_fsize) / zy

        height = min(dy, self.height)

        if pos == "aligned_bottom":
            y = y + dy - height

        self._box = Box(x, y, self.width / zx, height)
        return self._box

    def draw(self, drawer):
        x0, y, _, dy = self._box
        zx, zy = self.zoom

        p1 = (x0, y + dy - 5 / zy)
        p2 = (x0 + self.width, y + dy - self.vt_line_height / (2 * zy))
        if drawer.TYPE == 'circ':
            p1 = cartesian(p1)
            p2 = cartesian(p2)
        yield draw_line(p1, p2, style={'stroke-width': self.line_width,
                                       'stroke': self.color})


        nticks = round((self.width * zx) / self.tick_width)
        dx = self.width / nticks
        range_factor = (self.range[1] - self.range[0]) / self.width

        if self.viewport:
            sm_start = round(max(self.viewport[0] - self.viewport_margin - x0, 0) / dx)
            sm_end = nticks - round(max(x0 + self.width - (self.viewport[1] +
                self.viewport_margin), 0) / dx)
        else:
            sm_start, sm_end = 0, nticks

        for i in range(sm_start, sm_end + 1):
            x = x0 + i * dx
            number = range_factor * i * dx

            if number == 0:
                text = "0"
            else:
                text = self.formatter % number if self.formatter else str(number)

            text = text.rstrip('0').rstrip('.') if '.' in text else text

            self.compute_fsize(self.tick_width / len(text), dy, zx, zy)
            text_style = {
                'max_fsize': self._fsize,
                'text_anchor': 'middle',
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
            text_box = Box(x,
                    y,
                    # y + (dy - self._fsize / (zy * r)) / 2,
                    dx, dy)

            yield draw_text(text_box, text, style=text_style)

            p1 = (x, y + dy - self.vt_line_height / zy)
            p2 = (x, y + dy)

            yield draw_line(p1, p2, style={'stroke-width': self.line_width,
                                           'stroke': self.color})


class PieChartFace(CircleFace):

    def __init__(self, radius, data, name="",
            padding_x=0, padding_y=0, tooltip=None):

        super().__init__(self, name=name, color=None,
            padding_x=padding_x, padding_y=padding_y)

        self.radius = radius
        # Drawing private properties
        self._max_radius = 0
        self._center = (0, 0)

        # data = [ [name, value, color, tooltip], ... ]
        # self.data = [ (name, value, color, tooltip, a, da) ]
        self.data = []
        self.compute_pie(list(data))
        self.tooltip = tooltip

    def __name__(self):
        return "PieChartFace"

    def compute_pie(self, data):
        total_value = sum(d[1] for d in data)

        a = 0
        for name, value, color, tooltip in data:
            da = (value / total_value) * 2 * pi
            self.data.append((name, value, color, tooltip, a, da))
            a += da

        assert a >= 2 * pi - 1e-5 and a <= 2 * pi + 1e-5, "Incorrect pie"

    def draw(self, drawer):
        # Draw circle if only one datum
        if len(self.data) == 1:
            self.color = self.data[0][2]
            yield from CircleFace.draw(self, drawer)

        else:
            for name, value, color, tooltip, a, da in self.data:
                style = { 'fill': color }
                yield draw_slice(self._center, self._max_radius, a, da,
                        "", style=style, tooltip=tooltip)


class HTMLFace(RectFace):
    def __init__(self, html, width, height, name="", padding_x=0, padding_y=0):

        RectFace.__init__(self, width=width, height=height,
                name=name, padding_x=padding_x, padding_y=padding_y)

        self.content = html

    def __name__(self):
        return "HTMLFace"

    def draw(self, drawer):
        yield draw_html(self._box, self.content)


class ImgFace(RectFace):
    def __init__(self, img_path, width, height, name="", padding_x=0, padding_y=0):

        RectFace.__init__(self, width=width, height=height,
                name=name, padding_x=padding_x, padding_y=padding_y)



        with open(img_path, "rb") as handle:
            img = base64.b64encode(handle.read()).decode("utf-8")
        extension = pathlib.Path(img_path).suffix[1:]
        if extension not in ALLOWED_IMG_EXTENSIONS:
            print("The image does not have an allowed format: " +
                    extension + " not in " + str(ALLOWED_IMG_EXTENSIONS))

        self.content = f'data:image/{extension};base64,{img}'

        self.stretch = False

    def __name__(self):
        return "ImgFace"

    def draw(self, drawer):
        yield draw_img(self._box, self.content)


class LegendFace(Face):

    def __init__(self,
            colormap,
            title,
            min_fsize=6, max_fsize=15, ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, name=title,
                padding_x=padding_x, padding_y=padding_y)

        self._content = True
        self.title = title
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self._fsize = max_fsize
        self.ftype = ftype

    def __name__(self):
        return "LegendFace"

    def draw(self, drawer):
        self._check_own_variables()

        style = {'fill': self.color, 'opacity': self.opacity}

        x, y, dx, dy = self._box
        zx, zy = self.zoom

        entry_h = min(15 / zy, dy / (len(self.colormap.keys()) + 2))

        title_box = Box(x, y + 5, dx, entry_h)
        text_style = {
            'max_fsize': self.compute_fsize(title_box.dx, title_box.dy, zx, zy),
            'text_anchor': 'middle',
            'ftype': f'{self.ftype}, sans-serif', # default sans-serif
            }

        yield draw_text(title_box,
                self.title,
                style=text_style)

        entry_y = y + 2 * entry_h
        for value, color in self.colormap.items():
            text_box = Box(x, entry_y, dx, entry_h)
            yield draw_text(text_box,
                    value,
                    style=text_style)
            ty += entry_h
