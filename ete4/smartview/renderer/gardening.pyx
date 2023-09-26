"""
Tree-related operations.

Sorting, changing the root to a node, moving branches, removing (prunning)...
"""

# "Arboriculture" may be more precise than "gardening", but it's a mouthful :)

def sort(tree, key=None, reverse=False):
    """Sort the tree in-place."""
    key = key or (lambda node: (node.size[1], node.size[0], node.name))

    for node in tree.children:
        sort(node, key, reverse)

    tree.children.sort(key=key, reverse=reverse)


def root_at(node, bprops=None):
    """Return the tree of which node is part of, rerooted at the given node.

    :param node: Node where to set root (future first child of the new root).
    :param bprops: List of branch properties (other than "dist" and "support").
    """
    old_root, node_id = get_root_id(node)

    assert_consistency(old_root)
    assert node != old_root, 'cannot root on root node'

    if node.up == old_root:  # node is a direct child of the root node
        old_root.children.remove(node)      # the "node in which we root" is
        old_root.children.insert(0, node)   # the 1st child of the root node
        return old_root  # keep the same root node as before

    split_branch(node, bprops)

    root = old_root  # current root, which will change in each iteration
    for child_pos in node_id:
        root = rehang(root, child_pos, bprops)

    if len(old_root.children) == 1:
        join_branch(old_root)

    return root


def assert_consistency(root):
    """Raise AssertionError if the root node of a tree looks inconsistent."""
    assert not root.name, 'root has a name'

    assert root.dist in [0, None], 'root has a distance'

    if len(root.children) == 2:
        ch1, ch2 = root.children
        s1, s2 = ch1.props.get('support'), ch2.props.get('support')
        assert s1 == s2, 'inconsistent support at the root: %r != %r' % (s1, s2)


def get_root_id(node):
    """Return the root of the tree of which node is part of, and its node_id."""
    # For the returned  (root, node_id)  we have  root[node_id] == node
    positions = []
    current, parent = node, node.up
    while parent:
        positions.append(parent.children.index(current))
        current, parent = parent, parent.up
    return current, positions[::-1]


def rehang(root, child_pos, bprops):
    """Rehang node on its child at position child_pos and return it."""
    # root === child  ->  child === root
    child = root.pop_child(child_pos)

    child.up = root.up
    child.add_child(root)

    swap_props(root, child, ['dist', 'support'] + (bprops or []))

    return child  # which is now the parent of its previous parent


def swap_props(n1, n2, props):
    """Swap properties between nodes n1 and n2."""
    for pname in props:
        p1 = n1.props.pop(pname, None)
        p2 = n2.props.pop(pname, None)
        if p1 is not None:
            n2.props[pname] = p1
        if p2 is not None:
            n1.props[pname] = p2


def split_branch(node, bprops=None):
    """Add an intermediate parent to the given node and return it."""
    # == up ======= node  ->  == up === intermediate === node
    up = node.up

    pos_in_parent = up.children.index(node)  # save its position in parent
    up.children.pop(pos_in_parent)  # detach from parent

    intermediate = node.__class__()  # create intermediate node (of same type)
    intermediate.add_child(node)

    if 'dist' in node.props:  # split dist between the new and old nodes
        node.dist = intermediate.dist = node.dist / 2

    if 'support' in node.props:  # copy support if it has it
        intermediate.support = node.support

    for prop in (bprops or []):  # and copy other branch props if any
        if prop in node.props:
            intermediate.props[prop] = node.props[prop]

    up.children.insert(pos_in_parent, intermediate)  # put new where old was
    intermediate.up = up

    return intermediate


def join_branch(node):
    """Substitute node for its only child."""
    # == node ==== child  ->  ====== child
    assert len(node.children) == 1, 'cannot join branch with multiple children'

    child = node.children[0]

    if 'support' in node.props and 'support' in child.props:
        assert node.support == child.support, \
            'cannot join branches with different support'

    if 'dist' in node.props:
        child.dist = (child.dist or 0) + node.dist  # restore total dist

    up = node.up
    pos_in_parent = up.children.index(node)  # save its position in parent
    up.children.pop(pos_in_parent)  # detach from parent
    up.children.insert(pos_in_parent, child)  # put child where the old node was
    child.up = up


def move(node, shift=1):
    """Change the position of the current node with respect to its parent."""
    # ╴up╶┬╴node     ->  ╴up╶┬╴sibling
    #     ╰╴sibling          ╰╴node
    assert node.up, 'cannot move the root'

    siblings = node.up.children

    pos_old = siblings.index(node)
    pos_new = (pos_old + shift) % len(siblings)

    siblings[pos_old], siblings[pos_new] = siblings[pos_new], siblings[pos_old]


def remove(node):
    """Remove the given node from its tree."""
    assert node.up, 'cannot remove the root'

    parent = node.up
    parent.remove_child(node)


def update_sizes_all(tree):
    for node in tree.children:
        update_sizes_all(node)
    update_size(tree)


def update_sizes_from(node):
    "Update the sizes from the given node to the root of the tree"
    while node:
        update_size(node)
        node = node.up


def update_size(node):
    """Update the size of the given node."""
    sumdists, nleaves = get_size(node.children)
    dx = float(node.props.get('dist', 0 if node.up is None else 1)) + sumdists
    node.size = (dx, max(1, nleaves))


cdef (double, double) get_size(nodes):
    """Return the size of all the nodes stacked."""
    # The size of a node is (sumdists, nleaves) with sumdists the dist to
    # its furthest leaf (including itself) and nleaves its number of leaves.
    cdef double sumdists, nleaves

    sumdists = 0
    nleaves = 0
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

    update_sizes_all(tree)

    for node in tree.traverse():
        if not node.is_leaf and node.name is not None:
            name_split = node.name.rsplit(":", 1)
            if len(name_split) > 1:
                # Whether node name contains the support value
                name, support = name_split
            else:
                # Whether node name is the support value
                name, support = ('', node.name)
            try:
                node.support = float(support)
                node.name = name
            except ValueError:
                pass
