"""
Definition of the basic elements for a tree representation (Layout and
Decoration), extra labels (Label), and the default tree style.
"""

from collections import namedtuple
from dataclasses import dataclass, field
from functools import lru_cache
import inspect

from .faces import Face, PropFace


# Layouts have all the information needed to represent a tree.
#
# They compose. Using several layouts will add extra graphic
# representations, and/or overwrite some styles from previous layouts.
#
# They have a name and two functions providing the style and decorations of:
# - the full tree (for example rectangular/circular, with scale, etc.)
# - each visible node (called for each node) or group of collapsed sibling nodes

class Layout:
    """Contains all the info about how to represent a tree."""

    def __init__(self, name, tree_style=None, draw_node=None, cache_size=None):
        # Check types.
        assert type(name) is str
        assert tree_style is None or type(tree_style) is dict or callable(tree_style)
        assert draw_node is None or callable(draw_node)

        # Name. This is mainly to activate/deactivate the layout in the gui.
        self.name = name

        # Tree style. Can be a dict or a function of a tree that returns a dict.
        self.tree_style = tree_style or {}

        # Representation of a node (style and decorations).
        if draw_node is None:
            self.draw_node = lambda node, collapsed: ()
            return

        # We use an auxiliary function to cache its results.
        arity = len(inspect.signature(draw_node).parameters)
        if arity == 1:  # draw_node(node) (unspecified what to do with collapsed)
            @lru_cache(maxsize=cache_size)
            def cached_draw_node(node, collapsed):
                if not collapsed:  # just draw the node
                    return to_elements(draw_node(node))
                else:  # get representations from all siblings
                    return [x for n in collapsed for x in to_elements(draw_node(n))]
        elif arity == 2:  # draw_node(node, collapsed) (fully specified)
            @lru_cache(maxsize=cache_size)
            def cached_draw_node(node, collapsed):
                return to_elements(draw_node(node, collapsed))
        else:
            raise ValueError('draw_node can have only 1 or 2 arguments.')

        self.draw_node = cached_draw_node  # use the auxiliary caching function

    @property
    def tree_style(self):
        return self._tree_style

    @tree_style.setter
    def tree_style(self, value):
        self._tree_style = add_to_style(value, DEFAULT_TREE_STYLE)


def to_elements(xs):
    """Return a list of the elements of iterable xs as Decorations/dicts."""
    # Normally xs is already a list of decorations/dicts.
    if xs is None:  # but xs can be None (a draw_node() didn't return anything)
        return []

    if not hasattr(xs, '__iter__'):  # or it can be a single element
        xs = [xs]

    # Return elements, wrapped as Decorations if they need it.
    return [x if type(x) in [Decoration, dict] else Decoration(x) for x in xs]


DEFAULT_TREE_STYLE = {  # the default style of a tree
    'aliases': {  # to name styles that can be referenced in draw_nodes
        'dist': {'fill': '#888'},
        'support': {'fill': '#f88'},  # a light red
    }
}

# A tree style can have things like:
#   my_tree_style = {
#      'shape': 'rectangular',  # or 'circular'
#      'min-size': 10,
#      'min-size-content': 5,
#   }

def add_to_style(style, style_old):
    """Return a style dictionary merging properly style_old and style."""
    # Update a copy of the old dict with the new (except for aliases).
    style_new = style_old.copy()
    style_new.update((k, v) for k, v in style.items() if k != 'aliases')

    # Update aliases (which is itself a dict).
    aliases = style_old.get('aliases', {}).copy()
    aliases.update(style.get('aliases', {}))
    style_new['aliases'] = aliases

    return style_new


# A decoration is a face with a position ("top", "bottom", "right",
# etc.), a column (an integer used for relative order with other faces
# in the same position), and an anchor point (to fine-tune the
# position of things like texts within them).

@dataclass
class Decoration:
    face: Face
    position: str
    column: int
    anchor: tuple

    def __init__(self, face, position='top', column=0, anchor=None):
        self.face = face
        self.position = position
        self.column = column
        self.anchor = anchor or default_anchors[position]

default_anchors = {'top':     (-1, 1),   # left, bottom
                   'bottom':  (-1, -1),  # left, top
                   'right':   (-1, 0),   # left, middle
                   'left':    ( 1, 0),   # right, middle
                   'aligned': (-1, 0)}   # left, middle


# The default layout.

def default_draw_node(node, collapsed):
    if not collapsed:
        face_dist = PropFace('dist', '%.2g', style='dist')
        yield Decoration(face_dist, position='top')

        face_support = PropFace('support', '%.2g', style='support')
        yield Decoration(face_support, position='bottom')

    if node.is_leaf or collapsed:
        yield Decoration(PropFace('name'), position='right')

DEFAULT_LAYOUT = Layout(name='default', draw_node=default_draw_node)


# Description of a label that we want to add to the representation of a node.

Label = namedtuple('Label', 'code style node_type position column anchor fs_max')
