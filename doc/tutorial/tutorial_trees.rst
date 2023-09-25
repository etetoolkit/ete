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

The `Newick format <https://en.wikipedia.org/wiki/Newick_format>`_ is
one of the most widely used standard representations of trees in
bioinformatics. It uses nested parentheses to represent hierarchical
data structures as text strings. The original newick standard is able
to encode information about the tree topology, branch distances and
node names. Nevertheless, it is not uncommon to find slightly
different variations of the format.

ETE can read and write many of them:

.. table::

  ====== ========================================= =============================================
  Format Description                               Example
  ====== ========================================= =============================================
  0      internal nodes with support (flexible)    ((D:0.7,F:0.5)1.0:0.6,(B:0.2,H:0.7)1.0:0.8);
  1      internal nodes with names (flexible)      ((D:0.7,F:0.5)E:0.6,(B:0.2,H:0.7)B:0.8);
  2      internal w/ support, all lengths present  ((D:0.7,F:0.5)1.0:0.6,(B:0.2,H:0.7)1.0:0.8);
  3      internal w/ names, all lengths present    ((D:0.7,F:0.5)E:0.6,(B:0.2,H:0.7)B:0.8);
  4      names and lengths for leaves only         ((D:0.7,F:0.5),(B:0.2,H:0.7));
  5      leaf names and all lengths                ((D:0.7,F:0.5):0.6,(B:0.2,H:0.7):0.8);
  6      leaf names and internal lengths           ((D,F):0.6,(B,H):0.8);
  7      all names and leaf lengths                ((D:0.7,F:0.5)E,(B:0.2,H:0.7)B);
  8      all names (leaves and internal nodes)     ((D,F)E,(B,H)B);
  9      leaf names only                           ((D,F),(B,H));
  100    topology only                             ((,),(,));
  ====== ========================================= =============================================

Formats labeled as *flexible* allow for missing information. For
instance, format 0 will be able to load a newick tree even if it does
not contain branch support information. However, format 2 would raise
an exception. In other words, if you want to control that your newick
files strictly follow a given pattern you can use **strict** format
definitions.


Creating a tree
~~~~~~~~~~~~~~~

ETE's class :class:`Tree`, provided by the main module :mod:`ete4`,
can be used to construct trees. You can create a single node by
calling :func:`Tree` without any arguments::

  from ete4 import Tree

  # Empty tree (single node).
  t = Tree()

Or you can call it with a dictionary specifying the properties of that
single node. You can also use the :func:`populate` method to populate
a tree with a random topology::

  from ete4 import Tree

  # Also a single node, but with some properties.
  t = Tree({'name': 'root', 'dist': 1.0, 'support': 0.5, 'coolness': 'high'})

  # Populate t with a random topology of size 10.
  t.populate(10)

(In all the examples we will want to write ``from ete4 import Tree``
first to use the :class:`Tree` class, as we did above. In the
remaining examples we will assume that you have already imported it.)

The properties of a node are stored in its :attr:`props` dictionary.
With the previous example, writing ``print(t.props)`` will show us a
dictionary that should look familiar. And if you :func:`print` a tree,
you will see a simple visualization. For our example of the previously
populated tree::

  print(t.props)  # where the properties of a node are stored
  # {'name': 'root', 'dist': 1.0, 'support': 0.5, 'coolness': 'high'}

  print(t)  # will look more or less like:
  #  ╭─┬╴aaaaaaaaaa
  #  │ ╰╴aaaaaaaaab
  # ─┤ ╭─┬╴aaaaaaaaac
  #  │ │ ╰─┬╴aaaaaaaaad
  #  ╰─┤   ╰─┬╴aaaaaaaaae
  #    │     ╰╴aaaaaaaaaf
  #    ╰─┬╴aaaaaaaaag
  #      ╰─┬╴aaaaaaaaah
  #        ╰─┬╴aaaaaaaaai
  #          ╰╴aaaaaaaaaj


Reading newick trees
~~~~~~~~~~~~~~~~~~~~

To load a tree from a newick text string you can pass to :func:`Tree`
the text string containing the newick structure. Alternatively, you
can pass a file object that contains the newick string. And
optionally, you can also specify the format that should be used to
parse it (1 by default, see :ref:`sec:newick-formats`).

::

  # Load a tree structure from a newick string. It returns the root node.
  t1 = Tree('(A:1,(B:1,(E:1,D:1):0.5):0.5);')

  # Load a tree structure from a newick file.
  t2 = Tree(open('genes_tree.nw'))

  # You can also specify how to parse the newick. For instance,
  # for internal nodes with support we will use parser=0.
  t3 = Tree('(A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);', parser=0)


Writing newick trees
~~~~~~~~~~~~~~~~~~~~

Any ETE tree instance can be exported using newick notation using the
:func:`Tree.write` method. It also allows for parser selection, so you
can use the same function to convert between newick formats.

::

  # Load a tree with internal support values.
  t = Tree('(A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);', parser=0)

  # Print its newick using the default parser.
  print(t.write())  # (A:1,(B:1,(E:1,D:1):0.5):0.5);

  # To print the internal support values you can change the parser.
  print(t.write(parser=0))  # (A:1,(B:1,(E:1,D:1)0.4:0.5)0.9:0.5);

  # We can also write into a file.
  t.write(parser=0, outfile='new_tree.nw')


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

  ==================== ==========================================================================
  Method               Description
  ==================== ==========================================================================
  :attr:`node.dist`    Distance from the node to its parent (branch length)
  :attr:`node.support` Reliability of the partition defined by the node (like bootstrap support)
  :attr:`node.name`    Node's name
  ==================== ==========================================================================

In addition, several methods are provided to perform basic operations
on tree node instances:

.. table::

  ======================== ====================================================================
  Method                   Description
  ======================== ====================================================================
  :attr:`node.is_leaf`     True if node has no children
  :attr:`node.is_root`     True if node has no parent
  :attr:`node.root`        The top-most node within the same tree structure as node
  :attr:`len(node)`        Returns the number of leaves under node
  :attr:`print(node)`      Prints a text-based representation of the tree topology under node
  :attr:`n in node`        True if *n* is a leaf under node
  :attr:`for leaf in node` Iterates over all leaves under node
  :func:`node.explore`     Explore node graphically using a GUI
  ======================== ====================================================================

This is an example on how to access such attributes::

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


The meaning of the "root node" in unrooted trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a tree is loaded from external sources, a pointer to the top-most
node is returned. This is called the tree root, and **it will exist
even if the tree is conceptually considered as unrooted**. That is,
the root node can be considered as the master node, since it
represents the whole tree structure.

ETE will consider that a tree is "unrooted" if the master root node
has more than two children.

::

  unrooted_tree = Tree('(A,B,(C,D));')
  print(unrooted_tree)
  #  ╭╴A
  # ─┼╴B
  #  ╰─┬╴C
  #    ╰╴D

  rooted_tree = Tree('((A,B),(C,D));')
  print(rooted_tree)
  #  ╭─┬╴A
  # ─┤ ╰╴B
  #  ╰─┬╴C
  #    ╰╴D


Browsing trees (traversing)
---------------------------

One of the most basic operations for tree analysis is *tree browsing*.
This is, essentially, visiting nodes within a tree. ETE provides a
number of methods to search for specific nodes or to navigate over the
hierarchical structure of a tree.


Getting leaves, descendants and node's relatives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tree instances contain several functions to access their descendants.
Available methods are self explanatory:

.. autosummary::

   ete4.Tree.descendants
   ete4.Tree.ancestors
   ete4.Tree.leaves
   ete4.Tree.leaf_names
   ete4.Tree.get_children
   ete4.Tree.get_sisters


Traversing (browsing) trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Often, when processing trees, all nodes need to be visited. This is
called tree traversing. There are different ways to traverse a tree
structure depending on the order in which children nodes are visited.
ETE implements the three most common strategies: *preorder*,
*postorder* and *levelorder*. The following scheme shows the
differences in the strategy for visiting nodes (note that in all cases
the whole tree is browsed):

* *preorder*: 1) visit the root, 2) traverse the left subtree, 3)
  traverse the right subtree.
* *postorder*: 1) traverse the left subtree, 2) traverse the right
  subtree, 3) visit the root.
* *levelorder* (default): every node on a level is visited before going
  to a lower level.

Every node in a tree includes a :func:`traverse` method, which can be
used to visit, one by one, every node node under the current
partition. In addition, the :func:`descendants` method can be set to
use either a post- or a preorder strategy. The only difference between
:func:`traverse` and :func:`descendants` is that the first will
include the root node in the iteration.

.. autosummary::

   ete4.Tree.traverse
   ete4.Tree.descendants
   ete4.Tree.leaves

where :attr:`strategy` can take the values "preorder", "postorder", or
"levelorder"::

  # Make a tree.
  t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);')

  # Traverse the nodes in postorder.
  for node in t.traverse('postorder'):
      print(node.name)  # or do some analysis with the node

  # If we want to iterate over a tree excluding the root node, we can
  # use the descendants method instead.
  for node in t.descendants('postorder'):
      print(node.name)  # or do some analysis with the node

Additionally, you can implement your own traversing function using the
structural attributes of nodes. In the following example, only nodes
between a given leaf and the tree root are visited::

  t = Tree('(A:1,(B:1,(C:1,D:1):0.5):0.5);')

  # Browse the tree from a specific leaf to the root.
  node = t['C']  # selects the node named 'C'
  while node:
      print(node.dist)  # for example, or do some operations with it
      node = node.up


Advanced traversing
~~~~~~~~~~~~~~~~~~~

.. _is_leaf_fn:

Collapsing nodes while traversing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ETE supports the use of the :attr:`is_leaf_fn` argument in most of its
traversing functions. The value of :attr:`is_leaf_fn` is expected to
be a pointer to any python function that accepts a node instance as
its first argument and returns a boolean value (True if node should be
considered a leaf node).

By doing so, all traversing methods will use such a custom function to
decide if a node is a leaf. This becomes specially useful when dynamic
collapsing of nodes is needed, thus avoiding to prune the same tree in
many different ways.

For instance, given a large tree structure, the following code will
export the newick of the pruned version of the topology, where nodes
grouping the same tip labels are collapsed::

  t = Tree('((((a,a,a)a,a)aa,(b,b)b)ab,(c,(d,d)d)cd);')

  print(t.to_str(props=['name'], compact=True))  # show internal names too
  #                        ╭╴a
  #                    ╭╴a╶┼╴a
  #               ╭╴aa╶┤   ╰╴a
  #          ╭╴ab╶┤    ╰╴a
  # ╴(empty)╶┤    ╰╴b╶┬╴b
  #          │        ╰╴b
  #          ╰╴cd╶┬╴c
  #               ╰╴d╶┬╴d
  #                   ╰╴d

  # Cache for every node (for each node, a set of all its leaves' names).
  node2labels = t.get_cached_content('name')

  def collapsed_leaf(node):
      return len(node2labels[node]) == 1

  print(t.write(is_leaf_fn=collapsed_leaf))
  # ((aa,b)ab,(c,d)cd);

  # We can even load the collapsed version as a new tree.
  t2 = Tree( t.write(is_leaf_fn=collapsed_leaf) )

  print(t2.to_str(props=['name'], compact=True))
  #          ╭╴ab╶┬╴aa
  # ╴(empty)╶┤    ╰╴b
  #          ╰╴cd╶┬╴c
  #               ╰╴d

Another interesting use of this approach is to find the first matching
nodes in a given tree that match a custom set of criteria, without
browsing the whole tree structure.

Let's say we want to get all deepest nodes in a tree whose branch
length is defined and larger than one::

  t = Tree('(((a,b)ab:2,(c,d)cd:2)abcd:2,((e,f):2,g)efg:2);')

  print(t.to_str(props=['name', 'dist'], compact=True))  # name and distance
  #                             ╭╴ab,2.0╶┬╴a,(empty)
  #                  ╭╴abcd,2.0╶┤        ╰╴b,(empty)
  #                  │          ╰╴cd,2.0╶┬╴c,(empty)
  # ╴(empty),(empty)╶┤                   ╰╴d,(empty)
  #                  │         ╭╴(empty),2.0╶┬╴e,(empty)
  #                  ╰╴efg,2.0╶┤             ╰╴f,(empty)
  #                            ╰╴g,(empty)

  def processable_node(node):
      return node.dist and node.dist > 1

  for leaf in t.leaves(is_leaf_fn=processable_node):
      print(leaf.name)
  # Will print just these two "leaves" (according to processable_node):
  #   abcd
  #   efg


Iterators or lists?
~~~~~~~~~~~~~~~~~~~

The methods used to iterate over nodes are `python iterators
<https://docs.python.org/3/library/stdtypes.html#typesseq>`_. The
iterators produce only one element at a time, and thus are normally
faster and take less memory than lists.

Sometimes you will need a list instead, for example if you want to
refer to nodes that have appeared before in the iteration. In that
case, you can create it by adding ``list(...)`` to your call.

For example::

  leaves = list(t.leaves())  # constructs a list with all the leaves

The same is valid for :func:`traverse`, :func:`descendants`,
:func:`ancestors` and so on.


Finding nodes by their properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both terminal and internal nodes can be located by searching along the
tree structure. Several methods are available:

.. table::

  ========================================= =========================================================================
  Method                                    Description
  ========================================= =========================================================================
  t.search_nodes(prop=value)                Iterator over nodes that have property prop equal to value, as name='A'
  t.search_descendants(prop=value)          Same, but only on descendants (excludes the node t itself)
  t.search_ancestors(prop=value)            Iterator over ancestor nodes
  t.search_leaves_by_name(name)             Iterator over leaf nodes matching a given name
  t.common_ancestor([node1, node2, node3])  Return the first internal node grouping node1, node2 and node3
  t[name]                                   Return the first node named name, same as next(t.search_nodes(name=name))
  ========================================= =========================================================================


Search_all nodes matching a given criteria
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A custom list of nodes matching a given name can be easily obtained
through the :func:`Tree.search_nodes` function.

::

  t = Tree('((H:1,I:1):0.5,A:1,(B:1,(C:1,D:1):0.5):0.5);')

  print(t)
  #  ╭─┬╴H
  # ─┤ ╰╴I
  #  ├╴A
  #  ╰─┬╴B
  #    ╰─┬╴C
  #      ╰╴D

  n1 = t['D']  # get node named 'D'

  # Get all nodes with distance=0.5
  nodes = list(t.search_nodes(dist=0.5))
  print(len(nodes), 'nodes have distance 0.5')

  # We can limit the search to leaves and node names
  n2 = next(t.search_leaves_by_name('D'))  # takes the first match
  print(n1 == n2)  # True


Search nodes matching a given criteria (iteration)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A limitation of the :func:`Tree.search_nodes` method is that you
cannot use complex conditional statements to find specific nodes. When
the search criteria is too complex, you may want to create your own search
function. For example::

  def search_by_size(node, size):
      """Yield nodes with a given number of leaves."""
      for n in node.traverse():
          if len(n) == size:
              yield n

  t = Tree()
  t.populate(40)

  # Get a list of all nodes containing 6 leaves.
  list(search_by_size(t, size=6))


Find the first common ancestor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Searching for the first common ancestor of a given set of nodes is a
handy way of finding internal nodes::

  t = Tree('(((a,b)ab,(c,d)cd:2)abcd,((e,f)ef,g)efg)root;')

  print(t.to_str(props=['name'], compact=True))
  #              ╭╴ab╶┬╴a
  #       ╭╴abcd╶┤    ╰╴b
  #       │      ╰╴cd╶┬╴c
  # ╴root╶┤           ╰╴d
  #       │     ╭╴ef╶┬╴e
  #       ╰╴efg╶┤    ╰╴f
  #             ╰╴g

  ancestor = t.common_ancestor(['a', 'c', 'ab'])  # will be node abcd


Custom searching functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

A limitation of the previous methods is that you cannot use complex
conditional statements to find specific nodes. However you can use
traversing methods and apply your custom filters::

  t = Tree('((H:0.3,I:0.1):0.5,A:1,(B:0.4,(C:1,D:1):0.5):0.5):0;')

  # Use a list comprehension, iterating with the traverse() method.
  matches = [node for node in t.traverse() if node.dist > 0.3]
  print(len(matches), 'nodes have distance > 0.3')

  # Or create a small function to filter your nodes.
  def condition(node):
      return node.dist > 0.3 and node.is_leaf

  matches2 = [node for node in t.traverse() if condition(node)]
  print(len(matches2), 'nodes have distance > 0.3 and are leaves')


Shortcuts
^^^^^^^^^

Finally, ETE implements a built-in method to find the first node
matching a given name, which is one of the most common tasks needed
for tree analysis. This can be done through the operator ``[]``. Thus,
``t['A']`` will return the first node whose name is "A" and that is
under the tree ``t``.

::

  t = Tree('((H,I),A,(B,(C,(J,(F,D)))));')

  # Get the node D in a simple way.
  D = t['D']

  # Get the path from D to the root (similar to list(t.ancestors())).
  path = []
  node = D
  while node.up:
      node = node.up
      path.append(node)

  print('There are', len(path)-1, 'nodes between D and the root.')


.. _check_monophyly:

Checking the monophyly of properties within a tree
--------------------------------------------------

Although monophyly is actually a phylogenetic concept used to refer to
a set of species that group exclusively together within a tree
partition, the idea can be easily used for any type of trees.

Therefore, we could consider that a set of values for a given node
property present in our tree is monophyletic, if such values group
exclusively together as a single tree partition. If not, the
corresponding relationship connecting such values (para- or
poly-phyletic) could be also be inferred.

The :func:`Tree.check_monophyly` method will do so when a given tree
is queried for any custom attribute.

::

  t = Tree('((((((a,e),i),o),h),u),((f,g),j));')
  print(t)
  #         ╭─┬╴a
  #       ╭─┤ ╰╴e
  #     ╭─┤ ╰╴i
  #   ╭─┤ ╰╴o
  # ╭─┤ ╰╴h
  #─┤ ╰╴u
  # │ ╭─┬╴f
  # ╰─┤ ╰╴g
  #   ╰╴j

  # We can check how, indeed, all vowels are not monophyletic in the previous
  # tree, but paraphyletic (monophyletic except for a group that is monophyletic):
  print(t.check_monophyly(values=['a', 'e', 'i', 'o', 'u'], prop='name'))
  # False (not monophyletic), 'paraphyletic' (type of group), {h} (the leaves not included)

  # However, the following set of vowels are monophyletic:
  print(t.check_monophyly(values=['a', 'e', 'i', 'o'], prop='name'))
  # True (it is monophyletic), 'monophyletic' (type of group), {} (no leaves left)

  # When a group is not monophyletic nor paraphyletic, it is called polyphyletic.
  print(t.check_monophyly(values=['i', 'h'], prop='name'))
  # False, 'polyphyletic', {e, a, o}

.. note::

   When the property is set to "species" in a :class:`PhyloTree` node,
   this method will correspond to the standard phylogenetic definition
   of monophyletic, paraphyletic, and polyphyletic.

Finally, the :func:`Tree.get_monophyletic` method is also provided,
which returns a list of nodes within a tree where a given set of
properties are monophyletic. Note that, although a set of values are
not monophyletic regarding the whole tree, several independent
monophyletic partitions could be found within the same topology.

In the following example we get all clusters within the same tree
exclusively grouping a custom set of annotations::

  t = Tree("((((((a,e),i),o),h),u),((f,g),(j,k)));")

  # Annotate the tree using external data.
  colors = {'a': 'green', 'e': 'green',
            'i': 'yellow', 'o': 'black', 'u':'purple',
            'f': 'yellow', 'g': 'green',
            'j': 'yellow', 'k': 'yellow'}

  for leaf in t:
      leaf.add_props(color=colors.get(leaf.name, 'none'))

  print(t.to_str(props=['name', 'color'], show_internal=False, compact=True))
  #          ╭─┬╴a,green
  #        ╭─┤ ╰╴e,green
  #      ╭─┤ ╰╴i,yellow
  #    ╭─┤ ╰╴o,black
  #  ╭─┤ ╰╴h,none
  # ─┤ ╰╴u,purple
  #  │ ╭─┬╴f,yellow
  #  ╰─┤ ╰╴g,green
  #    ╰─┬╴j,yellow
  #      ╰╴k,yellow

  # Obtain clusters exclusively green and yellow.
  print('Green-yellow clusters:')
  for node in t.get_monophyletic(prop='color', values=['green', 'yellow']):
      print(node.to_str(props=[ 'name', 'color'], show_internal=False, compact=True))

  # Green-yellow clusters:
  #  ╭─┬╴a,green
  # ─┤ ╰╴e,green
  #  ╰╴i,yellow
  #  ╭─┬╴f,yellow
  # ─┤ ╰╴g,green
  #  ╰─┬╴j,yellow
  #    ╰╴k,yellow


.. _cache_node_content:

Caching tree content for faster lookup operations
-------------------------------------------------

If your program needs to access to the content of different nodes very
frequently, traversing the tree to get the leaves of each node over
and over will produce significant slowdowns in your algorithm.

ETE provides a convenient methods to cache frequently used data. The
method :func:`Tree.get_cached_content` returns a dictionary in which
keys are node instances and values represent the content of such
nodes. By default, "content" is understood as a set of leaf nodes.
After you retrieve this cached data, looking up the size or tip names
under a given node will be instantaneous.

Instead of caching the nodes themselves, specific properties can be
cached by setting a custom :attr:`prop` value.

::

  t = Tree()
  t.populate(50)

  node2leaves = t.get_cached_content()

  # Print the size of each node, without the need of traversing the subtrees every time.
  for n in t.traverse():
      print('Node %s contains %d tips.' % (n.name, len(node2leaves[n])))


Node annotation
---------------

Adding properties to the nodes of a tree is called tree annotation.
ETE stores the properties (annotations) of a node in a dictionary
called ``props``.

In a phylogenetic tree, the nodes (with their branches) often have
names, branch lengths, and branch supports. ETE provides a shortcut
for their corresponding properties :attr:`name`, :attr:`dist`, and
:attr:`support`, so instead of writing ``n.props.get('name')``, you
can write ``n.name``, and similarly for ``n.dist`` and ``n.support``.

The :func:`Tree.add_prop` and :func:`Tree.add_props` methods allow to
add extra properties (features, annotations) to any node. The first
one allows to add one one feature at a time, while the second one can
be used to add many features with the same call.

Similarly, :func:`Tree.del_prop` can be used to delete a property.

::

  t = Tree('((H:0.3,I:0.1),A:1,(B:0.4,(C:0.5,(J:1.3,(F:1.2,D:0.1)))));')

  print(t.to_str())
  #      ╭╴name=H,dist=0.3
  #   ╭──┤
  #   │  ╰╴name=I,dist=0.1
  #   │
  # ──┼╴name=A,dist=1.0
  #   │
  #   │  ╭╴name=B,dist=0.4
  #   ╰──┤
  #      │  ╭╴name=C,dist=0.5
  #      ╰──┤
  #         │  ╭╴name=J,dist=1.3
  #         ╰──┤
  #            │  ╭╴name=F,dist=1.2
  #            ╰──┤
  #               ╰╴name=D,dist=0.1

  # Reference some nodes (to use later).
  A = t['A']  # by name
  C = t['C']
  H = t['H']
  ancestor_JFC = t.common_ancestor(['J', 'F', 'C'])  # by common ancestor

  # Let's now add some custom features to our nodes.
  C.add_props(vowel=False, confidence=1.0)
  A.add_props(vowel=True, confidence=0.8)
  ancestor_JFC.add_props(nodetype='internal')
  H.add_props(vowel=False, confidence=0.3)

  for node in [A, C, H, ancestor_JFC]:
      print(f'Properties of {node.name}: {node.props}')

  # Let's annotate by looping over all nodes.
  # (Note that this overwrites the previous values.)
  for leaf in t:
      is_vowel = leaf.name in 'AEIOU'
      leaf.add_props(vowel=is_vowel, confidence=1)

  # Now we use this information to analyze the tree.
  print('This tree has', sum(1 for n in t.search_nodes(vowel=True)), 'vowel nodes')
  print('They are:', [leaf.name for leaf in t.leaves() if leaf.props['vowel']])

  # But features may refer to any kind of data, not only simple values.
  # For example, we can calculate some values and store them within nodes.
  #
  # Let's detect leaves under 'ancestor_JFC' with distance higher than 1.
  # Note that it traverses a subtree which starts from 'ancestor_JFC'.
  matches = [leaf for leaf in ancestor_JFC.leaves() if leaf.dist > 1.0]

  # And save this pre-computed information into the ancestor node.
  ancestor_JFC.add_props(long_branch_nodes=matches)

  # Prints the precomputed nodes
  print('These are the leaves under ancestor_JFC with long branches:',
        [n.name for n in ancestor_JFC.props['long_branch_nodes']])

  # We can also use the add_props() method to dynamically add new features.
  value = input('Custom label value: ')
  ancestor_JFC.add_props(label=value)
  print(f'Ancestor has now the "label" property with value "{value}":')
  print(ancestor_JFC.props)
