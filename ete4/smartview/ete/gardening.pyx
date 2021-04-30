"""
Tree-related operations.

Sorting, changing the root to a node, moving branches, removing (prunning)...
"""

# "Arboriculture" may be more precise than "gardening", but it's a mouthful :)

from ete4 import Tree


def sort(tree, key=None, reverse=False):
    "Sort the tree in-place"
    key = key or (lambda node: (node.size[1], node.size[0], node.name))
    for node in tree.children:
        sort(node, key, reverse)
    tree.children.sort(key=key, reverse=reverse)


def root_at(node):
    "Return the tree of which node is part of, rerooted at the given node"
    if not node.up:
        return node

    future_root = add_intermediate(node)

    old_root, node_id = get_root_id(future_root)

    current = old_root  # current root, which will change in each iteration
    for child_pos in node_id:
        current = rehang(current, child_pos)

    if len(old_root.children) == 1:
        substitute(old_root, old_root.children[0])

    return current


def add_intermediate(node):
    "Add an intermediate parent to the given node and return it"
    parent = node.up

    parent.children.remove(node)  # detach from parent

    intermediate = Tree('')  # create intermediate node
    intermediate.children = [node]
    intermediate.up = parent

    if node.dist >= 0:  # split dist between the new and old nodes
        node.dist = intermediate.dist = node.dist / 2

    parent.children.append(intermediate)

    return intermediate


def get_root_id(node):
    "Return the root of the tree of which node is part of, and its node_id"
    # For the returned  (root, node_id)  we have  root[node_id] == node
    positions = []
    current, parent = node, node.up
    while parent:
        positions.append(parent.children.index(current))
        current, parent = parent, parent.up
    return current, positions[::-1]


def rehang(node, child_pos):
    "Rehang node on its child at position child_pos and return it"
    # Swap parenthood.
    child = node.children.pop(child_pos)
    child.children.append(node)
    node.up, child.up = child, node.up

    swap_branch_properties(node, child)  # so they reflect the rehanging
    # The branch properties of a node reflect its relation wrt its parent.

    update_size(node)   # since their total dist till the furthest leaf and
    update_size(child)  # their total number of leaves will have changed

    return child  # which is now the parent of its previous parent


def swap_branch_properties(n1, n2):
    "Swap between nodes n1 and n2 all their branch properties"
    # "dist" (encoded as a data attribute) is a branch property -> swap
    n1.dist, n2.dist = n2.dist, n1.dist

    # "name" (also a data attribute) is a node property -> don't swap

    # "support" (encoded in the properties dict) is a branch property -> swap
    s1 = n1.properties.get('support')
    s2 = n2.properties.get('support')
    n1.properties.pop('support', None)
    n2.properties.pop('support', None)
    if s1:
        n2.properties['support'] = s1
    if s2:
        n1.properties['support'] = s2

    # And that's it. I don't know of any other standard branch properties.


def substitute(old, new):
    "Substitute old node for new node in the tree where the old node was"
    if old.dist > 0:
        new.dist += old.dist  # add its dist to the new if it has any

    parent = old.up
    parent.children.remove(old)
    parent.children.append(new)
    new.up = parent


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


def update_all_sizes(tree):
    for node in tree.children:
        update_all_sizes(node)
    update_size(tree)


def update_size(node):
    if node.is_leaf():
        node.size = (node.dist, 1)
    sumdists, nleaves = get_size(node.children)
    node.size = (abs(node.dist) + sumdists, max(1, nleaves))


cdef (double, double) get_size(nodes):
    "Return the size of all the nodes stacked"
    # The size of a node is (sumdists, nleaves) with sumdists the dist to
    # its furthest leaf (including itself) and nleaves its number of leaves.
    cdef double sumdists, nleaves
    sumdists = nleaves = 0
    for node in nodes:
        sumdists = max(sumdists, node.size[0])
        nleaves += node.size[1]
    return sumdists, nleaves


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


def standardize(tree):
    "Transform from a tree not following strict newick conventions"
    if tree.dist == -1: 
        tree.dist = 0

    update_all_sizes(tree)

    for node in tree.traverse():
        try:
            node.support = float(node.name)
            node.name = ''
        except ValueError:
            pass
