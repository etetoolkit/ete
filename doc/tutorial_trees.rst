:Author: Jaime Huerta-Cepas
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

The height of a node is the length of the longest downward path to a leaf from
that node. The height of the root is the height of the tree. The depth of a node
is the length of the path to its root (i.e., its root path).

* The topmost node in a tree is called the root node. Being the topmost node,
  the root node will not have parents. It is the node at which operations on the
  tree commonly begin (although some algorithms begin with the leaf nodes and work
  up ending at the root). All other nodes can be reached from it by following
  edges or links. Every node in a tree can be seen as the root node of the subtree
  rooted at that node.

* Nodes at the bottommost level of the tree are called leaf nodes. Since they
  are at the bottommost level, they do not have any children.

* An internal node or inner node is any node of a tree that has child nodes and
  is thus not a leaf node.

* A subtree is a portion of a tree data structure that can be viewed as a
  complete tree in itself. Any node in a tree T, together with all the nodes below
  it, comprise a subtree of T. The subtree corresponding to the root node is the
  entire tree; the subtree corresponding to any other node is called a proper
  subtree (in analogy to the term proper subset).

In bioinformatics, trees are the result of many analyses, such as phylogenetics
or clustering. Although each case entails specific considerations, many
properties remains constant among them. The Environment for Tree Exploration is
a python toolkit that assists in the automated manipulation, analysis and
visualization of hierarchical trees. Besides general tree handling options, ETEs
current version provides specific methods to analyze phylogenetic and clustering
trees. Moreover a programmable tree drawing engine is implemented that can be
used to automatize the graphical rendering of trees with customized node-
specific visualizations.


Understanding Tree Topology
===========================

A tree is a succession of TreeNodes connected in a hierarchical way. Therefore,
the topology of a tree is defined by the connections of its nodes. Each node
instance has two basic attributes: **node.up** and **node.children**. Up is a
pointer to the parent's node, while children is the list of nodes hanging for
the current node instance. Although it is possible to modify the structure of a
tree by changing these attributes, we strongly recommend not to do it. Several
methods are provided to manipulate each node's connections in a safe way (see
:ref:`sec:modifying-tree-topology`). Other three attributes are always present
in a tree node instance: i) **node.support**, which stores the branch support of
the partition defined by a given node (i.e. bootstrap value) ii) **node.dist**,
which stores the branch length/distance from a given node to its parent iii) and
**node.name**, which stores the node's name. Thus, a tree is internally encoded
as a succession of node instances connected in a hierarchical way. Given that
all nodes in a tree are the same type, any node of the tree contains the same
basic methods and attributes.

When a tree is loaded, a pointer to the top-most node is returned. This is
called the tree root, and it exists even if the tree is considered as
theoretically unrooted. The root node can be considered as the master tree node,
since it represents the whole tree structure. Internal an terminal nodes (all
hanging from the master node) represent different partitions of the tree, and
therefore can be used to access or manipulate all the possible sub-trees within
a general tree structure. Thus, once a tree is loaded, it can be split in
different subparts that will function as independent trees instances.

In order to evaluate the basic attributes of a node, you can use the following
methods:** tree.is_leaf(), **returns True if node has no children;
**tree.is_root()**, returns True if node has no parent; **len(node)**, returns
the number of terminal nodes (leaves) under a given internal node; and
**len(node.children)**, returns the number of node's children. Additionally tree
node instances can be queried or iterated as normal built-in python objects. For
example, the following operations are allowed i)** [for leaf in node if
leaf.dist>0.5]** ii)** if leaf in node: print "true" **iii)** print tree**. The
following example illustrates some basic things we can do with trees:


Reading and Writing Newick Trees
================================

The Newick format is the standard representation of trees in computer science.
It uses nested parentheses to represent hierarchical data structures as text
strings. The original newick standard is able to encode information about the
tree topology, branch distances and node names. However different variants of
this format are used by different programs. ETE supports many of these formats
both for reading and writing operations. Currently, this is the list of
supported newick formats:

Formats labeled as** flexible **allow missing information. For instance, format
0 will be able to load a newick tree even if they not contain branch support
information (it will be initialized with the default value), however, format 2
will rise a parsing error. If you want to control that your newick files
strictly follow a given pattern you should use **strict** format definitions.

Reading newick trees
-----------------------

In order to load a tree from a newick text string you can use the constructor
**Tree()**,** **provided by the main module **ete2**. You only need to pass a
text string containing the newick structure and the format that should be used
to parse it (0 by default). Alternatively, you can pass the path to a text file
containing the newick string.

Writing newick trees
-----------------------

Any ETE tree can be exported to the newick standard. To do it, you must call the
method **write(),** present in any Tree node instance, and choose the preferred
format (0 by default). This method will return the text string representing a
given tree. You can also specify an output file.


Some Basis on ETE's trees
=========================

Once loaded into the Environment for Tree Exploration, trees can be manipulated
as normal python objects. Given that a tree is actually a collection of nodes
connected in a hierarchical way, what you usually see as a tree will be the root
node instance from which the tree structure is hanging. However, every node
within a ETE's tree structure can be also considered a subtree. This means, for
example, that all the operational methods that we will review in the following
sections are available at any possible level within a tree. Moreover, this
feature will allow you to separate large trees into smaller partitions, or
concatenate several trees into a single structure.


Browsing trees
==============

One of the most basic operations related with tree analysis is tree browsing,
which is, essentially, the task of visiting nodes within a tree. In order to
facilitate this, ETE provides a number of methods to search for specific nodes
or to navigate over the hierarchical structure of a tree.


Getting leaves, Descendants and Node's Relatives
------------------------------------------------

The list of internal or leaf nodes within a given partition can be obtained by
using the **get_leaves()** and **get_descendants()** methods. The former will
return the list of terminal nodes (leaves) under a given internal node, while
**get_descendants()** will return the list of all nodes (terminal and internal)
under a given tree node. You can iterate over the returned list of nodes or
filter those meeting certain properties.

In addition, other methods are available to find nodes according to their
hierarchical relationships, namely: **get_sisters() **,** get_children() **and
**get_common_ancestor()**. Note that get_children returns an independent list of
children rather than the **node.children** attribute. This allows you to operate
with such list without affecting the integrity of the tree. The
**get_common_ancestor()** method is specially useful for finding internal nodes,
since it allows to search for the first internal node that connects several leaf
nodes.


Traversing (browsing) trees
---------------------------

Often, when processing trees, all nodes need to be visited. This is called tree
traversing. There are different ways to traverse a tree structure depending on
the order in which children nodes are visited. ETE implements the two most
common strategies: **pre- **and** post-order**. The following scheme shows the
differences in the strategy for visiting nodes (note that in both cases the
whole tree is browsed):

* preorder

* Visit the root.

* Traverse the left subtree.

* Traverse the right subtree.

* postorder

* Traverse the left subtree.

* Traverse the right subtree.

* Visit the root.

Every node in a tree includes a **traverse() **method, which can be used to
visit, one by one, every node node under the current partition.

Additionally, you can implement your own traversing function using the
structural attributes of nodes. In the following example, only nodes between a
given leaf and the tree root are visited.


.. _sub:finding-nodes-by:

Finding Nodes by Their Attributes
---------------------------------

Both terminal and internal nodes can be located by searching along the tree
structure. You can find, for instance, all nodes matching a given name. The
**search_nodes()** method is the most direct way to find specific nodes. Given
that every node has its own **search_nodes** method, you can start your search
from different points of the tree. Any node's attribute can be used as a filter
to find nodes.

A limitation of this method is that you cannot use complex conditional
statements to find specific nodes. However you can user traversing methods to
meet your custom filters. A possible general strategy would look like this:

Finally, ETE implements a built-in method to find the **first node matching a
given name**, which is one of the most common tasks needed for tree analysis.
This can be done through the operator **&** (AND). Thus, **MyTree&"A" **will
always return the first node whose name is "A" and that is under the tree
"MyTree". The syntaxis may seem confusing, but it can be very useful in some
situations.


Iterating instead of Getting
----------------------------

Methods starting with **get_** are all prepared to return results as a closed
list of items. This means, for instance, that if you want to process all tree
leaves and you ask for them using the **get_leaves()** method, the whole tree
structure will be browsed before returning the final list of terminal nodes.
This is not a problem in most of the cases, but in large trees, you can speed up
the browsing process by using iterators.

Most **get_-like** methods have their homologous iterator function. Thus,
**get_leaves()** can sometimes be substituted by **iter_leaves()**. The same
occurs with **iter_descendants()** and **iter_search_nodes().**

When iterators are used (note that is only applicable for looping), only one
step is processed at a time. For example, **iter_search_nodes()** will return
one match in each iteration. In practice, this makes no differences in the final
result, but it may increase the performance of loop functions (i.e. in case of
finding a match which interrupts the loop).


.. _sec:extending-node's-features:

Extending Node's Features
=========================

Although newick standard was only thought to contain branch lengths and node
names information, the truth is that many other features are usually required to
be linked to the different tree nodes. ETE allows to associated any kind of
extra information to the tree nodes. Extra information can be regarded as a
single numeric value, a text label or even as a reference to a more complex
python structure (i.e. lists, dictionaries or any other python object). Thus,
for example, with ETE it is possible to have fully annotated trees. The methods
**add feature()**,** add_features()** and** del_feature()** are prepared to
handle the task of adding and deleting information to a given node.

Once extra features are added, you can access their values at any time during
the analysis of a tree. To do so, you only need to access to the
**node.featurename** attributes. Let's see this with some examples:

Unfortunately, newick format does not support adding extra features to a tree.
Because of this drawback, several improved formats haven been (or are being)
developed to read and write tree based information. Some of these new formats
are based in a completely new standard (PhyloXML, NeXML), while others are
extensions of the original newick formar (NHX
http://phylosoft.org/NHX/http://phylosoft.org/NHX/). Currently, ETE includes
support for the New Hampshire eXtended format (NHX), which uses the original
newick standard and adds the possibility of saving additional date related to
each tree node. Here is an example of a extended newick representation in which
extra information is added to an internal node:

As you can notice, extra node features in the NHX format are enclosed between
brackets. ETE is able to read and write features using such format, however, the
encoded information is expected to be text-formattable. In the future, support
for more advanced formats such as PhyloXML will be included.

The NHX format is automatically detected when reading a newick file, and the
detected node features are added using the "**add_feature()**" method.
Consequently, you can access the information by using the normal ETE's feature
notation: **node.featurename**. Similarly, features added to a tree can be
included within the normal newick representation using the NHX notation. For
this, you can call the **write() **method using the **features **argument, which
is expected to be a list with the features names that you want to include in the
newick string. Note that all nodes containing the suplied features will be
exposed into the newick string. Use an empty features list (**features=[ ]**) to
include all node's data into the newick string.


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
