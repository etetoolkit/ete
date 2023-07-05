from ..treelayout import TreeLayout
from ..nodestyle import NodeStyle
from ..faces import AttrFace, TextFace, OutlineFace, AlignLinkFace

from ..draw_helpers import summary, Padding


__all__ = ['LayoutLeafName', 'LayoutNumberLeaves',
           'LayoutBranchLength', 'LayoutBranchSupport',
           'LayoutOutline']


class LayoutLeafName(TreeLayout):
    def __init__(self, name='Leaf name',
                 pos='branch_right', color='black',
                 ftype='sans-serif',
                 min_fsize=4, max_fsize=15,
                 padding_x=5, padding_y=0):
        super().__init__(name)
        self.pos = pos
        self.aligned_faces = self.pos == 'aligned'
        self.color = color
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        self.face = AttrFace(
            attr='name', name='leaf_name',
            ftype=self.ftype,
            min_fsize=self.min_fsize, max_fsize=self.max_fsize,
            color=self.color, padding_x=self.padding.x, padding_y=self.padding.y)

    def set_node_style(self, node):
        if node.is_leaf:
            node.add_face(self.face, position=self.pos, column=1)
        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, name='leaf_name',
                                color=self.color, ftype=self.ftype,
                                min_fsize=self.min_fsize, max_fsize=self.max_fsize,
                                padding_x=self.padding.x, padding_y=self.padding.y),
                        position=self.pos, column=2, collapsed_only=True)


class LayoutNumberLeaves(TreeLayout):
    def __init__(self, name='Number of leaves',
                 pos='branch_right', collapsed_only=True,
                 formatter='(%s)', color='black',
                 min_fsize=4, max_fsize=15, ftype='sans-serif',
                 padding_x=5, padding_y=0):
        super().__init__(name)
        self.pos = pos
        self.aligned_faces = self.pos == 'aligned'
        self.color = color
        self.formatter = formatter
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        self.active = False

        self.collapsed_only = collapsed_only

    def set_node_style(self, node):
        if not node.is_leaf:
            face = TextFace(
                self.formatter % len(node),  # number of leaves
                color=self.color,
                min_fsize=self.min_fsize, max_fsize=self.max_fsize,
                ftype=self.ftype,
                padding_x=self.padding.x, padding_y=self.padding.y)

            node.add_face(face, position=self.pos, column=1, collapsed_only=True)

            if not self.collapsed_only:
                node.add_face(face, position=self.pos, column=0)


def _get_layout_branch_attr(attr, pos, name=None,
                           formatter=None, color='black',
                           ftype='sans-serif',
                           min_fsize=6, max_fsize=15,
                           padding_x=0, padding_y=0):
    branch_attr_face = AttrFace(attr,
            formatter=formatter,
            name=name or f'branch_{attr}',
            color=color, ftype=ftype,
            min_fsize=min_fsize, max_fsize=max_fsize,
            padding_x=padding_x,
            padding_y=padding_y)

    def layout_fn(node):
        if not node.is_leaf and (node.dist is None or node.dist > 0):
            node.add_face(branch_attr_face, position=pos, column=0)
            node.add_face(branch_attr_face, position=pos, column=0,
                    collapsed_only=True)
    return layout_fn


class LayoutBranchLength(TreeLayout):
    def __init__(self, name='Branch length',
            pos='branch_top',
            formatter='%0.5s',
            color='#8d8d8d', ftype="sans-serif",
            min_fsize=6, max_fsize=15,
            padding_x=2, padding_y=0):
        super().__init__(name)
        self.pos = pos
        self.aligned_faces = self.pos == 'aligned'
        self.color = color
        self.formatter = formatter
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        self.set_node_style = _get_layout_branch_attr(attr='dist',
                formatter=formatter,
                name='Branch length',
                pos=pos,
                color=color, ftype=self.ftype,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


class LayoutBranchSupport(TreeLayout):
    def __init__(self, name='Branch support',
            pos='branch_bottom',
            formatter='%0.4s',
            color='#fa8072',  ftype="sans-serif",
            min_fsize=6, max_fsize=15,
            padding_x=2,padding_y=0):
        super().__init__(name)
        self.pos = pos
        self.aligned_faces = self.pos == 'aligned'
        self.color = color
        self.formatter = formatter
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        self.set_node_style = _get_layout_branch_attr(attr='support',
                formatter=formatter,
                name="Branch support",
                pos=pos,
                color=color, ftype=self.ftype,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


class LayoutOutline(TreeLayout):
    def __init__(self, name=None,
            stroke_color="black", stroke_width=0.5,
            color="lightgray", opacity=0.3, collapsing_height=5):
        super().__init__(None)

        self.always_render = True

        self.face = OutlineFace(stroke_color="black", stroke_width=stroke_width,
            color=color, opacity=opacity, collapsing_height=collapsing_height)

    def set_node_style(self, node):
        if not node.is_leaf:
            node.add_face(self.face,
                    position="branch_right", column=0,
                    collapsed_only=True)


def get_layout_align_link(stroke_color='gray', stroke_width=0.5,
            line_type=1, opacity=0.8):
    align_link_face = AlignLinkFace(stroke_color=stroke_color,
                                    stroke_width=stroke_width,
                                    line_type=line_type,
                                    opacity=opacity)
    def layout_fn(node):
        if node.is_leaf:
            node.add_face(align_link_face,
                          position='branch_right',
                          column=1e9)
        else:
            node.add_face(align_link_face,
                          position='branch_right',
                          column=1e9,
                          collapsed_only=True)
    layout_fn.__name__ = 'Aligned panel link'
    layout_fn._module = 'default'
    return layout_fn
