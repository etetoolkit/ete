"""
Tree-related operations.

Sorting, changing the root to a node, moving branches, removing (prunning)...
"""

# "Arboriculture" may be more precise than "gardening", but it's a mouthful :)

from ete4.smartview.tree import update_size
from ete4 import Tree


def sort(tree, key=None, reverse=False):
    "Sort the tree in-place"
    key = key or (lambda node: (node.size[1], node.size[0], node.name))
    for node in tree.children:
        sort(node, key, reverse)
    tree.children.sort(key=key, reverse=reverse)


def root_at(node):
    "Return the tree of which node is part of, rerooted at the given node"
    root = node.get_tree_root()
    root.set_outgroup(node)
    new_root = root.get_tree_root()
    update_size(new_root)
    return new_root


def move(node, shift=1):
    "Change the position of the current node with respect to its parent"
    assert node.up, 'cannot move the root'

    siblings = node.up.children
    pos_old = siblings.index(node)
    pos_new = (pos_old + shift) % len(siblings)
    siblings[pos_old], siblings[pos_new] = siblings[pos_new], siblings[pos_old]


def remove(node):
    "Remove the given node from its tree"
    assert node.up, 'cannot remove the root'

    parent = node.up
    parent.children.remove(node)

    while parent:
        update_size(parent)
        parent = parent.up


def standardize(tree):
    "Transform from a tree not following strict newick conventions"
    if tree.is_root():
        update_size(tree)

    for node in tree.traverse():
        try:
            node.support = float(node.name)
            node.name = ''
        except ValueError:
            pass
