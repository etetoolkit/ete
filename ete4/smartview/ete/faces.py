import re
from math import pi

from ete4.smartview.utils import InvalidUsage, get_random_string
from ete4.smartview.ete.draw import Box, SBox,\
                                    draw_text, draw_rect,\
                                    draw_circle, draw_ellipse,\
                                    draw_line, draw_outline,\
                                    draw_triangle, draw_rhombus,\
                                    clip_angles, cartesian


CHAR_HEIGHT = 1.4 # char's height to width ratio

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

    def __init__(self, name="", padding_x=0, padding_y=0):
        self.node = None
        self.name = name
        self._content = "Empty"
        self._box = None
        self.padding_x = padding_x
        self.padding_y = padding_y

        self.always_drawn = False # Use carefully to avoid overheading...

    def __name__(self):
        return "Face"

    def get_content(self):
        return self._content

    def get_box(self):
        self._check_own_variables()
        return self._box

    def compute_fsize(self, dx, dy, drawer, max_fsize=None):
        zx, zy = drawer.zoom
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
        zx, zy = drawer.zoom

        if pos == 'branch-top':  # above the branch
            avail_dx = dx / n_col
            avail_dy = bdy / n_row
            x = x + dx_before
            y = y + bdy - avail_dy - dy_before

        elif pos == 'branch-bottom':  # below the branch
            avail_dx = dx / n_col
            avail_dy = (dy - bdy) / n_row
            x = x + dx_before
            y = y + bdy + dy_before

        elif pos == 'branch-top-left':  # left of branch-top
            width, height = get_dimensions(dx / n_col, bdy)
            box = (x - (col + 1) * dx/n_col, y, width, height)

        elif pos == 'branch-bottom-left':  # left of branch-bottom
            width, height = get_dimensions(dx / n_col, dy - bdy)
            box = (x - (col + 1) * dx/n_col, y + bdy, width, height)

        elif pos == 'branch-right':  # right of node
            avail_dx = dx_to_closest_child / n_col\
                    if not (self.node.is_leaf() or self.node.is_collapsed)\
                    else None
            avail_dy = min([bdy, dy - bdy, bdy - bdy0, bdy1 - bdy]) * 2 / n_row
            x = x + bdx + dx_before
            y = y + bdy + (row - n_row / 2) * avail_dy

        elif pos == 'aligned': # right of tree
            avail_dx = None # should be overriden
            avail_dy = dy / n_row
            aligned_x = drawer.node_size(drawer.tree)[0]\
                    if drawer.panel == 0 else drawer.xmin
            x = aligned_x + dx_before
            y = y + dy / 2 + (row - n_row / 2) * avail_dy
        else:
            raise InvalidUsage(f'unkown position {pos}')

        r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
        padding_x = self.padding_x / zx
        padding_y = self.padding_y / (zy * r)

        self._box = Box(
            x + padding_x,
            y + padding_y,
            # avail_dx may not be initialized for branch-right and aligned
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
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

        self._content = text
        self.color = color
        self.min_fsize = min_fsize
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

        def fit_fontsize(text, dx, dy):
            dchar = dx / len(text) if dx != None else float('inf')
            self.compute_fsize(dchar, dy, drawer)
            dxchar = self._fsize / (zx * CHAR_HEIGHT)
            dychar = self._fsize / (zy * r)
            return dxchar * len(text), dychar

        width, height = fit_fontsize(self._content, dx, dy * r)

        if pos == 'branch-top':
            box = (x, y + dy - height, width, height) # container bottom

        elif pos == 'branch-bottom':
            box = (x, y, width, height) # container top

        else: # branch-right and aligned
            box = (x, y + (dy - height) / 2, width, height)

        self._box = Box(*box)
        return self._box

    def fits(self):
        return self._fsize >= self.min_fsize

    def draw(self, drawer):
        self._check_own_variables()
        style = {
                'fill': self.color,
                'max_fsize': self._fsize,
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
        yield draw_text(self._box, 
                self._content, self.name, style=style)


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
        self._check_own_node()
        content = str(getattr(self.node, self._attr, None)\
                or self.node.properties.get(self._attr))
        self._content = self.formatter % content if self.formatter else content
        return self._content


class CircleFace(Face):

    def __init__(self, radius, color, name="",
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

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
    def __init__(self, width, height, color='gray',
            text=None, fgcolor='black', # text color
            min_fsize=6, max_fsize=15,
            ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.width = width
        self.height = height
        self.color = color
        # Text related
        self.text = text
        self.rotate_text = True
        self.fgcolor = fgcolor
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize

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
            height = min(dy, (self.height - 2 * self.padding_y) / zy)
            box = (x, y + (dy - height) / 2, width, height)

        self._box = Box(*box)
        return self._box

    def draw(self, drawer):
        self._check_own_variables()

        circ_drawer = drawer.TYPE == 'circ'
        style = {'fill': self.color, 'opacity': 0.7}
        if self.text and circ_drawer:
            rect_id = get_random_string(10)
            style['id'] = rect_id

        yield draw_rect(self._box,
                self.name,
                style=style)

        if self.text:
            x, y, dx, dy = self._box
            zx, zy = drawer.zoom
            r = (x or 1e-10) if circ_drawer else 1
            if self.rotate_text:
                rotation = 90
                self.compute_fsize(dy * zy / (len(self.text) * zx) * r,
                                   dx * zx / zy, drawer)

                text_box = Box(x + (dx - self._fsize / (2 * zx)) / 2,
                        y + dy / 2,
                        dx, dy)
            else:
                rotation = 0
                self.compute_fsize(dx, dy, drawer)
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


class OutlineFace(Face):
    def __init__(self, 
            stroke_color='black', stroke_width=0.5,
            color="lightgray", opacity=0.3,
            collapsing_height=5, # height in px at which outline becomes a line
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.opacity = opacity
        self.color = color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
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
        style = {
                'stroke': self.stroke_color,
                'stroke-width': self.stroke_width,
                'fill': self.color,
                'fill-opacity': self.opacity,
                }
        x, y, dx_min, dx_max, dy = self.outline
        zx, zy = drawer.zoom
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
            yield draw_outline(self.outline, style)


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

        if drawer.NPANELS > 1 and drawer.viewport and pos == 'branch-right':
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
            self.compute_fsize(self.poswidth / zx, dy, drawer)

        self._box = Box(x, y, dx, dy)
        
        return self._box

    def draw(self, drawer):
        x0, y, _, dy = self._box
        zx, zy = drawer.zoom
        dx = self.poswidth / zx
        # Send sequences as a whole to be rendered by PIXIjs
        yield [ "pixi-aa_notext", Box(x0, y, dx * len(self.seq), dy), self.seq ]
        # Rende text if necessary
        if self.draw_text:
            text_style = {
                'max_fsize': self._fsize,
                'text_anchor': 'middle',
                'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                }
            for idx, pos in enumerate(self.seq):
                x = x0 + idx * dx
                r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
                # Draw rect
                if pos != '-':
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
        self.max_fsize = max_fsize
        self._fsize = None

        self.regions = []
        self.build_regions()

    def __name__(self):
        return "SeqMotifFace"

    def build_regions(self):
        """Build and sort sequence regions: seq representation and motifs"""
        seq = self.seq
        motifs = self.motifs
        
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

        self._box = Box(x, y, self.width / zx, dy)
        return self._box

    def fits(self):
        return True

    def draw(self, drawer):
        # Only leaf/collapsed branch-right or aligned
        x0, y, _, dy = self._box
        zx, zy = drawer.zoom
        x = x0
        prev_end = -1

        if self.gap_format in ["line", "-"]:
            p1 = (x0, y + dy / 2)
            p2 = (x0 + self.width / zx, y + dy / 2)
            if drawer.TYPE == 'circ':
                p1 = cartesian(p1)
                p2 = cartesian(p2)
            yield draw_line(p1, p2, style={'stroke-width': self.gap_linewidth,
                                           'stroke': self.gapcolor})

        for (start, end, shape, posw, h, fg, bg, text, opacity) in self.regions:
            posw = (posw or self.poswidth) * self.w_scale / zx
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
            elif shape in ('[]', '()'):
                yield [ "pixi-block", box ]
                # if shape == '()':
                    # style['rounded'] = 1;
                # yield draw_rect(box, '', style=style)

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
            elif shape == 'compactseq':
                seq = self.seq[start : end + 1]
                yield [ "pixi-aa_notext", box, seq ]

            elif shape == 'seq':
                seq = self.seq[start : end + 1]
                seq_face = SeqFace(seq, self.seqtype, posw * zx,
                        draw_text=True, max_fsize=self.max_fsize,
                        ftype=self.ftype)
                seq_face._box = box # assign box manually
                seq_face.compute_fsize(posw, h, drawer)
                yield from seq_face.draw(drawer)

            # Text on top of shape
            if text:
                try:
                    ftype, fsize, color, text = text.split("|")
                    fsize = int(fsize)
                except:
                    ftype, fsize, color = self.ftype, self.max_fsize, (fg or self.fcolor)
                self.compute_fsize(w / len(text), h, drawer, fsize)
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
