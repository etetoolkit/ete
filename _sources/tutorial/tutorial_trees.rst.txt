Working With Tree Data Structures
=================================

.. contents::

Trees
-----

Trees are a widely-used type of data structure that emulates a tree
design with a set of linked nodes. Formally, a tree is considered an
acyclic and connected graph. Each node in a tree has zero or more
child nodes, which are below it in the tree (by convention, trees grow
down, not up as they do in nature). A node that has a child is called
the child's parent node (or ancestor node, or superior). A node has at
most one parent.

The height of a node is the length of the longest downward path to a
leaf from that node. The height of the root is the height of the tree.
The depth of a node is the length of the path to its root (i.e., its
root path).

* The topmost node in a tree is called the root node. Being the
  topmost node, the root node will not have parents. It is the node at
  which operations on the tree commonly begin (although some
  algorithms begin with the leaf nodes and work up ending at the
  root). All other nodes can be reached from it by following edges or
  links. Every node in a tree can be seen as the root node of the
  subtree rooted at that node.

* Nodes at the bottommost level of the tree are called leaf nodes.
  Since they are at the bottommost level, they do not have any
  children.

* An internal node or inner node is any node of a tree that has child
  nodes and is thus not a leaf node.

* A subtree is a portion of a tree data structure that can be viewed
  as a complete tree in itself. Any node in a tree T, together with
  all the nodes below it, comprise a subtree of T. The subtree
  corresponding to the root node is the entire tree; the subtree
  corresponding to any other node is called a proper subtree (in
  analogy to the term proper subset).

In bioinformatics, trees are the result of many analyses, such as
phylogenetics or clustering. Although each case entails specific
considerations, many properties remains constant among them. In this
respect, ETE is a python toolkit that assists in the automated
manipulation, analysis and visualization of any type of hierarchical
trees. It provides general methods to handle and visualize tree
topologies, as well as specific modules to deal with phylogenetic and
clustering trees.


.. _sec:newick-formats:

Reading and writing newick trees
--------------------------------

The Newick format is one of the most widely used standard
representation of trees in bioinformatics. It uses nested parentheses
to represent hierarchical data structures as text strings. The
original newick standard is able to encode information about the tree
topology, branch distances and node names. Nevertheless, it is not
uncommon to find slightly different formats using the newick standard.

ETE can read and write many of them:

.. table::

  ====== ============================================== ====================================================================================
  FORMAT DESCRIPTION                                    SAMPLE
  ====== ============================================== ====================================================================================
  0      flexible with support values                   ((D:0.723274,F:0.567784)1.000000:0.067192,(B:0.279326,H:0.756049)1.000000:0.807788);
  1      flexible with internal node names              ((D:0.723274,F:0.567784)E:0.067192,(B:0.279326,H:0.756049)B:0.807788);
  2      all branches + leaf names + internal supports  ((D:0.723274,F:0.567784)1.000000:0.067192,(B:0.279326,H:0.756049)1.000000:0.807788);
  3      all branches + all names                       ((D:0.723274,F:0.567784)E:0.067192,(B:0.279326,H:0.756049)B:0.807788);
  4      leaf branches + leaf names                     ((D:0.723274,F:0.567784),(B:0.279326,H:0.756049));
  5      internal and leaf branches + leaf names        ((D:0.723274,F:0.567784):0.067192,(B:0.279326,H:0.756049):0.807788);
  6      internal branches + leaf names                 ((D,F):0.067192,(B,H):0.807788);
  7      leaf branches + all names                      ((D:0.723274,F:0.567784)E,(B:0.279326,H:0.756049)B);
  8      all names                                      ((D,F)E,(B,H)B);
  9      leaf names                                     ((D,F),(B,H));
  100    topology only                                  ((,),(,));
  ====== ============================================== ====================================================================================

Formats labeled as *flexible* allow for missing information. For
instance, format 0 will be able to load a newick tree even if it does
not contain branch support information. However, format 2 would raise
an exception. In other words, if you want to control that your newick
files strictly follow a given pattern you can use **strict** format
definitions.


Reading newick trees
~~~~~~~~~~~~~~~~~~~~

In order to load a tree from a newick text string you can use the
constructor :class:`Tree`, provided by the main module :mod:`ete4`.
You will only need to pass a text string containing the newick
structure and the format that should be used to parse it (1 by
default). Alternatively, you can pass a file object that contains the
newick string.

::

  from ete4 import Tree

  # Load a tree structure from a newick string. It returns the root node for the tree.
  t = Tree('(A:1,(B:1,(E:1,D:1):0.5):0.5);')

  # Load a tree structure from a newick file.
  t = Tree(open('genes_tree.nh'))

  # You can also specify how to parse the newick. For instance, for internal nodes with support we will use parser=0.
  t = Tree('(A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);', parser=0)


Writing newick trees
~~~~~~~~~~~~~~~~~~~~

Any ETE tree instance can be exported using newick notation using the
:func:`Tree.write` method. It also allows for format selection
(:ref:`sec:newick-formats`), so you can use the same function to
convert between newick formats.

::

  from ete4 import Tree

  # Load a tree with internal support values.
  t = Tree('(A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);', parser=0)

  # Print its newick using the default parser.
  print(t.write())
  # (A:1,(B:1,(E:1,D:1):0.5):0.5);

  # To print the internal support values you need to change the parser:
  print(t.write(parser=0))
  # (A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);

  # We can also write into a file
  t.write(parser=1, outfile='new_tree.nw')


Understanding ETE trees
-----------------------

Any tree topology can be represented as a succession of **nodes**
connected in a hierarchical way. Thus, for practical reasons, ETE
makes no distinction between the concepts of tree and node, as any
tree can be represented by its root node. This allows to use any
internal node within a tree as another sub-tree instance.

Once trees are loaded, they can be manipulated as normal python
objects. Given that a tree is actually a collection of nodes connected
in a hierarchical way, what you usually see as a tree will be the root
node instance from which the tree structure is hanging. However, every
node within a ETE's tree structure can be also considered a subtree.
This means, for example, that all the operational methods that we will
review in the following sections are available at any possible level
within a tree. Moreover, this feature will allow you to separate large
trees into smaller partitions, or concatenate several trees into a
single structure.


Basic tree attributes
---------------------

Each tree node has two basic attributes used to establish its position
in the tree: :attr:`Tree.up` and :attr:`Tree.children`. The first is a
pointer to its parent's node, while the latter is a list of children
nodes. Although it is possible to modify the structure of a tree by
changing these attributes, it is strongly recommend not to do it.
Several methods are provided to manipulate each node's connections in
a safe way (see :ref:`sec:modifying-tree-topology`).

In addition, three other basic attributes are always present in any
tree node instance (let's call it ``node``):

.. table::

  ==================== ============================================================================================
  Method               Description
  ==================== ============================================================================================
  :attr:`node.dist`    distance from the node to its parent (branch length). Default value = 1.0
  :attr:`node.support` informs about the reliability of the partition defined by the node (i.e. bootstrap support)
  :attr:`node.name`    node's name
  ==================== ============================================================================================

In addition, several methods are provided to perform basic operations
on tree node instances:

.. table::

  ======================== ======================================================================
  Method                   Description
  ======================== ======================================================================
  :attr:`node.is_leaf`     True if ``node`` has no children
  :attr:`node.is_root`     True if ``node`` has no parent
  :attr:`node.root`        the top-most node within the same tree structure as ``node``
  :attr:`len(node)`        returns the number of leaves under ``node``
  :attr:`print(node)`      prints a text-based representation of the tree topology under ``node``
  :attr:`n in node`        True if *n* is a leaf under ``node``
  :attr:`for leaf in node` iterates over all leaves under ``node``
  :func:`node.explore`     explore node graphically using a GUI
  ======================== ======================================================================

This is an example on how to access such attributes::

  from ete4 import Tree

  t = Tree()

  # Create a random tree topology.
  t.populate(15)

  print(t)  # text visualization of the tree
  print(t.children)  # list of children nodes directly hanging from the root
  print(t.up)  # should be None, since t is the root

  # You can also iterate over tree leaves using a simple syntax.
  for leaf in t:
      print(leaf.name)

  n = next(iter(t))  # take the first leaf
  print('First leaf name:', n.name)
  print('First leaf distance:', n.dist)
  print('t.is_leaf = %s   n.is_leaf = %s' % (t.is_leaf, n.is_leaf))
  print(n.root == t)  # True
  print(t.children[0].root == t)  # True too
  print(t.children[0].children[0].root == t)  # and True again


Root node on unrooted trees?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a tree is loaded from external sources, a pointer to the top-most
node is returned. This is called the tree root, and **it will exist
even if the tree is conceptually considered as unrooted**. That is,
the root node can be considered as the master node, since it
represents the whole tree structure. Unrooted trees can be identified
as trees where the master root node has more than two children.

::

  from ete4 import Tree

  unrooted_tree = Tree('(A,B,(C,D));')
  print(unrooted_tree)
  #  ╭╴A
  # ─┼╴B
  #  ╰─┬╴C
  #    ╰╴D

  rooted_tree = Tree('((A,B),(C,D));')
  print(rooted_tree)
  # ╭─┬╴A
  #─┤ ╰╴B
  # ╰─┬╴C
  #   ╰╴D


Browsing trees (traversing)
---------------------------

One of the most basic operations for tree analysis is *tree browsing*.
This is, essentially, visiting nodes within a tree. ETE provides a
number of methods to search for specific nodes or to navigate over the
hierarchical structure of a tree.
