from collections import defaultdict
from types import FunctionType, MethodType
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
    def __init__(self):

        self._layout_handler = []
        
        self.show_leaf_name = True
        self.show_branch_length = True
        self.show_branch_support = True

        self._set_default_layout()

    def _set_default_layout(self):
        self._layout_handler = []

        if self.show_leaf_name:
            self._layout_handler.append(get_leaf_name_layout())

        if self.show_branch_length:
            self._layout_handler.append(get_branch_attr_layout(
                attr='dist',
                pos='branch-top',
                color='#8d8d8d'))

        if self.show_branch_support:
            self._layout_handler.append(get_branch_attr_layout(
                attr='support',
                pos='branch-bottom',
                color='#fa8072'))

    @property
    def layout_fn(self):
        return self._layout_handler

    @layout_fn.setter
    def layout_fn(self, layout):
        self._set_default_layout()

        if type(layout) not in set([list, set, tuple, frozenset]):
            layout = [layout]

        for ly in layout:
            # Validates layout function (python function)
            # Consider `callable(ly)`
            if type(ly) == FunctionType or type(ly) == MethodType or ly is None:
                self._layout_handler.append(ly)
            else:
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")
