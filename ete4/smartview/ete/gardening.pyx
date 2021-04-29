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

    # Go from the current root towards the goal node, switching relations.
    old_root, node_id = get_root_id(future_root)

    current = old_root
    for i in node_id:
        new = current.children.pop(i)

        new.up, current.up = None, new
        new.dist, current.dist = 0, new.dist
        switch_property(current, new, 'support')

        new.children.append(current)

        # update_size(current)
        # update_size(new)

        current = new

    if len(old_root.children) == 1:
        substitute(old_root, old_root.children[0])

    update_size(current)
    return current


def add_intermediate(node):
    "Add an intermediate parent to the given node and return it"
    parent = node.up

    pos = parent.children.index(node)  # position of node in parent's children

    parent.children.pop(pos)  # detach from parent

    intermediate = Tree('')  # create intermediate node
    intermediate.children = [node]
    intermediate.up = parent

    if node.dist >= 0:  # split length between the new and old nodes
        node.dist = intermediate.dist = node.dist / 2

    parent.children.insert(pos, intermediate)  # add at previous position

    return intermediate


def get_root_id(node):
    "Return the root of the tree of which node is part of, and its node_id"
    # For the returned  (root, node_id)  we have  root[node_id] == node
    positions = []
    current_root, parent = node, node.up
    while parent:
        positions.append(parent.children.index(current_root))
        current_root, parent = parent, parent.up
    return current_root, positions[::-1]


def switch_property(n1, n2, pname='support'):
    "Switch for nodes n1 and n2 the values of property pname"
    p1 = n1.properties.get(pname)
    p2 = n2.properties.get(pname)

    if p1:
        n2.properties[pname] = p1  # update it from the value in n1
    elif pname in n2.properties:
        del n2.properties[pname]  # or delete it if n1 doesn't have it

    if p2:
        n1.properties[pname] = p2
    elif pname in n1.properties:
        del n1.properties[pname]


def substitute(old, new):
    "Substitute old node for new node in the tree where the old node was"
    if old.dist > 0:
        new.dist += old.dist  # add its length to the new if it has any

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


def update_size(node):
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
