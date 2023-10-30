.. currentmodule:: ete4.treeview

Programmable tree drawing
=========================

.. contents::

Overview
--------

Before exploring the novel features and enhancements introduced in ETE v4, it is essential to understand the foundational elements of ETE’s programmable tree drawing engine. Inherited from ETE v3, the following fundamental components form a highly adaptable backbone, enabling the various customization and structuring of visualizations: 

a) TreeStyle, a class can be used to create a custom set of options that control the general aspect of the tree image. For example, users can modify the scale used to render tree branches or choose between circular or rectangular tree drawing, and customize general settings for tree visualizing such as title, footer, legend, etc.

b) NodeStyle, defines the specific aspect of each node (size, color, background, line type, etc.). A node style can be defined statically and attached to several nodes, or customized the conditions so different NodeStyle applied for nodes in different conditions. NodeStyle can even dynamically change on the fly to adapt ETE4’s zooming algorithm, which can be set through a TreeLayout.

c) Face, as called as node faces, are small pieces of extra graphical information that can be linked to nodes (text labels, images, graphs, etc.). Several types of node faces are provided by the previous ETE3 module, ranging from simple text (TextFace) and geometric shapes (CircleFace), to molecular sequence representations (SequenceFace), etc. These faces are upgraded in ETE4 to adapt the large tree drawing engine.

d) TreeLayout, is a class which defines a foundational layout for trees to set specific styles for both the entire tree and individual nodes, acting as a pre-drawing hooking framework. When a tree is about to be drawn, the above elements such as TreeStyle, NodeStyle, Face of nodes can be then set up and modified on the fly and returned to the drawer engine. Hence TreeLayout class can be understood as a suite of rules tree’s basic setting and how different nodes should be drawn. 


Interactive visualization of trees
----------------------------------

ETE's tree drawing engine is fully integrated with a built-in
graphical user interface (GUI) which allows to explore and manipulate
node's properties and tree topology. To start the visualization of a
node (tree or subtree), you can simply call the :func:`show
<ete4.Tree.show>` method.

One of the advantages of this visualization is that you can use it to
interrupt a given program/analysis, explore the tree, manipulate it,
and continue with the execution. Note that **changes made using the
GUI will be kept after quiting the GUI**. This feature is specially
useful during python sessions, where analyses are performed
interactively.

::

  from ete4 import Tree
  t = Tree('((a,b),c);')
  t.explore(keep_server=True)

The GUI allows many operations to be performed graphically. However it
does not implement all the possibilities of the programming toolkit.


Rendering trees as images
-------------------------

Tree images can be directly written as image files. Supported formats
are png, svg, and pdf. Note that while png images are raster images,
pdf and svg pictures are rendered as `vector graphics
<http://en.wikipedia.org/wiki/Vector_graphics>`_, thus allowing their
later modification and scaling.

To generate an image, the :func:`render <ete4.Tree.render>` method
should be used instead of :func:`show <ete4.Tree.show>`. The only
required argument is the file name, whose extension will determine the
image format (png, svg, or pdf). Several parameters regarding the
image size and resolution can be adjusted:

.. table::

  ============= ===================================================
  Argument      Description
  ============= ===================================================
  :attr:`units` ``px``: pixels, ``mm``: millimeters, ``in``: inches
  :attr:`h`     height of the image in :attr:`units`
  :attr:`w`     width of the image in :attr:`units`
  :attr:`dpi`   dots per inch
  ============= ===================================================

.. note::

   If :attr:`h` and :attr:`w` values are both provided, image size
   will be adjusted even if it requires breaking the original aspect
   ratio of the image. If only one value (:attr:`h` or :attr:`w`) is
   provided, the other will be estimated to maintain the aspect ratio.
   If no sizing values are provided, the image will be adjusted to A4.

::

  from ete4 import Tree
  t = Tree('((a,b),c);')
  t.render('mytree.png', w=183, units='mm')


Customizing the aspect of trees
-------------------------------

Image customization is performed through four main elements: *tree
style*, *node style*, *faces*, and *layouts*.


Tree style
~~~~~~~~~~

a class can be used to create a custom set of options that control the general aspect of 
the tree image. For example, users can modify the scale used to render tree branches or 
choose between circular or rectangular tree drawing, and customize general settings for 
tree visualizing such as title, footer, legend, etc

A number of parameters can be controlled through custom tree style
objects. Check the :class:`TreeStyle` documentation for a complete
list of accepted values.

In the following, se show some common cases.


Show leaf node names, branch length and branch support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Users can choose to show leaf node names, branch length and branch support in the 
tree explore method.

Example::
  
   from ete4 import Tree
   from ete4.treeview import TreeStyle
   t = Tree()
   t.populate(10, random_branches=True)
   t.explore(show_leaf_name=True, show_branch_length=True, 
   show_branch_support=True, keep_server=True)

Customizing tree style
^^^^^^^^^^^^^^^^^^^^

Example::
  from ete4 import Tree
  from ete4.smartview import TreeStyle, TreeLayout

  t = Tree('(((((Phy004Z0OU_MELUD:0.0946697,Phy004V34S_CORBR:0.0843078)1:0.0296133,(Phy004U0LB_BUCRH:0.0424414,Phy004Z7RR_MERNU:0.115361)1:0.00300256)1:0.0131996,(Phy00527O5_PICPB:0.0684659,Phy004TLNA_APAVI:0.04435)1:0.0093323)1:0.0128687,Phy004STVX_187382:0.0385263)1:0.00468636,(((Phy00535AU_PYGAD:0.0330352,Phy004O1E0_APTFO:0.00383064)1:0.0122131,(Phy004UIZ8_CALAN:0.0575799,Phy004SNJQ_CHAVO:0.0713472)1:0.0103022)1:0.000902551,(Phy004OLZN_COLLI:5e-09,Phy004OLZM_COLLI:0.0203921)1:0.0549954)1:0.0019839)1:0.00477848;')

  def modify_tree_style(tree_style):
      tree_style.collapse_size = 70
      
  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ts=modify_tree_style)
  
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Add legend and title
^^^^^^^^^^^^^^^^^^^^
::

  from ete4 import Tree
  from ete4.treeview import TreeStyle, TextFace
  t = Tree('((a,b),c);')
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.title.add_face(TextFace('Hello ETE', fsize=20), column=0)
  t.show(tree_style=ts)


Node style
~~~~~~~~~~

Through the :class:`NodeStyle` class the aspect of each single node
can be controlled, including its size, color, background and branch
type.

A node style can be defined statically and attached to several nodes.

Simple tree in which the same style is applied to all nodes::

  from ete4 import Tree
  from ete4.treeview import NodeStyle, TreeStyle

  t = Tree('((a,b),c);')

  # Basic tree style.
  ts = TreeStyle()
  ts.show_leaf_name = True

  # Draw nodes as small red spheres of diameter equal to 10 pixels.
  nstyle = NodeStyle()
  nstyle['shape'] = 'sphere'
  nstyle['size'] = 10
  nstyle['fgcolor'] = 'darkred'

  # Gray dashed branch lines
  nstyle['hz_line_type'] = 1
  nstyle['hz_line_color'] = '#cccccc'

  # Apply the same static style to all nodes in the tree. Note that
  # if 'nstyle' is modified, changes will affect all nodes.
  for n in t.traverse():
      n.set_style(nstyle)

  t.show(tree_style=ts)

.. figure:: ../images/node_style_red_nodes.png

If you want to draw nodes with different styles, an independent
:class:`NodeStyle` instance must be created for each node. Note that
node styles can be modified at any moment by accessing the
:attr:`img_style <ete4.Tree.img_style>` attribute.

Simple tree in which the different styles are applied to each node::

  from ete4 import Tree
  from ete4.treeview import NodeStyle, TreeStyle
  t = Tree('((a,b),c);')

  # Basic tree style.
  ts = TreeStyle()
  ts.show_leaf_name = True

  # Create an independent node style for each node, which is
  # initialized with a red foreground color.
  for n in t.traverse():
      nstyle = NodeStyle()
      nstyle['fgcolor'] = 'red'
      nstyle['size'] = 15
      n.set_style(nstyle)

  # Let's now modify the aspect of the root node
  t.img_style['size'] = 30
  t.img_style['fgcolor'] = 'blue'

  t.show(tree_style=ts)

.. figure:: ../images/node_style_red_and_blue_nodes.png

Static node styles, set through the :func:`set_style
<ete4.Tree.set_style>` method, will be attached to the nodes and
exported as part of their information. For instance, :func:`copy
<ete4.Tree.copy>` will replicate all node styles in the replicate
tree. Note that node styles can also be modified on the fly through
:ref:`layout functions <sec:layout_functions>`.


Node faces
~~~~~~~~~~

Node faces are small pieces of graphical information that can be
linked to nodes. For instance, text labels or external images could be
linked to nodes and they will be plotted within the tree image.

Several types of node faces are provided by the main :mod:`treeview`
module, ranging from simple text (:class:`TextFace`) and geometric
shapes (:class:`CircleFace`), to molecular sequence representations
(:class:`SequenceFace`), heatmaps and profile plots
(:class:`ProfileFace`).

A complete list of available faces can be found at the :mod:`treeview`
reference page.


Faces position
^^^^^^^^^^^^^^

Faces can be added to different areas around the node, namely
**branch-right**, **branch-top**, **branch-bottom** or **aligned**.
Each area represents a table in which faces can be added through the
:func:`add_face <ete4.Tree.add_face>` method. For instance, if you
want two text labels drawn below the branch line of a given node, a
pair of :class:`TextFace` faces can be created and added to the
columns 0 and 1 of the **branch-bottom** area::

  from ete4 import Tree
  from ete4.treeview import TreeStyle, TextFace
  t = Tree('((a,b),c);')

  # Basic tree style.
  ts = TreeStyle()
  ts.show_leaf_name = True

  # Add two text faces to different columns.
  t.add_face(TextFace('hola '), column=0, position='branch-bottom')
  t.add_face(TextFace('mundo!'), column=1, position='branch-bottom')
  t.show(tree_style=ts)

If you add more than one face to the same area and column, they will
be piled up. See the following image as an example of face positions:

.. figure:: ../images/face_positions.png
   :alt: possible face positions

(Source code to generate the above image: :download:`face_grid_tutorial.py
<../../examples/treeview/face_grid_tutorial.py>`)

.. note::

  Once a face object is created, it can be linked to one or more
  nodes. For instance, the same text label can be recycled and added
  to several nodes.


Face properties
^^^^^^^^^^^^^^^

Apart from the specific config values of each face type, all face
instances contain the same basic attributes that permit to modify
general aspects such as margins, background colors, border, etc. A
complete list of face attributes can be found in the general
:class:`Face` class documentation. Here is a very simple example::

  from ete4 import Tree
  from ete4.treeview import TreeStyle, TextFace

  t = Tree('(a,b);')

  # Basic tree style.
  ts = TreeStyle()
  ts.show_leaf_name = True

  # Create two faces.
  hola = TextFace('hola')
  mundo = TextFace('mundo')

  # Set some attributes.
  hola.margin_top = 10
  hola.margin_right = 10
  hola.margin_left = 10
  hola.margin_bottom = 10
  hola.opacity = 0.5 # from 0 to 1
  hola.inner_border.width = 1 # 1 pixel border
  hola.inner_border.type = 1  # dashed line
  hola.border.width = 1
  hola.background.color = 'LightGreen'

  t.add_face(hola, column=0, position='branch-top')
  t.add_face(mundo, column=1, position='branch-bottom')

  t.show(tree_style=ts)

.. figure:: ../images/face_borders.png


.. _sec:layout_functions:

Layout functions
~~~~~~~~~~~~~~~~

Layout functions act as pre-drawing `hooking functions
<http://en.wikipedia.org/wiki/Hooking>`_. This means that, before a
node is drawn, it is first sent to a layout function. Node properties,
style and faces can be then modified on the fly and returned to the
drawing engine. Thus, layout functions can be understood as a
collection of rules controlling how different nodes should be drawn.

::

  from ete4 import Tree
  t = Tree('((((a,b),c),d),e);')

  def abc_layout(node):
      vowels = {'a', 'e', 'i', 'o', 'u'}

      if node.name in vowels:
          node.img_style['size'] = 15
          node.img_style['fgcolor'] = 'red'
          # Note that the node style was already initialized with the
          # default values.

  # Tree style.
  ts = TreeStyle()
  ts.show_leaf_name = True
  ts.layout_fn = abc_layout

  # Add two text faces to different columns.
  t.add_face(TextFace('hola '), column=0, position='branch-right')
  t.add_face(TextFace('mundo!'), column=1, position='branch-right')

  t.show(tree_style=ts)

.. figure:: ../images/example_layout_functions.png


Combining styles, faces and layouts
-----------------------------------

Examples are probably the best way to show how ETE works:


Fixed node styles
~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/node_style.py

.. figure:: ../../examples/treeview/node_style.png


Node backgrounds
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/node_background.py

.. figure:: ../../examples/treeview/node_background.png


Img faces
~~~~~~~~~

.. literalinclude:: ../../examples/treeview/img_faces/img_faces.py

.. figure:: ../../examples/treeview/img_faces/img_faces.png

Note that images are attached to terminal and internal nodes.


Bubble tree maps
~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/bubble_map.py

.. figure:: ../../examples/treeview/bubble_map.png


Trees within trees
~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/tree_faces.py

.. figure:: ../../examples/treeview/tree_faces.png


Phylogenetic trees and sequence domains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/seq_motif_faces.py

.. figure:: ../../examples/treeview/seq_motif_faces.png


Creating your custom interactive faces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/treeview/item_faces.py

.. figure:: ../../examples/treeview/item_faces.png

Note that the faces shown in this image are not static. When the tree
is viewed using the tree.show() method, you can interact with items.
