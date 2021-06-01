import re
from math import pi

from ete4.smartview.ete.draw import draw_text, draw_circle


class Face(object):

    def __init__(self):
        self.node = None
        self.type = 'svg'
        self._content = None
        self._box = None
        self._anchor = None

    def __name__(self):
        return "face"

    def get_content(self):
        return self._content

    def get_box(self):
        self._check_own_variables()
        return self._box

    def _check_own_content(self):
        if not self._content:
            raise Exception(f'**Content** has not been computed yet.')

    def _check_own_variables(self):
        if not self._box:
            raise Exception(f'**Box** has not been computed yet.\
                    \nPlease run `compute_box_anchor()` first')
        if not self._anchor:
            raise Exception(f'**Anchor** has not been computed yet.\
                    \nPlease run `compute_box_anchor()` first')
        self._check_own_content()
        return


class TextFace(Face):

    def __init__(self, text, text_type="", color="black"):
        Face.__init__(self)
        self._content = text
        self._text_type = text_type
        self._color = color

    def __name__(self):
        return "TextFace"

    def compute_bounding_box(self, 
            drawer,
            point, size,
            bdy, text_fit, 
            pos, row, col,
            n_row, n_col):

        self._check_own_content()
        x, y = point
        dx, dy = size
        i = col
        j = row
        n = n_col
        if pos == 'branch-top':
            box = (x + col * dx/n_col, y + (n_row - row - 1) * bdy/n_row,
                   dx/n_col, bdy/n_row)  # above the branch
            anchor = (0, 1)  # left x, bottom y
        elif pos == 'branch-bottom':
            box = (x + col * dx/n_col, y + bdy + row * dy/n_row,
                   dx/n_col, dy - bdy)  # below the branch
            anchor = (0, 0)  # left x, top y
        elif pos == 'branch-top-left':
            box = (x - (i + 1) * dx/n_col, y, dx/n_col, bdy)  # left of branch-top
            anchor = (1, 1)  # right x, bottom y
        elif pos == 'branch-bottom-left':
            box = (x - (i + 1) * dx/n_col, y + bdy, dx/n_col, dy - bdy)  # etc.
            anchor = (1, 0)  # right x, top y
        elif pos == 'float':
            fit = text_fit(self._content, dy/n_row)
            box = (x + (col + 1) * dx, y + row * dy/n_row, 
                   fit, dy/n_row)  # right of node
            anchor = (0, bdy / dy)  # left x, branch position in y
        elif pos == 'aligned':
            aligned_x = drawer.node_size(drawer.tree)[0] if drawer.panel == 0 else drawer.xmin
            fit = text_fit(self._content, dy/n_row)
            box = (aligned_x, y + row * dy/n_row, 
                   fit, dy/n_row) # right of tree
            anchor = (0, bdy / dy)  # left x, branch position in y
        else:
            raise InvalidUsage(f'unkown position {pos}')

        self._box = box
        self._anchor = anchor
        return self._box

    def draw(self):
        self._check_own_variables()
        return draw_text(self._box, self._anchor, 
                self._content, self._text_type, 
                style={'fill': self._color})


class AttrFace(TextFace):

    def __init__(self, attr, color="black"):
        Face.__init__(self)
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

    def __init__(self, radius, fill, circle_type=""):
        Face.__init__(self)
        self._radius = radius
        self._fill = fill
        self._circle_type = circle_type

    def __name__(self):
        return "CircleFace"

    def compute_bounding_box(self, drawer, point, size, bdy, _, pos, col, n_col):
        self._check_own_content()
        x, y = point
        dx, dy = size
        i = col
        n = n_col
        if pos == 'branch-top':
            box = (x + i * dx/n, y, dx/n, bdy)  # above the branch
        elif pos == 'branch-bottom':
            box = (x + i * dx/n, y + bdy, dx/n, dy - bdy)  # below the branch
            anchor = (0, 0)  # left x, top y
        elif pos == 'branch-top-left':
            box = (x - (i + 1) * dx/n, y, dx/n, bdy)  # left of branch-top
            anchor = (1, 1)  # right x, bottom y
        elif pos == 'branch-bottom-left':
            box = (x - (i + 1) * dx/n, y + bdy, dx/n, dy - bdy)  # etc.
            anchor = (1, 0)  # right x, top y
        elif pos == 'float':
            box = (x + dx, y + i * dy/n, 2 * self._radius, dy/n)  # right of node
            anchor = (0, bdy / dy)  # left x, branch position in y
        else:
            raise InvalidUsage(f'unkown position {pos}')

        x, y, dx, dy = box
        self._box = box
        self._center = (x + dx/2 + (dx/2 - self._radius),
                        y + dy/2 + (dy/2 - self._radius))
        return self._box
        

    def draw(self):
        self._check_own_variables()
        return draw_circle(self._center, self._radius,
                self._circle_type, style={'fill': self._fill})


class RectFace(Face):
    def __init(self, width, height, color=None):
        self.width = width


class LineFace(Face):
    def __init__(self, line_type):
        self._line_type = line_type
