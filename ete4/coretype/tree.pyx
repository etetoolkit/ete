import random
import copy
import itertools
from collections import deque, namedtuple
from hashlib import md5
from functools import cmp_to_key
import pickle
import logging
import math

from . import text_viz
from .. import utils
from ete4.parser import newick
from ..parser import ete_format

# the following imports are necessary to set fixed styles and faces
# try:
try:
    from ..treeview.main import NodeStyle
    from ..treeview.faces import Face
    TREEVIEW = True
except ImportError:
    TREEVIEW = False

from ..smartview import Face as smartFace
from ..smartview.renderer.nodestyle import NodeStyle as smNodeStyle
from ..smartview.renderer.face_positions import Faces, make_faces
from ..smartview.renderer.layouts.default_layouts import (
    LayoutLeafName, LayoutBranchLength, LayoutBranchSupport)


class TreeError(Exception):
    pass


cdef class Tree(object):
    """
    The Tree class is used to store a tree structure.

    A tree consists of a collection of Tree instances connected in a
    hierarchical way. Trees can be loaded from the New Hampshire
    Newick format (newick).
    """

    # TODO: Clean up all the memebers of Tree and leave only:
    #   up, props, children, size
    cdef public Tree up
    cdef public dict props
    cdef public list _children

    cdef public (double, double) size

    # All these members below should go away.
    cdef public object _img_style
    cdef public object _sm_style
    cdef public object _smfaces
    cdef public object _collapsed_faces
    cdef public int _initialized
    cdef public int _collapsed

    def __init__(self, data=None, children=None, parser=None):
        """
        :param data: A string or file object with the description of
            the tree as a newick, or a dict with the contents of a
            single node.
        :param children: List of nodes to add as children of this one.
        :param parser: A description of how to parse a newick to
            create a tree. It can be a single number specifying the
            format or a structure with a fine-grained description of
            how to interpret nodes (see ``newick.pyx``).

        Examples::

            t1 = Tree()  # empty tree
            t2 = Tree({'name': 'A'})
            t3 = Tree('(A:1,(B:1,(C:1,D:1):0.5):0.5);')
            t4 = Tree(open('/home/user/my-tree.nw'))
        """
        self.children = children or []

        self._img_style = None
        # Do not initialize _faces and _collapsed_faces
        # for performance reasons (pickling)
        self._initialized = 0 # Layout fns have not been run on node

        self.size = (0, 0)

        data = data.read() if hasattr(data, 'read') else data

        if data is None:
            self.props = {}
        elif type(data) == dict:
            self.props = data.copy()
        else:  # from newick or ete format
            assert not children, 'init from parsed content cannot have children'

            assert (type(parser) in [dict, int] or
                    parser in [None, 'newick', 'ete', 'auto']), 'bad parser'

            data = data.strip()

            if parser is None or parser == 'auto':
                guess_format = lambda x: 'newick'  # TODO
                parser = guess_format(data)

            if parser == 'newick':
                self.init_from_newick(data)
            elif type(parser) == dict:
                self.init_from_newick(data, parser)
            elif parser in newick.INT_PARSERS:
                self.init_from_newick(data, newick.INT_PARSERS[parser])
            elif parser == 'ete':
                self.init_from_ete(data)

    def init_from_newick(self, data, parser=None):
        tree = newick.loads(data, parser, self.__class__)
        self.children = tree.children
        self.props = tree.props

    def init_from_ete(self, data):
        t = ete_format.loads(data)
        self.name = t.name
        self.dist = t.dist
        self.support = t.support
        self.children = t.children

    @property
    def name(self):
        return str(self.props.get('name')) if 'name' in self.props else None

    @name.setter
    def name(self, value):
        self.props['name'] = str(value)

    @property
    def dist(self):
        return float(self.props['dist']) if 'dist' in self.props else None

    @dist.setter
    def dist(self, value):
        self.props['dist'] = float(value)

    @property
    def support(self):
        return float(self.props['support']) if 'support' in self.props else None

    @support.setter
    def support(self, value):
        self.props['support'] = float(value)

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        self._children = []
        self.add_children(value)

    @property
    def is_leaf(self):
        """Return True if the current node is a leaf."""
        return not self.children

    @property
    def is_root(self):
        """Return True if the current node has no parent."""
        return not self.up

    @property
    def root(self):
        """Return the absolute root node of the current tree structure."""
        node = self
        while node.up:
            node = node.up
        return node

    @property
    def id(self):
        """Return node_id (list of relative hops from root to node)."""
        reversed_id = []
        node = self
        while node.up:
            reversed_id.append(node.up.children.index(node))
            node = node.up
        return reversed_id[::-1]  # will look like  [0, 0, 1, 0]

    @property
    def level(self):
        """Return the number of nodes between this node and the root."""
        n = 0
        node = self.up
        while node:
            n += 1
            node = node.up
        return n

    def get_prop(self, prop, default=None):
        """Return the node's property prop (an attribute or in self.props)."""
        attr = getattr(self, prop, None)
        return attr if attr is not None else self.props.get(prop, default)

    # TODO: Move all the next functions out of the Tree class.
    def _get_style(self):
        if self._img_style is None:
            self._img_style = NodeStyle()
        return self._img_style

    def _set_style(self, value):
        self.set_style(value)

    def _get_sm_style(self):
        if self._sm_style is None:
            self._sm_style = smNodeStyle()
        return self._sm_style

    def _set_sm_style(self, value):
        self.set_style(value)

    def _get_initialized(self):
        return self._initialized == 1
    def _set_initialized(self, value):
        if value:
            self._initialized = 1
        else:
            self._initialized = 0

    def _get_collapsed(self):
        return self._collapsed == 1
    def _set_collapsed(self, value):
        if value:
            self._collapsed = 1
        else:
            self._collapsed = 0

    #: Node styling properties
    img_style = property(fget=_get_style, fset=_set_style)
    sm_style = property(fget=_get_sm_style, fset=_set_sm_style)

    #: Whether layout functions have been run on node
    is_initialized = property(fget=_get_initialized, fset=_set_initialized)
    is_collapsed = property(fget=_get_collapsed, fset=_set_collapsed)

    @property
    def faces(self):
        if self._smfaces is None:
            self._smfaces = make_faces()
        return self._smfaces

    @faces.setter
    def faces(self, value):
        assert isinstance(value, Faces), 'Not a Faces instance: %r' % value
        self._smfaces = value

    @property
    def collapsed_faces(self):
        if self._collapsed_faces is None:
            self._collapsed_faces = make_faces()
        return self._collapsed_faces

    @collapsed_faces.setter
    def collapsed_faces(self, value):
        assert isinstance(value, Faces), 'Not a Faces instance: %r' % value
        self._collapsed_faces = value

    def __bool__(self):
        # If this is not defined, bool(t) will call len(t).
        return True

    def __repr__(self):
        return 'Tree %r (%s)' % (self.name, hex(self.__hash__()))

    def __getitem__(self, node_id):
        """Return the node that matches the given node_id."""
        try:
            if type(node_id) == str:    # node_id can be the name of a node
                return next(n for n in self.traverse() if n.name == node_id)
            elif type(node_id) == int:  # or the index of a child
                return self.children[node_id]
            else:                       # or a list/tuple of a descendant
                node = self
                for i in node_id:
                    node = node.children[i]
                return node
        except StopIteration:
            raise TreeError(f'No node found with name: {node_id}')
        except (IndexError, TypeError) as e:
            raise TreeError(f'Invalid node_id: {node_id}')

    def __add__(self, value):
        """Sum trees. t1 + t2 returns a new tree with children=[t1, t2]."""
        # Should a make the sum with two copies of the original trees?
        if type(value) == self.__class__:
            new_root = self.__class__()
            new_root.add_child(self)
            new_root.add_child(value)
            return new_root
        else:
            raise TreeError("Invalid node type")

    def __str__(self):
        """Return a string with an ascii drawing of the tree."""
        return self.to_str(show_internal=False, compact=True, props=['name'])

    def to_str(self, show_internal=True, compact=False, props=None,
               px=None, py=None, px0=0, waterfall=False):
        return text_viz.to_str(self, show_internal, compact, props,
                               px, py, px0, waterfall)

    def __contains__(self, item):
        """Return True if the tree contains the given item.

        :param item: A node instance or its associated name.
        """
        if isinstance(item, self.__class__):
            return item in self.descendants()
        elif type(item) == str:
            return any(n.name == item for n in self.traverse())
        else:
            raise TreeError("Invalid item type")

    def __len__(self):
        """Return the number of leaves."""
        return sum(1 for _ in self.leaves())

    def __iter__(self):
        """Yield all the terminal nodes (leaves)."""
        yield from self.leaves()

    def add_prop(self, name, value):
        """Add or update node's property to the given value."""
        self.props[name] = value

    def add_props(self, **props):
        """Add or update several properties."""
        for name, value in props.items():
            self.add_prop(name, value)

    def del_prop(self, prop_name):
        """Permanently delete a node's property."""
        self.props.pop(prop_name, None)

    # DEPRECATED #
    def add_feature(self, pr_name, pr_value):
        """Add or update a node's feature."""
        logging.warning('add_feature is DEPRECATED use add_prop instead')
        self.add_prop(pr_name, pr_value)

    def add_features(self, **features):
        """Add or update several features."""
        logging.warning('add_features is DEPRECATED use add_props instead')
        self.add_props(**features)

    def del_feature(self, pr_name):
        """Permanently deletes a node's feature."""
        logging.warning('del_feature is DEPRECATED use del_prop instead')
        self.del_prop(pr_name)
    # DEPRECATED #

    # Topology management
    def add_child(self, child=None, name=None, dist=None, support=None):
        """Add a new child to this node and return it.

        If child node is not suplied, a new node instance will be created.

        :param child: Node to be added as a child.
        :param name: Name that will be given to the child.
        :param dist: Distance from the node to the child.
        :param support: Support value of child partition.
        """
        if child and type(child) != self.__class__:
            raise TreeError(f'Incorrect child type: {type(child)}')

        if child is None:
            child = self.__class__()  # can be Tree(), PhyloTree(), etc.

        if name is not None:
            child.name = name
        if dist is not None:
            child.dist = dist
        if support is not None:
            child.support = support

        child.up = self
        self.children.append(child)

        return child

    def add_children(self, children):
        for child in children:
            self.add_child(child)
        return children

    def pop_child(self, child_idx=-1):
        try:
            child = self.children.pop(child_idx)  # parent removes child

            if child.up == self:  # (it may point to another already!)
                child.up = None  # child removes parent

            return child
        except ValueError as e:
            raise TreeError(f'Cannot pop child: not found ({e})')

    def remove_child(self, child):
        """Remove child from this node and return it.

        After calling this function, parent and child nodes still exit,
        but are no longer connected.
        """
        try:
            self.children.remove(child)  # parent removes child

            if child.up == self:  # (it may point to another already!)
                child.up = None  # child removes parent

            return child
        except ValueError as e:
            raise TreeError(f'Cannot remove child: not found ({e})')

    def remove_children(self):
        """Remove all children from this node and return a list with them."""
        children = list(self.children)  # we need to make a copy of the list!
        return [self.remove_child(node) for node in children]

    def add_sister(self, sister=None, name=None, dist=None):
        """Add a sister to this node and return it.

        If sister node is not supplied, a new Tree instance will be created.
        """
        if self.up is None:
            raise TreeError("A parent node is required to add a sister")

        return self.up.add_child(child=sister, name=name, dist=dist)

    def remove_sister(self, sister=None):
        """Remove a sister node.

        It has the same effect as self.up.remove_child(sister).

        If a sister node is not supplied, the first sister will be deleted
        and returned.

        :param sister: A node instance to be removed as a sister.

        :return: The node removed.
        """
        sisters = self.get_sisters()
        if not sisters:
            raise TreeError("Cannot remove sister because there are no sisters")

        return self.up.remove_child(sister or sisters[0])

    def delete(self, prevent_nondicotomic=True, preserve_branch_length=False):
        """Delete node from the tree structure, keeping its children.

        The children from the deleted node are transferred to the old parent.

        :param prevent_nondicotomic: If True (default), it will also
            delete parent nodes until no single-child nodes occur.
        :param preserve_branch_length: If True, branch lengths
            of the deleted nodes are transferred (summed up) to the
            parent's branch, thus keeping original distances among
            nodes.

        Example::

            t = Tree('(C,(B,A)H)root;')
            print(t.to_str(props=['name']))
            #       ╭╴C
            # ╴root╶┤
            #       │   ╭╴B
            #       ╰╴H╶┤
            #           ╰╴A

            t['H'].delete()  # delete the "H" node
            print(t.to_str(props=['name']))
            #       ╭╴C
            #       │
            # ╴root╶┼╴B
            #       │
            #       ╰╴A
        """
        parent = self.up
        if not parent:
            return  # nothing to do, we cannot actually delete the root

        if preserve_branch_length and 'dist' in self.props:
            if len(self.children) == 1 and 'dist' in self.children[0].props:
                self.children[0].dist += self.dist
            elif len(parent.children) == 1 and 'dist' in parent.props:
                parent.dist += self.dist

        for ch in self.children:
            parent.add_child(ch)

        parent.remove_child(self)

        if prevent_nondicotomic and len(parent.children) == 1:
            parent.delete(prevent_nondicotomic=prevent_nondicotomic,
                          preserve_branch_length=preserve_branch_length)

    def detach(self):
        """Detach this node (and descendants) from its parent and return itself.

        The detached node conserves all its structure of descendants,
        and can be attached to another node with the :func:`add_child`
        function. This mechanism can be seen as a "cut and paste".
        """
        if self.up:
            self.up.children.remove(self)
            self.up = None

        return self

    def prune(self, nodes, preserve_branch_length=False):
        """Prune the topology conserving only the given nodes.

        It will only retain the minimum number of nodes that conserve the
        topological relationships among the requested nodes. The root node is
        always conserved.

        :param nodes: List of node names or objects that should be kept.
        :param bool preserve_branch_length: If True, branch lengths
            of the deleted nodes are transferred (summed up) to its
            parent's branch, thus keeping original distances among nodes.

        Examples::

          t = Tree('(((((A,B)C)D,E)F,G)H,(I,J)K)root;')
          print(t.to_str(props=['name']))
          #                       ╭╴A
          #               ╭╴D╶╌╴C╶┤
          #           ╭╴F╶┤       ╰╴B
          #           │   │
          #       ╭╴H╶┤   ╰╴E
          #       │   │
          # ╴root╶┤   ╰╴G
          #       │
          #       │   ╭╴I
          #       ╰╴K╶┤
          #           ╰╴J

          t1 = t.copy()
          t1.prune(['A', 'B'])
          print(t1.to_str(props=['name']))
          #       ╭╴A
          # ╴root╶┤
          #       ╰╴B

          t2 = t.copy()
          t2.prune(['A', 'B', 'C'])
          print(t2.to_str(props=['name']))
          #           ╭╴A
          # ╴root╶╌╴C╶┤
          #           ╰╴B

          t3 = t.copy()
          t3.prune(['A', 'B', 'I'])
          print(t3.to_str(props=['name']))
          #           ╭╴A
          #       ╭╴C╶┤
          # ╴root╶┤   ╰╴B
          #       │
          #       ╰╴I

          t4 = t.copy()
          t4.prune(['A', 'B', 'F', 'H'])
          print(t4.to_str(props=['name']))
          #               ╭╴A
          # ╴root╶╌╴H╶╌╴F╶┤
          #               ╰╴B
        """
        def cmp_nodes(x, y):
            # if several nodes are in the same path of two kept nodes,
            # only one should be maintained. This prioritize internal
            # nodes that are already in the to_keep list and then
            # deeper nodes (closer to the leaves).
            if n2depth[x] > n2depth[y]:
                return -1
            elif n2depth[x] < n2depth[y]:
                return 1
            else:
                return 0

        to_keep = set(self._translate_nodes(nodes))
        start = self.common_ancestor(to_keep)
        node2path = {n: n.lineage() for n in to_keep}
        to_keep.add(self)

        # Calculate which kept nodes are visiting the same nodes in
        # their path to the common ancestor.
        n2count = {}
        n2depth = {}
        for seed, path in node2path.items():
            for visited_node in path:
                if visited_node not in n2depth:
                    depth = visited_node.get_distance(visited_node, start,
                                                      topological=True)
                    n2depth[visited_node] = depth
                if visited_node is not seed:
                    n2count.setdefault(visited_node, set()).add(seed)

        # if several internal nodes are in the path of exactly the same kept
        # nodes, only one (the deepest) should be maintain.
        visitors2nodes = {}
        for node, visitors in n2count.items():
            # keep nodes connection at least two other nodes
            if len(visitors)>1:
                visitor_key = frozenset(visitors)
                visitors2nodes.setdefault(visitor_key, set()).add(node)

        for visitors, nodes in visitors2nodes.items():
            if not (to_keep & nodes):
                sorted_nodes = sorted(nodes, key=cmp_to_key(cmp_nodes))
                to_keep.add(sorted_nodes[0])

        for n in self.descendants('postorder'):
            if n not in to_keep:
                if preserve_branch_length:
                    if len(n.children) == 1:
                        n.children[0].dist += n.dist
                    elif len(n.children) > 1 and n.up and n.up.dist:
                        n.up.dist += n.dist

                n.delete(prevent_nondicotomic=False)

    def swap_children(self):
        """Swap current children order (reversing it)."""
        self.children.reverse()

    # #####################
    # Tree traversing
    # #####################

    def get_children(self):
        """Return an independent list of the node's children."""
        return self.children.copy()

    def get_sisters(self):
        """Return an independent list of sister nodes."""
        if self.up is not None:
            return [ch for ch in self.up.children if ch != self]
        else:
            return []

    def leaves(self, is_leaf_fn=None):
        """Yield the terminal nodes (leaves) under this node."""
        is_leaf = is_leaf_fn or (lambda n: n.is_leaf)
        for node in self.traverse("preorder", is_leaf):
            if is_leaf(node):
                yield node

    def leaf_names(self, is_leaf_fn=None):
        """Yield the leaf names under this node."""
        for n in self.leaves(is_leaf_fn):
            yield n.name

    def descendants(self, strategy="levelorder", is_leaf_fn=None):
        """Yield all descendant nodes."""
        for n in self.traverse(strategy, is_leaf_fn):
            if n is not self:
                yield n

    def traverse(self, strategy="levelorder", is_leaf_fn=None):
        """Traverse the tree structure under this node and yield the nodes.

        :param str strategy: Set the way in which tree
            will be traversed. Possible values are: "preorder" (first
            parent and then children) "postorder" (first children and
            the parent) and "levelorder" (nodes are visited in order
            from root to leaves).
        :param function is_leaf_fn: Function used to interrogate nodes about if
            they are terminal or internal. The function should
            receive a node instance as first argument and return True
            or False. Use this argument to traverse a tree by
            dynamically collapsing internal nodes matching `is_leaf_fn`.
        """
        if strategy == "preorder":
            return self._iter_descendants_preorder(is_leaf_fn)
        elif strategy == "levelorder":
            return self._iter_descendants_levelorder(is_leaf_fn)
        elif strategy == "postorder":
            return self._iter_descendants_postorder(is_leaf_fn)
        else:
            raise TreeError("Unknown strategy: %s" % strategy)

    def iter_prepostorder(self, is_leaf_fn=None):
        """Yield all nodes in a tree in both pre and post order.

        Each iteration returns a postorder flag (True if node is being visited
        in postorder) and a node instance.
        """
        is_leaf_fn = is_leaf_fn or (lambda n: n.is_leaf)
        to_visit = [self]

        while to_visit:
            node = to_visit.pop(-1)
            if type(node) != list:
                yield (False, node)
                if not is_leaf_fn(node):  # add children
                    to_visit.extend(reversed(node.children + [[1, node]]))
            else:  # postorder actions
                node = node[1]
                yield (True, node)

    def _iter_descendants_postorder(self, is_leaf_fn=None):
        """Yield all nodes in a tree in postorder."""
        is_leaf = is_leaf_fn or (lambda n: n.is_leaf)
        to_visit = [self]

        while to_visit:
            node = to_visit.pop(-1)
            if type(node) != list:  # preorder actions
                if not is_leaf(node):  # add children
                    to_visit.extend(reversed(node.children + [[1, node]]))
                else:
                    yield node
            else:  # postorder actions
                node = node[1]
                yield node

    def _iter_descendants_levelorder(self, is_leaf_fn=None):
        """Yield all descendant nodes in levelorder."""
        tovisit = deque([self])
        while len(tovisit) > 0:
            node = tovisit.popleft()
            yield node
            if not is_leaf_fn or not is_leaf_fn(node):
                tovisit.extend(node.children)

    def _iter_descendants_preorder(self, is_leaf_fn=None):
        """Yield all descendant nodes in preorder."""
        to_visit = deque()
        node = self
        while node is not None:
            yield node
            if not is_leaf_fn or not is_leaf_fn(node):
                to_visit.extendleft(reversed(node.children))
            try:
                node = to_visit.popleft()
            except:
                node = None

    def ancestors(self, root=None):
        """Yield all ancestor nodes of this node (up to the root if given)."""
        node = self

        if node == root:
            return  # node is not an ancestor of itself

        while node.up:
            node = node.up
            yield node
            if node == root:
                break  # by now, we already yielded root too

        if root is not None and node != root:
            raise TreeError('node is no descendant from given root: %r' % root)

    def lineage(self, root=None):
        """Yield all nodes in the lineage of this node (up to root if given)."""
        # Same as ancestors() but also yielding itself first.
        yield self
        yield from self.ancestors(root)

    def _translate_nodes(self, nodes):
        """Return a list of nodes that correspond to the given names or nodes."""
        # ['A', self['B'], 'C'] -> [self['A'], self['B'], self['C']]
        assert type(nodes) in [list, tuple, set, frozenset]

        names = {n for n in nodes if type(n) == str}

        if not names:
            return list(nodes)  # avoid traversing tree if no names to translate

        name2node = {}
        for node in self.traverse():
            if node.name in names:
                assert node.name not in name2node, f'Ambiguous node name: {node.name}'
                name2node[node.name] = node

        return [name2node[n] if type(n) == str else n for n in nodes]

    def describe(self):
        """Return a string with information on this node and its connections."""
        if len(self.root.children) == 2:
            rooting = 'Yes'
        elif len(self.root.children) > 2:
            rooting = 'No'
        else:
            rooting = 'No children'

        max_node, max_dist = self.get_farthest_leaf()
        cached_content = self.get_cached_content()

        return '\n'.join([
            'Number of leaf nodes: %d' % len(cached_content[self]),
            'Total number of nodes: %d' % len(cached_content),
            'Rooted: %s' % rooting,
            'Most distant node: %s' % (max_node.name or ''),
            'Max. distance: %g' % max_dist])

    def write(self, outfile=None, props=(), parser=None,
              format_root_node=False, is_leaf_fn=None):
        """Return or write to file the newick representation.

        :param str outfile: Name of the output file. If present, it will write
            the newick to that file instad of returning it as a string.
        :param list props: Properties to write for all nodes using the Extended
            Newick Format. If None, write all available properties.
        :param parser: Parser used to encode the tree in newick format.
        :param bool format_root_node: If True, write content of the root node
            too. For compatibility reasons, this is False by default.

        Example::

            t.write(props=['species', 'sci_name'])
        """
        parser = newick.INT_PARSERS[parser] if type(parser) == int else parser

        if not outfile:
            return newick.dumps(self, props, parser, format_root_node, is_leaf_fn)
        else:
            with open(outfile, 'w') as fp:
                newick.dump(self, fp, props, parser, format_root_node, is_leaf_fn)

    def common_ancestor(self, nodes):
        """Return the last node common to the lineages of the given nodes.

        All the nodes should have self as an ancestor, or an error is raised.
        """
        if not nodes:
            return None

        nodes = self._translate_nodes(nodes)

        curr = nodes[0]  # current node being the last common ancestor

        for node in nodes:  # NOTE: not  nodes[1:]  in case self is no root of node[0]
            lin_node = set(node.lineage(self))
            curr = next((n for n in curr.lineage(self) if n in lin_node), None)

        if curr is not None:
            return curr  # which is now the last common ancestor of all nodes
        else:
            raise TreeError(f'No common ancestor for nodes: {nodes}')

    def search_nodes(self, **conditions):
        """Yield nodes matching the given conditions.

        Example::

            for node in tree.search_nodes(dist=0.0, name='human'):
                print(node.prop['support'])
        """
        for n in self.traverse():
            if all(n.props.get(key) == value or getattr(n, key, None) == value
                   for key, value in conditions.items()):
                yield n

    def search_descendants(self, **conditions):
        """Yield descendant nodes matching the given conditions."""
        for n in self.search_nodes(**conditions):
            if n is not self:
                yield n

    def search_ancestors(self, **conditions):
        """Yield ancestor nodes matching the given conditions."""
        for n in self.ancestors():
            if all(n.props.get(key) == value or getattr(n, key, None) == value
                   for key, value in conditions.items()):
                yield n

    def search_leaves_by_name(self, name):
        """Yield leaf nodes matching the given name."""
        return self.search_nodes(name=name, children=[])

    # ###########################
    # Distance related functions
    # ###########################

    def get_distance(self, node1, node2, topological=False):
        """Return the distance between the given nodes.

        :param node1: A node within the same tree structure.
        :param node2: Another node within the same tree structure.
        :param topological: If True, distance will refer to the number of
            nodes between target and target2.
        """
        d = (lambda node: 1) if topological else (lambda node: node.dist or 0.0)

        node1, node2 = self._translate_nodes([node1, node2])

        root = self.root.common_ancestor([node1, node2])  # common root
        assert root is not None, 'nodes do not belong to the same tree'

        return (sum(d(n) for n in node1.lineage(root)) - d(root) +
                sum(d(n) for n in node2.lineage(root)) - d(root))

    def get_farthest_node(self, topological=False):
        """Returns the farthest descendant or ancestor node, and its distance.

        :param topological: If True, the distance between nodes will be the
            number of nodes between them (instead of the sum of branch lenghts).
        """
        # Init farthest node to current farthest leaf
        farthest_node, farthest_dist = self.get_farthest_leaf(topological=topological)

        dist = lambda node: node.dist if 'dist' in node.props else (0 if node.is_root else 1)

        prev = self
        cdist = 0.0 if topological else dist(prev)
        current = prev.up
        while current is not None:
            for ch in current.children:
                if ch != prev:
                    if not ch.is_leaf:
                        fnode, fdist = ch.get_farthest_leaf(topological=topological)
                    else:
                        fnode = ch
                        fdist = 0
                    if topological:
                        fdist += 1.0
                    else:
                        fdist += dist(ch)
                    if cdist+fdist > farthest_dist:
                        farthest_dist = cdist + fdist
                        farthest_node = fnode
            prev = current
            if topological:
                cdist += 1
            else:
                cdist  += dist(prev)
            current = prev.up
        return farthest_node, farthest_dist

    def _get_farthest_and_closest_leaves(self, topological=False, is_leaf_fn=None):
        # if called from a leaf node, no necessary to compute
        if (is_leaf_fn and is_leaf_fn(self)) or self.is_leaf:
            return self, 0.0, self, 0.0

        dist = lambda node: node.dist if 'dist' in node.props else 1

        min_dist = None
        min_node = None
        max_dist = None
        max_node = None
        d = 0.0
        for post, n in self.iter_prepostorder(is_leaf_fn=is_leaf_fn):
            if n is self:
                continue
            if post:
                d -= dist(n) if not topological else 1.0
            else:
                if (is_leaf_fn and is_leaf_fn(n)) or n.is_leaf:
                    total_d = d + dist(n) if not topological else d
                    if min_dist is None or total_d < min_dist:
                        min_dist = total_d
                        min_node = n
                    if max_dist is None or total_d > max_dist:
                        max_dist = total_d
                        max_node = n
                else:
                    d += dist(n) if not topological else 1.0
        return min_node, min_dist, max_node, max_dist


    def get_farthest_leaf(self, topological=False, is_leaf_fn=None):
        """Return the node's farthest descendant (a leaf), and its distance.

        :param topological: If True, the distance between nodes will be the
            number of nodes between them (instead of the sum of branch lenghts).
        """
        min_node, min_dist, max_node, max_dist = \
            self._get_farthest_and_closest_leaves(topological=topological,
                                                  is_leaf_fn=is_leaf_fn)
        return max_node, max_dist

    def get_closest_leaf(self, topological=False, is_leaf_fn=None):
        """Return the node's closest descendant leaf, and its distance.

        :param topological: If True, the distance between nodes will be the
            number of nodes between them (instead of the sum of branch lenghts).
        """
        min_node, min_dist, max_node, max_dist = \
            self._get_farthest_and_closest_leaves(topological=topological,
                                                  is_leaf_fn=is_leaf_fn)
        return min_node, min_dist

    def get_midpoint_outgroup(self, topological=False):
        """Return the node dividing into two distance-balanced partitions.

        :param topological: If True, the distance between nodes will be the
            number of nodes between them (instead of the sum of branch lenghts).
        """
        # Start at the farthest leaf from the root.
        current, _ = self.root.get_farthest_leaf(topological=topological)
        _, diameter = current.get_farthest_node(topological=topological)

        dist = 0
        while current.up:
            dist += 1 if topological else current.dist

            if dist > diameter / 2:
                return current

            current = current.up

        return current  # the midpoint was the root (we went back to it)

    def populate(self, size, names_library=None, random_branches=False,
                 dist_range=(0, 1), support_range=(0, 1)):
        """Populate current node with branches generating a random topology.

        All the nodes added will either be leaves or have two branches.

        :param size: Number of leaves to add. The necessary
            intermediate nodes will be created too.
        :param names_library: Collection (list or set) used to name leaves.
            If None, leaves will be named using short letter sequences.
        :param random_branches: If True, branch distances and support
            values will be randomized.
        :param dist_range: Range (tuple with min and max) of distances
            used to generate branch distances if random_branches is True.
        :param support_range: Range (tuple with min and max) of distances
            used to generate branch supports if random_branches is True.
        """
        assert names_library is None or len(names_library) >= size, \
            f'names_library too small ({len(names_library)}) for size {size}'

        NewNode = self.__class__

        if len(self.children) > 1:
            connector = NewNode()
            for ch in self.get_children():
                ch.detach()
                connector.add_child(ch)
            root = NewNode()
            self.add_child(connector)
            self.add_child(root)
        else:
            root = self

        #root.dist = root.dist or 0
        #root.support = root.support or 1

        next_deq = deque([root])  # will contain the current leaves
        for i in range(size - 1):
            p = next_deq.popleft() if random.randint(0, 1) else next_deq.pop()

            c1 = p.add_child()
            c2 = p.add_child()

            next_deq.extend([c1, c2])

            if random_branches:
                c1.dist = random.uniform(*dist_range)
                c2.dist = random.uniform(*dist_range)
                c1.support = random.uniform(*support_range)
                c2.support = random.uniform(*support_range)
            else:
                c1.dist = 1.0
                c2.dist = 1.0
                c1.support = 1.0
                c2.support = 1.0

        # Give names to leaves.
        if names_library is not None:
            for node, name in zip(next_deq, names_library):
                node.name = name
        else:
            chars = 'abcdefghijklmnopqrstuvwxyz'

            for i, node in enumerate(next_deq):
                # Create a short name corresponding to the index i.
                # 0: 'a', 1: 'b', ..., 25: 'z', 26: 'aa', 27: 'ab', ...
                name = ''
                while i >= 0:
                    name = chars[i % len(chars)] + name
                    i = i // len(chars) - 1

                node.name = name

    def set_outgroup(self, outgroup, branch_properties=None):
        """Set the given outgroup node at the root and return it.

        :param outgroup: The node too use as future root.
        :param branch_properties: List of branch properties (other than "support").
        """
        from ..smartview.renderer.gardening import root_at
        return root_at(outgroup, branch_properties)

    def set_outgroup_old(self, outgroup):
        """
        Sets a descendant node as the outgroup of a tree.  This function
        can be used to root a tree or even an internal node.

        :argument outgroup: a node instance within the same tree
          structure that will be used as a basal node.

        """
        outgroup = self._translate_nodes([outgroup])[0]

        if self == outgroup:
            raise TreeError("Cannot set the tree root as outgroup")

        parent_outgroup = outgroup.up

        # Detects (sub)tree root
        n = outgroup
        while n.up is not self:
            n = n.up

        # If outgroup is a child from root, but with more than one
        # sister nodes, creates a new node to group them
        self.children.remove(n)
        if len(self.children) != 1:
            down_branch_connector = self.__class__()
            down_branch_connector.dist = 0.0
            if n.support is not None:
                down_branch_connector.support = n.support
            for ch in self.get_children():
                down_branch_connector.children.append(ch)
                ch.up = down_branch_connector
                self.children.remove(ch)
        else:
            down_branch_connector = self.children[0]

        # Connects down branch to myself or to outgroup
        quien_va_ser_padre = parent_outgroup
        if quien_va_ser_padre is not self:
            # Parent-child swapping
            quien_va_ser_hijo = quien_va_ser_padre.up
            quien_fue_padre = None
            buffered_dist = quien_va_ser_padre.dist
            buffered_support = quien_va_ser_padre.support

            while quien_va_ser_hijo is not self:
                quien_va_ser_padre.children.append(quien_va_ser_hijo)
                quien_va_ser_hijo.children.remove(quien_va_ser_padre)

                buffered_dist2 = quien_va_ser_hijo.dist
                buffered_support2 = quien_va_ser_hijo.support
                if buffered_dist is not None:
                    quien_va_ser_hijo.dist = buffered_dist
                if buffered_support is not None:
                    quien_va_ser_hijo.support = buffered_support
                buffered_dist = buffered_dist2
                if buffered_support2 is not None:
                    buffered_support = buffered_support2

                quien_va_ser_padre.up = quien_fue_padre
                quien_fue_padre = quien_va_ser_padre

                quien_va_ser_padre = quien_va_ser_hijo
                quien_va_ser_hijo = quien_va_ser_padre.up

            quien_va_ser_padre.children.append(down_branch_connector)
            down_branch_connector.up = quien_va_ser_padre
            quien_va_ser_padre.up = quien_fue_padre

            if (down_branch_connector.dist is not None and
                buffered_dist is not None):
                down_branch_connector.dist += buffered_dist
            outgroup2 = parent_outgroup
            parent_outgroup.children.remove(outgroup)
            outgroup2.dist = 0

        else:
            outgroup2 = down_branch_connector

        outgroup.up = self
        outgroup2.up = self
        # outgroup is always the first children. Some function my
        # trust on this fact, so do no change this.
        self.children = [outgroup,outgroup2]
        if outgroup2.dist is not None and outgroup.dist is not None:
            middist = (outgroup2.dist + outgroup.dist)/2
            outgroup.dist = middist
            outgroup2.dist = middist

        if outgroup.support is not None:
            outgroup2.support = outgroup.support

    def unroot(self, mode='legacy'):
        """Unroot current node.

        This function is expected to be used on the absolute tree root
        node, but it can be also be applied to any other internal
        node. It will convert a split into a multifurcation.

        :param mode: The value can be "legacy" or "keep". If value is
            "keep", it keeps the distance between the leaves by adding
            the distance associated to the deleted edge to the
            remaining edge. Otherwise that distance is just dropped.
        """
        if not (mode == 'legacy' or mode == 'keep'):
            raise ValueError("The value of the mode parameter must be 'legacy' or 'keep'")
        if len(self.children)==2:
            if not self.children[0].is_leaf:
                if mode == "keep":
                    self.children[1].dist+=self.children[0].dist
                self.children[0].delete()
            elif not self.children[1].is_leaf:
                if mode == "keep":
                    self.children[0].dist+=self.children[1].dist
                self.children[1].delete()
            else:
                raise TreeError("Cannot unroot a tree with only two leaves")

    def show(self, layout=None, tree_style=None, name="ETE"):
        """Start an interactive session to visualize the current node."""
        from ..treeview import drawer
        drawer.show_tree(self, layout=layout,
                         tree_style=tree_style, win_name=name)

    def render(self, file_name, layout=None, w=None, h=None,
               tree_style=None, units='px', dpi=90):
        """Render the tree as an image.

        :param file_name: Name of the output image. Valid extensions
            are "svg", "pdf", and "png".
        :param layout: Layout function or layout function name to use.
        :param tree_style: A `TreeStyle` instance containing the image
            properties.
        :param units: Units for height (h) or width (w). They can be
            "px" for pixels, "mm" for millimeters, "in" for inches.
        :param h: Height of the image in :attr:`units`.
        :param w: Width of the image in :attr:`units`.
        :param dpi: Resolution in dots per inch.
        """
        from ..treeview import drawer

        if file_name.startswith('%%return'):  # generate img_map (for webplugin)
            return drawer.get_img(self, w=w, h=h,
                                  layout=layout, tree_style=tree_style,
                                  units=units, dpi=dpi, return_format=file_name)
        elif file_name.startswith('%%inline'):  # also return data (for jupyter)
            return drawer.render_tree(self, file_name, w=w, h=h,
                                      layout=layout, tree_style=tree_style,
                                      units=units, dpi=dpi)
        else:  # just generate the file
            drawer.render_tree(self, file_name, w=w, h=h,
                               layout=layout, tree_style=tree_style,
                               units=units, dpi=dpi)
            print('Wrote file:', file_name)

    def explore(self, name=None, layouts=None, show_leaf_name=True,
                show_branch_length=True, show_branch_support=True,
                include_props=('name', 'dist'), exclude_props=None,
                host='localhost', port=5000, quiet=True,
                compress=False, keep_server=False, open_browser=True):
        """Launch an interactive smartview session to visualize the tree.

        :param str name: Name used to store and refer to the tree.
        :param list layouts: Layouts that will be available from the
            front end. It is important to name functions (__name__), as they
            will be adressed by that name in the explorer.
        :param list include_props: Properties to show in the nodes popup.
            If None, show all.
        :param list exclude_props: Properties to exclude from the nodes popup.
        """
        from ..smartview.gui.server import run_smartview

        default_layouts = []

        if not show_leaf_name:
            layout = LayoutLeafName()
            layout.active = False
            default_layouts.append(layout)

        if not show_branch_length:
            layout = LayoutBranchLength()
            layout.active = False
            default_layouts.append(layout)

        if not show_branch_support:
            layout = LayoutBranchSupport()
            layout.active = False
            default_layouts.append(layout)

        run_smartview(tree=self, name=name,
                      layouts=list(default_layouts + (layouts or [])),
                      include_props=include_props, exclude_props=exclude_props,
                      host=host, port=port, quiet=quiet,
                      compress=compress, keep_server=keep_server,
                      open_browser=open_browser)

    def copy(self, method="cpickle"):
        """Return a copy of the current node.

        :param method: Protocol used to copy the node structure.

        The following values are accepted for the method:

        - "newick": Tree topology, node names, branch lengths and
           branch support values will be copied by as represented in
           the newick string (copy by newick string serialisation).
        - "newick-extended": Tree topology and all node properties
           will be copied based on the extended newick format
           representation. Only node properties will be copied, thus
           excluding other node attributes. As this method is also
           based on newick serialisation, properties will be converted
           into text strings when making the copy.
        - "cpickle": The whole node structure and its content is
           cloned based on cPickle object serialisation (slower, but
           recommended for full tree copying)
        - "deepcopy": The whole node structure and its content is
           copied based on the standard "copy" Python functionality
           (this is the slowest method but it allows to copy complex
           objects even if attributes point to lambda functions, etc.)
        """
        method = method.lower()
        if method=="newick":
            new_node = self.__class__(self.write(format_root_node=True))
        elif method=="newick-extended":
            new_node = self.__class__(self.write(props=None))
        elif method == "deepcopy":
            parent = self.up
            self.up = None
            new_node = copy.deepcopy(self)
            self.up = parent
        elif method == "cpickle":
            parent = self.up
            self.up = None
            new_node = pickle.loads(pickle.dumps(self, 2))
            self.up = parent
        else:
            raise TreeError("Invalid copy method")

        return new_node

    def ladderize(self, direction=0):
        """Sort branches according to the size of each partition.

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
        if not self.is_leaf:
            n2s = {}
            for n in self.get_children():
                s = n.ladderize(direction=direction)
                n2s[n] = s

            self.children.sort(key=lambda x: n2s[x])
            if direction == 1:
                self.children.reverse()
            size = sum(n2s.values())
        else:
            size = 1

        return size

    def sort_descendants(self, prop='name'):
        """Sort branches by node names.

        After the tree is sorted, if duplicated names are present,
        extra criteria should be added to sort nodes.
        """
        node2content = self.get_cached_content(prop, container_type=list)

        for n in self.traverse():
            if not n.is_leaf:
                n.children.sort(key=lambda x: str(sorted(node2content[x])))

    def get_cached_content(self, prop=None, container_type=set,
                           leaves_only=True):
        """Return dict that assigns to each node a set of its leaves.

        The dictionary serves as a cache for operations that require
        many traversals of the nodes under this tree.

        Instead of assigning a set, it can assign a list (with
        ``container_type``). And instead of the leaves themselves, it
        can be any of their properties (like their names, with ``prop``).

        :param prop: Node property that should be cached (i.e.
            name, distance, etc.). If None, it caches the node itself.
        :param container_type: Type of container for the leaves (set, list).
        :param leaves_only: If False, for each node it stores all its
            descendant nodes, not only its leaves.
        """

        def get_content():  # return the node itself, or its requested prop
            return self if prop is None else self.get_prop(prop)

        # Leaves, or nodes, or just their requested property, for each node.
        leaves = {self: container_type(
            [get_content()] if self.is_leaf or not leaves_only else [])}

        for node in self.children:
            node_leaves = node.get_cached_content(prop=prop,
                                                  container_type=container_type,
                                                  leaves_only=leaves_only)
            # Update the leaves dictionary.
            leaves.update(node_leaves)

            # Update the leaves (or nodes, or their prop) assigned to self.
            if container_type == set:
                leaves[self].update(node_leaves[node])
            elif container_type == list:
                leaves[self].extend(node_leaves[node])

        return leaves

    def robinson_foulds(self, t2, prop_t1='name', prop_t2='name',
                        unrooted_trees=False, expand_polytomies=False,
                        polytomy_size_limit=5, skip_large_polytomies=False,
                        correct_by_polytomy_size=False, min_support_t1=0.0,
                        min_support_t2=0.0):
        """Return the Robinson-Foulds distance to the tree, and related info.

        The returned tuple contains the Robinson-Foulds symmetric
        distance (rf), but also more information::

          (rf, rf_max, common,
           edges_t1, edges_t2, discarded_edges_t1, discarded_edges_t2)

        :param t2: Target tree (tree to compare to the reference tree).
        :param prop_t1: Property to use in the reference tree as the
            node name when comparing trees.
        :param prop_t2: Property to use in the target tree as the node
            name when comparing trees.
        :param unrooted_trees: If True, consider trees as unrooted.
        :param expand_polytomies: If True, all polytomies in the
           reference and target tree will be expanded into all
           possible binary trees. Robinson-Foulds distance will be
           calculated between all tree combinations and the minimum
           value will be returned. See also :func:`Tree.expand_polytomy`.
        """
        # Give aliases for clarity.
        origin_t = self  # reference tree
        target_t = t2

        # Check that the arguments are consistent.
        if not unrooted_trees and (len(origin_t.children) > 2 or
                                   len(target_t.children) > 2):
            raise TreeError('Unrooted tree found! You may want to set unrooted_trees=True.')

        if expand_polytomies and correct_by_polytomy_size:
            raise TreeError('expand_polytomies and correct_by_polytomy_size are mutually exclusive.')

        if expand_polytomies and unrooted_trees:
            raise TreeError('expand_polytomies and unrooted_trees are mutually exclusive.')

        # Some helper functions to access properties.
        def has_prop(node, prop):
            return hasattr(node, prop) or prop in node.props

        common = (  # common leaf values in the two trees
            {n.get_prop(prop_t1) for n in origin_t if has_prop(n, prop_t1)} &
            {n.get_prop(prop_t2) for n in target_t if has_prop(n, prop_t2)})

        # Check for duplicated items (is it necessary? can we optimize? what's the impact in performance?')
        size1 = sum(1 for n in origin_t if n.get_prop(prop_t1) in common)
        size2 = sum(1 for n in target_t if n.get_prop(prop_t2) in common)

        if size1 > len(common):
            raise TreeError('Duplicated items found in reference tree.')
        if size2 > len(common):
            raise TreeError('Duplicated items found in target tree.')

        if expand_polytomies:
            origin_trees = [Tree(nw) for nw in
                            origin_t.expand_polytomies(map_prop=prop_t1,
                                                       polytomy_size_limit=polytomy_size_limit,
                                                       skip_large_polytomies=skip_large_polytomies)]
            target_trees = [Tree(nw) for nw in
                            target_t.expand_polytomies(map_prop=prop_t2,
                                                       polytomy_size_limit=polytomy_size_limit,
                                                       skip_large_polytomies=skip_large_polytomies)]
            prop_t1, prop_t2 = 'name', 'name'
        else:
            origin_trees = [origin_t]
            target_trees = [target_t]

        polytomy_correction = 0
        if correct_by_polytomy_size:
            corr1 = sum(len(n.children) - 2 for n in origin_t.traverse() if len(n.children) > 2)
            corr2 = sum(len(n.children) - 2 for n in target_t.traverse() if len(n.children) > 2)

            if corr1 > 0 and corr2 > 0:
                raise TreeError('Both trees contain polytomies! Try expand_polytomies=True instead.')

            polytomy_correction = max(corr1, corr2)

        def from_common(nodes, prop):  # helper function
            """Yield values (if existing in both trees) for property prop."""
            for node in nodes:
                if has_prop(node, prop):
                    value = node.get_prop(prop)
                    if value in common:
                        yield value

        min_comparison = None
        for t1 in origin_trees:
            t1_leaves = t1.get_cached_content()
            t1_leaves_all = t1_leaves[t1]

            if unrooted_trees:
                edges1 = {  # set that looks like {((a, b, ...), (x, y, ...)), ...}
                    tuple(sorted([
                        tuple(sorted(from_common(leaves, prop_t1))),
                        tuple(sorted(from_common(t1_leaves_all - leaves, prop_t1)))]))
                    for leaves in t1_leaves.values()}
                edges1.discard(((), ()))  # probably unnecessary
            else:
                edges1 = {tuple(sorted(from_common(leaves, prop_t1)))
                          for leaves in t1_leaves.values()}
                edges1.discard(())

            if min_support_t1:
                support_t1 = {tuple(sorted(from_common(leaves, prop_t1) for n in leaves)): branch.support or 0
                              for branch, leaves in t1_leaves.items()}

            for t2 in target_trees:
                t2_leaves = t2.get_cached_content()
                t2_leaves_all = t2_leaves[t2]

                if unrooted_trees:
                    edges2 = {
                        tuple(sorted([
                            tuple(sorted(from_common(leaves, prop_t2))),
                            tuple(sorted(from_common(t2_leaves_all - leaves, prop_t2)))]))
                        for leaves in t2_leaves.values()}
                    edges2.discard(((), ()))
                else:
                    edges2 = {tuple(sorted(from_common(leaves, prop_t2)))
                              for leaves in t2_leaves.values()}
                    edges2.discard(())

                if min_support_t2:
                    support_t2 = {tuple(sorted(from_common(leaves, prop_t2) for n in leaves)): branch.support or 0
                                  for branch, leaves in t2_leaves.items()}

                # if a support value is passed as a constraint, discard lowly supported branches from the analysis
                discard_t1, discard_t2 = set(), set()
                if min_support_t1 and unrooted_trees:
                    discard_t1 = {p for p in edges1 if support_t1.get(p[0], support_t1.get(p[1], math.inf)) < min_support_t1}
                elif min_support_t1:
                    discard_t1 = {p for p in edges1 if support_t1[p] is not None and support_t1[p] < min_support_t1}

                if min_support_t2 and unrooted_trees:
                    discard_t2 = {p for p in edges2 if support_t2.get(p[0], support_t2.get(p[1], math.inf)) < min_support_t2}
                elif min_support_t2:
                    discard_t2 = {p for p in edges2 if support_t2[p] is not None and support_t2[p] < min_support_t2}

                # the two root edges are never counted here, as they are always
                # present in both trees because of the common property filters
                rf = len(((edges1 ^ edges2) - discard_t2) - discard_t1) - polytomy_correction

                if unrooted_trees:
                    max_parts = (
                        sum(1 for p in edges1 - discard_t1 if len(p[0]) > 1 and len(p[1]) > 1) +
                        sum(1 for p in edges2 - discard_t2 if len(p[0]) > 1 and len(p[1]) > 1))
                else:
                    # Otherwise we need to count the actual number of valid
                    # partitions in each tree -2 is to avoid counting the root
                    # partition of the two trees (only needed in rooted trees)
                    max_parts = (
                        sum(1 for p in edges1 - discard_t1 if len(p) > 1) +
                        sum(1 for p in edges2 - discard_t2 if len(p) > 1)) - 2

                if not min_comparison or (min_comparison[0] is not None and min_comparison[0] > rf):
                    min_comparison = [rf, max_parts, common, edges1, edges2, discard_t1, discard_t2]

        return min_comparison

    def compare(self, ref_tree, use_collateral=False, min_support_source=0.0, min_support_ref=0.0,
                has_duplications=False, expand_polytomies=False, unrooted=False,
                max_treeko_splits_to_be_artifact=1000, ref_tree_attr='name', source_tree_attr='name'):

        """compare this tree with another using robinson foulds symmetric difference
        and number of shared edges. Trees of different sizes and with duplicated
        items allowed.

        returns: a Python dictionary with results

        """
        source_tree = self

        def _safe_div(a, b):
            if a != 0:
                return a / float(b)
            else: return 0.0

        def _compare(src_tree, ref_tree):
            # calculate partitions and rf distances
            rf, maxrf, common, ref_p, src_p, ref_disc, src_disc  = ref_tree.robinson_foulds(src_tree,
                                                                                            expand_polytomies=expand_polytomies,
                                                                                            unrooted_trees=unrooted,
                                                                                            prop_t1=ref_tree_attr,
                                                                                            prop_t2=source_tree_attr,
                                                                                            min_support_t2=min_support_source,
                                                                                            min_support_t1=min_support_ref)

            # if trees share leaves, count their distances
            if len(common) > 0 and src_p and ref_p:
                if unrooted:
                    valid_ref_edges = set([p for p in (ref_p - ref_disc) if len(p[0])>1 and len(p[1])>0])
                    valid_src_edges = set([p for p in (src_p - src_disc) if len(p[0])>1 and len(p[1])>0])
                    common_edges = valid_ref_edges & valid_src_edges
                else:

                    valid_ref_edges = set([p for p in (ref_p - ref_disc) if len(p)>1])
                    valid_src_edges = set([p for p in (src_p - src_disc) if len(p)>1])
                    common_edges = valid_ref_edges & valid_src_edges

            else:
                valid_ref_edges = set()
                valid_src_edges = set()
                common_edges = set()

                # # % of ref edges found in tree
                # ref_found.append(float(len(p2 & p1)) / reftree_edges)

                # # valid edges in target, discard also leaves
                # p2bis = set([p for p in (p2-d2) if len(p[0])>1 and len(p[1])>1])
                # if p2bis:
                #     incompatible_target_branches = float(len((p2-d2) - p1))
                #     target_found.append(1 - (incompatible_target_branches / (len(p2-d2))))

            return rf, maxrf, len(common), valid_ref_edges, valid_src_edges, common_edges


        total_valid_ref_edges = len([n for n in ref_tree.traverse()
                                     if n.children and n.support is not None and n.support > min_support_ref])
        result = {}
        if has_duplications:
            orig_target_size = len(source_tree)
            ntrees, ndups, sp_trees = source_tree.get_speciation_trees(
                autodetect_duplications=True, newick_only=True,
                prop=source_tree_attr, map_properties=[source_tree_attr, "support"])

            if ntrees < max_treeko_splits_to_be_artifact:
                all_rf = []
                ref_found = []
                src_found = []
                tree_sizes = []
                all_max_rf = []
                common_names = 0

                for subtree_nw in sp_trees:

                    #if seedid and not use_collateral and (seedid not in subtree_nw):
                    #    continue
                    subtree = source_tree.__class__(subtree_nw,
                            sp_naming_function = source_tree.props.get('_speciesFunction'))
                    if not subtree.children:
                        continue

                    # only necessary if rf function is going to filter by support
                    # value.  It slows downs the analysis, obviously, as it has to
                    # find the support for each node in the treeko tree from the
                    # original one.
                    if min_support_source > 0:
                        subtree_content = subtree.get_cached_content('name')
                        for n in subtree.traverse():
                            if n.children:
                                n.support = source_tree.common_ancestor(subtree_content[n]).support
                                # TODO: This function is almost surely broken. It relies on
                                # an old behavior of get_common_ancestor().

                    total_rf, max_rf, ncommon, valid_ref_edges, valid_src_edges, common_edges = _compare(subtree, ref_tree)

                    all_rf.append(total_rf)
                    all_max_rf.append(max_rf)
                    tree_sizes.append(ncommon)

                    if unrooted:
                        ref_found_in_src = len(common_edges)/float(len(valid_ref_edges)) if valid_ref_edges else None
                        src_found_in_ref = len(common_edges)/float(len(valid_src_edges)) if valid_src_edges else None
                    else:
                        # in rooted trees, we want to discount the root edge
                        # from the percentage of congruence. Otherwise we will never see a 0%
                        # congruence for totally different trees
                        ref_found_in_src = (len(common_edges)-1)/float(len(valid_ref_edges)-1) if len(valid_ref_edges)>1 else None
                        src_found_in_ref = (len(common_edges)-1)/float(len(valid_src_edges)-1) if len(valid_src_edges)>1 else None

                    if ref_found_in_src is not None:
                        ref_found.append(ref_found_in_src)

                    if src_found_in_ref is not None:
                        src_found.append(src_found_in_ref)

                if all_rf:
                    # Treeko speciation distance
                    alld = [_safe_div(all_rf[i], float(all_max_rf[i])) for i in range(len(all_rf))]
                    a = sum([alld[i] * tree_sizes[i] for i in range(len(all_rf))])
                    b = float(sum(tree_sizes))
                    treeko_d = a/b if a else 0.0
                    result["treeko_dist"] = treeko_d

                    result["rf"] = utils.mean(all_rf)
                    result["max_rf"] = max(all_max_rf)
                    result["effective_tree_size"] = utils.mean(tree_sizes)
                    result["norm_rf"] = utils.mean([_safe_div(all_rf[i], float(all_max_rf[i])) for i in range(len(all_rf))])

                    result["ref_edges_in_source"] = utils.mean(ref_found)
                    result["source_edges_in_ref"] = utils.mean(src_found)

                    result["source_subtrees"] = len(all_rf)
                    result["common_edges"] = set()
                    result["source_edges"] = set()
                    result["ref_edges"] = set()
        else:
            total_rf, max_rf, ncommon, valid_ref_edges, valid_src_edges, common_edges = _compare(source_tree, ref_tree)

            result["rf"] = float(total_rf) if max_rf else "NA"
            result["max_rf"] = float(max_rf)
            if unrooted:
                result["ref_edges_in_source"] = len(common_edges)/float(len(valid_ref_edges)) if valid_ref_edges else "NA"
                result["source_edges_in_ref"] = len(common_edges)/float(len(valid_src_edges)) if valid_src_edges else "NA"
            else:
                # in rooted trees, we want to discount the root edge from the
                # percentage of congruence. Otherwise we will never see a 0%
                # congruence for totally different trees
                result["ref_edges_in_source"] = (len(common_edges)-1)/float(len(valid_ref_edges)-1) if len(valid_ref_edges)>1 else "NA"
                result["source_edges_in_ref"] = (len(common_edges)-1)/float(len(valid_src_edges)-1) if len(valid_src_edges)>1 else "NA"

            result["effective_tree_size"] = ncommon
            result["norm_rf"] = total_rf/float(max_rf) if max_rf else "NA"
            result["treeko_dist"] = "NA"
            result["source_subtrees"] = 1
            result["common_edges"] = common_edges
            result["source_edges"] = valid_src_edges
            result["ref_edges"] = valid_ref_edges
        return result

    def _diff(self, t2, output='topology', prop_t1='name', prop_t2='name', color=True):
        """Return the difference between two tree topologies.

        :param [raw|table|topology|diffs|diffs_tab] output: Output type.
        """
        from ..tools import ete_diff

        difftable = ete_diff.treediff(self, t2, prop1=prop_t1, prop2=prop_t2)

        # TODO: Fix the show_difftable*() functions and return get_difftable*() here.
        if output == 'topology':
            ete_diff.show_difftable_topo(difftable, prop_t1, prop_t2, usecolor=color)
        elif output == 'diffs':
            ete_diff.show_difftable(difftable)
        elif output == 'diffs_tab':
            ete_diff.show_difftable_tab(difftable)
        elif output == 'table':
            rf, rf_max, _, _, _, _, _ = self.robinson_foulds(t2, prop_t1=prop_t1, prop_t2=prop_t2)[:2]
            ete_diff.show_difftable_summary(difftable, rf, rf_max)
        elif output == 'raw':
            return difftable
        else:
            raise TreeError(f'Unknown output for diff: {output}')

    def edges(self, cached_content=None):
        """Yield a pair of sets of leafs for every partition of the tree.

        For every node, there are leaves that lay on one side of that
        node, and leaves that lay on the other. This generator yields
        all those pairs of sets.

        :param cached_content: Dictionary that to each node associates the
            leaves that descend from it. If passed, it won't be recomputed.
        """
        if not cached_content:
            cached_content = self.get_cached_content()  # d[node] = {leaf, ...}

        all_leaves = cached_content[self]

        for leaves_descendant in cached_content.values():
            yield (leaves_descendant, all_leaves - leaves_descendant)

    def standardize(self, delete_orphan=True, preserve_branch_length=True):
        """Resolve multifurcations and remove single-child nodes.

        This function changes the current tree structure to produce a
        standardized topology: nodes with only one child are removed
        and multifurcations are automatically resolved.
        """
        self.resolve_polytomy()

        for n in self.descendants():
            if len(n.children) == 1:
                n.delete(prevent_nondicotomic=True,
                         preserve_branch_length=preserve_branch_length)

    def get_topology_id(self, prop='name'):
        """Return a unique ID representing the topology of the tree.

        Two trees with the same topology will produce the same id.
        This is useful to detect the number of unique topologies over
        a bunch of trees, without requiring full distance methods.

        The id is, by default, calculated based on the terminal node's
        names. Any other node property could be used instead.

        If trees are unrooted, make sure that the root node is not
        binary or use the tree.unroot() function before generating the
        topology id.
        """
        edge_keys = []
        for s1, s2 in self.edges():
            k1 = sorted(e.props.get(prop, getattr(e, prop)) for e in s1)
            k2 = sorted(e.props.get(prop, getattr(e, prop)) for e in s2)

            edge_keys.append(sorted([k1, k2]))

        return md5(str(sorted(edge_keys)).encode('utf-8')).hexdigest()

    def to_ultrametric(self, topological=False):
        """Convert tree to ultrametric (all leaves equally distant from root)."""
        from ..smartview.renderer.gardening import update_sizes_all

        self.dist = self.dist or 0  # covers common case of not having dist set

        update_sizes_all(self)  # so node.size[0] are distances to leaves

        dist_full = self.size[0]  # original distance from root to furthest leaf

        if (topological or dist_full <= 0 or
            any(node.dist is None for node in self.traverse())):
            # Ignore original distances and just use the tree topology.
            for node in self.traverse():
                node.dist = 1 if node.up else 0
            update_sizes_all(self)
            dist_full = dist_full if dist_full > 0 else self.size[0]

        for node in self.traverse():
            if node.dist > 0:
                d = sum(n.dist for n in node.ancestors())
                node.dist *= (dist_full - d) / node.size[0]

    def is_monophyletic(self, nodes):
        """Return True if the nodes form a monophyletic group."""
        nodes = set(nodes)  # in case it is not a set already
        return all(n in nodes for n in self.common_ancestor(nodes).leaves())

    def check_monophyly(self, values, prop='name', unrooted=False):
        """Return tuple (is_monophyletic, clade_type, leaves_extra).

        :param values: List of values of the selected nodes.
        :param prop: Node property being used to check monophyly (i.e.
            'species' for species trees, 'name' for gene family trees,
            or any custom feature present in the tree).
        """
        values = set(values)  # in case it is not a set (so we check faster)

        nodes = set(n for n in self.leaves()
                        if n.props.get(prop, getattr(n, prop)) in values)

        if not unrooted:
            leaves_from_ancestor = set(n for n in self.common_ancestor(nodes).leaves())

            leaves_extra = leaves_from_ancestor - nodes
        else:
            smallest = None
            for side1, side2 in self.edges():
                if nodes.issubset(side1) and (not smallest or len(side1) < len(smallest)):
                    smallest = side1
                elif nodes.issubset(side2) and (not smallest or len(side2) < len(smallest)):
                    smallest = side2

                if smallest and len(smallest) == len(nodes):
                    break

            leaves_extra = smallest - nodes

        if not leaves_extra:  # nodes account for all leaves from common ancestor
            return True, 'monophyletic', leaves_extra
        elif self.is_monophyletic(leaves_extra):  # we leave out a monophyly
            return False, 'paraphyletic', leaves_extra
        else:  # a funny mixture
            return False, 'polyphyletic', leaves_extra

    def get_monophyletic(self, values, prop='name'):
        """Yield nodes matching the provided monophyly criteria.

        For a node to be considered a match, all ``prop`` values within
        the node, and exclusively them, should be grouped.

        :param values: List of values of the selected nodes.
        :param prop: Property being used to check monophyly (for example
            'species' for species trees, 'name' for gene family trees).
        """
        values = set(values)  # in case it is not a set

        n2values = self.get_cached_content(prop)

        is_monophyletic = lambda node: n2values[node] == values

        yield from self.leaves(is_leaf_fn=is_monophyletic)

    def expand_polytomies(self, map_prop="name", polytomy_size_limit=5,
                          skip_large_polytomies=False):
        """Return all combinations of solutions of the multifurcated nodes.

        If the tree has one or more polytomies, this functions returns
        the list of all trees (in newick format) resulting from the
        combination of all possible solutions of the multifurcated
        nodes.

        .. warning::
           Please note that the number of of possible binary trees grows
           exponentially with the number and size of polytomies. Using this
           function with large multifurcations is not feasible:

           polytomy size: 3 number of binary trees: 3
           polytomy size: 4 number of binary trees: 15
           polytomy size: 5 number of binary trees: 105
           polytomy size: 6 number of binary trees: 945
           polytomy size: 7 number of binary trees: 10395
           polytomy size: 8 number of binary trees: 135135
           polytomy size: 9 number of binary trees: 2027025

        See https://ajmonline.org/2010/darwin.php
        """

        class TipTuple(tuple):
            pass

        def add_leaf(tree, label):
          yield (label, tree)
          if not isinstance(tree, TipTuple) and isinstance(tree, tuple):
            for left in add_leaf(tree[0], label):
              yield (left, tree[1])
            for right in add_leaf(tree[1], label):
              yield (tree[0], right)

        def enum_unordered(labels):
          if len(labels) == 1:
            yield labels[0]
          else:
            for tree in enum_unordered(labels[1:]):
              for new_tree in add_leaf(tree, labels[0]):
                yield new_tree

        n2subtrees = {}
        for n in self.traverse("postorder"):
            if n.is_leaf:
                subtrees = [n.props.get(map_prop)]
            else:
                subtrees = []
                if len(n.children) > polytomy_size_limit:
                    if skip_large_polytomies:
                        for childtrees in itertools.product(*[n2subtrees[ch] for ch in n.children]):
                            subtrees.append(TipTuple(childtrees))
                    else:
                        raise TreeError("Found polytomy larger than current limit: %s" %n)
                else:
                    for childtrees in itertools.product(*[n2subtrees[ch] for ch in n.children]):
                        subtrees.extend([TipTuple(subtree) for subtree in enum_unordered(childtrees)])

            n2subtrees[n] = subtrees
        return ["%s;"%str(nw) for nw in n2subtrees[self]] # tuples are in newick format ^_^

    def resolve_polytomy(self, recursive=True, defaults=None):
        """Resolve all polytomies under the current node, randomly.

        A polytomy is a node that has more than 2 children. This
        function resolves them by creating an arbitrary dicotomic
        structure among the affected nodes. It randomly modifies the
        current tree topology and should only be used for
        compatibility reasons (like to later use programs that reject
        multifurcated nodes).

        :param recursive: If True, resolve all polytomies under this
             node too. Otherwise, only the current node will be
             checked and fixed.
        :param defaults: Dictionary of properties to use for new nodes.
        """
        def resolve(node):
            if len(node.children) <= 2:
                return  # nothing to resolve here!

            children = node.remove_children()
            next_node = root = node
            for i in range(len(children) - 2):
                next_node = next_node.add_child()
                next_node.props.update(defaults or {})

            next_node = root
            for ch in children:
                next_node.add_child(ch)
                if ch != children[-2]:
                    next_node = next_node.children[0]

        resolve(self)

        if recursive:
            for n in self.descendants():
                resolve(n)

    def cophenetic_matrix(self):
        """Return a cophenetic distance matrix of the tree.

        The `cophenetic matrix
        <https://en.wikipedia.org/wiki/Cophenetic>`_ is a matrix
        representation of the distance between each node.

        If we have a tree like::

                 ╭╴A
             ╭╴y╶┤
             │   ╰╴B
          ╴z╶┤
             │   ╭╴C
             ╰╴x╶┤
                 │   ╭╴D
                 ╰╴w╶┤
                     ╰╴E

        where w, x, y, z are internal nodes, then::

          d(A,B) = d(y,A) + d(y,B)

        and::

          d(A,E) = d(z,A) + d(z,E)
                 = (d(z,y) + d(y,A)) + (d(z,x) + d(x,w) + d(w,E))

        To compute it, we use an idea from
        https://gist.github.com/jhcepas/279f9009f46bf675e3a890c19191158b

        First, for each node we find its path to the root. For example::

          A -> A, y, z
          E -> E, w, x, z

        and make these orderless sets. Then we XOR the two sets to
        only find the elements that are in one or other sets but not
        both. In this case A, E, y, x, w.

        The distance between the two nodes is the sum of the distances
        from each of those nodes to the parent

        One more optimization: since the distances are symmetric, and
        distance to itself is zero we user itertools.combinations
        rather than itertools.permutations. This cuts our computes
        from theta(n^2) 1/2n^2 - n (= O(n^2), which is still not
        great, but in reality speeds things up for large trees).

        For this tree, we will return the two dimensional array::

                    A                B                C                D                E
          A         0         d(A-y) + d(B-y)  d(A-z) + d(C-z)  d(A-z) + d(D-z)  d(A-z) + d(E-z)
          B  d(B-y) + d(A-y)         0         d(B-z) + d(C-z)  d(B-z) + d(D-z)  d(B-z) + d(E-z)
          C  d(C-z) + d(A-z)  d(C-z) + d(B-z)         0         d(C-x) + d(D-x)  d(C-x) + d(E-x)
          D  d(D-z) + d(A-z)  d(D-z) + d(B-z)  d(D-x) + d(C-x)         0         d(D-w) + d(E-w)
          E  d(E-z) + d(A-z)  d(E-z) + d(B-z)  d(E-x) + d(C-x)  d(E-w) + d(D-w)         0

        We will also return the one dimensional array with the leaves
        in the order in which they appear in the matrix (i.e. the
        column and/or row headers).
        """
        leaves = list(self.leaves())
        paths = {x: set() for x in leaves}

        # get the paths going up the tree
        # we get all the nodes up to the last one and store them in a set

        for n in leaves:
            if n.is_root:
                continue
            movingnode = n
            while not movingnode.is_root:
                paths[n].add(movingnode)
                movingnode = movingnode.up

        # now we want to get all pairs of nodes using itertools combinations. We need AB AC etc but don't need BA CA

        leaf_distances = {x.name: {} for x in leaves}

        for (leaf1, leaf2) in itertools.combinations(leaves, 2):
            # figure out the unique nodes in the path
            uniquenodes = paths[leaf1] ^ paths[leaf2]
            distance = sum(x.dist for x in uniquenodes)
            leaf_distances[leaf1.name][leaf2.name] = leaf_distances[leaf2.name][leaf1.name] = distance

        allleaves = sorted(leaf_distances.keys()) # the leaves in order that we will return

        output = [] # the two dimensional array that we will return

        for i, n in enumerate(allleaves):
            output.append([])
            for m in allleaves:
                if m == n:
                    output[i].append(0) # distance to ourself = 0
                else:
                    output[i].append(leaf_distances[n][m])
        return output, allleaves

    def add_face(self, face, column=0, position='branch-right',
                 collapsed_only=False):
        if TREEVIEW and isinstance(face, Face):
            self.add_face_treeview(face, column, position)
        elif isinstance(face, smartFace):
            self.add_face_smartview(face, column, position, collapsed_only)
        else:
            raise ValueError('Invalid face format for: %r' % face)

    def add_face_treeview(self, face, column, position='branch-right'):
        """Add a fixed face to the node.

        This type of faces will be always attached to nodes,
        independently of the layout function.

        :param face: Face to add.
        :param column: An integer number starting from 0
        :param position: Position to place the face in the node. Posible
            values are: "branch-right", "branch-top", "branch-bottom", "float",
            "float-behind", "aligned".
        """
        from ..treeview.main import _FaceAreas, FaceContainer, FACE_POSITIONS

        if "_faces" not in self.props:
            self.props["_faces"] = _FaceAreas()

        if position not in FACE_POSITIONS:
            raise ValueError("face position not in %s" %FACE_POSITIONS)

        if isinstance(face, Face):
            getattr(self.props["_faces"], position).add_face(face, column=column)
        else:
            raise ValueError("not a Face instance")

    def add_face_smartview(self, face, column, position='branch-right',
                           collapsed_only=False):
        """Add a fixed face to the node.

        This type of faces will be always attached to nodes, independently of
        the layout function.

        :param face: Face to add.
        :param column: Column number where the face will go. Starts at 0.
        :param position: Position to place the face in the node. Posible
            values are: "branch-right", "branch-top", "branch-bottom", "aligned".
        """
        # TODO: Is it true that "This type of faces will be always attached
        # to nodes, independently of the layout function"? And why?
        from ..smartview.renderer.face_positions import FACE_POSITIONS

        assert position in FACE_POSITIONS, 'Invalid position %r' % position

        if collapsed_only:
            getattr(self.collapsed_faces, position).add_face(face, column=column)
        else:
            getattr(self.faces, position).add_face(face, column=column)

    def set_style(self, node_style):
        """
        .. versionadded: 2.1

        Set 'node_style' as the fixed style for the current node.
        """
        if isinstance(node_style, NodeStyle):
            self._img_style = node_style
        elif isinstance(node_style, smNodeStyle):
            self._sm_style = node_style
        else:
            raise ValueError("Invalid NodeStyle format")

    @staticmethod
    def from_parent_child_table(parent_child_table):
        """Convert a parent-child table into an ETE Tree instance.

        :param parent_child_table: List of tuples containing
            parent-child relationships. For example: [('A', 'B', 0.1),
            ('A', 'C', 0.2), ('C', 'D', 1), ('C', 'E', 1.5)], where
            each tuple represents: [parent, child, child-parent-dist]

        Example::

          t = Tree.from_parent_child_table([('A', 'B', 0.1),
                                            ('A', 'C', 0.2),
                                            ('C', 'D', 1),
                                            ('C', 'E', 1.5)])
          print(t.to_str(props=['name', 'dist']))
          #      ╭╴B,0.1
          # ╴A,⊗╶┤
          #      │       ╭╴D,1.0
          #      ╰╴C,0.2╶┤
          #              ╰╴E,1.5
        """
        def get_node(nodename, dist=None):
            if nodename not in nodes_by_name:
                data = {'name': nodename}
                if dist is not None:
                    data['dist'] = dist
                nodes_by_name[nodename] = Tree(data)
            node = nodes_by_name[nodename]
            if dist is not None:
                node.dist = dist
            node.name = nodename
            return nodes_by_name[nodename]

        nodes_by_name = {}
        for columns in parent_child_table:
            if len(columns) == 3:
                parent_name, child_name, distance = columns
                dist = float(distance)
            else:
                parent_name, child_name = columns
                dist = None
            parent = get_node(parent_name)
            parent.add_child(get_node(child_name, dist=dist))

        root = parent.root
        return root

    @staticmethod
    def from_skbio(skbio_tree, map_attributes=None):
        """Convert a scikit-bio TreeNode object into ETE Tree object.

        :param skbio_tree: A scikit bio TreeNode instance
        :param map_attributes: List of attribute names in the
            scikit-bio tree that should be mapped into the ETE tree
            instance. (name, id and branch length are always mapped)

        Example::

          t = Tree.from_skibio(skbioTree, map_attributes=['value'])
        """
        from skbio import TreeNode as skbioTreeNode

        def get_ete_node(skbio_node):
            ete_node = all_nodes.get(skbio_node, Tree())
            if skbio_node.props.get('length') is not None:
                ete_node.dist = float(skbio_node.props.get('length'))
            ete_node.name = skbio_node.name
            ete_node.add_props(id=skbio_node.props.get('id'))
            if map_attributes:
                for a in map_attributes:
                    ete_node.add_prop(a, skbio_node.props.get(a))
            return ete_node

        all_nodes = {}
        if isinstance(skbio_tree, skbioTreeNode):
            for node in skbio_tree.preorder(include_self=True):
                all_nodes[node] = get_ete_node(node)
                ete_node = all_nodes[node]
                for ch in node.children:
                    ete_ch = get_ete_node(ch)
                    ete_node.add_child(ete_ch)
                    all_nodes[ch] = ete_ch
            return ete_ch.root

    def phonehome(self):
        from .. import _ph
        _ph.call()
