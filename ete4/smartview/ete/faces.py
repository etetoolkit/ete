import re
from math import pi

from ete4.smartview.ete.draw import Box, draw_text, draw_circle, draw_rect, cartesian


class Face(object):

    def __init__(self, padding_x=0, padding_y=0, constrained=True):
        self.node = None
        self.type = 'svg'
        self._content = None
        self._box = None
        self.is_constrained = constrained
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
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before):

        self._check_own_content()
        x, y = point
        dx, dy = size
        zx, zy = drawer.zoom
        padding_x, padding_y = self.padding_x / zx, self.padding_y / zy

        if pos == 'branch-top':  # above the branch
            avail_dx = dx / n_col
            avail_dy = bdy / n_row
            xy = (x + dx_before,
                  y + (n_row - row - 1) * avail_dy)

        elif pos == 'branch-bottom':  # below the branch
            avail_dx = dx / n_col
            avail_dy = (dy - bdy) / n_row
            xy = (x + dx_before,
                  y + bdy + row * avail_dy)

        elif pos == 'branch-top-left':  # left of branch-top
            width, height = get_dimensions(dx / n_col, bdy)
            box = (x - (col + 1) * dx/n_col, y, width, height)

        elif pos == 'branch-bottom-left':  # left of branch-bottom
            width, height = get_dimensions(dx / n_col, dy - bdy)
            box = (x - (col + 1) * dx/n_col, y + bdy, width, height)

        elif pos == 'float':  # right of node
            avail_dx = dx / n_col
            avail_dy = min(bdy, dy - bdy) * 2 / n_row
            xy = (x + dx + dx_before,
                  y + bdy + (row - n_row / 2) * avail_dy)

        elif pos == 'aligned': # right of tree
            avail_dx = 10 / zx # arbitrary value. Should be overriden
            avail_dy = dy / n_row
            aligned_x = drawer.node_size(drawer.tree)[0] if drawer.panel == 0 else drawer.xmin
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

    def __init__(self, text, text_type="", color="black", constrained=True):
        Face.__init__(self, constrained=constrained)
        self._anchor = None
        self._content = text
        self._text_type = text_type
        self._color = color

    def __name__(self):
        return "TextFace"

    def _check_own_variables(self):
        super()._check_own_variables()
        if not self._anchor:
            raise Exception(f'**Anchor** has not been computed yet.\
                    \nPlease run `compute_bounding_box()` first')

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before):

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before)

        x, y , dx, dy = box

        if pos == 'branch-top':
            anchor = (0, 1)  # left x, bottom y

        elif pos == 'branch-bottom':
            anchor = (0, 0)  # left x, top y

        elif pos == 'branch-top-left':
            box = (x - (col + 1) * dx/n_col, y, dx/n_col, bdy)  # left of branch-top
            anchor = (1, 1)  # right x, bottom y

        elif pos == 'branch-bottom-left':
            box = (x - (col + 1) * dx/n_col, y + bdy, dx/n_col, dy - bdy)  # etc.
            anchor = (1, 0)  # right x, top y

        elif pos == 'float':
            fit = text_fit(self._content, dy)
            box = (x, y, fit, dy)
            anchor = (0, 0.5)  # left x, branch position in y

        elif pos == 'aligned':
            fit = text_fit(self._content, dy)
            box = (x, y, fit, dy)
            anchor = (0, 0.5)  # left x, branch position in y

        else:
            raise InvalidUsage(f'unkown position {pos}')

        self._box = Box(*box)
        self._anchor = anchor
        return self._box

    def draw(self):
        self._check_own_variables()
        return draw_text(self._box, self._anchor, 
                self._content, self._text_type, 
                style={'fill': self._color})


class AttrFace(TextFace):

    def __init__(self, attr, color="black", constrained=True):
        Face.__init__(self, constrained=constrained)
        self._attr = attr
        self._text_type = "attr_" + self._attr
        self._color = color

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
        self._text_type = "label_" + expression

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

    def __init__(self, radius, fill, circle_type="",
            padding_x=0, padding_y=0, constrained=True):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                constrained=constrained)
        self.radius = radius
        self.fill = fill
        self._circle_type = circle_type
        # Drawing private properties
        self._max_radius = 0
        self._center = (0, 0)
        self._content = True

    def __name__(self):
        return "CircleFace"

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before):

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before)

        x, y, dx, dy = box
        zx, zy = drawer.zoom
        padding_x, padding_y = self.padding_x / zx, self.padding_y / zy

        max_diameter = min(dx * zx, dy * zy)
        self._max_radius = min(max_diameter / 2, self.radius)

        cx = x + self._max_radius / zx - padding_x

        if pos == 'branch-top':
            cy = y + dy - self._max_radius / zy # container bottom

        elif pos == 'branch-bottom':
            cy = y + self._max_radius / zy # container top

        elif pos == 'branch-top-left':
            pass

        elif pos == 'branch-bottom-left':
            pass

        elif pos == 'float':
            cx = x + dx / 2 - padding_x # centered
            cy = y + dy / 2 # centered

        elif pos == 'aligned':
            self._max_radius = min(dy * zy / 2, self.radius)
            cx = x + self._max_radius / zx - padding_x
            cy = y + dy / 2 # centered

        self._center = (cx, cy)
        
        if drawer.TYPE == 'circ':
            self._center = cartesian(self._center)

        self._box = Box(cx, cy, 
                2 * (self._max_radius / zx - padding_x),
                2 * (self._max_radius) / zy - padding_y)

        return self._box
        
    def draw(self):
        self._check_own_variables()
        return draw_circle(self._center, self._max_radius,
                self._circle_type, style={'fill': self.fill})


class RectFace(Face):
    def __init__(self, width, height, color="black",
            padding_x=0, padding_y=0, constrained=True):
        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                constrained=constrained)
        self.width = width
        self.height = height
        self._color = color
        self._content = True
        self._rect_type = 'rect_' + 'rect'

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before):

        def get_dimensions(max_width, max_height):
            width = self.width / zx
            height = self.height / zy
            hw_ratio = height / width

            if width > max_width:
                width = max_width
                height = width * hw_ratio
            if height > max_height:
                height = max_height
                width = height / hw_ratio

            return width, height

        box = super().compute_bounding_box( 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row,
            n_row, n_col,
            dx_before)

        x, y, dx, dy = box
        zx, zy = drawer.zoom

        if pos == 'branch-top':
            width, height = get_dimensions(dx, dy)
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch-bottom':
            width, height = get_dimensions(dx, dy)
            box = (x, y, width, height) # container top

        elif pos == 'branch-top-left':
            width, height = get_dimensions(dx / n_col, bdy)
            box = (x - (col + 1) * dx/n_col, y, width, height)

        elif pos == 'branch-bottom-left':
            width, height = get_dimensions(dx / n_col, dy - bdy)
            box = (x - (col + 1) * dx/n_col, y + bdy, width, height)

        elif pos == 'float':
            width, height = get_dimensions(dx, dy)
            box = (x + (dx - width) / 2, y + (dy - height) / 2, width, height)

        elif pos == 'aligned':
            width = (self.width - 2 * self.padding_x) / zx
            height = min(dy, (self.height - 2 * self.padding_y) / zy)
            box = (x, y + (dy - height) / 2, width, height)

        if drawer.TYPE == 'circ':
            r, a = cartesian((box[0], box[1]))
            dr, da = box[2:]
            box = (r, a, dr, da)

        self._box = Box(*box)
        return self._box

    def draw(self):
        self._check_own_variables()
        return draw_rect(self._box,
                self._rect_type,
                style={'fill': self._color})
