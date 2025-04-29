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
    if node.is_root:
        return  # nothing to do!

    root = node.root  # get the root of the tree

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
        up1.children[pos1] = node2

    if up2 is not None:
        up2.children[pos2] = node1

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
    up = node.up  # original parent of node

    pos_in_parent = up.children.index(node)  # save its position in parent

    intermediate.add_child(node)  # == intermediate === node

    # Update dist in intermediate (and in node), and branch properties.
    if 'dist' in node.props:  # split dist between the new and old nodes
        if dist is not None:
            node.dist, intermediate.dist = dist, node.dist - dist
        else:
            node.dist = intermediate.dist = node.dist / 2

    for prop in ['support'] + (bprops or []):  # copy other branch props if any
        if prop in node.props:
            intermediate.props[prop] = node.props[prop]

    # == up === intermediate  (and we already have  intermediate === node)
    up.children[pos_in_parent] = intermediate  # put the new where old node was
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
    if not node.is_root:
        i = up.children.index(node)  # position that node had in its parent
        up.children[i] = child  # put child where the old node was
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
    for _ in range(size - 1):  # grow 2 leaves from a leaf in each iteration
        i = random.randrange(len(leaves))  # pick one leaf index
        node = leaves[i]  # take that leaf, which will be the parent node

        leaf0 = node.add_child()  # grow leaves from that parent
        leaf1 = node.add_child()

        leaves[i] = leaf0  # put one of the leaves where the old one was
        leaves.append(leaf1)  # and append the other leaf to our leaves list too


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

        nodes.append(intermediate)
        nodes.append(leaf)


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


def closest_leaf(tree, dist_max=-1, selector=None,
                 is_leaf_fn=None, topological=False):
    """Return the closest descendant leaf from the tree.

    :param tree: Tree (starting node) for which to find its closest leaf.
    :param dist_max: If > 0, do not consider nodes farther than this distance.
    :param selector: Function that returns True for the selected leaves.
        If None, all leaves will be selected.
    :param is_leaf_fn: Function that takes a node and returns True if it is
        considered a leaf. If None, node.is_leaf is used.
    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    """
    # Get default functions to select leaves and find if a node is a leaf.
    selector = selector or (lambda node: True)  # select all by default
    is_leaf = is_leaf_fn or (lambda node: node.is_leaf)

    # Create a traversing generator that we can control while traversing.
    descend = [True]  # to control if we want to stop descending
    traversal = traverse_full(tree, order=-1, is_leaf_fn=is_leaf_fn,
                              topological=topological, descend=descend)

    leaf_closest, dist_closest = None, -1  # current closest leaf and distance
    for node, _, dist in traversal:
        if ((leaf_closest is not None and dist > dist_closest) or
            (dist_max > 0             and dist > dist_max)):
            descend[0] = False  # signal the generator not to descend
        elif (is_leaf(node) and selector(node) and  # valid leaf
              (leaf_closest is None or dist < dist_closest)):  # closer!
            leaf_closest, dist_closest = node, dist

    return leaf_closest, dist_closest


def closest_relative(leaf, selector=None, is_leaf_fn=None, topological=False):
    """Return the closest relative leaf to the given leaf.

    :param leaf: Leaf for which to find its closest relative leaf.
    :param selector: Function that returns True for the selected leaves.
        If None, all leaves will be selected.
    :param is_leaf_fn: Function that takes a node and returns True if it is
        considered a leaf. If None, node.is_leaf is used.
    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    """
    d = get_distance_fn(topological)

    closest, dist_closest = None, -1  # current closest relative and distance

    node = leaf  # we'll go from the leaf towards the root
    dist_from_leaf = 0  # and accumulate the distance from the leaf
    while not node.is_root and (closest is None or dist_from_leaf < dist_closest):
        dist_from_leaf += d(node)

        for sis in node.get_sisters():
            sdist = d(sis)  # sister dist (length of sister branch)
            dist_max = dist_closest - (dist_from_leaf + sdist)
            if closest is None or dist_max > 0:
                closest_sis, dist = closest_leaf(sis, dist_max, selector,
                                                 is_leaf_fn, topological)
                if closest_sis is not None:  # found closest leaf from sis
                    dist_total = dist_from_leaf + sdist + dist  # leaf to leaf
                    if closest is None or dist_total < dist_closest:
                        closest, dist_closest = closest_sis, dist_total

        node = node.up

    return closest, dist_closest


def farthest_descendant(tree, is_leaf_fn=None, topological=False):
    """Return the farthest descendant and its distance."""
    node_farthest, dist_farthest = tree, 0
    for node, _, dist in traverse_full(tree, order=-1, is_leaf_fn=is_leaf_fn,
                                       topological=topological):
        if dist > dist_farthest:
            node_farthest, dist_farthest = node, dist

    return node_farthest, dist_farthest


def farthest_nodes(tree, topological=False):
    """Return the farthest nodes and the diameter of the tree."""
    d = get_distance_fn(topological)

    def last(x):
        return x[-1]  # return the last element (used later for comparison)

    # Part 1: Find the farthest descendant for all nodes.

    fd = {}  # dict of {node: (farthest_descendant, dist_from_parent_to_it)}
    for node in traverse(tree, order=+1):  # traverse in postorder
        if node.is_leaf:
            fd[node] = (node, d(node))
        else:
            f_leaf, dist = max([fd[n] for n in node.children], key=last)
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
        leaf, dist = max([fd[n] for n in curr.children if n is not prev],
                         default=(curr, 0), key=last)
        if dist + d_curr_e1 > diameter:
            extreme2, diameter = leaf, dist + d_curr_e1

        d_curr_e1 += d(curr) if curr is not tree else 0
        prev, curr = curr, curr.up

    return extreme1, extreme2, diameter


def midpoint(tree, topological=False):
    """Return the node in the middle and its distance from the exact center."""
    d = get_distance_fn(topological)

    # Find the farthest node and diameter.
    node, _, diameter = farthest_nodes(tree, topological)

    # Go thru ancestor nodes until we cover more distance than the tree radius.
    dist = diameter / 2 - d(node)  # radius of the tree minus branch dist
    while dist > 0:
        node = node.up
        dist -= d(node)

    return node, dist + d(node)  # NOTE: `dist` is negative


def set_midpoint_outgroup(tree, topological=False):
    node, dist = midpoint(tree, topological)
    set_outgroup(node, dist=dist)


def mean_distance(tree, weight_fn=None, leaf=None, topological=False):
    """Return the weighted mean distance between leaves, or from given leaf.

    This is also called the "Mean Phylogenetic Distance" (MPD) for
    phylogenetic trees.

    To "select" certain leaves, weight_fn can be used for example like::

      weight_fn=lambda node: 1 if node.name in names else 0

    But it can be used generally as relative leaf importance for averaging.

    The algorithm is quite fast: for n leaves, it runs in O(n * log(n)).

    :param tree: Tree (starting node) for which to compute the mean.
    :param weight_fn: Function that returns the weight of each leaf.
        If None, all leaves will have weight 1.
    :param leaf: Leaf for which to compute the weighted mean distance to
        leaves. If None, a weighted mean for all leaves is made.
    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    """
    # Get default functions to weight leaves and compute distances.
    weight_fn = weight_fn or (lambda node: 1)  # weight of 1 by default
    d = get_distance_fn(topological)

    # Store info on descendant leaves, and total distance to them.
    nums = {}  # weighted number of descendant leaves
    sums = {}  # weighted sum of distances from node to descendant leaves
    for node in traverse(tree, order=+1):  # postorder (descendants first)
        if node.is_leaf:
            nums[node] = weight_fn(node)
            sums[node] = 0
        else:
            children = node.children
            nums[node] = sum(nums[x] for x in children)
            sums[node] = sum(d(x) * nums[x] + sums[x] for x in children)

    # Function to get the weighted number of paths, and total distance sum.
    def nums_sums(leaf):
        node = leaf  # current node
        d_leaf = 0  # distance from leaf to current node
        n = 0  # number of paths (distances)
        s = 0  # sum of distances
        while not node.is_root:  # will add values for all possible paths
            d_leaf += d(node)  # add distance from parent to current node
            sisters = node.get_sisters()  # or "siblings"
            n += sum(nums[x] for x in sisters)
            s += sum((d_leaf + d(x)) * nums[x] + sums[x] for x in sisters)
            node = node.up
        return n, s

    # Return the mean distance (from a single leaf, or averaged).
    if leaf is not None:  # from a single leaf
        n, s = nums_sums(leaf)  # number of distances, sum of distances
        return s / n if n > 0 else 0  # mean distance
    else:  # weighted mean over all leaves
        n_total = 0
        s_total = 0
        for leaf in tree.leaves():
            w = weight_fn(leaf)
            n, s = nums_sums(leaf)  # number of distances, sum of distances
            n_total += w * n
            s_total += w * s
        return s_total / n_total if n_total > 0 else 0  # mean of means


def distance_matrix(tree, selector=None, topological=False, squared=False):
    """Return a matrix of paired distances between all the selected leaves.

    :param tree: Tree (starting node) for which to compute the matrix.
    :param selector: Function that returns True for the selected leaves.
        If None, all leaves will be selected.
    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    :param squared: If True, the output matrix will be squared and symmetrical.
        Otherwise, only the upper triangle is returned (to save memory).
    """
    # Get default functions to select leaves and compute distances.
    selector = selector or (lambda node: True)  # select all by default
    d = get_distance_fn(topological)

    # Store info on the distance to each node's leaves.
    dists = {}  # {node: [dist0, ...]} (list of dists with leaves in order)
    for node in traverse(tree, order=+1):  # postorder (descendants first)
        if node.is_leaf:
            dists[node] = [0] if selector(node) else []
        else:
            ds = []  # will have dists to selected descendant leaves, in order
            for ch in node.children:
                d_ch = d(ch)
                ds += [d_ch + x for x in dists[ch]]
            dists[node] = ds

    # Function to get the distances from leaf to all leaves after it, in order.
    def dists_from(leaf):
        node = leaf  # current node
        d_leaf = 0  # distance from leaf to current node
        ds = []  # will have dists to all selected leaves after it, in order
        while not node.is_root:
            d_leaf += d(node)  # add distance from parent to current node
            found = False  # have we found node when traversing its siblings?
            for ch in node.up.children:
                if found:  # all leaves hanging on this node come after "leaf"
                    d_ch = d_leaf + d(ch)
                    ds += [d_ch + x for x in dists[ch]]  # so we add their dists
                elif ch is node:
                    found = True
            node = node.up
        return ds

    matrix = [dists_from(leaf) for leaf in tree.leaves() if selector(leaf)]

    if squared:  # convert matrix into an actual symmetric square matrix
        for i in range(len(matrix)):
            row = [matrix[j][i] for j in range(i)]  # the missing distances
            row.append(0)  # distance of node i to itself (= 0)
            row += matrix[i]  # the distances that we already had
            matrix[i] = row  # and this is our new row of the matrix

    return matrix


# The next two functions appear as defined in the Glossary of Terms in
# doi 10.1016/j.cub.2014.03.011:
#
# - PD (phylogenetic diversity)
#   - Sum of all lengths of all branches in a defined phylogenetic tree.
#
# - ED (evolutionary distinctness)
#   - A species-level measure representing the weighted sum of the
#     branch lengths along the path from the root of a tree to a given
#     tip (species). Identical to and sometimes referred to as the fair
#     proportion (FP) metric. Note that the ED of all species in a tree
#     sums to PD.

def phylogenetic_diversity(tree, topological=False):
    """Return the phylogenetic diversity of the tree."""
    d = get_distance_fn(topological)
    return sum(d(node) for node in traverse(tree) if not node.is_root)


def evolutionary_distinctness(tree, leaves, topological=False):
    """Return the evolutionary distinctness for the given leaves."""
    d = get_distance_fn(topological)

    nleaves = {}  # will have for each node the number of descendant leaves
    for node in traverse(tree, order=+1):
        nleaves[node] = (1 if node.is_leaf else
                         sum(nleaves[ch] for ch in node.children))

    eds = []  # list of evolutionary distinctness for the given leaves
    for leaf in leaves:
        node = leaf
        ed = 0  # evolutionary distinctness
        while not node.is_root:
            ed += d(node) / nleaves[node]
            node = node.up
        eds.append(ed)

    return eds


def get_distance_fn(topological, asserted=True):
    """Return a function that returns node distances (branch lengths).

    :param topological: If True, the distance of a node is just 1 (a step).
    :param asserted: If True, raises AssertionError on undefined distances.
    """
    if topological:
        return lambda node: 1 if not node.is_root else 0
    elif asserted:
        def asserted_dist(node):
            assert node.dist is not None, 'node without distance: %r' % node
            return node.dist
        return asserted_dist
    else:
        return lambda node: node.dist


# Traversing the tree.

def traverse(tree, order=-1, is_leaf_fn=None):
    """Traverse the tree and yield nodes in pre (< 0) or post (> 0) order."""
    visiting = [(tree, False)]  # nodes we are visiting, and if we saw them
    while visiting:
        node, seen = visiting.pop()

        is_leaf = is_leaf_fn(node) if is_leaf_fn else node.is_leaf

        if is_leaf or (order <= 0 and not seen) or (order >= 0 and seen):
            yield node

        if not seen and not is_leaf:
            visiting.append((node, True))  # add node back, but mark as seen
            visiting += [(n, False) for n in node.children[::-1]]


def traverse_full(tree, order=-1, is_leaf_fn=None,
                  topological=False, descend=None):
    """Traverse tree depth-first and yield (node, seen status, total distance).

    Similar to traverse(), but more fully featured (and complex).

    :param tree: Tree (starting node) to traverse.
    :param order: When to yield (-1 preorder, +1 postorder, 0 prepostorder).
    :param is_leaf_fn: Function that takes a node and returns True if it is
        considered a leaf. If None, node.is_leaf is used.
    :param topological: If True, the distance between nodes will be the
        number of nodes between them (instead of the sum of branch lenghts).
    :param descend: If not None, a list whose first element is always checked
        before going deeper in the traversal. To dynamically cut/avoid branches.
    """
    d = get_distance_fn(topological)
    descend = descend if descend is not None else [True]

    dist_total = 0  # distance from tree (our root)
    visiting = [(tree, False, 0)]  # nodes, if we saw them, and their distance
    while visiting:
        node, seen, ndist = visiting.pop()

        is_leaf = is_leaf_fn(node) if is_leaf_fn else node.is_leaf

        if not seen:
            dist_total += ndist  # we are going forwards in the tree

        if is_leaf or (order <= 0 and not seen) or (order >= 0 and seen):
            yield node, seen, dist_total

        if descend[0] and not seen and not is_leaf:
            ndist = d(node) if node is not tree else 0  # node dist
            visiting.append((node, True, ndist))  # add node back, as seen
            visiting += [(n, False, d(n)) for n in node.children[::-1]]
        else:
            descend[0] = True  # in case it was changed in the caller
            dist_total -= ndist  # we are going backwards in the tree


def traverse_bfs(tree, is_leaf_fn=None):
    """Yield nodes with a breadth-first search (level order traversal)."""
    visiting = deque([tree])
    while visiting:
        node = visiting.popleft()
        yield node
        if not is_leaf_fn or not is_leaf_fn(node):
            visiting += node.children


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
