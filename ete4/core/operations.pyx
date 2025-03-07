"""
Tree-related operations.

Sorting, changing the root to a node, moving branches, removing (prunning)...
"""

import random
from collections import namedtuple, deque


def sort(tree, key=None, reverse=False):
    """Sort the tree in-place."""
    key = key or (lambda node: (node.size[1], node.size[0], node.name))

    for node in tree.traverse('postorder'):
        node.children.sort(key=key, reverse=reverse)


def root_at(node, bprops=None):
    """Set the given node as the root of the tree.

    The original root node will be used as the new root node, so any
    reference to it in the code will still be valid.

    :param node: Node to set as root. Its reference will be lost.
    :param bprops: List of branch properties (other than "dist" and "support").
    """
    root = node.root

    if root is node:
        return  # nothing to do!

    assert_root_consistency(root, bprops)

    positions = node.id  # child positions from root to node (like [1, 0, ...])

    interchange_references(root, node)  # root <--> node
    old_root = node  # now "node" points to where the old root was

    current_root = old_root  # current root, which will change in each iteration
    for child_pos in positions:
        current_root = rehang(current_root, child_pos, bprops)

    if len(old_root.children) == 1:
        join_branch(old_root, bprops)


def interchange_references(node1, node2):
    """Interchange the references of the given nodes.

    node1 will point where node2 was, and viceversa.
    """
    if node1 is node2:
        return

    # Interchange properties.
    node1.props, node2.props = node2.props, node1.props

    # Interchange children.
    children1 = node1.remove_children()
    children2 = node2.remove_children()
    node1.add_children(children2)
    node2.add_children(children1)

    # Interchange parents.
    up1 = node1.up
    up2 = node2.up
    pos1 = up1.children.index(node1) if up1 else None
    pos2 = up2.children.index(node2) if up2 else None

    if up1 is not None:
        up1.children.pop(pos1)
        up1.children.insert(pos1, node2)

    if up2 is not None:
        up2.children.pop(pos2)
        up2.children.insert(pos2, node1)

    node1.up = up2
    node2.up = up1


def set_outgroup(node, bprops=None, dist=None):
    """Change tree so the given node is set as outgroup.

    The original root node will be used as the new root node, so any
    reference to it in the code will still be valid.

    :param node: Node to set as outgroup (future first child of the root).
    :param bprops: List of branch properties (other than "dist" and "support").
    :param dist: Distance from the node, where we put the new root of the tree.
    """
    assert not node.is_root, 'cannot set the absolute tree root as outgroup'
    assert_root_consistency(node.root, bprops)

    intermediate = node.__class__()  # could be Tree() or PhyloTree(), etc.
    insert_intermediate(node, intermediate, bprops, dist)

    root_at(intermediate, bprops)


def assert_root_consistency(root, bprops=None):
    """Raise AssertionError if the root node of a tree looks inconsistent."""
    assert root.dist in [0, None], 'root has a distance'

    for pname in ['support'] + (bprops or []):
        assert pname not in root.props, f'root has branch property: {pname}'

    if len(root.children) == 2:
        s1, s2 = [n.support for n in root.children]
        assert s1 == s2, 'inconsistent support at the root: %r != %r' % (s1, s2)


def rehang(root, child_pos, bprops=None):
    """Rehang root on its child at position child_pos and return it."""
    # root === child  ->  child === root
    child = root.pop_child(child_pos)

    child.add_child(root)

    swap_props(root, child, ['dist', 'support'] + (bprops or []))

    return child  # which is now the new root


def swap_props(n1, n2, props):
    """Swap properties between nodes n1 and n2."""
    for pname in props:
        p1 = n1.props.pop(pname, None)
        p2 = n2.props.pop(pname, None)
        if p1 is not None:
            n2.props[pname] = p1
        if p2 is not None:
            n1.props[pname] = p2


def insert_intermediate(node, intermediate, bprops=None, dist=None):
    """Insert, between node and its parent, an intermediate node."""
    # == up ======= node  ->  == up === intermediate === node
    up = node.up

    pos_in_parent = up.children.index(node)  # save its position in parent
    up.children.pop(pos_in_parent)  # detach from parent

    intermediate.add_child(node)

    if 'dist' in node.props:  # split dist between the new and old nodes
        if dist is not None:
            node.dist, intermediate.dist = dist, node.dist - dist
        else:
            node.dist = intermediate.dist = node.dist / 2

    for prop in ['support'] + (bprops or []):  # copy other branch props if any
        if prop in node.props:
            intermediate.props[prop] = node.props[prop]

    up.children.insert(pos_in_parent, intermediate)  # put new where old was
    intermediate.up = up


def join_branch(node, bprops=None):
    """Substitute node for its only child."""
    # == node ==== child  ->  ====== child
    assert len(node.children) == 1, 'cannot join branch with multiple children'

    child = node.children[0]

    for pname in ['support'] + (bprops or []):
        if pname in node.props or pname in child.props:
            assert node.props.get(pname) == child.props.get(pname), \
                f'cannot join branches with different branch property: {pname}'

    if 'dist' in node.props:
        child.dist = (child.dist or 0) + node.dist  # restore total dist

    up = node.up
    pos_in_parent = up.children.index(node)  # save its position in parent
    up.children.pop(pos_in_parent)  # detach from parent
    up.children.insert(pos_in_parent, child)  # put child where the old node was
    child.up = up


def unroot(tree, bprops=None):
    """Unroot the tree (make the root not have 2 children).

    The convention in phylogenetic trees is that if the root has 2
    children, it is a "rooted" tree (the root is a real ancestor).
    Otherwise (typically a root with 3 children), the root is just
    an arbitrary place to hang the tree.
    """
    assert tree.is_root, 'unroot only makes sense from the root node'
    if len(tree.children) == 2:
        n1, n2 = tree.children
        assert not (n1.is_leaf and n2.is_leaf), 'tree has just two leaves'
        root_at(n1 if not n1.is_leaf else n2, bprops)


def move(node, shift=1):
    """Change the position of the current node with respect to its parent."""
    # ╴up╶┬╴node     ->  ╴up╶┬╴sibling
    #     ╰╴sibling          ╰╴node
    assert not node.is_root, 'cannot move the root'

    siblings = node.up.children

    pos_old = siblings.index(node)
    pos_new = (pos_old + shift) % len(siblings)

    siblings[pos_old], siblings[pos_new] = siblings[pos_new], siblings[pos_old]


def remove(node):
    """Remove the given node from its tree."""
    assert not node.is_root, 'cannot remove the root'

    parent = node.up
    parent.remove_child(node)


# Functions that used to be defined inside tree.pyx.

def common_ancestor(nodes):
    """Return the last node common to the lineages of the given nodes.

    If the given nodes don't have a common ancestor, it will return None.

    :param nodes: List of nodes whose common ancestor we want to find.
    """
    if not nodes:
        return None

    curr = nodes[0]  # current node being the last common ancestor

    for node in nodes[1:]:
        lin_node = set(node.lineage())
        curr = next((n for n in curr.lineage() if n in lin_node), None)

    return curr  # which is now the last common ancestor of all nodes


def populate(tree, size, names=None, model='yule',
             dist_fn=None, support_fn=None):
    """Populate tree with a dichotomic random topology.

    :param size: Number of leaves to add. All necessary intermediate
        nodes will be created too.
    :param names: Collection (list or set) of names to name the leaves.
        If None, leaves will be named using short letter sequences.
    :param model: Model used to generate the topology. It can be:

        - "yule" or "yule-harding": Every step a randomly selected leaf
          grows two new children.
        - "uniform" or "pda": Every step a randomly selected node (leaf
          or interior) grows a new sister leaf.

    :param dist_fn: Function to produce values to set as distance
        in newly created branches, or None for no distances.
    :param support_fn: Function to produce values to set as support
        in newly created internal branches, or None for no supports.
    """
    assert names is None or len(names) >= size, \
        f'names too small ({len(names)}) for size {size}'

    root = tree if not tree.children else create_dichotomic_sister(tree)

    if model in ['yule', 'yule-harding']:
        populate_yule(root, size)
    elif model in ['uniform', 'pda']:
        populate_uniform(root, size)
    else:
        raise ValueError(f'unknown model: {model}')

    if dist_fn or support_fn:
        add_branch_values(root, dist_fn, support_fn)

    add_leaf_names(root, names)


def create_dichotomic_sister(tree):
    """Make tree start with a dichotomy, with the old tree and a new sister."""
    children = tree.remove_children()  # pass all the children to a connector
    connector = tree.__class__(children=children)
    sister = tree.__class__()  # new sister, dichotomic with the old tree
    tree.add_children([connector, sister])
    return sister


def populate_yule(root, size):
    """Populate with the Yule-Harding model a topology with size leaves."""
    leaves = [root]  # will contain the current leaves
    for _ in range(size - 1):
        leaf = leaves.pop( random.randrange(len(leaves)) )

        node0 = leaf.add_child()
        node1 = leaf.add_child()

        leaves.extend([node0, node1])


def populate_uniform(root, size):
    """Populate with the uniform model a topology with size leaves."""
    if size < 2:
        return

    child0 = root.add_child()
    child1 = root.add_child()

    nodes = [child0]  # without child1, since it is in the same branch!

    for _ in range(size - 2):
        node = random.choice(nodes)  # random node (except root and child1)

        if node is child0 and random.randint(0, 1) == 1:  # 50% chance
            node = child1  # take the other child

        intermediate = root.__class__()  # could be Tree(), PhyloTree()...
        insert_intermediate(node, intermediate)  # ---up---inter---node
        leaf = intermediate.add_child()          # ---up---inter===node,leaf
        random.shuffle(intermediate.children)  # [node,leaf] or [leaf,node]

        nodes.extend([intermediate, leaf])


def add_branch_values(root, dist_fn, support_fn):
    """Add distances and support values to the branches."""
    for node in root.descendants():
        if dist_fn:
            node.dist = dist_fn()
        if support_fn and not node.is_leaf:
            node.support = support_fn()

    # Make sure the children of root have the same support.
    if any(node.support is None for node in root.children):
        for node in root.children:
            node.props.pop('support', None)
    else:
        for node in root.children[1:]:
            node.support = root.children[0].support


def add_leaf_names(root, names):
    """Add names to the leaves."""
    leaves = list(root.leaves())
    random.shuffle(leaves)  # so we name them in no particular order
    if names is not None:
        for node, name in zip(leaves, names):
            node.name = name
    else:
        for i, node in enumerate(leaves):
            node.name = make_name(i)


def make_name(i, chars='abcdefghijklmnopqrstuvwxyz'):
    """Return a short name corresponding to the index i."""
    # 0: 'a', 1: 'b', ..., 25: 'z', 26: 'aa', 27: 'ab', ...
    name = ''
    while i >= 0:
        name = chars[i % len(chars)] + name
        i = i // len(chars) - 1
    return name


def ladderize(tree, topological=False, reverse=False):
    """Sort branches according to the size of each partition.

    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    :param reverse: If True, sort with biggest partitions first.

    Example::

      t = Tree('(f,((d,((a,b),c)),e));')
      print(t)
      #   ╭╴f
      # ──┤     ╭╴d
      #   │  ╭──┤  ╭──┬╴a
      #   ╰──┤  ╰──┤  ╰╴b
      #      │     ╰╴c
      #      ╰╴e

      t.ladderize()
      print(t)
      # ──┬╴f
      #   ╰──┬╴e
      #      ╰──┬╴d
      #         ╰──┬╴c
      #            ╰──┬╴a
      #               ╰╴b
    """
    sizes = {}  # sizes of the nodes

    # Key function for the sort order. Sort by size, then by # of children.
    key = lambda node: (sizes[node], len(node.children))

    # Distance function (branch length to consider for each node).
    dist = ((lambda node: 1) if topological else
            (lambda node: float(node.props.get('dist', 1))))

    for node in tree.traverse('postorder'):
        if node.is_leaf:
            sizes[node] = dist(node)
        else:
            node.children.sort(key=key, reverse=reverse)  # time to sort!

            sizes[node] = dist(node) + max(sizes[n] for n in node.children)

            for n in node.children:
                sizes.pop(n)  # free memory, no need to keep all the sizes


def to_dendrogram(tree):
    """Convert tree to dendrogram (remove all distance values)."""
    for node in tree.traverse():
        node.props.pop('dist', None)


def to_ultrametric(tree, topological=False):
    """Convert tree to ultrametric (all leaves equidistant from root)."""
    tree.dist = tree.dist or 0  # covers common case of not having dist set

    update_sizes_all(tree)  # so node.size[0] are distances to leaves

    dist_full = tree.size[0]  # original distance from root to furthest leaf

    if (topological or dist_full <= 0 or
        any(node.dist is None for node in tree.traverse())):
        # Ignore original distances and just use the tree topology.
        for node in tree.traverse():
            node.dist = 1 if node.up else 0
        update_sizes_all(tree)
        dist_full = dist_full if dist_full > 0 else tree.size[0]

    for node in tree.traverse():
        if node.dist > 0:
            d = sum(n.dist for n in node.ancestors(root=tree))
            node.dist *= (dist_full - d) / node.size[0]


def resolve_polytomy(tree, descendants=True):
    """Convert tree to a series of dicotomies if it is a polytomy.

    A polytomy is a node that has more than 2 children. This
    function changes them to a ladderized series of dicotomic
    branches. The tree topology modification is arbitrary (no
    important results should depend on it!).

    :param descendants: If True, resolve all polytomies in the tree,
        including all root descendants. Otherwise, do it only for the root.
    """
    for node in tree.traverse():
        if len(node.children) > 2:
            children = node.remove_children()  #  x ::: a,b,c,d,e

            # Create "backbone" nodes:  x --- * --- * ---
            for i in range(len(children) - 2):
                node = node.add_child(dist=0, support=0)

            # Add children in order:  x === d,* === c,* === b,a
            node.add_child(children[0])  # first:  x --- * --- * --- a
            for i in range(1, len(children)):
                node.add_child(children[i], support=0)
                node = node.up

        if not descendants:
            break


def farthest_descendant(tree, topological=False):
    """Return the farthest descendant and its distance."""
    d = (lambda node: 1) if topological else (lambda node: node.dist)  # dist

    dist_root = {tree: 0}  # will contain all distances to the root

    node_farthest, dist_farthest = tree, 0
    for node in traverse(tree, order=-1):  # traverse in preorder
        if node is not tree:
            dist_root[node] = dist = dist_root[node.up] + d(node)
            if dist > dist_farthest:
                node_farthest, dist_farthest = node, dist

    return node_farthest, dist_farthest


def farthest(tree, topological=False):
    """Return the farthest nodes and the diameter of the tree."""
    d = (lambda node: 1) if topological else (lambda node: node.dist)  # dist

    def last(x):
        return x[-1]  # return the last element (used later for comparison)

    # Part 1: Find the farthest descendant for all nodes.

    fd = {}  # dict of {node: (farthest_descendant, dist_from_parent_to_it)}
    for node in traverse(tree, order=+1):  # traverse in postorder
        if node.is_leaf:
            fd[node] = (node, d(node))
        else:
            f_leaf, dist = max((fd[n] for n in node.children), key=last)
            fd[node] = (f_leaf, (d(node) if node is not tree else 0) + dist)

    # Part 2: Find the extremes and the diameter.

    # The first extreme is fixed. The second and the diameter will be updated.
    extreme1, diameter = fd[tree]  # first extreme: farthest node from the root
    extreme2 = tree  # so far, but may change later

    # Go towards the root, updating the second extreme and diameter.
    prev = extreme1  # the node that we saw previous to the current one
    curr = extreme1.up  # the current node we are visiting
    d_curr_e1 = d(extreme1)  # distance from current to the 1st extreme
    while curr is not tree.up:
        leaf, dist = max((fd[n] for n in curr.children if n is not prev),
                         default=(curr, 0), key=last)
        if dist + d_curr_e1 > diameter:
            extreme2, diameter = leaf, dist + d_curr_e1

        d_curr_e1 += d(curr) if curr is not tree else 0
        prev, curr = curr, curr.up

    return extreme1, extreme2, diameter


def midpoint(tree, topological=False):
    """Return the node in the middle and its distance from the exact center."""
    d = (lambda node: 1) if topological else (lambda node: node.dist)

    # Find the farthest node and diameter.
    node, _, diameter = farthest(tree, topological)

    # Go thru ancestor nodes until we cover more distance than the tree radius.
    dist = diameter / 2 - d(node)  # radius of the tree minus branch dist
    while dist > 0:
        node = node.up
        dist -= d(node)

    return node, dist + d(node)  # NOTE: `dist` is negative


def set_midpoint_outgroup(tree, topological=False):
    node, dist = midpoint(tree, topological)
    set_outgroup(node, dist=dist)


# Traversing the tree.

def traverse(tree, order=-1, is_leaf_fn=None):
    """Traverse the tree and yield nodes in pre (< 0) or post (> 0) order."""
    visiting = [(tree, False)]
    while visiting:
        node, seen = visiting.pop()

        is_leaf = is_leaf_fn(node) if is_leaf_fn else node.is_leaf

        if is_leaf or (order <= 0 and not seen) or (order >= 0 and seen):
            yield node

        if not seen and not is_leaf:
            visiting.append((node, True))  # add node back, but mark as seen
            visiting += [(n, False) for n in node.children[::-1]]


def traverse_bfs(tree, is_leaf_fn=None):
    """Yield nodes with a breadth-first search (level order traversal)."""
    visiting = deque([tree])
    while visiting:
        node = visiting.popleft()
        yield node
        if not is_leaf_fn or not is_leaf_fn(node):
            visiting.extend(node.children)


# Position on the tree: current node, number of visited children.
TreePos = namedtuple('TreePos', 'node nch')

class Walker:
    """Represents the position when traversing a tree."""

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
        return tuple(branch.nch for branch in self.visiting[:-1])

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


def walk(tree):
    """Yield an iterator as it traverses the tree."""
    it = Walker(tree)  # node iterator
    while it.visiting:
        if it.first_visit:
            yield it

            if it.node.is_leaf or not it.descend:
                it.go_back()
                continue

        if it.has_unvisited_branches:
            it.add_next_branch()
        else:
            yield it
            it.go_back()


# Size-related functions.

def update_sizes_all(tree):
    """Update sizes of all the nodes in the tree."""
    for node in tree.traverse('postorder'):
        update_size(node)


def update_sizes_from(node):
    """Update the sizes from the given node to the root of the tree."""
    while node is not None:
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
