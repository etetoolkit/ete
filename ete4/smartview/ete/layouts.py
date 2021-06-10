from types import FunctionType, MethodType
from ete4.smartview.ete.faces import AttrFace, CircleFace, RectFace, TextFace,\
                                     OutlineFace
from ete4.smartview.ete.draw import summary


def get_leaf_name_layout(pos='branch-right', color='black', padding_x=5, padding_y=0):
    leaf_name_face = AttrFace(attr='name', name='leaf_name',
            color=color, padding_x=padding_x, padding_y=padding_y,
            constrained=False)
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
                                padding_x=padding_x, padding_y=padding_y,
                                constrained=False),
                        position=pos, column=1, collapsed_only=True)
                
    return layout_fn


def get_branch_length_layout(pos='branch-top', 
        color='#8d8d8d', 
        padding_x=2, padding_y=0):

    return get_branch_attr_layout(attr='dist',
                pos=pos,
                color=color,
                padding_x=padding_x, padding_y=padding_y,
                constrained=False)


def get_branch_support_layout(pos='branch-bottom', 
        color='#fa8072', 
        padding_x=2,padding_y=0):

    return get_branch_attr_layout(attr='support',
                pos=pos,
                color=color,
                padding_x=padding_x, padding_y=padding_y,
                constrained=False)
    

def get_branch_attr_layout(attr, pos, name=None, color='black',
        padding_x=0, padding_y=0, constrained=True):
    branch_attr_face = AttrFace(attr,
            name=name or f'branch_{attr}',
            color=color,
            padding_x=padding_x,
            padding_y=padding_y,
            constrained=constrained)
    def layout_fn(node):
        if not node.is_leaf() and node.dist > 0:
            node.add_face(branch_attr_face, position=pos, column=0)
            node.add_face(branch_attr_face, position=pos, column=0,
                    collapsed_only=True)
    return layout_fn


def get_outline_layout():
    outline_face = OutlineFace(constrained=False)
    def layout_fn(node):
        if not node.is_leaf():
            node.add_face(outline_face, 
                    position='branch-right', column=0,
                    collapsed_only=True)
    return layout_fn



class TreeStyle(object):
    def __init__(self):
        self._layout_handler = []
        
    @property
    def layout_fn(self):
        return self._layout_handler

    @layout_fn.setter
    def layout_fn(self, layout):
        if type(layout) not in set([list, set, tuple, frozenset]):
            layout = [layout]

        for ly in layout:
            # Validates layout function (python function)
            # Consider `callable(ly)`
            if type(ly) == FunctionType or type(ly) == MethodType or ly is None:
                self._layout_handler.append(ly)
            else:
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")
