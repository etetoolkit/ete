import re
from math import pi

from ete4.smartview.utils import InvalidUsage
from ete4.smartview.ete.draw import Box, SBox,\
                                    draw_text, draw_rect,\
                                    draw_circle, draw_ellipse,\
                                    draw_line, draw_outline,\
                                    clip_angles,\
                                    draw_triangle

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
            dx_to_closest_child,
            bdx, bdy, 
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        self._check_own_content()
        x, y = point
        dx, dy = size
        zx, zy = drawer.zoom
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1

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
            avail_dx = dx_to_closest_child / n_col \
                    if not (self.node.is_leaf() or self.node.is_collapsed)\
                    else None
            avail_dy = min([bdy, dy - bdy, bdy - bdy0, bdy1 - bdy]) * 2 / n_row
            xy = (x + bdx + dx_before,
                  y + bdy + (row - n_row / 2) * avail_dy)

        elif pos == 'aligned': # right of tree
            avail_dx = None # should be overriden
            avail_dy = dy / n_row
            aligned_x = drawer.node_size(drawer.tree)[0]\
                    if drawer.panel == 0 else drawer.xmin
            xy = (aligned_x + dx_before,
                  y + bdy + (row - n_row / 2) * avail_dy)
        else:
            raise InvalidUsage(f'unkown position {pos}')

        padding_x = (self.padding_x) / zx
        padding_y = self.padding_y / (zy * r)

        self._box = Box(
            xy[0] + padding_x,
            xy[1] + padding_y,
            # avail_dx may not be initialized for branch-right and aligned
            max(avail_dx - 2 * padding_x, 0) if avail_dx else None,
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
        width, height = fit_fontsize(self._content, dx, max_dy)

        if pos == 'branch-top':
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch-bottom':
            box = (x, y, width, height) # container top

        else: # branch-right and aligned
            box = (x, y + (dy - height) / 2, width, height)

        self._fsize = height * zy * r

        self._box = Box(*box)
        return self._box

    def draw(self, drawer):
        self._check_own_variables()
        style = {
                'fill': self.color,
                'max_fsize': self._fsize,
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
        yield draw_text(self._box, 
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
        zx, zy = drawer.zoom
        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        padding_x, padding_y = self.padding_x / zx, self.padding_y / (zy * r)

        max_dy = dy * zy * r
        max_diameter = min(dx * zx, max_dy) if dx != None else max_dy
        self._max_radius = min(max_diameter / 2, self.radius)

        cx = x + self._max_radius / zx - padding_x

        if pos == 'branch-top':
            cy = y + dy - self._max_radius / (zy * r) # container bottom

        elif pos == 'branch-bottom':
            cy = y + self._max_radius / (zy * r) # container top

        else: # branch-right and aligned
            if pos == 'aligned':
                self._max_radius = min(dy * zy * r / 2, self.radius)
            cx = x + self._max_radius / zx - padding_x # centered
            cy = y + dy / 2 # centered

        self._center = (cx, cy)
        self._box = Box(cx, cy, 
                2 * (self._max_radius / zx - padding_x),
                2 * (self._max_radius) / (zy * r) - padding_y)

        return self._box
        
    def draw(self, drawer):
        self._check_own_variables()
        yield draw_circle(self._center, self._max_radius,
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
            width, height = get_dimensions(dx, max_dy)
            box = (x, y + (dy - height) / 2, width, height)

        elif pos == 'aligned':
            width = (self.width - 2 * self.padding_x) / zx
            height = min(dy, (self.height - 2 * self.padding_y) / zy) / r
            box = (x, y + (dy - height) / 2, width, height)

        self._box = Box(*box)
        return self._box

    def draw(self, drawer):
        self._check_own_variables()
        yield draw_rect(self._box,
                self.name,
                style={'fill': self.color})


class OutlineFace(Face):
    def __init__(self, 
            stroke_color='black', stroke_width=0.5,
            color="lightgray", opacity=0.3,
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
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
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

    def draw(self, drawer):
        style = {
                'stroke': self.stroke_color,
                'stroke-width': self.stroke_width,
                'fill': self.color,
                'fill-opacity': self.opacity,
                }
        yield draw_outline(self.outline, style)


class SeqFace(Face):
    def __init__(self, seq, seqtype='aa', poswidth=15,
            draw_text=True, max_fsize=15, ftype='sans-serif',
            padding_x=0, padding_y=0, is_constrained=True):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self.seq = seq
        self.seqtype = seqtype
        self.colors = _aacolors if self.seqtype == 'aa' else _ntcolors
        self.poswidth = poswidth  # width of each nucleotide/aa

        # Text
        self.draw_text = draw_text
        self.ftype = ftype
        self.max_fsize = max_fsize
        self._fsize = None

    def compute_fsize(self, dy, r, drawer):
        zy = drawer.zoom[1]
        self._fsize = min([self.poswidth / 1.4, dy * zy * r, self.max_fsize])

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos not in ('branch-right', 'aligned'):
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

        zx, zy = drawer.zoom

        x, y, _, dy = box
        dx = self.poswidth * len(self.seq) / zx

        if self.draw_text:
            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            self.compute_fsize(dy, r, drawer)

        self._box = Box(x, y, dx, dy)
        
        return self._box

    def draw(self, drawer):
        x0, y, _, dy = self._box
        zx, zy = drawer.zoom
        dx = self.poswidth / zx
        text_style = {
            'max_fsize': self._fsize,
            'text_anchor': 'middle',
            'ftype': f'{self.ftype}, sans-serif', # default sans-serif
            }
        for idx, pos in enumerate(self.seq):
            x = x0 + idx * dx
            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            # Draw rect
            box = Box(x, y, dx, dy)
            yield draw_rect(box,
                    self.seqtype + "_" + pos,
                    style={'fill': self.colors[pos]})
            # Draw text
            if self.draw_text:
                text_box = Box(x + dx / 2,
                        y + (dy - self._fsize / (zy * r)) / 2,
                        dx, dy)
                yield draw_text(text_box,
                        pos,
                        style=text_style)


class SeqMotifFace(Face):
    def __init__(self, seq=None, motifs=None, seqtype='aa', 
            gap_format='line', seq_format='[]', 
            width=None, height=None, # max height
            fgcolor='black', bgcolor='#bcc3d0', gapcolor='black',
            max_fsize=15, ftype='sans-serif',
            padding_x=0, padding_y=0, is_constrained=True):

        if not motifs and not seq:
            raise ValueError(
                    "At least one argument (seq or motifs) should be provided.")

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y,
                is_constrained=is_constrained)

        self.seq = seq or '-' * max([m[1] for m in motifs])
        self.seqtype = seqtype

        self.motifs = motifs
        self.overlaping_motif_opacity = 0.5

        self.seq_format = seq_format
        self.gap_format = gap_format

        self.width = width or (len(seq) * 15 if seq else 15)
        self.poswidth = self.width / len(seq) # 15 if argument width=None
        self.height = height  # dynamically computed if not provided

        self.fg = '#000'
        self.bg = _aacolors if self.seqtype == 'aa' else _ntcolors
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.gapcolor = gapcolor

        self.triangles = {'^': 'top', '>': 'right', 'v': 'bottom', '<': 'left'}

        # Text
        self.ftype = ftype
        self.max_fsize = max_fsize
        self._fsize = None

        self.regions = []
        self.build_regions()

    def build_regions(self):
        """Build and sort sequence regions: seq representation and motifs"""
        seq = self.seq
        motifs = self.motifs
        
        # if only sequence is provided, build regions out of gap spaces
        if not motifs:
            if self.seq_format == "seq":
                motifs = [[0, len(seq), "seq", 
                    10, self.height, None, None, None]]
            else:
                motifs = []
                pos = 0
                for reg in re.split('([^-]+)', seq):
                    if reg:
                        if not reg.startswith("-"):
                            if self.seq_format == "compactseq":
                                motifs.append([pos, pos+len(reg)-1,
                                    "compactseq", 4, self.height,
                                    None, None, None])
                            elif self.seq_format == "line":
                                motifs.append([pos, pos+len(reg)-1,
                                    "-", 1, 1, self.fgcolor, None, None])
                            else:
                                motifs.append([pos, pos+len(reg)-1,
                                    self.seq_format, None, self.height, 
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
                                self.gap_format, 1, 1,
                                self.gapcolor, None, None])
                        else:
                            self.regions.append([pos, pos+len(reg)-1, 
                                self.seq_format, self.width, self.height,
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
                            self.gap_format, 1, 1, 
                            self.gapcolor, None, None])
                    else:
                        self.regions.append([pos, pos+len(reg)-1, 
                            self.seq_format,
                            self.width, self.height,
                            self.fgcolor, self.bgcolor, None])
                    pos += len(reg)

    def compute_fsize(self, dy, r, drawer):
        zy = drawer.zoom[1]
        self._fsize = min([self.poswidth / 1.4, dy * zy * r, self.max_fsize])

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos not in ('branch-right', 'aligned'):
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
        zx, zy = drawer.zoom

        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        self.compute_fsize(dy, r, drawer)
        
        self._box = Box(x, y, self.width / zx, dy)
        return self._box

    def draw(self, drawer):
        x0, y, dx, dy = self._box
        zx, zy = drawer.zoom
        pos_dx = dx / len(self.seq)
        x = x0
        for (start, end, shape, w, h, fg, bg, text) in self.regions:
            w = (w / zx if w else pos_dx) * (end + 1 - start)
            h = min([h or dy * zy, dy * zy, self.height or dy * zy]) / zy
            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            box = Box(x, y + (dy - h / r) / 2, w, h / r)

            # Line
            if shape == 'line':
                yield draw_line((x, y + dy / 2), (x + w, y + dy / 2))

            # Rectangle
            elif shape == '[]':
                style = {'fill': bg}
                yield draw_rect(box, '', style=style)

            # Triangle
            elif shape in self.triangles.keys():
                box = Box(x, y + (dy - h / r) / 2, w, h / r)
                yield draw_triangle(box, self.triangles[shape],
                        style={'fill': bg})

            # Circle/ellipse
            elif shape == 'o':
                center = (x + w / 2, y + dy / 2)
                rx = w * zx / 2
                ry = h * zy / 2
                ellipse_style = {'fill': bg}
                if rx == ry:
                    yield draw_circle(center, rx, style=ellipse_style)
                else:
                    yield draw_ellipse(center, rx, ry, style=ellipse_style)

            # Sequence and compact sequence
            elif shape.endswith('seq'):
                if shape == 'seq':
                    postext = True
                    poswidth = self.poswidth
                elif shape == 'compactseq':
                    postext = False
                    poswidth = w / (end + 1 - start) * zx

                seq = self.seq[start : end + 1]
                seq_face = SeqFace(seq, self.seqtype, poswidth,
                        draw_text=postext, max_fsize=self.max_fsize,
                        ftype=self.ftype, is_constrained=self.is_constrained)
                seq_face._box = box # assign box manually
                seq_face.compute_fsize(h, 1, drawer)
                yield from seq_face.draw(drawer)

            # Text on top of shape
            if text:
                self.compute_fsize(h, 1, drawer)
                text_box = Box(x + w / 2,
                        y + (dy - self._fsize / (zy * r)) / 2,
                        dx, self._fsize / zy)
                text_style = {
                    'max_fsize': self._fsize,
                    'text_anchor': 'middle',
                    'ftype': f'{self.ftype}, sans-serif',
                    'fill': fg or self.fgcolor,
                    }
                yield draw_text(text_box, text, style=text_style)

            # Update x to draw consecutive motifs
            x += w
