.. module:: ete2
  :synopsis: provides main objects and modules

.. moduleauthor:: Jaime Huerta-Cepas
.. currentmodule:: ete2

Working With Tree Data Structures
************************************

.. contents::

Trees
==========

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

Reading and Writing Newick Trees
================================

The Newick format is one of the most widely used standard
representation of trees in bioinformatics. It uses nested parentheses
to represent hierarchical data structures as text strings. The
original newick standard is able to encode information about the tree
topology, branch distances and node names. Nevertheless, it is not
uncommon to find slightly different formats using the newick standard.

ETE can read and write many of them: 

.. table::

  ======  ============================================== =========================================================================================
  FORMAT  DESCRIPTION                                         SAMPLE
  ======  ============================================== =========================================================================================
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
  ======  ============================================== =========================================================================================

Formats labeled as *flexible* allow for missing information. For
instance, format 0 will be able to load a newick tree even if it does
not contain branch support information (it will be initialized with
the default value). However, format 2 would raise an exception.  In
other words, if you want to control that your newick files strictly
follow a given pattern you should use **strict** format definitions.


Reading newick trees
-----------------------

In order to load a tree from a newick text string you can use the
constructor :class:`TreeNode` or its :class:`Tree` alias, provided by the main module
:mod:`ete2`. You will only need to pass a text string containing
the newick structure and the format that should be used to parse it (0
by default). Alternatively, you can pass the path to a text file
containing the newick string.

::
 
  from ete2 import Tree
   
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
(:ref:`sec:newick-formats`), so you can use the same function to
convert between newick formats.

::
   
  from ete2 import Tree
   
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

  from ete2 import Tree
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

  from ete2 import Tree
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




Browsing trees (traversing)
=================================

One of the most basic operations for tree analysis is *tree
browsing*. This is, essentially, visiting nodes within a tree. ETE
provides a number of methods to search for specific nodes or to
navigate over the hierarchical structure of a tree.




Getting Leaves, Descendants and Node's Relatives
------------------------------------------------

TreeNode instances contain several functions to access their
descendants. Available methods are self explanatory:

.. autosummary::  

   :signatures:
   TreeNode.get_descendants
   TreeNode.get_leaves    
   TreeNode.get_leaf_names
   TreeNode.get_children
   TreeNode.get_sisters


Traversing (browsing) trees
---------------------------


Often, when processing trees, all nodes need to be visited. This is
called tree traversing. There are different ways to traverse a tree
structure depending on the order in which children nodes are
visited. ETE implements the three most common strategies:
**preorder**, **levelorder** and **postorder**. The following scheme
shows the differences in the strategy for visiting nodes (note that in
both cases the whole tree is browsed):

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


.. autosummary::

   :signature:
   TreeNode.traverse
   TreeNode.iter_descendants
   TreeNode.iter_leaves

**strategy** can take one of the following values: ``"postorder"``, ``"preorder"`` or  ``"levelorder"``

::

   # we load a tree
   t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);', format=1)
    
   for node in t.traverse("postorder"):
     # Do some analysis on node
     print node.name
     
   # If we want to iterate over a tree excluding the root node, we can
   # use the iter_descendant method
   for node in t.iter_descendants("postorder"):
     # Do some analysis on node
     print node.name


Additionally, you can implement your own traversing function using the
structural attributes of nodes. In the following example, only nodes
between a given leaf and the tree root are visited.

::

   from ete2 import Tree
   tree = Tree( "(A:1,(B:1,(C:1,D:1):0.5):0.5);" )
    
   # Browse the tree from a specific leaf to the root
   node = t.search_nodes(name="C")[0]
   while node:
      print node
      node = node.up   


Advanced traversing (stopping criteria)
-----------------------------------------

.. _is_leaf_fn:

Collapsing nodes while traversing (custom is_leaf definition)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From version 2.2, ETE supports the use of the :attr:`is_leaf_fn`
argument in most of its traversing functions. The value of
:attr:`is_leaf_fn` is expected to be a pointer to any python function
that accepts a node instance as its first argument and returns a
boolean value (True if node should be considered a leaf node).

By doing so, all traversing methods will use such a custom function to
decide if a node is a leaf. This becomes specially useful when dynamic
collapsing of nodes is needed, thus avoiding to prune the same tree in
many different ways.

For instance, given a large tree structure, the following code will
export the newick of the pruned version of the topology, where nodes
grouping the same tip labels are collapsed.

:: 

  from ete2 import Tree
  def collapsed_leaf(node):
      if len(node2labels[node]) == 1:
         return True
      else:
         return False

  t = Tree("((((a,a,a)a,a)aa, (b,b)b)ab, (c, (d,d)d)cd);", format=1)
  print t
  # We create a cache with every node content 
  node2labels = t.get_cached_content(store_attr="name")
  print t.write(is_leaf_fn=collapsed_leaf)
  #             /-a
  #            |
  #          /-|--a
  #         |  |
  #       /-|   \-a
  #      |  |
  #    /-|   \-a
  #   |  |
  #   |  |   /-b
  # --|   \-|
  #   |      \-b
  #   |
  #   |   /-c
  #    \-|
  #      |   /-d
  #       \-|
  #          \-d

  # We can even load the collapsed version as a new tree
  t2 = Tree( t.write(is_leaf_fn=collapsed_leaf) )
  print t2
  #       /-aa
  #    /-|
  #   |   \-b
  # --|
  #   |   /-c
  #    \-|
  #       \-d


Another interesting use of this approach is to find the first matching
nodes in a given tree that match a custom set of criteria, without
browsing the whole tree structure.

Let's say we want get all deepest nodes in a tree whose branch length
is larger than one:
:: 

  from ete2 import Tree
  t = Tree("(((a,b)ab:2, (c, d)cd:2)abcd:2, ((e, f):2, g)efg:2);", format=1)
  def processable_node(node):
      if node.dist > 1: 
         return True
      else:
         return False

  for leaf in t.iter_leaves(is_leaf_fn=processable_node):
      print leaf

  #       /-a
  #    /-|
  #   |   \-b
  # --|
  #   |   /-c
  #    \-|
  #       \-d
  #  
  #       /-e
  #    /-|
  # --|   \-f
  #   |
  #    \-g


Iterating instead of Getting
------------------------------

As commented previously, methods starting with **get_** are all
prepared to return results as a closed list of items. This means, for
instance, that if you want to process all tree leaves and you ask for
them using the :func:`TreeNode.get_leaves` method, the whole tree
structure will be browsed before returning the final list of terminal
nodes.  This is not a problem in most of the cases, but in large
trees, you can speed up the browsing process by using iterators.

Most **get_** methods have their homologous iterator functions. Thus,
:func:`TreeNode.get_leaves` could be substituted by :func:`TreeNode.iter_leaves`. The same
occurs with :func:`TreeNode.iter_descendants` and :func:`TreeNode.iter_search_nodes`.

When iterators are used (note that is only applicable for looping),
only one step is processed at a time. For instance,
:func:`TreeNode.iter_search_nodes` will return one match in each
iteration. In practice, this makes no differences in the final result,
but it may increase the performance of loop functions (i.e. in case of
finding a match which interrupts the loop).


Finding nodes by their attributes
------------------------------------

Both terminal and internal nodes can be located by searching along the
tree structure. Several methods are available:

.. table:: 

  ==============================================       ==============================================================================================================
  method                                                Description
  ==============================================       ==============================================================================================================
  t.search_nodes(attr=value)                            Returns a list of nodes in which attr is equal to value, i.e. name=A
  t.iter_search_nodes(attr=value)                       Iterates over all matching nodes matching attr=value. Faster when you only need to get the first occurrence
  t.get_leaves_by_name(name)                            Returns a list of leaf nodes matching a given name. Only leaves are browsed.
  t.get_common_ancestor([node1, node2, node3])          Return the first internal node grouping node1, node2 and node3
  t&"A"                                                 Shortcut for t.search_nodes(name="A")[0]
  ==============================================       ==============================================================================================================


Search_all nodes matching a given criteria
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A custom list of nodes matching a given name can be easily obtain
through the :func:`TreeNode.search_node` function.

::
 
   from ete2 import Tree
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



Search nodes matching a given criteria (iteration)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A limitation of the :func:`TreeNode.search_nodes` method is that you cannot use
complex conditional statements to find specific nodes.  When search
criteria is too complex, you may need to create your own search
function.

::

  from ete2 import Tree

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

Find the first common ancestor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Searching for the first common ancestor of a given set of nodes it is
a handy way of finding internal nodes.

::

  from ete2 import Tree
  t = Tree( "((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:0.5,(J:1.3, (F:1.2, D:0.1):0.5):0.5):0.5):0.5);" )
  print t
  ancestor = t.get_common_ancestor("C", "J", "B")
  


Custom searching functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A limitation of the previous methods is that you cannot use complex
conditional statements to find specific nodes. However you can user
traversing methods to meet your custom filters. A possible general
strategy would look like this:

::

  from ete2 import Tree
  t = Tree("((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:1,D:1):0.5):0.5);")
  # Create a small function to filter your nodes
  def conditional_function(node):
      if node.dist > 0.3:
          return True
      else:
          return False
   
  # Use previous function to find matches. Note that we use the traverse
  # method in the filter function. This will iterate over all nodes to
  # assess if they meet our custom conditions and will return a list of
  # matches.
  matches = filter(conditional_function, t.traverse())
  print len(matches), "nodes have ditance >0.3"
   
  # depending on the complexity of your conditions you can do the same
  # in just one line with the help of lambda functions:
  matches = filter(lambda n: n.dist>0.3 and n.is_leaf(), t.traverse() )
  print len(matches), "nodes have ditance >0.3 and are leaves"


Shortcuts 
^^^^^^^^^^^^

Finally, ETE implements a built-in method to find the first node
matching a given name, which is one of the most common tasks needed
for tree analysis. This can be done through the operator &
(AND). Thus, TreeNode&”A” will always return the first node whose name
is “A” and that is under the tree “MyTree”. The syntaxis may seem
confusing, but it can be very useful in some situations.

::

  from ete2 import Tree
  t = Tree("((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:1,(J:1, (F:1, D:1):0.5):0.5):0.5):0.5);")
  # Get the node D in a very simple way
  D = t&"D"
  # Get the path from B to the root
  node = D
  path = []
  while node.up:
    path.append(node)
    node = node.up
  print t
  # I substract D node from the total number of visited nodes
  print "There are", len(path)-1, "nodes between D and the root"
  # Using parentheses you can use by-operand search syntax as a node
  # instance itself
  Dsparent= (t&"C").up
  Bsparent= (t&"B").up
  Jsparent= (t&"J").up
  # I check if nodes belong to certain partitions
  print "It is", Dsparent in Bsparent, "that C's parent is under B's ancestor"
  print "It is", Dsparent in Jsparent, "that C's parent is under J's ancestor"

.. _check_monophyly:

Checking the monophyly of attributes within a tree
========================================================

Although monophyly is actually a phylogenetic concept used to refer to
a set of species that group exclusively together within a tree
partition, the idea can be easily exported to any type of trees. 

Therefore, we could consider that a set of values for a given node
attribute present in our tree is monophyletic, if such values group
exclusively together as a single tree partition. If not, the
corresponding relationship connecting such values (para or
poly-phyletic) could be also be inferred.


The :func:`TreeNode.check_monophyly` method will do so when a given
tree is queried for any custom attribute. 

:: 

  from ete2 import Tree
  t =  Tree("((((((a, e), i), o),h), u), ((f, g), j));")
  print t

  #                   /-a
  #                /-|
  #             /-|   \-e
  #            |  |
  #          /-|   \-i
  #         |  |
  #       /-|   \-o
  #      |  |
  #    /-|   \-h
  #   |  |
  #   |   \-u
  # --|
  #   |      /-f
  #   |   /-|
  #    \-|   \-g
  #      |
  #       \-j


  # We can check how, indeed, all vowels are not monophyletic in the
  # previous tree, but polyphyletic (a foreign label breaks its monophyly)
  print t.check_monophyly(values=["a", "e", "i", "o", "u"], target_attr="name")

  # however, the following set of vowels are monophyletic
  print t.check_monophyly(values=["a", "e", "i", "o"], target_attr="name")  

  # A special case of polyphyly, called paraphyly, is also used to
  # define certain type of grouping. See this wikipedia article for
  # disambiguation: http://en.wikipedia.org/wiki/Paraphyly
  print t.check_monophyly(values=["i", "o"], target_attr="name")    

Finally, the :func:`TreeNode.get_monophyletic` method is also
provided, which allows to return a list of nodes within a tree where a
given set of attribute values are monophyletic. Note that, although a
set of values are not monophyletic regarding the whole tree, several
independent monophyletic partitions could be found within the same
topology.

For instance, in the following example, all clusters within the same
tree exclusively grouping a custom set of annotations are obtained. 

:: 

   from ete2 import Tree
   t =  Tree("((((((4, e), i), o),h), u), ((3, 4), (i, june)));")
   # we annotate the tree using external data
   colors = {"a":"red", "e":"green", "i":"yellow", 
             "o":"black", "u":"purple", "4":"green",
             "3":"yellow", "1":"white", "5":"red", 
             "june":"yellow"}
   for leaf in t:
       leaf.add_features(color=colors.get(leaf.name, "none"))
   print t.get_ascii(attributes=["name", "color"], show_internal=False)

   #                   /-4, green
   #                /-|
   #             /-|   \-e, green
   #            |  |
   #          /-|   \-i, yellow
   #         |  |
   #       /-|   \-o, black
   #      |  |
   #    /-|   \-h, none
   #   |  |
   #   |   \-u, purple
   # --|
   #   |      /-3, yellow
   #   |   /-|
   #   |  |   \-4, green
   #    \-|
   #      |   /-i, yellow
   #       \-|
   #          \-june, yellow

   print "Green-yellow clusters:" 
   # And obtain clusters exclusively green and yellow
   for node in t.get_monophyletic(values=["green", "yellow"], target_attr="color"):
      print node.get_ascii(attributes=["color", "name"], show_internal=False)

   # Green-yellow clusters:
   #  
   #       /-green, 4
   #    /-|
   # --|   \-green, e
   #   |
   #    \-yellow, i
   #  
   #       /-yellow, 3
   #    /-|
   #   |   \-green, 4
   # --|
   #   |   /-yellow, i
   #    \-|
   #       \-yellow, june

.. note::

   When the target attribute is set to the "species" feature name,
   associated to any :class:`PhyloTree` node, this method will
   accomplish with the standard phylogenetic definition of monophyly,
   polyphyly and paraphyly.


.. _cache_node_content:

Caching tree content for faster lookup operations 
======================================================

If your program needs to access to the content of different nodes very
frequently, traversing the tree to get the leaves of each node over
and over will produce significant slowdowns in your algorithm.  From
version 2.2 ETE provides a convenient methods to cache frequent data. 

The method :func:`TreeNode.get_cached_content` returns a dictionary in
which keys are node instances and values represent the content of such
nodes. By default, content is understood as a list of leave nodes, so
looking up size or tip names under a given node will be
instant. However, specific attributes can be cached by setting a
custom :attr:`store_attr` value. 

::

   from ete2 import Tree
   t = Tree()
   t.populate(50)

   node2leaves = t.get_cached_content()

   # lets now print the size of each node without the need of
   # recursively traverse 
   for n in t.traverse():
       print "node %s contains %s tips" %(n.name, len(node2leaves[n]))
  

Node annotation
=========================

Every node contains three basic attributes: name
(:attr:`TreeNode.name`), branch length (:attr:`TreeNode.dist`) and
branch support (:attr:`TreeNode.support`). These three values are
encoded in the newick format.  However, any extra data could be linked
to trees. This is called tree annotation.

The :func:`TreeNode.add_feature` and :func:`TreeNode.add_features`
methods allow to add extra attributes (features) to any node.  The
first allows to add one one feature at a time, while the second can be
used to add many features with the same call.

Once extra features are added, you can access their values at any time
during the analysis of a tree. To do so, you only need to access to
the :attr:`TreeNode.feature_name` attributes.

Similarly, :func:`TreeNode.del_feature` can be used to delete an
attribute.

::
 
   import random
   from ete2 import Tree
   # Creates a tree
   t = Tree( '((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:0.5,(J:1.3, (F:1.2, D:0.1):0.5):0.5):0.5):0.5);' )

   # Let's locate some nodes using the get common ancestor method
   ancestor=t.get_common_ancestor("J", "F", "C")
   # the search_nodes method (I take only the first match )
   A = t.search_nodes(name="A")[0]
   # and using the shorcut to finding nodes by name
   C= t&"C"
   H= t&"H"
   I= t&"I"

   # Let's now add some custom features to our nodes. add_features can be
   # used to add many features at the same time.
   C.add_features(vowel=False, confidence=1.0)
   A.add_features(vowel=True, confidence=0.5)
   ancestor.add_features(nodetype="internal")

   # Or, using the oneliner notation
   (t&"H").add_features(vowel=False, confidence=0.2)

   # But we can automatize this. (note that i will overwrite the previous
   # values)
   for leaf in t.traverse():
      if leaf.name in "AEIOU":
         leaf.add_features(vowel=True, confidence=random.random())
      else:
         leaf.add_features(vowel=False, confidence=random.random())

   # Now we use these information to analyze the tree.
   print "This tree has", len(t.search_nodes(vowel=True)), "vowel nodes"
   print "Which are", [leaf.name for leaf in t.iter_leaves() if leaf.vowel==True]

   # But features may refer to any kind of data, not only simple
   # values. For example, we can calculate some values and store them
   # within nodes.
   #
   # Let's detect leaf nodes under "ancestor" with distance higher thatn
   # 1. Note that I'm traversing a subtree which starts from "ancestor"
   matches = [leaf for leaf in ancestor.traverse() if leaf.dist>1.0]

   # And save this pre-computed information into the ancestor node
   ancestor.add_feature("long_branch_nodes", matches)

   # Prints the precomputed nodes
   print "These are nodes under ancestor with long branches", \
      [n.name for n in ancestor.long_branch_nodes]

   # We can also use the add_feature() method to dynamically add new features.
   label = raw_input("custom label:")
   value = raw_input("custom label value:")
   ancestor.add_feature(label, value)
   print "Ancestor has now the [", label, "] attribute with value [", value, "]"  


Unfortunately, newick format does not support adding extra features to
a tree.  Because of this drawback, several improved formats haven been
(or are being) developed to read and write tree based
information. Some of these new formats are based in a completely new
standard (:doc:`tutorial_xml`), while others are extensions of the
original newick formar (NHX
http://phylosoft.org/NHX/http://phylosoft.org/NHX/).

Currently, ETE
includes support for the New Hampshire eXtended format (NHX), which
uses the original newick standard and adds the possibility of saving
additional date related to each tree node. Here is an example of a
extended newick representation in which extra information is added to
an internal node:

::

 (A:0.35,(B:0.72,(D:0.60,G:0.12):0.64[&&NHX:conf=0.01:name=INTERNAL]):0.56);

As you can notice, extra node features in the NHX format are enclosed
between brackets. ETE is able to read and write features using such
format, however, the encoded information is expected to be exportable
as plain text.

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
(:attr:`features=[]`) to include all node's data into the newick
string.

::
   
  import random
  from ete2 import Tree
  # Creates a normal tree
  t = Tree('((H:0.3,I:0.1):0.5, A:1,(B:0.4,(C:0.5,(J:1.3,(F:1.2, D:0.1):0.5):0.5):0.5):0.5);')
  print t
  # Let's locate some nodes using the get common ancestor method
  ancestor=t.get_common_ancestor("J", "F", "C")
  # Let's label leaf nodes
  for leaf in t.traverse():
      if leaf.name in "AEIOU":
        leaf.add_features(vowel=True, confidence=random.random())
      else:
        leaf.add_features(vowel=False, confidence=random.random())
   
  # Let's detect leaf nodes under "ancestor" with distance higher thatn
  # 1. Note that I'm traversing a subtree which starts from "ancestor"
  matches = [leaf for leaf in ancestor.traverse() if leaf.dist>1.0]
   
  # And save this pre-computed information into the ancestor node
  ancestor.add_feature("long_branch_nodes", matches)
  print
  print "NHX notation including vowel and confidence attributes"
  print
  print t.write(features=["vowel", "confidence"])
  print
  print "NHX notation including all node's data"
  print
   
  # Note that when all features are requested, only those with values
  # equal to text-strings or numbers are considered. "long_branch_nodes"
  # is not included into the newick string.
  print t.write(features=[])
  print
  print "basic newick formats are still available"
  print
  print t.write(format=9, features=["vowel"])
  # You don't need to do anything speciall to read NHX notation. Just
  # specify the newick format and the NHX tags will be automatically
  # detected.
  nw = """
  (((ADH2:0.1[&&NHX:S=human:E=1.1.1.1], ADH1:0.11[&&NHX:S=human:E=1.1.1.1])
  :0.05[&&NHX:S=Primates:E=1.1.1.1:D=Y:B=100], ADHY:0.1[&&NHX:S=nematode:
  E=1.1.1.1],ADHX:0.12[&&NHX:S=insect:E=1.1.1.1]):0.1[&&NHX:S=Metazoa:
  E=1.1.1.1:D=N], (ADH4:0.09[&&NHX:S=yeast:E=1.1.1.1],ADH3:0.13[&&NHX:S=yeast:
  E=1.1.1.1], ADH2:0.12[&&NHX:S=yeast:E=1.1.1.1],ADH1:0.11[&&NHX:S=yeast:E=1.1.1.1]):0.1
  [&&NHX:S=Fungi])[&&NHX:E=1.1.1.1:D=N];
  """
  # Loads the NHX example found at http://www.phylosoft.org/NHX/
  t = Tree(nw)
  # And access node's attributes.
  for n in t.traverse():
      if hasattr(n,"S"):
         print n.name, n.S


.. _sec:modifying-tree-topology:


.. _robinson_foulds:

Comparing Trees
=====================


Calculate distances between trees
-----------------------------------
.. versionadded 2.3


The :Tree:`compare` function allows to calculate distances between two trees
based on any node feature (i.e. name, species, other tags) using robinson-foulds
and edge compatibility distances. It automatically handles differences in tree
sizes, shared nodes and duplicated feature names.


- result["rf"] = robinson-foulds distance between the two trees. (average of
  robinson-foulds distances if target tree contained duplication and was split
  in several subtrees)
- result["max_rf"] = Maximum robinson-foulds distance expected for this comparison
- result["norm_rf"] = normalized robinson-foulds distance (from 0 to 1)
- result["effective_tree_size"] = the size of the compared trees, which are pruned to the common shared nodes. 
- result["ref_edges_in_source"] = compatibility score of the target tree with
  respect to the source tree (how many edges in reference are found in the
  source)
- result["source_edges_in_ref"] = compatibility score of the source tree with
  respect to the reference tree (how many edges in source are found in the
  reference)
- result["source_subtrees"] = number of subtrees in the source tree (1 if do not contain duplications)
- result["common_edges"] = a set of common edges between source tree and reference
- result["source_edges"] = the set of edges found in the source tree
- result["ref_edges"] = the set of edges found in the reference tree
- result["treeko_dist"] = TreeKO speciation distance for comparisons including duplication nodes. 




Robinson-foulds distance 
-------------------------------- 
.. versionadded 2.2


Two tree topologies can be compared using ETE and the Robinson-Foulds
(RF) metric. The method :func:`TreeNode.robinson_foulds` available for
any ETE tree node allows to:

 - compare two tree topologies by their name labels (default) or any
   other annotated feature in the tree. 

 - compare topologies of different size and content. When two trees
   contain a different set of labels, only shared leaves will be used.

 - examine size and content of matching and missing partitions. Since
   the method return the list of partitions found in both trees,
   details about matching partitions can be obtained easily. 

.. versionchanged 2.3 

  - allows to discard edges from the comparison based on their support value.
 
  - allows to automatically expand polytomies (multifurcations) in source and target trees.  

  - a command line tool providing most used features is available: `ete compare`


In the following example, several of above mentioned features are
shown:

::
 
  from ete2 import Tree
  t1 = Tree('(((a,b),c), ((e, f), g));')
  t2 = Tree('(((a,c),b), ((e, f), g));')
  rf, max_rf, common_leaves, parts_t1, parts_t2 = t1.robinson_foulds(t2)
  print t1, t2
  print "RF distance is %s over a total of %s" %(rf, max_rf)
  print "Partitions in tree2 that were not found in tree1:", parts_t1 - parts_t2
  print "Partitions in tree1 that were not found in tree2:", parts_t2 - parts_t1

  # We can also compare trees sharing only part of their labels

  t1 = Tree('(((a,b),c), ((e, f), g));')
  t2 = Tree('(((a,c),b), (g, H));')
  rf, max_rf, common_leaves, parts_t1, parts_t2 = t1.robinson_foulds(t2)

  print t1, t2
  print "Same distance holds even for partially overlapping trees"
  print "RF distance is %s over a total of %s" %(rf, max_rf)
  print "Partitions in tree2 that were not found in tree1:", parts_t1 - parts_t2
  print "Partitions in tree1 that were not found in tree2:", parts_t2 - parts_t1





Modifying Tree Topology
=======================

Creating Trees from Scratch
---------------------------

If no arguments are passed to the :class:`TreeNode` class constructor,
an empty tree node will be returned. Such an orphan node can be used
to populate a tree from scratch. For this, the :attr:`TreeNode.up`,
and :attr:`TreeNode.children` attributes should never be used (unless
it is strictly necessary). Instead, several methods exist to
manipulate the topology of a tree:


.. autosummary:: 

   :signature:
   TreeNode.populate
   TreeNode.add_child
   TreeNode.add_child
   TreeNode.delete 
   TreeNode.detach


::

  from ete2 import Tree
  t = Tree() # Creates an empty tree
  A = t.add_child(name="A") # Adds a new child to the current tree root
                             # and returns it
  B = t.add_child(name="B") # Adds a second child to the current tree
                             # root and returns it
  C = A.add_child(name="C") # Adds a new child to one of the branches
  D = C.add_sister(name="D") # Adds a second child to same branch as
                               # before, but using a sister as the starting
                               # point
  R = A.add_child(name="R") # Adds a third child to the
                             # branch. Multifurcations are supported
  # Next, I add 6 random leaves to the R branch names_library is an
  # optional argument. If no names are provided, they will be generated
  # randomly.
  R.populate(6, names_library=["r1","r2","r3","r4","r5","r6"])
  # Prints the tree topology
  print t
  #                     /-C
  #                    |
  #                    |--D
  #                    |
  #           /--------|                              /-r4
  #          |         |                    /--------|
  #          |         |          /--------|          \-r3
  #          |         |         |         |
  #          |         |         |          \-r5
  #          |          \--------|
  # ---------|                   |                    /-r6
  #          |                   |          /--------|
  #          |                    \--------|          \-r2
  #          |                             |
  #          |                              \-r1
  #          |
  #           \-B
  # a common use of the populate method is to quickly create example
  # trees from scratch. Here we create a random tree with 100 leaves.
  t = Tree()
  t.populate(100)



Deleting (eliminating) and Removing (detaching) nodes
-----------------------------------------------------

As currently implemented, there is a difference between detaching and
deleting a node. The former disconnects a complete partition from the
tree structure, so all its descendants are also disconnected from the
tree. There are two methods to perform this action:
:func:`TreeNode.remove_child` and :func:`TreeNode.detach`. In
contrast, deleting a node means eliminating such node without
affecting its descendants. Children from the deleted node are
automatically connected to the next possible parent. This is better
understood with the following example:

:: 

  from ete2 import Tree
  # Loads a tree. Note that we use format 1 to read internal node names
  t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);', format=1)
  print "original tree looks like this:"
  # This is an alternative way of using "print t". Thus we have a bit
  # more of control on how tree is printed. Here i print the tree
  # showing internal node names
  print t.get_ascii(show_internal=True)
  #
  #                                        /-H
  #                              /D-------|
  #                             |          \-K
  #                    /B-------|
  #                   |         |          /-F
  #          /A-------|          \G-------|
  #         |         |                    \-I
  #         |         |
  #         |          \-E
  #-NoName--|
  #         |                    /-L
  #         |          /J-------|
  #         |         |         |          /-N
  #         |         |          \O-------|
  #          \C-------|                    \-Q
  #                   |
  #                   |          /-P
  #                    \M-------|
  #                              \-S
  # Get pointers to specific nodes
  G = t.search_nodes(name="G")[0]
  J = t.search_nodes(name="J")[0]
  C = t.search_nodes(name="C")[0]
  # If we remove J from the tree, the whole partition under J node will
  # be detached from the tree and it will be considered an independent
  # tree. We can do the same thing using two approaches: J.detach() or
  # C.remove_child(J)
  removed_node = J.detach() # = C.remove_child(J)
  # if we know print the original tree, we will see how J partition is
  # no longer there.
  print "Tree after REMOVING the node J"
  print t.get_ascii(show_internal=True)
  #                                        /-H
  #                              /D-------|
  #                             |          \-K
  #                    /B-------|
  #                   |         |          /-F
  #          /A-------|          \G-------|
  #         |         |                    \-I
  #         |         |
  #-NoName--|          \-E
  #         |
  #         |                    /-P
  #          \C------- /M-------|
  #                              \-S
  # however, if we DELETE the node G, only G will be eliminated from the
  # tree, and all its descendants will then hang from the next upper
  # node.
  G.delete()
  print "Tree after DELETING the node G"
  print t.get_ascii(show_internal=True)
  #                                        /-H
  #                              /D-------|
  #                             |          \-K
  #                    /B-------|
  #                   |         |--F
  #          /A-------|         |
  #         |         |          \-I
  #         |         |
  #-NoName--|          \-E
  #         |
  #         |                    /-P
  #          \C------- /M-------|
  #                              \-S



Pruning trees
=============

Pruning a tree means to obtain the topology that connects a certain
group of items by removing the unnecessary edges. To facilitate this
task, ETE implements the :func:`TreeNode.prune` method, which can be
used by providing the list of terminal and/or internal nodes that must
be kept in the tree. 

From version 2.2, this function includes also the
`preserve_branch_length` flag, which allows to remove nodes from a
tree while keeping original distances among remaining nodes.

::

  from ete2 import Tree
  # Let's create simple tree
  t = Tree('((((H,K),(F,I)G),E),((L,(N,Q)O),(P,S)));')
  print "Original tree looks like this:"
  print t
  #
  #                                        /-H
  #                              /--------|
  #                             |          \-K
  #                    /--------|
  #                   |         |          /-F
  #          /--------|          \--------|
  #         |         |                    \-I
  #         |         |
  #         |          \-E
  #---------|
  #         |                    /-L
  #         |          /--------|
  #         |         |         |          /-N
  #         |         |          \--------|
  #          \--------|                    \-Q
  #                   |
  #                   |          /-P
  #                    \--------|
  #                              \-S
  # Prune the tree in order to keep only some leaf nodes.
  t.prune(["H","F","E","Q", "P"])
  print "Pruned tree"
  print t
  #
  #                              /-F
  #                    /--------|
  #          /--------|          \-H
  #         |         |
  #---------|          \-E
  #         |
  #         |          /-Q
  #          \--------|
  #                    \-P
  # Let's re-create the same tree again


Concatenating trees
===================

Given that all tree nodes share the same basic properties, they can be
connected freely. In fact, any node can add a whole subtree as a
child, so we can actually *cut & paste* partitions. To do so, you only
need to call the :func:`TreeNode.add_child` method using another tree
node as a first argument. If such a node is the root node of a
different tree, you will concatenate two structures. But caution!!,
this kind of operations may result into circular tree structures if
add an node's ancestor as a new node's child. Some basic checks are
internally performed by the ETE topology related methods, however, a
fully qualified check of this issue would affect seriously the
performance of the method. For this reason, users themselves should
take care about not creating circular structures by mistake.

::

  from ete2 import Tree
  # Loads 3 independent trees
  t1 = Tree('(A,(B,C));')
  t2 = Tree('((D,E), (F,G));')
  t3 = Tree('(H, ((I,J), (K,L)));')
  print "Tree1:", t1
  #            /-A
  #  ---------|
  #           |          /-B
  #            \--------|
  #                      \-C
  print "Tree2:", t2
  #                      /-D
  #            /--------|
  #           |          \-E
  #  ---------|
  #           |          /-F
  #            \--------|
  #                      \-G
  print "Tree3:", t3
  #            /-H
  #           |
  #  ---------|                    /-I
  #           |          /--------|
  #           |         |          \-J
  #            \--------|
  #                     |          /-K
  #                      \--------|
  #                                \-L
  # Locates a terminal node in the first tree
  A = t1.search_nodes(name='A')[0]
  # and adds the two other trees as children.
  A.add_child(t2)
  A.add_child(t3)
  print "Resulting concatenated tree:", t1
  #                                          /-D
  #                                /--------|
  #                               |          \-E
  #                      /--------|
  #                     |         |          /-F
  #                     |          \--------|
  #            /--------|                    \-G
  #           |         |
  #           |         |          /-H
  #           |         |         |
  #           |          \--------|                    /-I
  #           |                   |          /--------|
  #  ---------|                   |         |          \-J
  #           |                    \--------|
  #           |                             |          /-K
  #           |                              \--------|
  #           |                                        \-L
  #           |
  #           |          /-B
  #            \--------|
  #                      \-C


.. _sec:tree-rooting:

.. _copying_trees:

Copying (duplicating) trees
=============================

ETE provides several strategies to clone tree structures. The method
:func:`TreeNode.copy()` can be used to produce a new independent tree
object with the exact topology and features as the original. However,
as trees may involve many intricate levels of branches and nested
features, 4 different methods are available to create a tree copy:

 - "newick": Tree topology, node names, branch lengths and branch
   support values will be copied as represented in the newick string
   This method is based on newick format serialization works very fast
   even for large trees.

 - "newick-extended": Tree topology and all node features will be
   copied based on the extended newick format representation. Only
   node features will be copied, thus excluding other node
   attributes. As this method is also based on newick serialisation,
   features will be converted into text strings when making the
   copy. Performance will depend on the tree size and the number and
   type of features being copied.

 - "cpickle": This is the default method. The whole node structure and
   its content will be cloned based on the cPickle object
   serialization python approach.  This method is slower, but
   recommended for full tree copying.

 - "deepcopy": The whole node structure and its content is copied
   based on the standard "copy" Python functionality. This is the
   slowest method, but it allows to copy very complex objects even
   when attributes point to lambda functions.

::


   from ete2 import Tree
   t = Tree("((A, B)Internal_1:0.7, (C, D)Internal_2:0.5)root:1.3;", format=1)
   # we add a custom annotation to the node named A
   (t & "A").add_features(label="custom Value")
   # we add a complex feature to the A node, consisting of a list of lists
   (t & "A").add_features(complex=[[0,1], [2,3], [1,11], [1,0]])
   print t.get_ascii(attributes=["name", "dist", "label", "complex"])

   #                         /-A, 0.0, custom Value, [[0, 1], [2, 3], [1, 11], [1, 0]]
   #          /Internal_1, 0.7
   #         |               \-B, 0.0
   # -root, 1.3
   #         |               /-C, 0.0
   #          \Internal_2, 0.5
   #                         \-D, 0.0

   # Newick copy will loose custom node annotations, complex features,
   # but not names and branch values

   print t.copy("newick").get_ascii(attributes=["name", "dist", "label", "complex"])

   #                           /-A, 0.0
   #            /Internal_1, 0.7
   #           |               \-B, 0.0
   # -NoName, 0.0
   #           |               /-C, 0.0
   #            \Internal_2, 0.5
   #                           \-D, 0.0
   
   # Extended newick copy will transfer custom annotations as text
   # strings, so complex features are lost.

   print t.copy("newick-extended").get_ascii(attributes=["name", "dist", "label", "complex"])

   #                              /-A, 0.0, custom Value, __0_ 1__ _2_ 3__ _1_ 11__ _1_ 0__
   #            /Internal_1, 0.7
   #           |               \-B, 0.0
   # -NoName, 0.0
   #           |               /-C, 0.0
   #            \Internal_2, 0.5
   #                           \-D, 0.0

   # The default pickle method will produce a exact clone of the
   # original tree, where features are duplicated keeping their
   # python data type.

   print t.copy().get_ascii(attributes=["name", "dist", "label", "complex"])
   print "first element in complex feature:", (t & "A").complex[0]

   #                         /-A, 0.0, custom Value, [[0, 1], [2, 3], [1, 11], [1, 0]]
   #          /Internal_1, 0.7
   #         |               \-B, 0.0
   # -root, 1.3
   #         |               /-C, 0.0
   #          \Internal_2, 0.5
   #                         \-D, 0.0
   # first element in complex feature: [0, 1]



.. _resolve_polytomy:

Solving multifurcations
=============================

When a tree contains a polytomy (a node with more than 2 children),
the method :func:`resolve_polytomy` can be used to convert the node
into a randomly bifurcated structure in which branch lengths are set
to 0. This is really not a solution for the polytomy but it allows to
export the tree as a strictly bifurcated newick structure, which is a
requirement for some external software.

The method can be used on a very specific node while keeping the rest
of the tree intact by disabling the :attr:`recursive` flag.

:: 

  from ete2 import Tree
  t = Tree("(( (a, b, c), (d, e, f, g)), (f, i, h));")
  print t

  #             /-a
  #            |
  #         /--|--b
  #        |   |
  #        |    \-c
  #     /--|
  #    |   |    /-d
  #    |   |   | y
  #    |   |   |--e
  #    |    \--|
  # ---|       |--f
  #    |       |
  #    |        \-g
  #    |
  #    |    /-f
  #    |   |
  #     \--|--i
  #        |
  #         \-h


  polynode = t.get_common_ancestor("a", "b")
  polynode.resolve_polytomy(recursive=False)
  print t

  #                 /-b
  #             /--|
  #         /--|    \-c
  #        |   |
  #        |    \-a
  #     /--|
  #    |   |    /-d
  #    |   |   |
  #    |   |   |--e
  #    |    \--|
  # ---|       |--f
  #    |       |
  #    |        \-g
  #    |
  #    |    /-f
  #    |   |
  #     \--|--i
  #        |
  #         \-h


  t.resolve_polytomy(recursive=True)
  print t

  #  
  #                 /-b
  #             /--|
  #         /--|    \-c
  #        |   |
  #        |    \-a
  #        |
  #     /--|            /-f
  #    |   |        /--|
  #    |   |    /--|    \-g
  #    |   |   |   |
  #    |    \--|    \-e
  # ---|       |
  #    |        \-d
  #    |
  #    |        /-i
  #    |    /--|
  #     \--|    \-h
  #        |
  #         \-f




Tree Rooting
============

Tree rooting is understood as the technique by with a given tree is
conceptually polarized from more basal to more terminal nodes. In
phylogenetics, for instance, this a crucial step prior to the
interpretation of trees, since it will determine the evolutionary
relationships among the species involved. The concept of rooted trees
is different than just having a root node, which is always necessary
to handle a tree data structure. Usually, the way in which a tree is
differentiated between rooted and unrooted, is by counting the number
of branches of the current root node. Thus, if the root node has more
than two child branches, the tree is considered unrooted. By contrast,
when only two main branches exist under the root node, the tree is
considered rooted. 

Having an unrooted tree means that any internal branch within the tree
could be regarded as the root node, and there is no conceptual reason
to place the root node where it is placed at the moment. Therefore, in
an unrooted tree, there is no information about which internal nodes
are more basal than others. By setting the root node between a given
edge/branch of the tree structure the tree is polarized, meaning that
the two branches under the root node are the most basal nodes. In
practice, this is usually done by setting an **outgroup** **node**,
which would represent one of these main root branches. The second one
will be, obviously, the brother node. When you set an outgroup on
unrooted trees, the multifurcations at the current root node are
solved.

In order to root an unrooted tree or re-root a tree structure, ETE
implements the :func:`TreeNode.set_outgroup` method, which is present
in any tree node instance.  Similarly, the :func:`TreeNode.unroot`
method can be used to perform the opposite action.

::

  from ete2 import Tree
  # Load an unrooted tree. Note that three branches hang from the root
  # node. This usually means that no information is available about
  # which of nodes is more basal.
  t = Tree('(A,(H,F)(B,(E,D)));')
  print "Unrooted tree"
  print t
  #          /-A
  #         |
  #         |          /-H
  #---------|---------|
  #         |          \-F
  #         |
  #         |          /-B
  #          \--------|
  #                   |          /-E
  #                    \--------|
  #                              \-D
  #
  # Let's define that the ancestor of E and D as the tree outgroup.  Of
  # course, the definition of an outgroup will depend on user criteria.
  ancestor = t.get_common_ancestor("E","D")
  t.set_outgroup(ancestor)
  print "Tree rooteda at E and D's ancestor is more basal that the others."
  print t
  #
  #                    /-B
  #          /--------|
  #         |         |          /-A
  #         |          \--------|
  #         |                   |          /-H
  #---------|                    \--------|
  #         |                              \-F
  #         |
  #         |          /-E
  #          \--------|
  #                    \-D
  #
  # Note that setting a different outgroup, a different interpretation
  # of the tree is possible
  t.set_outgroup( t&"A" )
  print "Tree rooted at a terminal node"
  print t
  #                              /-H
  #                    /--------|
  #                   |          \-F
  #          /--------|
  #         |         |          /-B
  #         |          \--------|
  #---------|                   |          /-E
  #         |                    \--------|
  #         |                              \-D
  #         |
  #          \-A


Note that although **rooting** is usually regarded as a whole-tree
operation, ETE allows to root subparts of the tree without affecting
to its parent tree structure.

::

  from ete2 import Tree
  t = Tree('(((A,C),((H,F),(L,M))),((B,(J,K))(E,D)));')
  print "Original tree:"
  print t
  #                              /-A
  #                    /--------|
  #                   |          \-C
  #                   |
  #          /--------|                    /-H
  #         |         |          /--------|
  #         |         |         |          \-F
  #         |          \--------|
  #         |                   |          /-L
  #         |                    \--------|
  #---------|                              \-M
  #         |
  #         |                    /-B
  #         |          /--------|
  #         |         |         |          /-J
  #         |         |          \--------|
  #          \--------|                    \-K
  #                   |
  #                   |          /-E
  #                    \--------|
  #                              \-D
  #
  # Each main branch of the tree is independently rooted.
  node1 = t.get_common_ancestor("A","H")
  node2 = t.get_common_ancestor("B","D")
  node1.set_outgroup("H")
  node2.set_outgroup("E")
  print "Tree after rooting each node independently:"
  print t
  #
  #                              /-F
  #                             |
  #                    /--------|                    /-L
  #                   |         |          /--------|
  #                   |         |         |          \-M
  #                   |          \--------|
  #          /--------|                   |          /-A
  #         |         |                    \--------|
  #         |         |                              \-C
  #         |         |
  #         |          \-H
  #---------|
  #         |                    /-D
  #         |          /--------|
  #         |         |         |          /-B
  #         |         |          \--------|
  #          \--------|                   |          /-J
  #                   |                    \--------|
  #                   |                              \-K
  #                   |
  #                    \-E


Working with branch distances
=============================

The branch length between one node an its parent is encoded as the
:attr:`TreeNode.dist` attribute. Together with tree topology, branch
lengths define the relationships among nodes.


Getting distances between nodes
-------------------------------

The :func:`TreeNode.get_distance` method can be used to calculate the
distance between two connected nodes. There are two ways of using this
method: a) by querying the distance between two descendant nodes (two
nodes are passed as arguments) b) by querying the distance between the
current node and any other relative node (parental or descendant).


::

  from ete2 import Tree
   
  # Loads a tree with branch lenght information. Note that if no
  # distance info is provided in the newick, it will be initialized with
  # the default dist value = 1.0
  nw = """(((A:0.1, B:0.01):0.001, C:0.0001):1.0,
  (((((D:0.00001:0,I:0):0,F:0):0,G:0):0,H:0):0,
  E:0.000001):0.0000001):2.0;"""
  t = Tree(nw)
  print t
  #                              /-A
  #                    /--------|
  #          /--------|          \-B
  #         |         |
  #         |          \-C
  #         |
  #         |                                                  /-D
  #         |                                        /--------|
  #---------|                              /--------|          \-I
  #         |                             |         |
  #         |                    /--------|          \-F
  #         |                   |         |
  #         |          /--------|          \-G
  #         |         |         |
  #          \--------|          \-H
  #                   |
  #                    \-E
  #
  # Locate some nodes
  A = t&"A"
  C = t&"C"
  # Calculate distance from current node
  print "The distance between A and C is",  A.get_distance("C")
  # Calculate distance between two descendants of current node
  print "The distance between A and C is",  t.get_distance("A","C")
  # Calculate the toplogical distance (number of nodes in between)
  print "The number of nodes between A and D is ",  \
      t.get_distance("A","D", topology_only=True)



Additionally to this, ETE incorporates two more methods to calculate
the most distant node from a given point in a tree. You can use the
:func:`TreeNode.get_farthest_node` method to retrieve the most distant
point from a node within the whole tree structure. Alternatively,
:func:`TreeNode.get_farthest_leaf` will return the most distant
descendant (always a leaf). If more than one node matches the farthest
distance, the first occurrence is returned.

Distance between nodes can also be computed as the number of nodes
between them (considering all branch lengths equal to 1.0). To do so,
the **topology_only** argument must be set to **True** for all the
above mentioned methods.


::

  # Calculate the farthest node from E within the whole structure
  farthest, dist = (t&"E").get_farthest_node()
  print "The farthest node from E is", farthest.name, "with dist=", dist
  # Calculate the farthest node from E within the whole structure,
  # regarding the number of nodes in between as distance value
  # Note that the result is differnt.
  farthest, dist = (t&"E").get_farthest_node(topology_only=True)
  print "The farthest (topologically) node from E is", \
      farthest.name, "with", dist, "nodes in between"
  # Calculate farthest node from an internal node
  farthest, dist = t.get_farthest_node()
  print "The farthest node from root is is", farthest.name, "with dist=", dist
  #
  # The program results in the following information:
  #
  # The distance between A and C is 0.1011
  # The distance between A and C is 0.1011
  # The number of nodes between A and D is  8.0
  # The farthest node from E is A with dist= 1.1010011
  # The farthest (topologically) node from E is I with 5.0 nodes in between
  # The farthest node from root is is A with dist= 1.101


.. _sub:getting-midpoint-outgroup:

getting midpoint outgroup
-------------------------

In order to obtain a balanced rooting of the tree, you can set as the tree
outgroup that partition which splits the tree in two equally distant clusters
(using branch lengths). This is called the midpoint outgroup.

The :func:`TreeNode.get_midpoint_outgroup` method will return the
outgroup partition that splits current node into two balanced branches
in terms of node distances.

::

  from ete2 import Tree
  # generates a random tree
  t = Tree();
  t.populate(15);
  print t
  #
  #
  #                    /-qogjl
  #          /--------|
  #         |          \-vxbgp
  #         |
  #         |          /-xyewk
  #---------|         |
  #         |         |                    /-opben
  #         |         |                   |
  #         |         |          /--------|                    /-xoryn
  #          \--------|         |         |          /--------|
  #                   |         |         |         |         |          /-wdima
  #                   |         |          \--------|          \--------|
  #                   |         |                   |                    \-qxovz
  #                   |         |                   |
  #                   |         |                    \-isngq
  #                    \--------|
  #                             |                    /-neqsc
  #                             |                   |
  #                             |                   |                              /-waxkv
  #                             |          /--------|                    /--------|
  #                             |         |         |          /--------|          \-djeoh
  #                             |         |         |         |         |
  #                             |         |          \--------|          \-exmsn
  #                              \--------|                   |
  #                                       |                   |          /-udspq
  #                                       |                    \--------|
  #                                       |                              \-buxpw
  #                                       |
  #                                        \-rkzwd
  # Calculate the midpoint node
  R = t.get_midpoint_outgroup()
  # and set it as tree outgroup
  t.set_outgroup(R)
  print t
  #                              /-opben
  #                             |
  #                    /--------|                    /-xoryn
  #                   |         |          /--------|
  #                   |         |         |         |          /-wdima
  #                   |          \--------|          \--------|
  #          /--------|                   |                    \-qxovz
  #         |         |                   |
  #         |         |                    \-isngq
  #         |         |
  #         |         |          /-xyewk
  #         |          \--------|
  #         |                   |          /-qogjl
  #         |                    \--------|
  #---------|                              \-vxbgp
  #         |
  #         |                    /-neqsc
  #         |                   |
  #         |                   |                              /-waxkv
  #         |          /--------|                    /--------|
  #         |         |         |          /--------|          \-djeoh
  #         |         |         |         |         |
  #         |         |          \--------|          \-exmsn
  #          \--------|                   |
  #                   |                   |          /-udspq
  #                   |                    \--------|
  #                   |                              \-buxpw
  #                   |
  #                    \-rkzwd


