"""
Definition of the basic elements for a tree representation (Layout and
Decoration), extra labels (Label), and the default tree style.
"""

from collections import namedtuple
from dataclasses import dataclass, field

from .faces import Face, TextFace


# Layouts have all the information needed to represent a tree.
#
# They compose. Using several layouts will add extra graphic
# representations, and/or overwrite some styles from previous layouts.
#
# They have a name and 3 functions that provide the style and
# decorations related to:
#   the full tree (for example rectangular/circular, with scale, etc.)
#   each visible node (called for each node)
#   each group of collapsed sibling nodes (too small to fully represent)

def empty_dict_fn():
    return lambda _: {}  # function that takes a tree or a node and returns {}

def empty_list_fn():
    return lambda _: []  # function that takes a tree or a node and returns []

@dataclass
class Layout:
    """Contains all the info about how to represent a tree."""
    name: str
    tree_style: None = field(default_factory=empty_dict_fn)
    tree_decos: None = field(default_factory=empty_list_fn)
    node_style: None = field(default_factory=empty_dict_fn)  # dict or str
    node_decos: None = field(default_factory=empty_list_fn)
    collapsed_style: None = field(default_factory=empty_dict_fn)  # dict or str
    collapsed_decos: None = field(default_factory=empty_list_fn)


# A decoration is a face with a position ("top", "bottom", "right",
# etc.), a column (an integer used for relative order with other faces
# in the same position), and an anchor point (to fine-tune the
# position of things like texts within them).

@dataclass
class Decoration:
    face: Face
    position: str = 'top'
    column: int = 0
    anchor: tuple = (-1, 1)


# The default style of a tree.

DEFAULT_TREE_STYLE = {
    'shape': 'rectangular',  # or 'circular'
    'min-size': 6, 'min-size-content': 4,
    'styles': {},  # to name styles that can be referenced in node styles
}


# The default layout.

def default_node_decos(node):
    decos = []
    face_dist = TextFace('"%.2g" % dist if dist else ""')
    decos.append(Decoration(face_dist, position='top', anchor=(-1, 1)))
    if node.is_leaf:
        decos.append(Decoration(TextFace('name'),
                                position='right', anchor=(-1, 0)))
    return decos

def default_collapsed_decos(nodes):
    return [Decoration(TextFace('name'),
                       position='right', anchor=(-1, 0))]

DEFAULT_LAYOUT = Layout(
    name='default',
    tree_style=lambda tree: DEFAULT_TREE_STYLE,
    node_decos=default_node_decos,
    collapsed_decos=default_collapsed_decos)


# Description of a label that we want to add to the representation of a node.

Label = namedtuple('Label', 'code style node_type position column anchor fs_max')
