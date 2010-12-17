.. module:: ete_dev
  :synopsis: provides main objects and modules
.. moduleauthor:: Jaime Huerta-Cepas


*********************************
Working With Tree Data Structures
*********************************

Trees are a widely-used type of data structure that emulates a tree
design with a set of linked nodes.  Formally, a tree is considered an
acyclic and connected graph. Each node in a tree has zero or more
child nodes, which are below it in the tree (by convention, trees grow
down, not up as they do in nature). A node that has a child is called
the child's parent node (or ancestor node, or superior). A node has at
most one parent.

The height of a node is the length of the longest downward path to a
leaf from that node. The height of the root is the height of the
tree. The depth of a node is the length of the path to its root (i.e.,
its root path).

* The topmost node in a tree is called the root node. Being the
  topmost node, the root node will not have parents. It is the node at
  which operations on the tree commonly begin (although some
  algorithms begin with the leaf nodes and work up ending at the
  root). All other nodes can be reached from it by following edges or
  links. Every node in a tree can be seen as the root node of the
  subtree rooted at that node.

* Nodes at the bottommost level of the tree are called leaf
  nodes. Since they are at the bottommost level, they do not have any
  children.

* An internal node or inner node is any node of a tree that has child nodes and
  is thus not a leaf node.

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



Reading and Writing Newick Trees
================================

The Newick format is one of the most widely used standard
representation of trees in bioinformatics. It uses nested parentheses
to represent hierarchical data structures as text strings. The
original newick standard is able to encode information about the tree
topology, branch distances and node names. Nevertheless, it is not
uncommon to find slightly different formats using the newick standard.

ETE can read and write many of them: 

.. _sub:newick-formats:
.. table::

  ======  ============================================== ======================================================================================
  FORMAT  DESCRIPTION                                         SAMPLE
  ======  ============================================== ======================================================================================
  0        flexible with support values                    ((D:0.723274,F:0.567784)1.000000:0.067192,(B:0.279326,H:0.756049)1.000000:0.807788);
  1        flexible with internal node names               ((D:0.723274,F:0.567784)E:0.067192,(B:0.279326,H:0.756049)B:0.807788);
  2        all branches + leaf names + internal supports   ((D:0.723274,F:0.567784)1.000000:0.067192,(B:0.279326,H:0.756049)1.000000:0.807788);
  3        all branches + all names                        ((D:0.723274,F:0.567784)E:0.067192,(B:0.279326,H:0.756049)B:0.807788);
  4        leaf branches + leaf names                      ((D:0.723274,F:0.567784),(B:0.279326,H:0.756049));
  5        internal and leaf branches + leaf names         ((D:0.723274,F:0.567784):0.067192,(B:0.279326,H:0.756049):0.807788);
  6        internal branches + leaf names                  ((D,F):0.067192,(B,H):0.807788);
  7        leaf branches + all names                       ((D:0.723274,F:0.567784)E,(B:0.279326,H:0.756049)B);
  8        all names                                       ((D,F)E,(B,H)B);
  9        leaf names                                      ((D,F),(B,H));
  100      topology only                                   ((,),(,)); 
  ======  ============================================== ======================================================================================

Formats labeled as *flexible* allow for missing information. For
instance, format 0 will be able to load a newick tree even if it does
not contain branch support information (it will be initialized with
the default value). However, format 2 would raise an exception.  In
other words, if you want to control that your newick files strictly
follow a given pattern you should use **strict** format definitions.


Reading newick trees
-----------------------

In order to load a tree from a newick text string you can use the
constructor :class:`Tree`, provided by the main module
:mod:`ete_dev`. You will only need to pass a text string containing
the newick structure and the format that should be used to parse it (0
by default). Alternatively, you can pass the path to a text file
containing the newick string.

::
 
  from ete_dev import Tree
   
  # Loads a tree structure from a newick string. The returned variable ’t’ is the root node for the tree.
  t = Tree("(A:1,(B:1,(E:1,D:1):0.5):0.5);" )
   
  # Load a tree structure from a newick file.
  t = Tree("genes_tree.nh")
   
  # You can also specify the newick format. For instance, for named internal nodes we will use format 1.
  t = Tree("(A:1,(B:1,(E:1,D:1)Internal_1:0.5)Internal_2:0.5)Root;", format=1)


Writing newick trees
-----------------------

Any ETE tree instance can be exported using newick notation using the
:func:`Tree.write` method, which is available in any tree node
instance. It also allows for format selection
(:ref:`sub:newick-format`), so you can use the same function to
convert between newick formats.

::
   
  from ete_dev import Tree
   
  # Loads a tree with internal node names
  t = Tree("(A:1,(B:1,(E:1,D:1)Internal_1:0.5)Internal_2:0.5)Root;", format=1)
   
  # And prints its newick using the default format
   
  print t.write() # (A:1.000000,(B:1.000000,(E:1.000000,D:1.000000)1.000000:0.500000)1.000000:0.500000);
   
  # To print the internal node names you need to change the format:
   
  print t.write(format=1) # (A:1.000000,(B:1.000000,(E:1.000000,D:1.000000)Internal_1:0.500000)Internal_2:0.500000);
   
  # We can also write into a file
  t.write(format=1, outfile="new_tree.nw")


Understanding ETE Trees
===========================

Any tree topology can be represented as a succession of **nodes**
connected in a hierarchical way. Thus, for practical reasons, ETE
makes no distinction between tree and node concepts, as any tree can
be represented by its root node. This allows to use any internal node
within a tree as another sub-tree instance.

Once trees are loaded, they can be manipulated as normal python
objects. Given that a tree is actually a collection of nodes connected
in a hierarchical way, what you usually see as a tree will be the root
node instance from which the tree structure is hanging. However, every
node within a ETE's tree structure can be also considered a
subtree. This means, for example, that all the operational methods
that we will review in the following sections are available at any
possible level within a tree. Moreover, this feature will allow you to
separate large trees into smaller partitions, or concatenate several
trees into a single structure. For this reason, you will find that the
:class:`TreeNode` and :class:`Tree` classes are synonymous.


Basic tree attributes
=========================

Each tree node has two basic attributes used to establish its position
in the tree: :attr:`TreeNode.up` and :attr:`TreeNode.children`.  The first is
a pointer to parent's node, while the later is a list of children
nodes.  Although it is possible to modify the structure of a tree by
changing these attributes, it is strongly recommend not to do
it. Several methods are provided to manipulate each node's connections
in a safe way (see :ref:`sec:modifying-tree-topology`).

In addition, three other basic attributes are always present in any
tree node instance:


.. table::
 
   ==========================     =============================================================================================  ================
   Method                         Description                                                                                    Default value       
   ==========================     =============================================================================================  ================ 
     :attr:`TreeNode.dist`          stores the distance from the node to its parent (branch length). Default value = 1.0             1.0      
     :attr:`TreeNode.support`       informs about the reliability of the partition defined by the node (i.e. bootstrap support)      1.0    
     :attr:`TreeNode.name`          Custom node's name.                                                                              NoName      
   ==========================     =============================================================================================  ================ 

In addition, several methods are provided to perform basic operations
on tree node instances:


.. table:: 

  =================================  =============================================================================================
  Method                              Description
  =================================  =============================================================================================
    :func:`TreeNode.is_leaf`           returns True if *node* has no children 
    :func:`TreeNode.is_root`           returns True if *node* has no parent
    :func:`TreeNode.get_tree_root`     returns the top-most node within the same tree structure as *node*
    :attr:`len(TreeNode)`              returns the number of leaves under *node*
    :attr:`print node`                 prints a text-based representation of the tree topology under *node*
    :attr:`if node in tree`            returns true if *node* is a leaf under *tree*
    :attr:`for leaf in node`           iterates over all leaves under *node*
    :func:`TreeNode.show`              Explore node graphically using a GUI.
  =================================  =============================================================================================


This is an example on how to access such attributes:

:: 

  from ete_dev import Tree
  t = Tree()
  # We create a random tree topology
  t.populate(15) 
  print t
  print t.children
  print t.get_children()
  print t.up
  print t.name
  print t.dist
  print t.is_leaf()
  print t.get_tree_root()
  print t.children[0].get_tree_root()
  print t.children[0].children[0].get_tree_root()
  # You can also iterate over tree leaves using a simple syntax
  for leaf in t:
    print leaf.name


Root node on unrooted trees?
------------------------------

When a tree is loaded from external sources, a pointer to the top-most
node is returned. This is called the tree root, and **it will exist
even if the tree is conceptually considered as unrooted**. This is,
the root node can be considered as the master node, since it
represents the whole tree structure. Unrooted trees can be identified
as trees in which master root node has more than two children.

::

  from ete_dev import Tree
  unrooted_tree = Tree( "(A,B,(C,D));" )
  print unrooted_tree
  #
  #     /-A      
  #    |         
  #----|--B      
  #    |           
  #    |     /-C   
  #     \---|      
  #          \-D 

  rooted_tree = Tree( "((A,B).(C,D));" )
  print rooted_tree                     
  #
  #          /-A
  #     /---|
  #    |     \-B
  #----|
  #    |     /-C
  #     \---|
  #          \-D




Browsing trees
=================

One of the most basic operations for tree analysis is *tree
browsing*. This is, essentially, visiting nodes within a tree. ETE
provides a number of methods to search for specific nodes or to
navigate over the hierarchical structure of a tree.


Getting Leaves, Descendants and Node's Relatives
------------------------------------------------

Any tree instance contains several functions to access its
descendants. This can be done in a single step (**get_** methods) or
by iteration (**iter_** methods, recommended when trees are very
large). Available methods are self explanatory:

.. table:: Browsing method

  =======================================  ==================================================================================================
  method                                   Description
  =======================================  ==================================================================================================
  :func:`TreeNode.iter_descendants`             Iterates over all descendant nodes excluding the root node tree in postorder way 
  :func:`TreeNode.iter_leaves`                  Iterates only over leaf nodes
  :func:`TreeNode.get_descendants`              Returns the list of nodes under tree
  :func:`TreeNode.get_leaves`                   Returns the list leaf nodes under tree
  :func:`TreeNode.get_leaf_names`               Returns the list leaf names under tree
  :func:`TreeNode.get_children`                 Returns the list of first level children nodes of tree
  :func:`TreeNode.get_sisters`                  Returns the list of sister branches/nodes
  =======================================  ==================================================================================================


Finding nodes by their attributes
------------------------------------

Both terminal and internal nodes can be located by searching along the
tree structure. You can find, for instance, all nodes matching a given
name.  However, any node's attribute can be used as a filter to find
nodes.

In addition, ETE implements a built-in method to find the **first node
matching a given name**, which is one of the most common tasks needed
for tree analysis.  This can be done using a special syntaxis: ``node
& "name"``. Thus, ``Tree&"A"`` will always return the first leaf node
whose name is "A" (even if there are mode "A" nodes) in the same tree.

Other methods are also available that restrict search criteria.

.. table:: 

  ==========================================       ==============================================================================================================
  method                                            Description
  ==========================================       ==============================================================================================================
  t.search_nodes(attr=value)                        Returns a list of nodes in which attr is equal to value, i.e. name=A
  t.iter_search_nodes(attr=value)                   Iterates over all matching nodes matching attr=value. Faster when you only need to get the first occurrence
  t.get_leaves_by_name(name)                        Returns a list of leaf nodes matching a given name. Only leaves are browsed.
  t.get_common_ancestor(node1, node2, node3)        Return the first internal node grouping node1, node2 and node3
  t&"A"                                             Shortcut for t.search_nodes(name="A")[0]
  ==========================================       ==============================================================================================================


A custom list of nodes matching a given name can be easily obtain
through the :func:`TreeNode.search_node` function.

::
 
   from ete_dev import Tree
   t = Tree( '((H:1,I:1):0.5, A:1, (B:1,(C:1,D:1):0.5):0.5);' )
   print t
   #                    /-H
   #          /--------|
   #         |          \-I
   #         |
   #---------|--A
   #         |
   #         |          /-B
   #          \--------|
   #                   |          /-C
   #                    \--------|
   #                              \-D

   # I get D
   D = t.search_nodes(name="D")[0]

   # I get all nodes with distance=0.5
   nodes = t.search_nodes(dist=0.5)
   print len(nodes), "nodes have distance=0.5"

   # We can limit the search to leaves and node names (faster method).
   D = t.get_leaves_by_name(name="D")
   print D


Searching for the first common ancestor of a given set of nodes it is
a handy way of finding internal nodes.

::

  from ete_dev import Tree
  t = Tree( '((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:0.5,(J:1.3, (F:1.2, D:0.1):0.5):0.5):0.5):0.5);' )
  print t
  ancestor = t.get_common_ancestor("C", "J", "B")
  


A limitation of the :func:`TreeNode.search_nodes` method is that you cannot use
complex conditional statements to find specific nodes.  When search
criteria is too complex, you may need to create your own search
function.

::

  from ete_dev import Tree

  def search_by_size(node, size):
      "Finds nodes with a given number of leaves"
      matches = []
      for n in node.traverse(): 
         if len(n) == size: 
            matches.append(n)
      return matches

  t = Tree()
  t.populate(40)
  # returns nodes containing 6 leaves
  search_by_size(t, size=6) 


Traversing (browsing) trees
---------------------------


Often, when processing trees, all nodes need to be visited. This is
called tree traversing. There are different ways to traverse a tree
structure depending on the order in which children nodes are
visited. ETE implements the two most common strategies: **pre-** and
**post-order**. The following scheme shows the differences in the
strategy for visiting nodes (note that in both cases the whole tree is
browsed):

* preorder: 1)Visit the root, 2) Traverse the left subtree , 3) Traverse the right subtree.
* postorder: 1) Traverse the left subtree , 2) Traverse the right subtree, 3) Visit the root 
* levelorder (default): every node on a level before is visited going to a lower level 


.. note::

    * Preorder traversal sequence: F, B, A, D, C, E, G, I, H (root, left, right)
    * Inorder traversal sequence: A, B, C, D, E, F, G, H, I (left, root, right); note how this produces a sorted sequence
    * Postorder traversal sequence: A, C, E, D, B, H, I, G, F (left, right, root)
    * Level-order traversal sequence: F, B, G, A, D, I, C, E, H

Every node in a tree includes a :func:`TreeNode.traverse` method, which can be
used to visit, one by one, every node node under the current
partition. In addition, the :func:`TreeNode.iter_descendants` method can be set
to use either a post- or a preorder strategy.  The only different
between :func:`TreeNode.traverse` and :func:`TreeNode.iter_descendants` is that the
first will include the root node in the iteration.


.. table:: 

  ==========================================  ==============================================================================================================
   Method                                       Description
  ==========================================  ==============================================================================================================
   :attr:`node.traverse(method)`               Iterates over the whole tree structure, yielding internal and external nodes, as well as the root node
   :attr:`node.iter_descendants(method)`       Iterates over all descendants except the root node, yielding internal and external nodes. 
  ==========================================  ==============================================================================================================

**method** can take one of the following values: ``"postorder"`` or ``"preorder"``

Additionally, you can implement your own traversing function using the
structural attributes of nodes. In the following example, only nodes
between a given leaf and the tree root are visited.

.. warning::
   Example missing, sorry


Iterating instead of Getting
----------------------------

As commented previously, methods starting with **get_** are all
prepared to return results as a closed list of items. This means, for
instance, that if you want to process all tree leaves and you ask for
them using the **get_leaves()** method, the whole tree structure will
be browsed before returning the final list of terminal nodes.  This is
not a problem in most of the cases, but in large trees, you can speed
up the browsing process by using iterators.

Most **get_** methods have their homologous iterator functions. Thus,
:func:`TreeNode.get_leaves` could be substituted by :func:`TreeNode.iter_leaves`. The same
occurs with :func:`TreeNode.iter_descendants` and :func:`TreeNode.iter_search_nodes`.

When iterators are used (note that is only applicable for looping),
only one step is processed at a time. For instance,
:func:`TreeNode.iter_search_nodes` will return one match in each iteration. In
practice, this makes no differences in the final result, but it may
increase the performance of loop functions (i.e. in case of finding a
match which interrupts the loop).























Node annotation
=========================

Every node contains three basic attributes: name, branch length and
branch support. These three values are encoded in the newick format.
However, any extra data could be linked to trees. This is called tree
annotation.

The :func:`TreeNode.add_feature` and :func:`TreeNode.add_features`
methods allow to add extra attributes (features) to any node.  The
first allows to add one one feature at a time, while the second can be
used to add many features with the same call.

::
 
  from ete_dev import Tree
  t = Tree( "((a,b),c);" )
  

:func:`TreeNode.del_feature` can be used to delete an attribute.

Once extra features are added, you can access their values at any time
during the analysis of a tree. To do so, you only need to access to
the ``node.feature_name`` attribute. Let's see this with some
examples:

.. warning::
   example missing, sorry

Unfortunately, newick format does not support adding extra features to
a tree.  Because of this drawback, several improved formats haven been
(or are being) developed to read and write tree based
information. Some of these new formats are based in a completely new
standard (PhyloXML, NeXML), while others are extensions of the
original newick formar (NHX
http://phylosoft.org/NHX/http://phylosoft.org/NHX/). Currently, ETE
includes support for the New Hampshire eXtended format (NHX), which
uses the original newick standard and adds the possibility of saving
additional date related to each tree node. Here is an example of a
extended newick representation in which extra information is added to
an internal node:

As you can notice, extra node features in the NHX format are enclosed
between brackets. ETE is able to read and write features using such
format, however, the encoded information is expected to be dumped as
plain text.


The NHX format is automatically detected when reading a newick file,
and the detected node features are added using the
:func:`TreeNode.add_feature` method.  Consequently, you can access the
information by using the normal ETE's feature notation:
``node.feature_name``. Similarly, features added to a tree can
be included within the normal newick representation using the NHX
notation. For this, you can call the :func:`TreeNode.write` method
using the :attr:`features` argument, which is expected to be a list
with the features names that you want to include in the newick
string. Note that all nodes containing the suplied features will be
exposed into the newick string. Use an empty features list
(:attr:`features=[ ]`) to include all node's data into the newick
string.


.. _sec:modifying-tree-topology:

Modifying Tree Topology
=======================


Creating Trees from Scratch
---------------------------

If no arguments are passed to the **Tree** class constructor, an empty tree node
will be returned. Then, you can use such an orphan node to populate a tree from
scratch. For this, you should never manipulate the **up**, and** children
**attributes of a node (unless it is strictly necessary). Instead, you must use
the methods created to this end. **add_child()**, **add_sister()**, and
**populate()** are the most common methods to create a tree structure. While the
two first adds one node at a time, populate() is able to create a custom number
of random nodes. This is useful to quickly create random trees.


Deleting (eliminating) and Removing (detaching) nodes
-----------------------------------------------------

As currently implemented, there is a difference between removing or deleting a
node. The former (removing) detaches a node's partition from the tree structure,
so all its descendants are also disconnected from the tree. There are two
methods to perform this action: **node.remove_child(ch)** and
**child.detach()**. In contrast, deleting a node means eliminating such node
without affecting its descendants. Children from the deleted node are
automatically connected to the next possible parent. This is better understood
with the following example:


Pruning trees
=============

Pruning a tree means to obtain the topology that connects a certain group of
items by removing the unnecessary edges. To facilitate this task, ETE implements
the **prune()** method, which can be used in two different ways: by providing
the list of terminal nodes that must be kept in the tree; or by providing a list
of nodes that must be removed. In any case, the result is a pruned tree
containing the topology that connects a custom set of nodes.


Concatenating trees
===================

Given that all tree nodes share the same basic properties, they can be connected
freely. In fact, any node can add a whole subtree as a child, so we can actually
*cut & paste* partitions. To do so, you only need to call the **add_child()
**method using another tree node as a first argument. If such a node is the root
node of a different tree, you will concatenate two structures. But caution!!,
this kind of operations may result into circular tree structures if add an
node's ancestor as a new node's child. Some basic checks are internally
performed by the ETE topology related methods, however, a fully qualified check
of this issue would affect seriously to the performance of the program. For this
reason, users should take care about not creating circular structures by
mistake.


.. _sec:tree-rooting:

Tree Rooting
============

Tree rooting is understood as the technique by with a given tree is conceptually
polarized from more basal to more terminal nodes. In phylogenetics, for
instance, this a crucial step prior to the interpretation of trees, since it
will determine the evolutionary relationships among the species involved. The
concept of rooted trees is different than just having a root node, which is
always necessary to handle a tree data structure. Usually, the way in which a
tree is differentiated between rooted and unrooted, is by counting the number of
branches of the current root node. Thus, if the root node has more than two
child branches, the tree is considered unrooted. By contrast, when only two main
branches exist under the root node, the tree is considered rooted. Having an
unrooted tree means that any internal branch within the tree could be regarded
as the root node, and there is no conceptual reason to place the root node where
it is placed at the moment. Therefore, in an unrooted tree, there is no
information about which internal nodes are more basal than others. By setting
the root node between a given edge/branch of the tree structure the tree is
polarized, meaning that the two branches under the root node are the most basal
nodes. In practice, this is usually done by setting an **outgroup** **node**,
which would represent one of these main root branches. The second one will be,
obviously, the brother node. When you set an outgroup on unrooted trees, the
multifurcations at the current root node are solved.

In order to root an unrooted tree or re-root a tree structure, ETE implements
the **set_outgroup()** method, which is present in any tree node instance.
Similarly, the **unroot()** method can be used to perform the opposite action.

Note that although **rooting** is usually regarded as a whole-tree operation,
ETE allows to root subparts of the tree without affecting to its parent tree
structure.


Working with branch distances
=============================

The branch length between one node an its parent is encoded as the **node.dist**
attribute. Together with tree topology, branch lengths define the relationships
among nodes.


Getting distances between nodes
-------------------------------

The **get_distance()** method can be used to calculate the distance between two
connected nodes. There are two ways of using this method: a) by querying the
distance between two descendant nodes (two nodes are passed as arguments) b) by
querying the distance between the current node and any other relative node
(parental or descendant).

Additionally to this, ETE incorporates two more methods to calculate the most
distant node from a given point in a tree. You can use the
**get_farthest_node()** method to retrieve the most distant point from a node
within the whole tree structure. Alternatively, **get_farthest_leaf()** will
return the most distant descendant (always a leaf). If more than one node
matches the farthest distance, the first occurrence is returned.

Distance between nodes can also be computed as the number of nodes between them
(considering all branch lengths equal to 1.0). To do so, the **topology_only**
argument must be set to **True **for all the above mentioned methods.


.. _sub:getting-midpoint-outgroup:

getting midpoint outgroup
-------------------------

In order to obtain a balanced rooting of the tree, you can set as the tree
outgroup that partition which splits the tree in two equally distant clusters
(using branch lengths). This is called the midpoint outgroup.

The **get_midpoint_outgroup()** method will return the outgroup partition that
splits current node into two balanced branches in terms of node distances.


.. _cha:the-programmable-tree:

:Author: Jaime Huerta-Cepas
