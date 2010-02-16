# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
import os
import random

__all__ = ["Tree", "TreeNode"]

from ete_dev.parser.newick import read_newick, write_newick

DEFAULT_COMPACT = False
DEFAULT_SHOWINTERNAL = False

class TreeError(Exception):
    """Exception class designed for tree."""
    def __init__(self, value=''):
        self.value = value
    def __str__(self):
        return repr(self.value)


class TreeNode(object):
    """ TreeNode (Tree) class is used to store a tree structure. A tree
    consists of a collection of TreeNode instances connected in a
    hierarchical way. Trees can be loaded from the New Hampshire Newick
    format (newick).

    CONSTRUCTOR ARGUMENTS:
    ======================

     * newick: Path to the file containing the tree or, alternatively,
       the text string containing the same information.

    RETURNS:
    ========
     The TreeNode object which represents the base (root) of the
    tree.

    EXAMPLES:
    =========
        t1 = Tree() # creates an empty tree
        t2 = Tree( '(A:1,(B:1,(C:1,D:1):0.5):0.5);' )
        t3 = Tree( '/home/user/myNewickFile.txt' )
    """

    def _get_dist(self):
        return self._dist
    def _set_dist(self, value):
        try:
            self._dist = float(value)
        except ValueError:
            raise

    def _get_support(self):
        return self._support
    def _set_support(self, value):
        try:
            self._support = float(value)
        except ValueError:
            raise

    def _get_up(self):
        return self._up
    def _set_up(self, value):
        if type(value) == type(self) or value is None:
            self._up = value
        else:
            raise ValueError, "up: wrong type"

    def _get_children(self):
        return self._children
    def _set_children(self, value):
        if type(value) == list and \
           len(set([type(n)==type(self) for n in value]))<2:
            self._children = value
        else:
            raise ValueError, "children:wrong type"

    dist = property(fget=_get_dist, fset=_set_dist)
    support = property(fget=_get_support, fset=_set_support)
    up = property(fget=_get_up, fset=_set_up)
    children = property(fget=_get_children, fset=_set_children)

    def __init__(self, newick=None, format=0):
        self._children = []
        self._up = None
        self._dist = 1.0
        self._support = 1.0

        self.features = set([])
        self.collapsed = False
        # Add basic features
        self.add_features(name="NoName")
        self.features.update(["dist", "support"])
        # Initialize tree
        if newick is not None:
            read_newick(newick, root_node = self, format=format)

    def __and__(self, value):
        """ This allows to execute tree&'A' to obtain the descendant node
        A"""
        value=str(value)
        try:
            first_match = self.iter_search_nodes(name=value).next()
            return first_match
        except StopIteration:
            raise ValueError, "Node not found"

    def __add__(self, value):
        """ This allows to sum two trees."""
        # Should a make the sum with two copies of the original trees?
        if type(value) == self.__class__:
            new_root = self.__class__()
            new_root.add_child(self)
            new_root.add_child(value)
            return new_root
        else:
            raise ValueError, "Invalid node type"

    def __str__(self):
        """ Print tree in newick format. """
        return self.get_ascii(compact=DEFAULT_COMPACT, \
                                show_internal=DEFAULT_SHOWINTERNAL)

    def __contains__(self, item):
        """ Check if item belongs to this node. The 'item' argument must
        be a node instance or its associated name."""
        if isinstance(item, self.__class__):
            return item in set(self.get_descendants())
        elif type(item)==str:
            return item in set([n.name for n in self.get_descendants()])

    def __len__(self):
        """Node len returns number of children."""
        return len(self.get_leaves())

    def __iter__(self):
        """ Iterator over leaf nodes"""
        return self.iter_leaves()

    def add_feature(self, pr_name, pr_value):
        """ Adds or updates a node's feature. """
        setattr(self, pr_name, pr_value)
        self.features.add(pr_name)

    def add_features(self, **features):
        """ Adds or updates a node's feature. """
        for fname, fvalue in features.iteritems():
            setattr(self, fname, fvalue)
            self.features.add(fname)

    def del_feature(self, pr_name):
        """ Deletes permanently a node's feature. """
        if hasattr(self, pr_name):
            delattr(self, pr_name)
            self.features.remove(pr_name)

    # Topology management
    def add_child(self, child=None, name=None, dist=None, support=None):
        """
        Adds a new child to this node. If child node is not suplied
        as an argument, a new node instance will be created.

        ARGUMENTS:
        ==========

         * 'child': the node instance to be added as a child.
         * 'name': the name that will be given to the child.
         * 'dist': the distance from the node to the child.
         * 'support': the support value of child partition.

        RETURNS:
        ========

          The child node instace

        """
        if child is None:
            child = self.__class__()

        # This prevents from circular connections, but it would take too
        # much time to check it every time a node is creted.
        #
        # if self in child:
        #  raise ValueError, "child is an ancestor of current node"

        if name is not None:
            try:
                child.add_feature("name", str(name))
            except ValueError:
                raise TreeError, "Node's name has to be a string"

        if dist is not None:
            try:
                child.add_feature("dist", float(dist))
            except ValueError:
                raise TreeError, "Node's dist has must be a float number"

        if support is not None:
            try:
                child.add_feature("support", float(support))
            except ValueError:
                raise TreeError, "Node's support must be a float number"

        self.children.append(child)
        child.up = self
        return child

    def remove_child(self, child):
        """ Removes a child from this node (parent and child
        nodes still exit but are no longer connected). """
        try:
            self.children.remove(child)
        except ValueError, e:
            raise TreeError, e
        else:
            child.up = None
            return child

    def add_sister(self, sister=None, name=None, dist=None):
        """
        Adds a sister to this node. If sister node is not supplied
        as an argument, a new TreeNode instance will be created and
        returned.
        """
        if self.up == None:
            raise TreeError, "A parent node is required to add a sister"
        else:
            return self.up.add_child(child=sister, name=name, dist=dist)

    def remove_sister(self, sister=None):
        """
        Removes a node's sister node. It has the same effect as
        node.up.remove_child(sister).

        If a sister node is not supplied, the first sister will be deleted
        and returned.

        ARGUMENTS:
        ==========
          'sister': A node instance

        RETURNS:
        ========
          The removed node

        """
        sisters = self.get_sisters()
        if len(sisters)>0:
            if sister==None:
                sister = sisters.pop(0)
            return self.up.remove_child(sister)

    def delete(self, prevent_nondicotomic=True):
        """
        Deletes node from the tree structure. Notice that this
        method makes 'disapear' the node from the tree structure. This
        means that children from the deleted node are transferred to the
        next available parent.

        EXAMPLE:
        ========
                / C
          root-|
               |        / B
                \--- H |
                        \ A

          > root.delete(H) will produce this structure:

                / C
               |
          root-|--B
               |
                \ A

        """
        parent = self.up
        if parent:
            for ch in self.children:
                parent.add_child(ch)
            parent.remove_child(self)

        # Avoids the parents with only one child
        if prevent_nondicotomic and parent and\
              len(parent.children)<2:
            parent.delete(prevent_nondicotomic=False)


    def detach(self):
        """
        Detachs this node (and all its descendants) from its parent
        and returns the referent to itself.

        Detached node conserves all its structure of descendants, and can
        be attached to another node through the 'add_child' function. This
        mechanisim can be seen as a cut and paste."""

        if self.up:
            self.up.children.remove(self)
            self.up = None
        return self

    def prune(self, nodes):
        """
        Prunes the topology of this node in order to conserve only a
        selected list of leaf or internal nodes. The algorithm deletes
        nodes until getting a consistent topology with a subset of
        nodes. Topology relationships among kept nodes is maintained.

        ARGUMENTS:
        ==========
          * 'nodes' is a list of node names or node objects that must be kept.

        EXAMPLES:
        =========
          t = Tree("(((A:0.1, B:0.01):0.001, C:0.0001):1.0[&&NHX:name=I], (D:0.00001):0.000001[&&NHX:name=J]):2.0[&&NHX:name=root];")
          node_C = t.search_nodes(name="C")[0]
          t.prune(["A","D", node_C])
          print t
        """
       
        to_keep = set(_translate_nodes(self, *nodes))
        to_detach = []
        for node in self.traverse("postorder"):
            for c in node.children:
                if c in to_keep:
                    to_keep.add(node)
                    break
            if node not in to_keep:
                to_detach.append(node)
                for c in node.children:
                    to_detach.remove(c)
        for node in to_detach:
            node.detach()
        for node in to_keep:
            if len(node.children) == 1:
                node.delete()
        if len(self.children)==1:
            self.children[0].delete()
                
    def iter_leaves(self):
        """ Returns an iterator over the leaves under this node. """
        for n in self.traverse(strategy="preorder"):
            if n.is_leaf():
                yield n

    def iter_leaf_names(self):
        """ Returns an iterator over the leaf names under this node. """
        for n in self.iter_leaves():
            yield n.name

    def iter_descendants(self, strategy="preorder"):
        """ Returns an iterator over descendant nodes. """
        for n in self.traverse(strategy=strategy):
            if n != self:
                yield n
    def _iter_descendants_postorder(self):
        """ Iterator over all desdecendant nodes. """
        current = self
        end = self.up
        visited_childs = set([])
        while current is not end:
            childs = False
            for c in current.children:
                if c not in visited_childs:
                    childs = True
                    current = c
                    break
            if not childs:
                visited_childs.add(current)
                yield current
                current = current.up

    def _iter_descendants_preorder(self):
        """ Iterator over all desdecendant nodes. """
        tovisit = [self]
        while len(tovisit)>0:
            current = tovisit.pop(0)
            yield current
            tovisit.extend(current.children)

    def traverse(self, strategy="preorder"):
        """
         Returns an iterator that traverse the tree structure under this
         node.

         ARGUMENTS:
         ==========

           'strategy' defines the way in which tree will be
           traversed. Possible values are: "preorder" (first parent and
           then children) 'postorder' (first children and the parent).

        """
        if strategy=="preorder":
            return self._iter_descendants_preorder()
        elif strategy=="postorder":
            return self._iter_descendants_postorder()
    def swap_childs(self):
        """
        Swaps current childs order.
        """
        if len(self.children)>1:
            self.children.reverse()
    def get_children(self):
        """ Returns an independent list of node's children. """
        return [ch for ch in self.children]

    def get_sisters(self):
        """ Returns an indepent list of sister nodes. """
        if self.up!=None:
            return [ch for ch in self.up.children if ch!=self]
        else:
            return []

    def describe(self):
        """ Prints general information about this node and its
        connections."""
        if len(self.get_tree_root().children)==2:
            rooting = "Yes"
        elif len(self.get_tree_root().children)>2:
            rooting = "No"
        else:
            rooting = "Unknown"
        max_node, max_dis = get_farthest_leaf()
        print "Number of nodes:\t %d" % len(self.get_descendants())
        print "Number of leaves:\t %d" % len(self.get_leaves())
        print "Rooted:", rooting
        print "Max. lenght to root:"
        print "The Farthest descendant node is", max_node.name,\
            "with a branch distance of", max_dist

    def write(self, features=None, outfile=None, format=0):
        """ Returns the newick representation of this node
        topology. Several arguments control the way in which extra
        data is shown for every node:

        features: a list of feature names that want to be shown
        (when available) for every node. Extended newick format is
        used to represent data.

        'format' defines the newick standard used to encode the
        tree. See tutorial for details.

        Example:
             t.get_newick(["species","name"], format=1)
        """

        nw = write_newick(self, features = features, format=format)
        if outfile is not None:
            open(outfile, "w").write(nw)
            return nw
        else:
            return nw

    def get_tree_root(self):
        """ Returns the absolute root node of current tree structure. """
        root = self
        while root.up is not None:
            root = root.up
        return root

    def get_common_ancestor(self, *target_nodes):
        """ Returns the first common ancestor between this node and a given
        list of 'target_nodes'.

        EXAMPLES:
        =========
         t = tree.Tree("(((A:0.1, B:0.01):0.001, C:0.0001):1.0[&&NHX:name=common], (D:0.00001):0.000001):2.0[&&NHX:name=root];")
         A = t.get_descendants_by_name("A")[0]
         C = t.get_descendants_by_name("C")[0]
         common =  A.get_common_ancestor(C)
         print common.name

        """

        # Convert node names into node instances
        target_nodes = _translate_nodes(self, *target_nodes)

        # If only one node is provided, use self as the second target
        if type(target_nodes) != list:
            target_nodes = [target_nodes, self]
        elif len(target_nodes)==1:
            target_nodes = tree_nodes.append(self)

        start = target_nodes[-1]
        targets = set(target_nodes)
        nodes_bellow = set([start]+start.get_descendants())
        current = start
        prev_node = start
        while current is not None:
            # all nodes under current (skip vissited)
            new_nodes = [n for s in current.children for n in s.traverse() \
                           if s is not prev_node]+[current]
            nodes_bellow.update(new_nodes)
            if targets.issubset(nodes_bellow):
                break
            else:
                prev_node = current
                current = current.up

        return current

    def get_leaves(self):
        """
        Returns the list of terminal nodes (leaves) under this node.
        """
        return [n for n in self.iter_leaves()]

    def get_leaf_names(self):
        """
        Returns the list of terminal node names under the current
        node.
        """
        return [ n.name for n in self.iter_leaves() ]

    def get_descendants(self, strategy="preorder"):
        """
        Returns the list of all nodes (leaves and internal) under
        this node.
        re buil
        See iter_descendants method.
        """
        return [n for n in self.traverse(strategy="preorder") if n != self]

    def iter_search_nodes(self, **conditions):
        for n in self.traverse():
            conditions_passed = 0
            for key, value in conditions.iteritems():
                if hasattr(n, key) and getattr(n, key) == value:
                    conditions_passed +=1
            if conditions_passed == len(conditions):
                yield n

    def search_nodes(self, **conditions):
        matching_nodes = []
        for n in self.iter_search_nodes(**conditions):
            matching_nodes.append(n)
        return matching_nodes

    def get_leaves_by_name(self,name):
        """ Returns a list of nodes marching a given name. """
        return self.search_nodes(name=name, children=[])

    def is_leaf(self):
        if self.collapsed or len(self.children)==0:
            return True
        else:
            return False

    def is_root(self):
        if self.up is None:
            return True
        else:
            return False

    def collapse(self):
        self.collapse = True
    def expand(self):
        self.collapse = False

    # Distance related functions
    def get_distance(self, target, target2=None, topology_only=False):
        """

        Returns the distance between two nodes. If only one target is
        specified, it returns the distance bewtween the target and the
        current node.

        ARGUMENTS:
        ==========
          'target': a node within the same tree structure.

          'target2': a node within the same tree structure. If
          not specified, current node is used as target2.

        RETURNS:
        ========
          the distance between nodes

        """

        if target2 is None:
            target2 = self
            root = self.get_tree_root()
        else:
            # is target node under current node?
            root = self

        target, target2 = _translate_nodes(root, target, target2)
        ancestor = root.get_common_ancestor(target, target2)
        if ancestor is None:
            raise TreeError, "Nodes are not connected"

        dist = 0.0
        for n in [target2, target]:
            current = n
            while current != ancestor:
                if topology_only:
                    if  current!=target:
                        dist += 1
                else:
                    dist += current.dist
                current = current.up
        return dist

    def get_farthest_node(self, topology_only=False):
        """
        Returns the node's farthest descendant or ancestor node, and the
        distance to it.

        ARGUMENTS:
        ==========

          * 'topology_only' [True or False]: defines whether branch node
           distances should be discarded from analysis or not. If
           "True", only topological distance (number of steps to get the
           target node) will be used.

        RETURNS:
        ========
          A tuple = (farthest_node, dist_to_farthest_node)

        """
        # Init fasthest node to current farthest leaf
        farthest_node,farthest_dist = self.get_farthest_leaf(topology_only=topology_only)
        prev    = self
        if topology_only:
            cdist = 0
        else:
            cdist = prev.dist
        current = prev.up
        while current is not None:
            for ch in current.children:
                if ch != prev:
                    if not ch.is_leaf():
                        fnode, fdist = ch.get_farthest_leaf(topology_only=topology_only)
                    else:
                        fnode = ch
                        fdist = 0
                    if topology_only:
                        fdist += 1.0
                    else:
                        fdist += ch.dist
                    if cdist+fdist > farthest_dist:
                        farthest_dist = cdist + fdist
                        farthest_node = fnode
            prev = current
            if topology_only:
                cdist += 1
            else:
                cdist  += prev.dist
            current = prev.up
        return farthest_node, farthest_dist

    def get_farthest_leaf(self, topology_only=False):
        """
        Returns node's farthest descendant node (which is always a leaf), and the
        distance to it.

        ARGUMENTS:
        ==========

          * 'topology_only' [True or False]: defines whether branch node
             distances should be discarded from analysis or not. If
             "True", only topological distance (number of steps to get the
             target node) will be used.

         RETURNS:
         ========
          A tuple = (farthest_node, dist_to_farthest_node)

        """
        max_dist = 0.0
        max_node = None
        if self.is_leaf():
            return self, 0.0
        else:
            for ch in self.children:
                node, d = ch.get_farthest_leaf(topology_only=topology_only)
                if topology_only:
                    d += 1.0
                else:
                    d += ch.dist
                if d>=max_dist:
                    max_dist = d
                    max_node = node
            return max_node, max_dist

    def get_midpoint_outgroup(self):
        """
        Returns the node that divides the current tree into two distance-balanced
        partitions.
        """
        # Gets the farthest node to the current root
        root = self.get_tree_root()
        nA , r2A_dist = root.get_farthest_leaf()
        nB , A2B_dist = nA.get_farthest_node()

        outgroup = nA
        middist  = A2B_dist / 2.0
        cdist = 0
        current = nA
        while current is not None:
            cdist += current.dist
            if cdist > (middist): # Deja de subir cuando se pasa del maximo
                break
            else:
                current = current.up
        return current

    def populate(self, size, names_library=[], reuse_names=True):
        """
        Populates the partition under this node with a given number
        of leaves. Internal nodes are added as required.

        ARGUMENTS:
        ==========

          * 'size' is the number of leaf nodes to add to the current
            tree structure.
        """

        charset =  "abcdefghijklmnopqrstuvwxyz"
        prev_size = len(self)
        terminal_nodes = set(self.get_leaves())
        silly_nodes = set([n for n in self.traverse() \
                           if len(n)==1 and n.children!=[]])

        if self.is_leaf():
            size -=1
        names_library = set(names_library)
        while len(terminal_nodes) != size+prev_size:
            try:
                target = random.sample(silly_nodes, 1)[0]
                silly_nodes.remove(target)
            except ValueError:
                target = random.sample(terminal_nodes, 1)[0]
                terminal_nodes.remove(target)
                silly_nodes.add(target)
                if target is not self:
                    names_library.add(target.name)
                    #target.name = "NoName"

            if len(names_library)>0:
                tname = random.sample(names_library,1)[0]
                if not reuse_names:
                    names_library.remove(tname)

            else:
                tname = ''.join(random.sample(charset,5))
            tdist = random.random()
            new_node = target.add_child( name=tname, dist=tdist )
            terminal_nodes.add(new_node)
    def set_outgroup(self, outgroup):
        """
        Sets a descendant node as the outgroup of a tree.  This function
        can be used to root a tree or even an internal node.

        ARGUMENTS:
        ==========

          * 'outgroup' is a leaf or internal node under the current tree
            structure.
        """

        outgroup = _translate_nodes(self, outgroup)

        if self == outgroup:
            raise ValueError, "Cannot set myself as outgroup"

        parent_outgroup = outgroup.up

        # Down branch connector
        n = outgroup
        while n.up is not self:
            n = n.up

        self.children.remove(n)
        if len(self.children)>1:
            down_branch_connector = self.__class__()
            down_branch_connector.dist = 0.0
            for ch in self.get_children():
                down_branch_connector.children.append(ch)
                ch.up = down_branch_connector
                self.children.remove(ch)
        else:
            down_branch_connector = self.children[0]

        # Connects down branch to myself or to outgroup
        quien_va_ser_padre = parent_outgroup
        if quien_va_ser_padre is not self:
            # Parent-child swaping
            quien_va_ser_hijo = quien_va_ser_padre.up
            quien_fue_padre = None
            buffered_dist = quien_va_ser_padre.dist

            while quien_va_ser_hijo is not self:
                quien_va_ser_padre.children.append(quien_va_ser_hijo)
                quien_va_ser_hijo.children.remove(quien_va_ser_padre)

                buffered_dist2 = quien_va_ser_hijo.dist
                quien_va_ser_hijo.dist = buffered_dist
                buffered_dist = buffered_dist2

                quien_va_ser_padre.up = quien_fue_padre
                quien_fue_padre = quien_va_ser_padre

                quien_va_ser_padre = quien_va_ser_hijo
                quien_va_ser_hijo = quien_va_ser_padre.up

            quien_va_ser_padre.children.append(down_branch_connector)
            down_branch_connector.up = quien_va_ser_padre
            quien_va_ser_padre.up = quien_fue_padre

            down_branch_connector.dist += buffered_dist

            outgroup2 = parent_outgroup
            parent_outgroup.children.remove(outgroup)
            outgroup2.dist = 0
        else:
            outgroup2 = down_branch_connector

        outgroup.up = self
        outgroup2.up = self
        self.children = [outgroup,outgroup2]
        middist = (outgroup2.dist + outgroup.dist)/2
        outgroup.dist = middist
        outgroup2.dist = middist
        self.children.sort()

    def unroot(self):
        """ Unroots this node. This function is intented to be used over
        the absolute tree root node, but it can be also be applied to any
        other internal node. """
        # if is rooted
        if not self.is_root():
            print >>sys.stderr, "Warning. You are unrooting an internal node.!!"
        if len(self.children)==2:
            if not self.children[0].is_leaf():
                self.children[0].delete()
            elif not self.children[1].is_leaf():
                self.children[1].delete()
            else:
                raise TreeError, "Cannot unroot a tree with only two leaves"

    def show(self, layout=None, \
               image_properties=None):
        """ Begins an interative session to visualize this node
        structure."""
        try:
            from ete_dev.treeview import drawer
        except ImportError, e:
            print "'treeview' module could not be loaded.\n",e
            print "\n\n"
            print self
        else:
            drawer.show_tree(self,layout,image_properties)

    def render(self, file_name, layout=None, w=None, h=None, \
                       img_properties=None, header=None):
        """ Renders the tree structure into an image file. """
        try:
            from ete_dev.treeview import drawer
        except ImportError, e:
            print "'treeview' module could not be loaded.\n",e
            print "\n\n"
            print self
            print e
        else:
            drawer.render_tree(self, file_name, w=w, h=h, style=layout, \
                                   img_properties=img_properties, \
                                   header=header)

    def _asciiArt(self, char1='-', show_internal=True, compact=False):
        """
        Returns the ASCII representation of the tree. Code taken from the
        PyCogent GPL project.
        """

        LEN = 5
        PAD = ' ' * LEN
        PA = ' ' * (LEN-1)
        if not self.is_leaf():
            mids = []
            result = []
            for c in self.children:
                if c is self.children[0]:
                    char2 = '/'
                elif c is self.children[-1]:
                    char2 = '\\'
                else:
                    char2 = '-'
                (clines, mid) = c._asciiArt(char2, show_internal, compact)
                mids.append(mid+len(result))
                result.extend(clines)
                if not compact:
                    result.append('')
            if not compact:
                result.pop()
            (lo, hi, end) = (mids[0], mids[-1], len(result))
            prefixes = [PAD] * (lo+1) + [PA+'|'] * (hi-lo-1) + [PAD] * (end-hi)
            mid = (lo + hi) / 2
            prefixes[mid] = char1 + '-'*(LEN-2) + prefixes[mid][-1]
            result = [p+l for (p,l) in zip(prefixes, result)]
            if show_internal:
                stem = result[mid]
                result[mid] = stem[0] + self.name + stem[len(self.name)+1:]
            return (result, mid)
        else:
            return ([char1 + '-' + self.name], 0)

    def get_ascii(self, show_internal=True, compact=False):
        """Returns a string containing an ascii drawing of the tree.

        Arguments:
        - show_internal: includes internal edge names.
        - compact: use exactly one line per tip.
        """
        (lines, mid) = self._asciiArt(
                show_internal=show_internal, compact=compact)
        return '\n'+'\n'.join(lines)


def _translate_nodes(root, *nodes):
    target_nodes = []
    for n in nodes:
        if type(n) is str:
            mnodes = root.search_nodes(name=n)
            if len(mnodes) == 0:
                raise ValueError, "Node name not found: "+str(n)
            elif len(mnodes)>1:
                raise ValueError, "Ambiguos node name: "+str(n)
            else:
                target_nodes.append(mnodes[0])
        elif type(n) != root.__class__:
            raise ValueError, "Invalid target node: "+str(n)
        else:
            target_nodes.append(n)

    if len(target_nodes) == 1:
        return target_nodes[0]
    else:
        return target_nodes

### R bindings
def asETE(R_phylo_tree):
    try:
        import rpy2.robjects as robjects
        R = robjects.r
    except ImportError, e:
        print e
        print >>sys.stderr, "RPy >= 2.0 is required to connect"
        return

    R.library("ape")
    return Tree( R["write.tree"](R_phylo_tree)[0])

def asRphylo(ETE_tree):
    try:
        import rpy2.robjects as robjects
        R = robjects.r
    except ImportError, e:
        print e
        print >>sys.stderr, "RPy >= 2.0 is required to connect"
        return
    R.library("ape")
    return R['read.tree'](text=ETE_tree.write())


# A cosmetic alias :)
Tree = TreeNode
