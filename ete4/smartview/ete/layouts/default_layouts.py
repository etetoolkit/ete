from ete4.smartview import Face, AttrFace, TextFace,\
        CircleFace, RectFace,\
        OutlineFace, AlignLinkFace

from ete4.smartview.ete.draw import summary


__all__ = [ "get_layout_leaf_name", "get_layout_nleaves",
        "get_layout_branch_length", "get_layout_branch_support",
        "get_layout_outline", "get_layout_align_link" ]


def get_layout_leaf_name(pos='branch_right', color='black', 
                         min_fsize=4, max_fsize=15,
                         padding_x=5, padding_y=0):
    leaf_name_face = AttrFace(attr='name', name='leaf_name',
            min_fsize=min_fsize, max_fsize=max_fsize,
            color=color, padding_x=padding_x, padding_y=padding_y)
    def layout_fn(node):
        if node.is_leaf():
            node.add_face(leaf_name_face, position=pos, column=1)
        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, name='leaf_name', 
                                color=color, 
                                min_fsize=min_fsize, max_fsize=max_fsize,
                                padding_x=padding_x, padding_y=padding_y),
                        position=pos, column=2, collapsed_only=True)
    layout_fn.__name__ = 'Leaf name'
    layout_fn.contains_aligned_face = pos == "aligned"
    layout_fn._module = 'default'
    return layout_fn


def get_layout_nleaves(pos='branch_right', collapsed_only=True,
        formatter='(%s)', color="black",
        min_fsize=4, max_fsize=15, ftype="sans-serif", 
        padding_x=5, padding_y=0):
    def layout_fn(node):
        if not node.is_leaf():
            nleaves = str(len(node))
            nleaves_face = TextFace(f'{formatter}' % nleaves, color=color,
                    min_fsize=min_fsize, max_fsize=max_fsize, ftype=ftype,
                    padding_x=padding_x, padding_y=padding_y)
            node.add_face(nleaves_face, position=pos, column=1,
                    collapsed_only=True)
            if not collapsed_only:
                node.add_face(nleaves_face, position=pos, column=0)

    layout_fn.__name__ = "Number of leaves"
    layout_fn.contains_aligned_face = pos == "aligned"
    layout_fn._module = 'default'
    return layout_fn


def get_layout_branch_length(pos='branch_top', 
        formatter='%0.5s',
        color='#8d8d8d', 
        min_fsize=6, max_fsize=15,
        padding_x=2, padding_y=0):

    return _get_layout_branch_attr(attr='dist',
                formatter=formatter,
                name='Branch length',
                pos=pos,
                color=color,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)


def get_layout_branch_support(pos='branch_bottom', 
                              formatter='%0.4s',
                              color='#fa8072', 
                              min_fsize=6, max_fsize=15,
                              padding_x=2,padding_y=0):

    return _get_layout_branch_attr(attr='support',
                formatter=formatter,
                name="Branch support",
                pos=pos,
                color=color,
                min_fsize=min_fsize, max_fsize=max_fsize,
                padding_x=padding_x, padding_y=padding_y)
    

def _get_layout_branch_attr(attr, pos, name=None, 
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
    layout_fn.contains_aligned_face = pos == "aligned"
    layout_fn._module = 'default'
    return layout_fn


def get_layout_outline(stroke_color="black", stroke_width=0.5, 
        color="lightgray", opacity=0.3, collapsing_height=5):

    outline_face = OutlineFace(stroke_color="black", stroke_width=stroke_width, 
            color=color, opacity=opacity, collapsing_height=collapsing_height)
    def layout_fn(node):
        if not node.is_leaf():
            node.add_face(outline_face, 
                    position='branch_right', column=0,
                    collapsed_only=True)
    layout_fn.__name__ = 'Outline'
    layout_fn._module = 'default'
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
