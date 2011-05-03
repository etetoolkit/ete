:Author: Jaime Huerta-Cepas

.. currentmodule:: ete_dev

The Programmable Tree Drawing Engine
************************************

ETE's treeview extension provides a highly programmable drawing system
to render any hierarchical tree structure as PDF, SVG or PNG
images. Although several predefined visualization layouts are included
with the default installation, custom styles can be easily created
from scratch.

Image customization is performed through four elements: **a)**
:class:`TreeStyle`, setting general options about the image (shape,
rotation, etc.), **b)** :class:`NodeStyle`, which defines the
specific aspect of each node (size, color, background, line type,
etc.), **c)** node :class:`faces.Face` which are small pieces of extra
graphical information that can be added to nodes (text labels, images,
graphs, etc.) **d)** a :attr:`layout` function, a normal python
function that controls how node styles and faces are dynamically added
to nodes.

Images can be rendered as **PNG**, **PDF** or **SVG** files using the
:func:`TreeNode.render` method or interactively visualized using a
built-in Graphical User Interface (GUI) invoked by the
:func:`TreeNode.show` method.


Interactive visualization of trees
==================================

ETE's tree drawing engine is fully integrated with a built-in
graphical user interface (GUI). Thus, ETE allows to visualize trees
using an interactive interface that allows to explore and manipulate
node's properties and tree topology.  To start the visualization of a
node (tree or subtree), you can simply call the :func:`TreeNode.show`
method.

One of the advantages of this on-line GUI visualization is that you
can use it to interrupt a given program/analysis, explore the tree,
manipulate them, and continuing with the execution thread. Note that
**changes made using the GUI will be kept after quiting the
GUI**. This feature is specially useful for using during python
sessions, in which analyses are performed interactively.

The GUI allows many operations to be performed graphically, however it
does not implement all the possibilities of the programming toolkit.

:: 

  from ete_dev import Tree 
  t = Tree( "((a,b),c);" )
  t.show()

Rendering trees as images
=============================

Tree images can be directly written as image files. SVG, PDF and PNG
formats are supported. Note that, while PNG images are raster images,
PDF and SVG pictures are rendered as `vector graphics
<http://en.wikipedia.org/wiki/Vector_graphics>`_, thus allowing its
later modification and scaling.

To generate an image, the :func:`TreeNode.render` method should be
used instead of :func:`TreeNode.show`. The only required argument is
the file name, whose extension will determine the image format (.PDF,
.SVG or .PNG). Several parameters regarding the image size and
resolution can be adjusted:

.. table::

   ================= ==============================================================
   Argument           Description
   ================= ==============================================================
   :attr:`units`     "**px**": pixels, "**mm**": millimeters, "**in**": inches
   :attr:`h`         height of the image in :attr:`units`.       
   :attr:`w`         weight of the image in :attr:`units`.
   :attr:`dpi`       dots per inches.
   ================= ==============================================================

.. note:: 

   If :attr:`h` and :attr:`w` values are both provided, image size
   will be adjusted even if it requires to break the original aspect
   ratio of the image. If only one value (:attr:`h` or :attr:`w`) is
   provided, the other will be estimated to maintain aspect ratio. If
   no sizing values are provided, image will be adjusted to A4
   dimensions.

:: 

  from ete_dev import Tree 
  t = Tree( "((a,b),c);" )
  t.render("mytree.png", w=183, units="mm")

Customizing the aspect of trees
==================================

Image customization is performed through four main elements:

Tree style 
-------------------

The :class:`TreeStyle` class can be used to create a custom set of
options that control the general aspect of the tree image. Tree styles
can be passed to the :func:`TreeNode.show` and :func:`TreeNode.render`
methods.  For instance, :class:`TreeStyle` allows to modify the scale
used to render tree branches or choose between circular or rectangular
tree drawing modes.

:: 

  from ete_dev import Tree, TreeStyle

  t = Tree( "((a,b),c);" )
  circular_style = TreeStyle()
  circular_style.mode = "c" # draw tree in circular mode
  circular_mode.scale = 20
  t.render("mytree.png", w=183, units="mm", tree_style=circular_style)
  
A number of parameters can be controlled through custom tree style
objetcs, check :class:`TreeStyle` documentation for a complete list of
accepted values. Some common configurations include:

Show leaf node names, branch length and branch support 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This will automatically add node names and branch information to the tree image

::

  from ete_dev import Tree, TreeStyle
  t = Tree()
  t.populate(50, random_dist=True)
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.show_branch_length = True
  ts.show_branch_support = True
  t.show(tree_style=ts)

Change branch length scale (zoom in X)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  from ete_dev import Tree, TreeStyle
  t = Tree()
  t.populate(50, random_dist=True)
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.scale =  60 # 60 pixels per branch length unit
  t.show(tree_style=ts)


Change branch separation between nodes (zoom in Y)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  from ete_dev import Tree, TreeStyle
  t = Tree()
  t.populate(50, random_dist=True)
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.branch_vertical_margin = 10 # 10 pixels between adjacent branches
  t.show(tree_style=ts)


Rotate a tree
^^^^^^^^^^^^^^^

This will render a rectangular tree from top to bottom
:: 

  from ete_dev import Tree, TreeStyle
  t = Tree()
  t.populate(50)
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.rotation = 90
  t.show(tree_style=ts)

circular tree in 180 degrees
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Draws a circular tree using a semi-circumference 

:: 

  from ete_dev import Tree, TreeStyle
  t = Tree()
  t.populate(50)
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.mode = "c"
  ts.arc_start = -90 # 0 degrees = 3 o'clock
  ts.arc_span = 180
  t.show(tree_style=ts)


Add legend and title 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:: 

  from ete_dev import Tree, TreeStyle, TextFace
  t = Tree( "((a,b),c);" )
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.title.add_face(TextFace("Hello ETE", fsize=20), column=0) 
  t.show(tree_style=ts)


Node style
-------------------

Through the :class:`NodeStyle` class the aspect of each single node
can be controlled, including its size, color, background and branch type.

A node style can be defined statically and attached to several nodes: 

:: 

  from ete_dev import Tree, NodeStyle
  t = Tree( "((a,b),c);" )
  nstyle = NodeStyle()
  
  # Draws nodes as small red spheres of diameter equal to 10 pixels
  nstyle["shape"] = "sphere"   
  nstyle["size"] = 10  
  nstyle["fgcolor"] = "darkred" 

  # Gray dashed branch lines
  nstyle["hz_line_type"] = 1 
  nstyle["hz_line_color"] = "#cccccc" 

  # Applies the same static style to all nodes in the tree. Note that,
  # if "nstyle" is modified, changes will affect to all nodes
  for n in t.traverse():
     n.set_style(nstyle)

  t.show() 

If each node should be drawn differently, an independent
:class:`NodeStyle` instance could be created for each node. Note that
node styles can be modified at any moment by accessing the
:attr:`TreeNode.img_style` attribute.

::

  from ete_dev import Tree, NodeStyle
  t = Tree( "((a,b),c);" )

  # Creates an independent node style for each node, which is
  # initialized with a red foreground color.
  for n in t.traverse():
     nstyle = NodeStyle()
     nstyle["fgcolor"] = "red"
     nstyle["size"] = 15
     n.set_style(nstyle)

  # Let's now modify the aspect of the root node
  t.img_style["size"] = 30
  t.img_style["fgcolor"] = "blue"

  t.show() 


Static node styles, set through the :func:`set_style` method, will be
attached to the nodes and exported as part of their information. For
instance, :func:`TreeNode.copy` will replicate all node styles in the
replicate tree.

Note that node styles can be also modified on the fly through a
:attr:`layout` function (see :ref:`sec:layout_functions`)


Node faces
-------------

.. currentmodule:: ete_dev.treeview.faces

Node faces are small pieces of graphical information that can be
linked to nodes. For instance, text labels or external images could be
linked to nodes and they will be plotted within the tree image. 

Several types of node faces are provided by the main :mod:`ete_dev`
module, ranging from simple text (:class:`TextFace`) and geometric
shapes (:class:`CircleFace`), to molecular sequence representations
(:class:`SequenceFace`), heatmaps and profile plots
(:class:`ProfileFace`). A full list of available faces can be found at
the :mod:`ete_dev.treeview` reference page.

Faces can be added to different areas around the node, namely
**branch-right**, **branch-top**, **branch-bottom** or **aligned**.
Each area represents a table in which faces can be added through the
:func:`TreeNode.add_face` method. For instance, if two text labels
want to be drawn bellow the branch line of a given node, a pair of
:class:`TextFace` faces can be created and added to the columns 0
and 1 of the **branch-bottom** area:

:: 
   
  from ete_dev import Tree, TreeStyle, TextFace
  t = Tree( "((a,b),c);" )

  # Basic tree style
  ts = TreeStyle()
  ts.show_leaf_name = True

  # Add two text faces to different columns 
  t.add_face(TextFace("hola "), column=0, position = "branch-right")
  t.add_face(TextFace("mundo!"), column=1, position = "branch-right")
  t.show(tree_style=ts)

If you add more than one face to the same area and column, they will
be piled up. See the following image as an example of face positions:

 .. figure:: ../face_positions.png
  :alt: possible face positions

  :download:`Source code <../face_grid.py>` used to generate the
  above image.

.. note::

  Once a face object is created, it can be linked to one or more
  nodes. For instance, the same text label can be recycled and added
  to several nodes.


.. _sec:layout_functions:

layouts
-------

.. note::
   
  Layout functions are the key component of the tree drawing
  customization.  Any python function accepting a node instance as a
  first argument can be used as a layout function. Essentially, such
  function will be called just before drawing each tree node, so you
  can use it perform any operation prior to render nodes.  In
  practice, layout functions are used to define the set of rules that
  control nodes style attributes and the faces that will be linked to
  them. Of course, such rules can be based on a previous node
  analysis. For instance: ``if node has more than 5 descendants, then
  add a text label, set a different background color, perform an
  analysis on leaves and associate an external image`` with node. As
  you imagine, rules can be are as sophisticated as you want. Thus,
  the advantage of this method is that you can create your own drawing
  algorithms to render trees dynamically and fitting very specific
  needs.

  In order to apply your custom layouts functions, function's name
  (the reference to it) can be passed to both **render()** and
  **show()** methods: ``node.render(``\ filename.pdf'',
  layout=mypythonFn) ``**or**`` node.show(layout=mypythonFn)``.


Example: combining styles, faces and layouts
--------------------------------------------

.. warning::

   Missing example
