.. currentmodule:: ete4.smartview

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

Scheme of fundamental components in ETE4's programmable tree drawing engine

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/fundamental_ete4.jpg?raw=true
   :alt: alternative text
   :align: center

Explore interactive isualization of trees 
-----------------------------------------

ETE's tree drawing engine is fully integrated with a built-in
graphical user interface (GUI) which allows to explore and manipulate
node's properties and tree topology. To start the visualization of a
node (tree or subtree), you can simply call the :func:`explore
<ete4.Tree.explore>` method.

One of the advantages of this visualization is that you can use it to
interrupt a given program/analysis, explore the tree, manipulate it,
and continue with the execution. Note that **changes made using the
GUI will be kept after quiting the GUI**. This feature is specially
useful during python sessions, and it can be utilized in various environments 
by modifying argument *keep_server*, including standalone scripts and interactive 
sessions such as IPython or Jupyter Notebooks. Below are examples demonstrating 
the method's usage in each context.

Standalone scripts
~~~~~~~~~~~~~~~~~~
When running a standalone script, *keep_server* should be set as *True* to keep 
the server running.

::

  from ete4 import Tree
  t = Tree('((a,b),c);')
  t.explore(keep_server=True)

Source code can be found in in ETE4 here: `explore_standalone.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/explore_standalone.py>`_.

Interactive sessions
~~~~~~~~~~~~~~~~~~~~
When running in interactive sessions such as IPython or Jupyter Notebooks, *keep_server* 
should be set as *False*

::

  Python 3.9.7 (default, Sep 16 2021, 13:09:58) 
  Type 'copyright', 'credits' or 'license' for more information
  IPython 7.29.0 -- An enhanced Interactive Python. Type '?' for help.

  In [1]: from ete4 import Tree

  In [2]: t = Tree('((a,b),c);')

  In [3]: t.explore(keep_server=False)
  Added tree tree-1 with id 0.

Verbose mode
~~~~~~~~~~~~
When running in verbose mode by setting *quiet* argument, every actions 
will be printed in the terminal.

::

  Python 3.9.7 (default, Sep 16 2021, 13:09:58) 
  Type 'copyright', 'credits' or 'license' for more information
  IPython 7.29.0 -- An enhanced Interactive Python. Type '?' for help.

  In [1]: from ete4 import Tree

  In [2]: t = Tree('((a,b),c);')

  In [3]: t.explore(keep_server=False, quiet=False)
  Added tree tree-1 with id 0.
  Bottle v0.12.25 server starting up (using WSGIRefServer())...

  Listening on http://localhost:5000/
  Hit Ctrl-C to quit.

  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET / HTTP/1.1" 303 0
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees HTTP/1.1" 200 29
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /layouts HTTP/1.1" 200 106
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/size HTTP/1.1" 200 29
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/collapse_size HTTP/1.1" 200 2
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /drawers/RectFaces/0 HTTP/1.1" 200 30
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/ultrametric HTTP/1.1" 200 5
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/nodecount HTTP/1.1" 200 27
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /layouts/0 HTTP/1.1" 200 106
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/searches HTTP/1.1" 200 16
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/all_selections HTTP/1.1" 200 16
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/all_active HTTP/1.1" 200 27
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/draw?drawer=RectFaces&min_size=10&zx=555.9&zy=284.40000000000003&za=1&x=-0.33333333333333337&y=-0.16666666666666666&w=3.3333333333333335&h=3.333333333333333&collapsed_ids=%5B%5D&layouts=%5B%22default%3ABranch+length%22%2C%22default%3ABranch+support%22%2C%22default%3ALeaf+name%22%5D&ultrametric=0 HTTP/1.1" 200 1765
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /drawers/RectFaces/0 HTTP/1.1" 200 30
  127.0.0.1 - - [02/Nov/2023 11:19:15] "GET /trees/0/draw?drawer=RectFaces&min_size=10&zx=555.9&zy=284.40000000000003&za=1&x=-0.33333333333333337&y=-0.16666666666666666&w=3.3333333333333335&h=3.333333333333333&collapsed_ids=%5B%5D&layouts=%5B%22default%3ABranch+length%22%2C%22default%3ABranch+support%22%2C%22default%3ALeaf+name%22%5D&ultrametric=0&panel=-1 HTTP/1.1" 200 2


Show leaf node names, branch length and branch support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Users can choose to show leaf node names, branch length and branch support in the 
tree explore method.

Example::
  
   from ete4 import Tree
   t = Tree()
   t.populate(10, random_branches=True)
   t.explore(show_leaf_name=True, show_branch_length=True, \
   show_branch_support=True, keep_server=True)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/explore_show.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `explore_show.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/explore_show.py>`_.


Customizing the aspect of trees
-------------------------------

Image customization is performed through four main elements: *tree
style*, *node style*, *faces*, and *layouts*.

Tree Layout
~~~~~~~~~~~
As shown in scheme of fundamental components from the previous section, TreeLayout contains element of 
tree style, node style and faces. Therefore, TreeLayout is the most important element in ETE4's drawing engine 
in regards to visualize information other than pure tree topology. TreeLayout can be called from :class:`TreeLayout` 
from :class:`ete4.smartview:`. It contains the following arguments:

- *name*: name of the TreeLayout object, obligatory field.
- *ts*: a function to set tree style.
- *ns*: a function to set node style.
- *aligned_faces*: whether to draw faces in aligned position, default *False*.
- *active*: whether to activate the TreeLayout, default *True*.
- *legend*: whether to show legend(need to be defined in tree style function), default *False*.

Here we demonstrate the basic usage of TreeLayout::

  from ete4 import Tree
  from ete4.smartview import TreeLayout

  t = Tree()
  t.populate(20, random_branches=True)

  # define a TreeLayout
  tree_layout = TreeLayout(name="MyTreeLayout")

  # add TreeLayout to layouts
  layouts = []
  layouts.append(tree_layout)

  # explore tree
  t.explore(keep_server=True, layouts=layouts)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/treelayout_1.jpg?raw=true
   :alt: alternative text
   :align: center

As the red frame highlighted the TreeLayout name, which is defined as "MyTreeLayout" is shown 
and activated in tree panel.

Source code can be found in in ETE4 here: `treelayout_1.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/treelayout_1.py>`_.

Tree Style
~~~~~~~~~~

a class can be used to create a custom set of options that control the general aspect of 
the tree image. For example, users can modify the scale used to render tree branches or 
choose between circular or rectangular tree drawing, and customize general settings for 
tree visualizing such as title, footer, legend, etc

A number of parameters can be controlled through custom tree style
objects. Check the :class:`TreeStyle` documentation for a complete
list of accepted values.

As we described in the previous section, to modify tree style, we could define a function 
and pass it to the TreeLayout class which defined as custom layout for futher explore.

In the following, we show some common cases to modify tree style.

Customizing tree style
^^^^^^^^^^^^^^^^^^^^^^
::

  from ete4 import Tree
  from ete4.smartview import TreeLayout

  t.populate(20, random_branches=True)

  def modify_tree_style(tree_style):
      tree_style.collapse_size = 70
      
  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ts=modify_tree_style)
  
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Source code can be found in in ETE4 here: `treestyle_1.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/treestyle_1.py>`_.

Add legend
^^^^^^^^^^
::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((a,b),c);')
  def modify_tree_style(tree_style):
      
      # add legend
      tree_style.add_legend(
          title="MyLegend", 
          variable="discrete", 
          colormap={"a":"red", "b":"blue", "c":"green"}
          )

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ts=modify_tree_style)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)


.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/treestyle_legend.png?raw=true
   :alt: alternative text
   :align: center


Source code can be found in in ETE4 here: `treestyle_legend.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/treestyle_legend.py>`_.


Node style
~~~~~~~~~~

Through the :class:`NodeStyle` class the aspect of each single node
can be controlled, including its size, color, background and branch
type.

A node style can be defined statically and attached to several nodes.
Here is the full list of attributtes that can be modified of node style:

- *fgcolor*, foreground color, color thats appear in node, i.e. *red* or #ff0000 in hex code, default *#0030c1*. 
- *bgcolor*, background color, background color of node, default *transparent*.
- *outline_line_color*, border color of the triangle when node is collapsed, default *#000000*.
- *outline_line_width*, border width of the triangle when node is collapsed, default *0.5*.
- *outline_color*, color of the triangle when node is collapsed, default *#e5e5e5*.
- *outline_opacity*, opacity of the triangle when node is collapsed, default *0.3*.
- *vt_line_color*, color of verticle line of node, default *#000000*. 
- *hz_line_color*, color of horizontal line of node, default *#000000*.
- *hz_line_type*, type of horizontal line of node, default *0*, options are 0 solid, 1 dashed, 2 dotted.
- *vt_line_type*, type pf verticle line of node, default *0*, options are 0 solid, 1 dashed, 2 dotted.
- *hz_line_width*, size of horizontal line of node, default *0.5*.
- *vt_line_width*, size of verticle line of node, default *0.5*.
- *size*, diameter of node, default *0* piexl.
- *shape*, shape of node, default *circle*, options are *circle*, *square*, *triangle*.
- *draw_descendants*, whether to draw descendants of node or collapse node, default *True*.

Simple tree in which the same style is applied to all nodes::

  from ete4 import Tree
  from ete4.smartview import NodeStyle, TreeStyle

  t = Tree('((a,b),c);')

  # modtify node style in function
  def modify_node_style(node):
    # Draw nodes as small red square of diameter equal fo 10 pixels
    node.sm_style["fgcolor"] = "red"
    node.sm_style["shape"] = "traingle"
    node.sm_style["size"] = 10

    # brown dashed branch lines with width equal to 2 pixels
    node.sm_style["hz_line_type"] = 1
    node.sm_style["hz_line_width"] = 2
    node.sm_style["hz_line_color"] = "#964B00"
    return

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_node_style)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodestyle_triangle.png?raw=true
   :alt: alternative text
   :align: center
Now in legend of the layout shows in top-right corner of the tree panel.

Source code can be found in in ETE4 here: `nodestyle_traingle.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodestyle_traingle.py>`_.


If you want to draw nodes with different styles, an independent
:class:`NodeStyle` instance must be created for each node. 

Simple tree in which the different styles are applied to each node::

  from ete4 import Tree
  from ete4.smartview import TreeLayout

  t = Tree('((a,b),c);')

  # Draw nodes as small red square of diameter equal fo 10 pixels
  def modify_node_style(node):
      # Draw nodes as small red square of diameter equal fo 10 pixels
      # Create an independent node style for each node, which is
      # initialized with a red foreground color.
      node.sm_style["fgcolor"] = "red"
      node.sm_style["shape"] = "circle"
      node.sm_style["size"] = 10

      # Let's now modify the aspect of the root node
      # we set the foreground color to blue and the size to 30 for the root node with different verticle line style
      
      # Check if the node is the root node
      if node.is_root:
          node.sm_style["fgcolor"] = "blue"
          node.sm_style["size"] = 30
          node.sm_style["vt_line_type"] = 2
          node.sm_style["vt_line_width"] = 10
          node.sm_style["vt_line_color"] = "#964B00"
      return

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_node_style)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodestyle_different.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `nodestyle_different.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodestyle_different.py>`_.

Node faces
~~~~~~~~~~

Node faces are small pieces of graphical information that can be
linked to nodes. For instance, text labels or external images could be
linked to nodes and they will be plotted within the tree image.

Several types of node faces are provided by the main :mod:`smartview`
module, ranging from simple text (:class:`TextFace`) and geometric
shapes (:class:`CircleFace`) or (:class:`RectFace`), to molecular sequence representations
(:class:`SeqFace`), and specific faces for collapsed clade (:class:`OutlinedFace`), etc.

A complete list of available faces can be found at the :mod:`smartview`
reference page.


Faces position
^^^^^^^^^^^^^^

Faces can be added to different areas around the node, namely
**branch_right**, **branch_top**, **branch_bottom** or **aligned**.
Each area represents a table in which faces can be added through the
:func:`add_face <ete4.Tree.add_face>` method. For instance, if you
want two text labels drawn below the branch line of a given node, a
pair of :class:`TextFace` faces can be created and added to the
columns 0 and 1 of the **branch_bottom** area::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((a:1,b:1):1,c:1)Root:1;')

  # Draw nodes text face in root node
  def modify_face_position(node):
      if node.is_root:
          node.add_face(TextFace("Hola!", color="red"), column=0, position='branch_bottom')
          node.add_face(TextFace('mundo!', color="blue"), column=1, position='branch_bottom')
      return

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_face_position)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_bottom_1.png?raw=true
   :alt: alternative text
   :align: center

If we set the column of "mundo" text face as 0

::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  .....
    node.add_face(TextFace('mundo!', color="blue"), column=0, position='branch_bottom')
  .....
  t.explore(keep_server=True, layouts=layouts)


.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_bottom_2.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `faceposition_bottom.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_bottom.py>`_.


If you add more than one face to the same area and column, they will
be piled up. If position set **aligned**, the face of node will be drawn
aligned in an aligned column. If doing so, TreeLayout's argument **aligned_faces**
should be set as **True** to avoid the tree node's name overlapped with node faces.

**aligned** position example::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((a,b),c);')

  # Draw nodes text face in leaf node
  def modify_face_position(node):
      if node.is_leaf:
          node.add_face(TextFace("Hola!", color="red"), column=0, position='aligned')
          node.add_face(TextFace('mundo!', color="blue"), column=1, position='aligned')
      return

  # set aligned_faces=True because we want to align the faces
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_face_position, aligned_faces=True)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

See the following image

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_aligned.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `faceposition_aligned.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_aligned.py>`_.

.. note::

  Once a face object is created, it can be linked to one or more
  nodes. For instance, the same text label can be recycled and added
  to several nodes.

Face for collapsed clades 
^^^^^^^^^^^^^^^^^^^^^^^^^
A notable feature in smartview in ete4 is able to collapse clades in the tree. 
When a clade is collapsed, a triangle will be drawn as default in the node. Therefore,
a face can be added to the collapsed clade to show more information. 

For node faces in collapsed clades, modify *collapsed_only* argument to True in method 
:func:`add_face <ete4.Tree.add_face>` 

**collapsed_only** example::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((a:1,b:1)n1:1,c):1;')

  # Draw nodes text face in node with name n1
  def modify_face_position(node):
      # find node with name n1
      if node.name == "n1":
          # write text face "Hola" in node n1 and show it in branch_right directly
          node.add_face(TextFace("Hola!", color="red"), column=0, position='branch_right', collapsed_only=False)
          # write text face "Hola" in node n1 and show it in branch_right only when node is collapsed
          node.add_face(TextFace('mundo!', color="blue"), column=1, position='branch_right', collapsed_only=True)
      return

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_face_position)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

"Hola" TextFace shown in branch_right of node "n1" directly with argument **collapsed_only=False**

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_collapsed_before.png?raw=true
   :alt: alternative text
   :align: center

"mundo" TextFace shown in branch_right of node "n1" only when node is collapsed with argument **collapsed_only=False**

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_collapsed_after.png?raw=true
   :alt: alternative text
   :align: center

   
Source code can be found in in ETE4 here: `faceposition_collapsed.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_collapsed.py>`_.


Face properties
^^^^^^^^^^^^^^^

Each face instance has its specific config values, although all face
instances contain the same basic attributes that permit to modify
general aspects such as padding, etc.  In order to explore the properties of each face,
a complete list of face attributes can be found in 
each :class:`Face` class documentation, such as :class:`TextFace`, :class:`RectFace`, etc. 
Here is a very simple example::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((a:1,b:1):1,c:1):1;')

  top_textface = TextFace(text="branch top!")
  top_textface.color = 'blue'
  top_textface.min_fsize = 6
  top_textface.max_fsize = 25
  top_textface.ftype = 'courier'
  top_textface.padding_x = 0
  top_textface.padding_y = 0
  top_textface.width = None
  top_textface.rotation = 0

  # or all together
  bottom_textface = TextFace(text="branch bottom!", color='red',
              min_fsize=6, max_fsize=25, ftype='sans-serif',
              padding_x=1, padding_y=1, width=None, rotation=0)


  # Draw nodes text face in root node
  def modify_face_property(node):
      node.add_face(top_textface, column=0, position='branch_top')
      node.add_face(bottom_textface, column=0, position='branch_bottom')
      return

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=modify_face_property)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceproperties_textface.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `faceproperties_textface.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceproperties_textface.py>`_.



Advanced Layout functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Layout functions act as pre-drawing `hooking functions
<http://en.wikipedia.org/wiki/Hooking>`_. This means that, before a
node is drawn, it is first sent to a layout function. Node properties,
style and faces can be then modified on the fly and returned to the
drawing engine. Thus, layout functions can be understood as a
collection of rules controlling how different nodes should be drawn.

Wrap in function::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((((a,b),c),d),e);')


  def vowel_node_layout(node):
      vowels = {'a', 'e', 'i', 'o', 'u'}

      # here to set the node style
      if node.is_leaf:
          if node.name in vowels:
              node.sm_style['size'] = 15
              node.sm_style['fgcolor'] = 'red'


  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", ns=vowel_node_layout)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

.. figure:: ../images/example_layout_functions.png


Combining styles, faces and layouts
-----------------------------------

Fixed node styles, faces and tree style
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

example ::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((((a,b),c),d),e);')

  def vowel_tree_style(tree_style):
      text = TextFace("Vowel title", min_fsize=5, max_fsize=12, width=50, rotation=0)
      tree_style.aligned_panel_header.add_face(text, column=0)
      tree_style.add_legend(
          title="MyLegend", 
          variable="discrete", 
          colormap={"vowel":"red", "conostant":"blue"}
          )

  def vowel_node_layout(node):
      vowels = {'a', 'e', 'i', 'o', 'u'}

      # here to set the node style
      if node.is_leaf:
          if node.name in vowels:
              node.sm_style['size'] = 5
              node.sm_style['fgcolor'] = 'red'
          else:
              node.sm_style['size'] = 5
              node.sm_style['fgcolor'] = 'blue'   
              
              # here to add text face to node in aligned position
              node.add_face(TextFace('not vowel!', color="blue"), column=0, position='aligned')


  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", 
      ts=vowel_tree_style, 
      ns=vowel_node_layout,
      active=False, 
      aligned_faces=True)


  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)
.. literalinclude:: ../../examples/smartview/node_style.py

.. figure:: ../../examples/smartview/node_style.png



Define Layout objects
~~~~~~~~~~~~~~
As we showed above, layout functions can be passed to the TreeLayout class to 
create a TreeLayout object. Therefore we can defined our own customized layout

Example::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, TextFace

  t = Tree('((((a,b),c),d),e);')


  class MyTreeLayout(TreeLayout):
      def __init__(self, name="My First TreeLayout", min_fsize=5, max_fsize=12, 
              width=50, rotation=0, vowel_color="red", conostant_color="blue", 
              vowel_node_size=5, conostant_node_size=5, aligned_faces=True,
              column=0):
          
          # Ensuring that any initialization that TreeLayout needs to do is done, 
          # before MyTreeLayout goes on to do its own additional initialization. 
          super().__init__(name, aligned_faces=True) 

          self.name = name
          self.min_fsize = min_fsize
          self.max_fsize = max_fsize
          self.width = width
          self.rotation = rotation

          self.vowel_color = vowel_color
          self.conostant_color = conostant_color
          self.vowel_node_size = vowel_node_size
          self.conostant_node_size = conostant_node_size
          self.aligned_faces = aligned_faces
          self.column = column


      def set_tree_style(self, tree, style):
          text = TextFace(self.name, min_fsize=self.min_fsize, 
              max_fsize=self.max_fsize, width=self.width, rotation=self.rotation)

          style.aligned_panel_header.add_face(text, column=self.column)
          style.add_legend(
              title=self.name,  
              variable="discrete", 
              colormap={"vowel":"red", "conostant":"blue"}
              )

      def set_node_style(self, node):
          vowels = {'a', 'e', 'i', 'o', 'u'}
          vowel_textface = TextFace(
              text="vowel", color=self.vowel_color, 
              min_fsize=self.min_fsize, max_fsize=self.max_fsize,
              width=self.width, rotation=self.rotation
          )

          conostant_textface = TextFace(
              text="not vowel!", color=self.conostant_color, 
              min_fsize=self.min_fsize, max_fsize=self.max_fsize,
              width=self.width, rotation=self.rotation
          )

          # here to set the node style
          if node.is_leaf:
              if node.name in vowels:
                  node.sm_style['size'] = self.vowel_node_size
                  node.sm_style['fgcolor'] = self.vowel_color

                  # here to add text face to node in aligned position
                  node.add_face(vowel_textface, column=self.column, position='aligned')
              else:
                  node.sm_style['size'] = self.conostant_node_size
                  node.sm_style['fgcolor'] = self.conostant_color
                  
                  # here to add text face to node in aligned position
                  node.add_face(conostant_textface, column=self.column, position='aligned')


  # Create a TreeLayout object, passing in the function
  tree_layout = MyTreeLayout(name="MyTreeLayout", aligned_faces=True, active=True)
  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Node backgrounds
~~~~~~~~~~~~~~~~

You can find an example of a circle face in ETE4 here: `ete4_circleface.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/ete4_circleface.py>`_.

.. literalinclude:: ../../examples/smartview/node_background.py

.. figure:: ../../examples/smartview/node_background.png


Phylogenetic trees and sequence domains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/smartview/seq_motif_faces.py

.. figure:: ../../examples/smartview/seq_motif_faces.png



Note that the faces shown in this image are not static. When the tree
is viewed using the tree.show() method, you can interact with items.
