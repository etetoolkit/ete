from collections import defaultdict
from types import FunctionType, MethodType
from ete4.smartview import AttrFace, TextFace,\
                                     CircleFace, RectFace,\
                                     OutlineFace, AlignLinkFace
from ete4.smartview.ete.draw import summary


def get_layout_leaf_name(pos='branch-right', color='black', 
                         min_fsize=4, max_fsize=15,
                         padding_x=5, padding_y=0):
    leaf_name_face = AttrFace(attr='name', name='leaf_name',
            min_fsize=min_fsize, max_fsize=max_fsize,
            color=color, padding_x=padding_x, padding_y=padding_y)
    def layout_fn(node):
        if node.is_leaf():
            node.add_face(leaf_name_face, position=pos, column=0)
        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, name='leaf_name', 
                                color=color, 
                                min_fsize=min_fsize, max_fsize=max_fsize,
                                padding_x=padding_x, padding_y=padding_y),
                        position=pos, column=1, collapsed_only=True)
    layout_fn.__name__ = 'Leaf name'
    layout_fn.contains_aligned_face = pos == "aligned"
    return layout_fn


def get_layout_nleaves(pos='branch-right', collapsed_only=True,
        formatter='(%s)', color="black",
        min_fsize=4, max_fsize=15, ftype="sans-serif", 
        padding_x=5, padding_y=0):
    def layout_fn(node):
        if not node.is_leaf():
            nleaves = str(len(node))
            nleaves_face = TextFace(f'{formatter}' % nleaves, color=color,
                    min_fsize=min_fsize, max_fsize=max_fsize, ftype=ftype,
                    padding_x=padding_x, padding_y=padding_y)
            node.add_face(nleaves_face, position=pos, column=2,
                    collapsed_only=True)
            if not collapsed_only:
                node.add_face(nleaves_face, position=pos, column=1)

    layout_fn.__name__ = "Number of leaves"
    layout_fn.contains_aligned_face = pos == "aligned"
    return layout_fn


def get_layout_branch_length(pos='branch-top', 
        formatter='%0.5s',
        color='#8d8d8d', 
        min_fsize=6, max_fsize=15,
        padding_x=2, padding_y=0):

    return get_layout_branch_attr(attr='dist',
                formatter=formatter,
                name='Branch length',
                pos=pos,
                color=color,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


def get_layout_branch_support(pos='branch-bottom', 
                              formatter='%0.4s',
                              color='#fa8072', 
                              min_fsize=6, max_fsize=15,
                              padding_x=2,padding_y=0):

    return get_layout_branch_attr(attr='support',
                formatter=formatter,
                name="Branch support",
                pos=pos,
                color=color,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)
    

def get_layout_branch_attr(attr, pos, name=None, 
                           formatter=None, color='black',
                           min_fsize=6, max_fsize=15,
                           padding_x=0, padding_y=0):
    branch_attr_face = AttrFace(attr,
            formatter=formatter,
            name=name or f'branch_{attr}',
            color=color,
            min_fsize=min_fsize, max_fsize=max_fsize,
            padding_x=padding_x,
            padding_y=padding_y)
    def layout_fn(node):
        if not node.is_leaf() and node.dist > 0:
            node.add_face(branch_attr_face, position=pos, column=0)
            node.add_face(branch_attr_face, position=pos, column=0,
                    collapsed_only=True)
    layout_fn.__name__ = name or 'branch_' + str(attr)
    layout_fn.contain = pos == "aligned"
    return layout_fn


def get_layout_outline(stroke_color="black", stroke_width=0.5, 
        color="lightgray", opacity=0.3, collapsing_height=5):

    outline_face = OutlineFace(stroke_color="black", stroke_width=stroke_width, 
            color=color, opacity=opacity, collapsing_height=collapsing_height)
    def layout_fn(node):
        if not node.is_leaf():
            node.add_face(outline_face, 
                    position='branch-right', column=0,
                    collapsed_only=True)
    layout_fn.__name__ = 'Outline'
    return layout_fn


def get_layout_align_link(stroke_color='gray', stroke_width=0.5,
            line_type=1, opacity=0.8):
    align_link_face = AlignLinkFace(stroke_color=stroke_color,
                                    stroke_width=stroke_width,
                                    line_type=line_type,
                                    opacity=opacity)
    def layout_fn(node):
        if node.is_leaf():
            node.add_face(align_link_face,
                          position='branch-right',
                          column=1e10)
        else:
            node.add_face(align_link_face,
                          position='branch-right',
                          column=1e10,
                          collapsed_only=True)
    layout_fn.__name__ = 'Aligned panel link'
    return layout_fn



class TreeStyle(object):
    def __init__(self):
        self._layout_handler = []
        self.aligned_grid = True
        self.aligned_grid_dxs = defaultdict(lambda: 0)
        self.show_align_link = False

        self.ultrametric = False
        
        self.show_outline = True
        self.show_leaf_name = True
        self.show_nleaves = False
        self.show_branch_length = False
        self.show_branch_support = False
        self.default_layouts = ['Outline', 'Leaf name', 'Number of leaves',
                                'Branch length', 'Branch support',
                                'Aligned panel link']
        
    @property
    def layout_fn(self):
        default_layout = self._get_default_layout()
        return default_layout + self._layout_handler

    @layout_fn.setter
    def layout_fn(self, layout):
        if type(layout) not in set([list, set, tuple, frozenset]):
            layout = [layout]

        for ly in layout:
            # Validates layout function (python function)
            # Consider `callable(ly)`
            if type(ly) == FunctionType or type(ly) == MethodType or ly is None:
                name = ly.__name__
                if name in self.default_layouts:
                    self._update_layout_flags(name, True)
                else:
                    self._layout_handler.append(ly)
            else:
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")

    def del_layout_fn(self, name):
        """ Deletes layout function given its __name__ """
        # Modify flags if name refers to defaults
        if name in self.default_layouts:
            self._update_layout_flags(name, False)
        else:
            for layout in self.layout_fn:
                if layout.__name__ == name:
                    self._layout_handler.remove(layout)

    def _update_layout_flags(self, name, status):
        if name == 'Outline':
            self.show_outline = status
        if name == 'Aligned panel link':
            self.show_align_link = status
        if name == 'Leaf name':
            self.show_leaf_name = status
        if name == 'Number of leaves':
            self.show_nleaves = status
        if name == 'Branch length':
            self.show_branch_length = status
        if name == 'Branch support':
            self.show_branch_support = status

    def _get_default_layout(self):
        layouts = []

        # Set clean node style
        try:
            clean = NodeStyle()
        except:
            from ete4 import NodeStyle
            clean = NodeStyle()

        clean['size'] = 0
        clean['bgcolor'] = 'transparent'
        layouts.append(lambda node: node.set_style(clean))

        if self.show_outline:
            layouts.append(get_layout_outline())
        if self.show_align_link:
            layouts.append(get_layout_align_link())
        if self.show_leaf_name:
            layouts.append(get_layout_leaf_name())
        if self.show_nleaves:
            layouts.append(get_layout_nleaves())
        if self.show_branch_length:
            layouts.append(get_layout_branch_length())
        if self.show_branch_support:
            layouts.append(get_layout_branch_support())
        return layouts
