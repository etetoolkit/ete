Frequently Asked Questions (FAQs)
=================================

.. contents::


General
-------

How do I use ETE?
~~~~~~~~~~~~~~~~~

ETE includes a basic standalone program that can be used to quickly
visualize your trees. Type ``ete4 explore -t <file>`` in a terminal to
run the program. For instance::

  ete4 explore -t mytreefile.nw

The ``ete4`` script is a very simple implementation and does not allow
for fancy customization. However, ETE is more than a standalone
program. The main goal of ETE is to provide a Python programming
library, so you can create your own scripts to manipulate and
visualize phylogenetic trees.

For example, in a python shell or script, you could::

  from ete4 import Tree

  t1 = Tree('((A,B),C);')  # create tree from newick string
  t1.explore()

  t2 = Tree(open('mytreefile.nw'))  # create tree from file
  t2.explore()


You can find many examples in the ETE tutorial.


Tree Browsing
-------------

How do I find a leaf by its name?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the following shortcut (note that it assumes no duplicated
names)::

  node = t['tip1']


How do I visit all nodes within a tree?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are many ways, but this is the easiest one::

  for node in t.traverse():
      print(node.name)


Can I control the order in which nodes are visited?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, currently 3 strategies are implemented: pre-order, post-order and
level-over. You can check the differences at
http://packages.python.org/ete4/tutorial/tutorial_trees.html#traversing-browsing-trees


Reading and writing
-------------------

How do I load a tree with internal node names or support?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newick format can be slightly different across programs. ETE allows to
read and write several newick subformats, including support for
internal node labeling:

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

In order to load (or write) a tree with internal node support, you can
specify to use the parser for format 0::

  from ete4 import Tree

  t = Tree('my_tree.nw', parser=0)

  t.write(parser=0)


How do I export tree node annotations using the Newick format?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When writing a tree, by default ETE only writes the node's names,
distances and support (depending on the format). If you want to save
other properties, you need to specify them when calling
``tree.write()``. For instance::

  tree.write(props=['name', 'species', 'size'])

If you want all node features to be exported in the newick string, use
``props=None``::

  tree.write(props=None)


Tree visualization
------------------

Can ETE draw circular trees?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, starting from version 2.1, ETE can render trees in circular
mode.


How do I export tree images as SVG?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Image format is automatically detected from the filename extension.
The following code will automatically render the tree as a vector
image::

  tree.render('mytree.svg')


How do I visualize internal node names?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to change the default tree layout. By creating your
custom layout functions, you will be able to add, remove or modify
almost any element of the tree image.

A basic example::

  from ete4 import Tree, faces, AttrFace, TreeStyle

  def my_layout(node):
      if node.is_leaf:
           name_face = AttrFace("name")  # draw name for leaves
      else:  # internal node
           name_face = AttrFace("name", fsize=10)  # draw label with small font

      # Add the name face to the image at the preferred position
      faces.add_face_to_node(name_face, node, column=0, position="branch-right")

  ts = TreeStyle()
  ts.show_leaf_name = False  # do not add leaf names again
  ts.layout_fn = my_layout  # use custom layout

  t = Tree("((B,(E,(A,G)M1_t1)M_1_t2)M2_t3,(C,D)M2_t1)M2_t2;", parser=8)

  t.show(tree_style=ts)  # visualize with custom tree style


Can the visualization of trees with very unbalanced tree branches be improved?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, the experience of visualizing trees with extreme differences in
branch lengths can be improved in several ways.

1) Convert your tree to ultrametric. This will modify all branches in
your tree to make all nodes end at the same length.

::

  from ete4 import Tree

  t = Tree()
  t.populate(50, random_branches=True)
  t.to_ultrametric()
  t.explore()


2) You can enable the :attr:`force_topology` option in
:class:`TreeStyle`, so all branches will be seen as the same length by
the tree drawing engine (note that in this case, actual tree branches
are not modified)

::

  from ete4 import Tree, TreeStyle

  t = Tree()
  t.populate(50, random_branches=True)

  ts = TreeStyle()
  ts.force_topology = True

  t.show(tree_style=ts)
