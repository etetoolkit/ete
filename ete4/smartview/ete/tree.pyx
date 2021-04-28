"""
Class to represent trees (which are nodes connected to other nodes) and
functions to read and write them.

The text representation of the trees are expected to be in the newick format:
https://en.wikipedia.org/wiki/Newick_format
"""

from collections import namedtuple
from ete4 import Tree

TreePos = namedtuple('TreePos', 'node nch')
# Position on the tree: current node, number of visited children.



# cdef class Tree:
    # cdef public str name
    # cdef public double length
    # cdef public dict properties
    # cdef public list children
    # cdef public Tree parent
    # cdef public (double, double) size  # sum of lenghts, number of leaves

    # def __init__(self, content='', children=None):
        # self.parent = None
        # self.name = ''
        # self.length = -1
        # self.properties = {}
        # if not content.startswith('('):
            # self.init_normal(content.rstrip(';'), children)
            # # the rstrip() avoids ambiguity when the full tree is just ";"
        # else:
            # if children:
                # raise NewickError('init from newick cannot have children')
            # self.init_from_newick(content)

    # def init_normal(self, content, children):
        # self.content = content
        # self.children = children or []
        # for node in self.children:
            # node.parent = self
        # update_size(self)

    # def init_from_newick(self, tree_text):
        # tree = loads(tree_text)
        # self.content = tree.content
        # self.children = tree.children
        # for node in self.children:
            # node.parent = self
        # self.size = tree.size

    # @property
    # def content(self):
        # return content_repr(self)

    # @content.setter
    # def content(self, content):
        # self.name, self.length, self.properties = get_content_fields(content)

    # @property
    # def is_leaf(self):
        # return not self.children

    # def walk(self):
        # return walk(self)

    # def copy(self):
        # return copy(self)

    # def __iter__(self):
        # "Yield all the nodes of the tree in preorder"
        # yield self
        # for node in self.children:
            # yield from node

    # def __getitem__(self, node_id):
        # "Return the node that matches the given node_id, or None"
        # if type(node_id) == str:  # node_id can be the name of a node
            # return next((node for node in self if node.name == node_id), None)
        # elif type(node_id) == int:  # or the index of a child
            # return self.children[node_id]
        # else:                       # or a list/tuple of the (sub-sub-...)child
            # node = self
            # for i in node_id:
                # node = node.children[i]
            # return node

    # def __repr__(self):
        # children_reprs = ', '.join(repr(c) for c in self.children)
        # return 'Tree(%r, [%s])' % (self.content, children_reprs)

    # def __str__(self):
        # return to_str(self)

def copy(tree):
    "Return a copy of the tree"
    return Tree(tree.content, children=[copy(node) for node in tree.children])


def to_str(tree, are_last=None):
    "Return a string with a visual representation of the tree"
    are_last = are_last or []
    line = get_branches_repr(are_last) + (tree.content or '<empty>')
    return '\n'.join([line] +
        [to_str(n, are_last + [False]) for n in tree.children[:-1]] +
        [to_str(n, are_last + [True])  for n in tree.children[-1:]])


def get_branches_repr(are_last):
    """Return a text line representing the open branches according to are_last

    are_last is a list of bools. It says at each level if we are the last node.

    Example (with more spaces for clarity):
      [True , False, True , True , True ] ->
      '│             │      │      └─   '
    """
    if len(are_last) == 0:
        return ''

    prefix = ''.join('  ' if is_last else '│ ' for is_last in are_last[:-1])
    return prefix + ('└─' if are_last[-1] else '├─')


def  update_size(node):
    if node.is_leaf():
        node.size = (node.dist, 1)
    sumlengths, nleaves = get_size(node.children)
    node.size = (abs(node.dist) + sumlengths, max(1, nleaves))

cdef (double, double) get_size(nodes):
    "Return the size of all the nodes stacked"
    # The size of a node is (sumlengths, nleaves) with sumlengths the length to
    # its furthest leaf (including itself) and nleaves its number of leaves.
    sumlengths = nleaves = 0
    for node in nodes:
        update_size(node)
        sumlengths = max(sumlengths, node.size[0])
        nleaves += node.size[1]
    return sumlengths, nleaves



def get_node(tree, node_id):
    "Return the node that matches the given node_id, or None"
    if callable(node_id):       # node_id can be a True/False function
        return next((node for node in tree.traverse() if node_id(node)), None)
    elif type(node_id) == str:  # or the name of a node
        return next((node for node in tree.traverse() if node.name == node_id), None)
    elif type(node_id) == int:  # or the index of a child
        return tree.children[node_id]
    else:                       # or a list/tuple of the (sub-sub-...)child
        node = tree
        for i in node_id:
            node = node.children[i]
        return node


def walk(tree):
    "Yield an iterator as it traverses the tree"
    it = Walker(tree)  # node iterator
    while it.visiting:
        if it.first_visit:
            yield it

            if it.node.is_leaf() or not it.descend:
                it.go_back()
                continue

        if it.has_unvisited_branches:
            it.add_next_branch()
        else:
            yield it
            it.go_back()


class Walker:
    def __init__(self, root):
        self.visiting = [TreePos(node=root, nch=0)]
        # will look like: [(root, 2), (child2, 5), (child25, 3), (child253, 0)]
        self.descend = True

    def go_back(self):
        self.visiting.pop()
        if self.visiting:
            node, nch = self.visiting[-1]
            self.visiting[-1] = TreePos(node, nch + 1)
        self.descend = True

    @property
    def node(self):
        return self.visiting[-1].node

    @property
    def node_id(self):
        return tuple([branch.nch for branch in self.visiting[:-1]])

    @property
    def first_visit(self):
        return self.visiting[-1].nch == 0

    @property
    def has_unvisited_branches(self):
        node, nch = self.visiting[-1]
        return nch < len(node.children)

    def add_next_branch(self):
        node, nch = self.visiting[-1]
        self.visiting.append(TreePos(node=node.children[nch], nch=0))
