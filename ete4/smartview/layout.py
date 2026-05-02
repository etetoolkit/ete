"""
Definition of the basic elements for a tree representation (Layout and
Faces), extra labels (Label), and the default tree style.

The valid keys for a tree style are:

- shape
- radius
- angle-start
- angle-end
- angle-span
- node-height-min
- content-height-min
- collapsed
- show-popup-props
- hide-popup-props
- is-leaf-fn
- box
- dot
- hz-line
- vt-line
- aliases

Some properties will be used directly by the backend: shape,
node-height-min, content-height-min, radius, angle-start, angle-end,
angle-span, show-popup-props, hide-popup-props, is-leaf-fn.

Others  will be controlled by the css class of the element in the frontend:
box, dot, hz-line, vt-line.

And the "aliases" part will tell the frontend which styles are referenced.

Example of a tree style in use::

  my_tree_style = {
      'shape': 'circular',  # or 'rectangular'
      'radius': 5,
      'angle-start': -180,
      'angle-end': 180,  # alternatively we can give 'angle-span'
      'node-height-min': 10,
      'content-height-min': 5,
      'collapsed': {'shape': 'outline', 'fill-opacity': 0.8},
      'show-popup-props': None,  # all defined properties
      'hide-popup-props': ['support'],  # except support
      'is-leaf-fn': lambda node: node.level > 4,
      'box': {'fill': 'green', 'opacity': 0.1, 'stroke': 'blue'},
      'dot': {'shape': 'hexagon', 'fill': 'red'},
      'hz-line': {'stroke-width': 2},
      'vt-line': {'stroke': '#ffff00'},
      'aliases': {
          'support': {'fill': 'green'},  # changes the default one
          'my-leaf': {'fill': 'blue', 'font-weight': 'bold'},
      },
  }

  layout = Layout(name='Example layout', draw_tree=my_tree_style)
"""

from collections import namedtuple
from dataclasses import dataclass, field
from functools import lru_cache
import inspect
import copy

from .faces import Face, PropFace, TextFace


# Layouts have all the information needed to represent a tree.

class Layout:
    """
    A complete specification of how to represent a tree.

    Layouts have a name and two functions providing the style and
    faces of the full tree and the visible nodes.

    When exploring a tree, layouts compose. Using several layouts will
    add extra graphic representations, and/or overwrite some styles
    from previous layouts.
    """

    # Optional: list of prop names this layout will access during draw_node().
    # Used by SmartView to preload lazy props before rendering.
    preload_props: list = []

    def __init__(self, name, draw_tree=None, draw_node=None, cache_size=None,
                 active=True):
        """
        :param name: String identifying the layout (to select in the gui, etc.)
        :param draw_tree: Function specifying tree style and faces.
        :param draw_node: Function specifying node style and faces.
        :param cache_size: Number of elements that draw_node() will memorize
            (useful values are None for infinite cache, and 0 for no cache).
        :param active: If True, the layout is used immediately when exploring.
        """
        self.cache_size = cache_size  # used to cache functions in the setters

        # Name. This is mainly to activate/deactivate the layout in the gui.
        assert type(name) is str
        self.name = name

        # Tree representation (style and faces).
        self.draw_tree = draw_tree

        # Node representation (style and faces).
        self.draw_node = draw_node

        # Set if the layout should be initially active in the gui.
        self.active = active  # TODO: Find a better place for this

    @property
    def draw_tree(self):
        return self._draw_tree

    @draw_tree.setter
    def draw_tree(self, value):
        if value is None:
            self._draw_tree = lambda tree: [DEFAULT_TREE_STYLE]
        elif type(value) is dict:
            self._draw_tree = lambda tree: [DEFAULT_TREE_STYLE, value]
        elif callable(value):
            @lru_cache(maxsize=self.cache_size)
            def cached_draw_tree(tree):
                return [DEFAULT_TREE_STYLE] + to_elements(value(tree))
            self._draw_tree = cached_draw_tree
        else:
            raise ValueError('draw_tree can be either a dict or a function')

    @property
    def draw_node(self):
        return self._draw_node

    @draw_node.setter
    def draw_node(self, value):
        assert value is None or callable(value)

        if value is None:
            self._draw_node = lambda node, collapsed: []
            return

        f = value  # nicer name, since it is a function

        # We use an auxiliary function to cache its results.
        arity = len(inspect.signature(f).parameters)
        if arity == 1:  # f(node) (unspecified what to do with collapsed)
            @lru_cache(maxsize=self.cache_size)
            def cached_draw_node(node, collapsed):
                if not collapsed:
                    return to_elements(f(node))  # get just for the node
                else:
                    return [x for n in collapsed   # get from all siblings
                                for x in to_elements(f(n))]
        elif arity == 2:  # f(node, collapsed) (fully specified)
            @lru_cache(maxsize=self.cache_size)
            def cached_draw_node(node, collapsed):
                return to_elements(f(node, collapsed))
        else:
            raise ValueError('draw_node can have only 1 or 2 arguments.')

        self._draw_node = cached_draw_node  # use the auxiliary caching function


def to_elements(xs):
    """Return a list of the elements of iterable xs as Faces/dicts."""
    # Normally xs is already a list of faces/dicts.
    if xs is None:  # but xs can be None (a draw_node() didn't return anything)
        return []
    elif type(xs) is dict or issubclass(type(xs), Face):  # or single element
        return [xs]  # return a list containing just that element
    else:  # normal case (iterable of faces/dicts)
        return list(xs)  # return a list with the elements
    # NOTE: If xs is a generator, its cached value is an empty list!


DEFAULT_TREE_STYLE = {  # the default style of a tree
    'show-popup-props': ['dist', 'support'],
    'aliases': {  # to name styles that can be referenced in draw_node
        'dist': {'fill': '#888'},
        'support': {'fill': '#f88'},  # a light red
    }
}


def update_style(style, style_new):
    """Update the style dictionary merging properly with style_new."""
    subdicts = {k for k in style_new if type(style_new[k]) is dict and
                                        type(style.get(k)) is dict}
    style.update((k, copy.deepcopy(v)) for k, v in style_new.items()
                     if k not in subdicts)
    for k in subdicts:
        update_style(style[k], style_new[k])


# The default layout.

def default_draw_node(node, collapsed):
    if not collapsed:
        yield PropFace('dist', '%.2g', style='dist', position='top')
        yield PropFace('support', '%.2g', style='support', position='bottom')
    if node.is_leaf or collapsed:
        yield PropFace('name', position='right')

BASIC_LAYOUT = Layout(name='basic', draw_node=default_draw_node)


# Description of a label that we want to add to the representation of a node.

Label = namedtuple('Label', 'code style node_type position column anchor fs_max')
