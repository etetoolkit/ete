Frequently Asked Questions (FAQs)
**********************************
.. contents::


General 
============

How do I use ETE?
-----------------------------------------------------------------

From 2.1 version, ETE includes a basic standalone program that can be
used to quickly visualize your trees. Type ``ete2`` in a terminal to
access the program. For instance:

  ``# ete2 "((A,B),C);"``

or 

  ``# ete2 mytreefile.nw``


However, ETE is not a standalone program. The ``ete2`` script is a
very simple implementation and does not allow for fancy
customization. The main goal of ETE is to provide a Python programming
library, so you can create your own scripts to manipulate and
visualize phylogenetic trees. Many examples are available `here
<http:://etetoolkit.org/releases/ete2/examples-ete2.tar.gz>`_ and
along with the ETE tutorial.


Tree Browsing
===============


How do I find a leaf by its name?
-----------------------------------------------------------------
You can use the :func:`TreeNode.search_nodes` function: 

:: 
  
  matching_nodes = tree.search_nodes(name="Tip1")
  
Or use the following shortcut (not that it assumes no duplicated
names)

:: 

  node = tree&"Tip1"

How do I visit all nodes within a tree?
-----------------------------------------

There are many ways, but this is the easiest one:

:: 

  for node in t.traverse():
      print node.name

Can I control the order in which nodes are visited?
-----------------------------------------------------

Yes, currently 3 strategies are implemented: pre-order, post-order and
level-over. You can check the differences at
http://packages.python.org/ete2/tutorial/tutorial_trees.html#traversing-browsing-trees
      

What's the difference between :func:`Tree.get_leaves` and :func:`Tree.iter_leaves`?
--------------------------------------------------------------------------------------

All methods starting with :attr:`get_` (i.e. get_leaves,
get_descendants, etc.) return an independent list of items. This means
that tree traversing is fully performed before returning the result.
In contrast, iter\_ methods return one item at a time, saving memory
and, increasing the performance of some operations.

Note also that tree topology cannot be modified while iterating
methods are being executed. This limitation does not apply for get\_
methods.

In addition, get\_ methods can be used to cache tree browsing paths
(the order in which nodes must be visited), so the same tree
traversing operations don't need to be repeated:

::

  nodes_in_preorder = tree.get_descendants("preorder")
  for n in nodes_in_preorder:
      pass # Do something
  #
  # (...)
  #
  for n in nodes_in_preorder:
      pass # Do something else
  

Reading and writing tree
===========================

How do I load a tree with internal node names?
-----------------------------------------------

Newick format can be slightly different across programs. ETE allows to
read and write several newick subformats, including support for
internal node labeling:

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

In order to load (or write) a tree with internal node names, you can
specify format 1:

:: 
   
   from ete2 import Tree
   t = Tree("myTree.nw", format=1)

   t.write(format=1)


How do I export tree node annotations using the Newick format?
---------------------------------------------------------------

You will need to use the extended newick format. To do so, you only
need to specify the name of the node attributes that must be exported
when calling tree.write() function. For instance:

::

   tree.write(features=["name", "dist"])

If you want all node features to be exported in the newick string, use
"features=[]":

::

   tree.write(features=[])



Tree visualization
===================

Can ETE draw circular trees?
----------------------------------

Yes, starting from version 2.1, ete can render trees in circular
mode. Install the latest version from
http://pypi.python.org/pypi/ete2 or by executing ``easy_install -U
ete2``.


What are all these dotted lines that appear in my circular trees?
-------------------------------------------------------------------

Opposite to other popular visualization software, ETE's drawing engine
will try by all means to avoid overlaps among lines and all other
graphical elements. When faces are added to nodes (specially to
internal nodes), the required space to allocate such elements requires
to expand the branches of the tree. Instead of breaking the relative
length of all branches, it will add dotted lines until reaching the
its minimal position. This effect could only be avoided by increasing
the branch scale. Alternatively, you can modify the aspect of the
dotted lines using :class:`TreeStyle` options, such as
:attr:`extra_branch_line_type`.

As by Jun 2012, ETE 2.1 includes a patch that allows to automatically
detect the optimal scale value that would avoid dotted lines. Two
levels of optimization are available, see :attr:`optimal_scale_level`
option in :class:`TreeStyle` class. This feature is now
user-transparent and enabled by default, so, if no scale is provided,
the optimal one will be used.


Why some circular trees are too large?
-------------------------------------------------------------------

In order to avoid overlaps among elements of the tree (i.e. node
faces), ETE will expand branch lengths until the desired layout is
fully satisfied. 


How do I export tree images as SVG
-----------------------------------------------------------------

Image format is automatically detected from the filename extension.
The following code will automatically render the tree as a vector
image.

::
                
        tree.render("mytree.svg")

How do I visualize internal node names?
----------------------------------------

You will need to change the default tree layout. By creating your
custom layout functions, you will be able to add, remove or modify
almost any element of the tree image.

A basic example would read as follow:

::
    
    from ete2 import Tree, faces, AttrFace, TreeStyle
     
    def my_layout(node):
        if node.is_leaf():
             # If terminal node, draws its name
             name_face = AttrFace("name")
        else:                
             # If internal node, draws label with smaller font size
             name_face = AttrFace("name", fsize=10)
        # Adds the name face to the image at the preferred position
        faces.add_face_to_node(name_face, node, column=0, position="branch-right")
     
    ts = TreeStyle()
    # Do not add leaf names automatically
    ts.show_leaf_name = False
    # Use my custom layout 
    ts.layout_fn = my_layout
         
    t = Tree("((B,(E,(A,G)M1_t1)M_1_t2)M2_t3,(C,D)M2_t1)M2_t2;", format=8)
    # Tell ETE to use your custom Tree Style
    t.show(tree_style=ts)

Can the visualization of trees with very unbalanced tree branches be improved? 
--------------------------------------------------------------------------------

Yes, the experience of visualizing trees with extreme differences in
branch lengths can be improved in several ways.

1) Convert your tree to ultrametric topology. This will modify all
branches in your tree to make all nodes to end at the same length.

::
   
    from ete2 import Tree, TreeStyle

    t = Tree()
    t.populate(50, random_branches=True)
    t.convert_to_ultrametric()
    t.show()


2) You can enable the :attr:`force_topology` option in
:class:`TreeStyle`, so all branches will be seen as the same length by
the tree drawing engine (Note that in this case, actual tree branches
are not modified)

::
   
    from ete2 import Tree, TreeStyle

    t = Tree()
    t.populate(50, random_branches=True)
    ts = TreeStyle()
    ts.force_topology = True
    t.show(tree_style=ts)



