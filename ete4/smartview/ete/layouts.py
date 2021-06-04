from collections import defaultdict
from ete4.smartview.ete.faces import AttrFace, CircleFace, RectFace, TextFace
from ete4.smartview.ete.draw import summary


def get_leaf_name_layout():
    leaf_name_face = AttrFace('name', constrained=False)
    pos = 'float'
    def layout_fn(node):
        if node.is_leaf():
            node.add_face(leaf_name_face, position=pos, column=0)
        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, text_type="attr_name", constrained=False),
                        position=pos, column=0, collapsed=True)
                
    return layout_fn


def get_branch_attr_layout(attr, pos, color='black'):
    branch_attr_face = AttrFace(attr, color=color)
    def layout_fn(node):
        if not node.is_leaf():
            node.add_face(branch_attr_face, position=pos, column=0)
    return layout_fn



class TreeStyle(object):
    def __init__(self, layout_fn=None, 
            aligned_panel=False,
            show_leaf_name=True, 
            show_branch_length=True,
            show_branch_support=True):

        self.layout_fn = []
        self.collapsed_layout_fn = []

        if show_leaf_name:
            self.layout_fn.append(get_leaf_name_layout())

        if show_branch_length:
            self.layout_fn.append(get_branch_attr_layout(
                attr='dist',
                pos='branch-top',
                color='#8d8d8d'))

        if show_branch_support:
            self.layout_fn.append(get_branch_attr_layout(
                attr='support',
                pos='branch-bottom',
                color='#fa8072'))

        if layout_fn:
            self.layout_fn.append(layout_fn)
