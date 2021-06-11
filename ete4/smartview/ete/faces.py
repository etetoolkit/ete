import re
from math import pi

from ete4.smartview.ete.draw import Box, SBox,\
                                    draw_text, draw_circle, draw_rect,\
                                    draw_outline,\
                                    cartesian, clip_angles


def swap_pos(pos, angle):
    if abs(angle) >= pi / 2:
        if pos == 'branch-top':
            pos = 'branch-bottom'
        elif pos == 'branch-bottom':
            pos = 'branch-top'
    return pos


class Face(object):

    def __init__(self, name="", padding_x=0, padding_y=0, is_constrained=True):
        self.node = None
        self.name = name
        self._content = "Empty"
        self._box = None
        self.is_constrained = is_constrained
        self.padding_x = padding_x
        self.padding_y = padding_y

    def __name__(self):
        return "face"

    def get_content(self):
        return self._content

    def get_box(self):
        self._check_own_variables()
        return self._box

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdx, bdy, 
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        self._check_own_content()
        x, y = point
        dx, dy = size
        zx, zy = drawer.zoom
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

        padding_x = self.padding_x / zx
        padding_y = self.padding_y / (zy * r)

        if pos == 'branch-top':  # above the branch
            avail_dx = dx / n_col
            avail_dy = bdy / n_row
            xy = (x + dx_before, y + bdy - avail_dy - dy_before)

        elif pos == 'branch-bottom':  # below the branch
            avail_dx = dx / n_col
            avail_dy = (dy - bdy) / n_row
            xy = (x + dx_before, y + bdy + dy_before)

        elif pos == 'branch-top-left':  # left of branch-top
            width, height = get_dimensions(dx / n_col, bdy)
            box = (x - (col + 1) * dx/n_col, y, width, height)

        elif pos == 'branch-bottom-left':  # left of branch-bottom
            width, height = get_dimensions(dx / n_col, dy - bdy)
            box = (x - (col + 1) * dx/n_col, y + bdy, width, height)

        elif pos == 'branch-right':  # right of node
            avail_dx = dx / n_col
            avail_dy = min(bdy, dy - bdy) * 2 / n_row
            xy = (x + bdx + dx_before,
                  y + bdy + (row - n_row / 2) * avail_dy)

        elif pos == 'aligned': # right of tree
            avail_dx = 10 / zx # arbitrary value. Should be overriden
            avail_dy = dy / n_row
            aligned_x = drawer.node_size(drawer.tree)[0]\
                    if drawer.panel == 0 else drawer.xmin
            xy = (aligned_x + dx_before,
                  y + bdy + (row - n_row / 2) * avail_dy)
        else:
            raise InvalidUsage(f'unkown position {pos}')

        self._box = Box(
            xy[0] + padding_x,
            xy[1] + padding_y,
            max(avail_dx - 2 * padding_x, 0),
            max(avail_dy - 2 * padding_y, 0))

        return self._box

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
            max_fsize=15, ftype="sans-serif",
            padding_x=0, padding_y=0,
            is_constrained=True):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self._content = text
        self.color = color
        self.max_fsize = max_fsize
        self._fsize = max_fsize
        self.ftype = ftype

    def __name__(self):
        return "TextFace"

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdx, bdy, 
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        zx, zy = drawer.zoom
        x, y , dx, dy = box
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

        hw_ratio = 1.5
        def fit_fontsize(text, dx, dy):
            max_dchar = dx * zx * r / len(text) if dx != None else float('inf')
            max_dy = dy * zy * r

            dchar = min(max_dy / hw_ratio, max_dchar) / r
            dy = dchar * hw_ratio
            return dchar * len(text) / zx, dy / (zy * r)

        max_dy = min(dy, self.max_fsize / zy)

        if pos == 'branch-top':
            width, height = fit_fontsize(self._content, dx, max_dy)
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch-bottom':
            width, height = fit_fontsize(self._content, dx, max_dy)
            box = (x, y, width, height) # container top

        else: # branch-right and aligned
            width, height = fit_fontsize(self._content, None, max_dy)
            box = (x, y + (dy - height) / 2, width, height)

        self._fsize = height * zy * r

        self._box = Box(*box)
        return self._box

    def draw(self):
        self._check_own_variables()
        style = {
                'fill': self.color,
                'max_fsize': self._fsize,
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
        return draw_text(self._box, 
                self._content, self.name, style)


class AttrFace(TextFace):

    def __init__(self, attr, 
            name=None,
            color="black", 
            max_fsize=15, ftype="sans-serif",
            padding_x=0, padding_y=0,
            is_constrained=True):


        TextFace.__init__(self, text="",
                name=name, color=color,
                max_fsize=max_fsize, ftype=ftype,
                padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self._attr = attr

    def __name__(self):
        return "LabelFace"

    def _check_own_node(self):
        if not self.node:
            raise Exception(f'An associated **node** must be provided to compute **content**.')

    def get_content(self):
        self._check_own_node()
        self._content = str(getattr(self.node, self._attr, None)\
                or self.node.properties.get(self._attr))
        return self._content


class LabelFace(AttrFace):

    def __init__(self, expression):
        Face.__init__(self)
        self._code = self.compile_expression(expression)
        self.name = "label_" + expression
        self._content = None

    def __name__(self):
        return "LabelFace"
    
    def get_content(self):
        self._check_own_node()
        self._content = str(self.safer_eval(self._code))
        return self._content

    def compile_expression(self, expression):
        try:
            code = compile(expression, '<string>', 'eval')
        except SyntaxError as e:
            raise InvalidUsage(f'compiling expression: {e}')
        return code

    def safer_eval(self, code):
        "Return a safer version of eval(code, context)"
        context = {
            'name': self.node.name, 'is_leaf': self.node.is_leaf(),
            'length': self.node.dist, 'dist': self.node.dist, 'd': self.node.dist,
            'support': self.node.support,
            'properties': self.node.properties, 'p': self.node.properties,
            'get': dict.get, 'split': str.split,
            'children': self.node.children, 'ch': self.node.children,
            'regex': re.search,
            'len': len, 'sum': sum, 'abs': abs, 'float': float, 'pi': pi
        }
        for name in code.co_names:
            if name not in context:
                raise InvalidUsage('invalid use of %r during evaluation' % name)
        return eval(code, {'__builtins__': {}}, context)


class CircleFace(Face):

    def __init__(self, radius, color, name="",
            padding_x=0, padding_y=0, is_constrained=True):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self.radius = radius
        self.color = color
        # Drawing private properties
        self._max_radius = 0
        self._center = (0, 0)

    def __name__(self):
        return "CircleFace"

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, dx, dy = box
        zx, zy = drawer.zoom
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        padding_x, padding_y = self.padding_x / zx, self.padding_y / (zy * r)

        max_dy = dy * zy * r
        max_diameter = min(dx * zx, max_dy)
        self._max_radius = min(max_diameter / 2, self.radius)

        cx = x + self._max_radius / zx - padding_x

        if pos == 'branch-top':
            cy = y + dy - self._max_radius / (zy * r) # container bottom

        elif pos == 'branch-bottom':
            cy = y + self._max_radius / (zy * r) # container top

        else: # branch-right and aligned
            self._max_radius = min(dy * zy * r / 2, self.radius)
            cx = x + self._max_radius / zx - padding_x # centered
            cy = y + dy / 2 # centered

        self._center = (cx, cy)
        self._box = Box(cx, cy, 
                2 * (self._max_radius / zx - padding_x),
                2 * (self._max_radius) / (zy * r) - padding_y)

        return self._box
        
    def draw(self):
        self._check_own_variables()
        return draw_circle(self._center, self._max_radius,
                self.name, style={'fill': self.color})


class RectFace(Face):
    def __init__(self, width, height, color="black",
            padding_x=0, padding_y=0, is_constrained=True):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self.width = width
        self.height = height
        self.color = color

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, dx, dy = box
        zx, zy = drawer.zoom
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

        def get_dimensions(max_width, max_height):
            if not (max_width or max_height):
                return 0, 0
            if (type(max_width) in (int, float) and max_width <= 0) or\
               (type(max_height) in (int, float) and max_height <= 0):
                return 0, 0

            width = self.width / zx
            height = self.height / zy
            hw_ratio = height / width

            if max_width and width > max_width:
                width = max_width
                height = width * hw_ratio
            if max_height and height > max_height:
                height = max_height
                width = height / hw_ratio

            height /= r  # in circular drawer
            return width, height

        max_dy = dy * r  # take into account circular mode

        if pos == 'branch-top':
            width, height = get_dimensions(dx, max_dy)
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch-bottom':
            width, height = get_dimensions(dx, max_dy)
            box = (x, y, width, height) # container top

        elif pos == 'branch-right':
            width, height = get_dimensions(None, max_dy)
            box = (x, y + (dy - height) / 2, width, height)

        elif pos == 'aligned':
            width = (self.width - 2 * self.padding_x) / zx
            height = min(dy, (self.height - 2 * self.padding_y) / zy) / r
            box = (x, y + (dy - height) / 2, width, height)

        self._box = Box(*box)
        return self._box

    def draw(self):
        self._check_own_variables()
        return draw_rect(self._box,
                self.name,
                style={'fill': self.color})


class OutlineFace(Face):
    def __init__(self, 
            stroke_color='black', stroke_width=1,
            color="lightgray", opacity=1,
            padding_x=0, padding_y=0, is_constrained=True):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self.opacity = opacity
        self.color = color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.outline = None

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdx, bdy,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        self.outline = drawer.outline

        if drawer.TYPE == 'circ':
            r, a, dr_min, dr_max, da = self.outline
            a1, a2 = clip_angles(a, a + da)
            self.outline = SBox(r, a1, dr_min, dr_max, a2 - a1)

        return self.get_box()

    def get_box(self):
        if not self.outline:
            raise Exception(f'**Outline** has not been computed yet.\
                    \nPlease run `compute_bounding_box()` first')

        x, y, dx_min, dx_max, dy = self.outline
        return Box(x, y, dx_max, dy)

    def draw(self):
        style = {
                'stroke': self.stroke_color,
                'stroke-width': self.stroke_width,
                'fill': self.color,
                'fill-opacity': self.opacity,
                }
        return draw_outline(self.outline, style)
