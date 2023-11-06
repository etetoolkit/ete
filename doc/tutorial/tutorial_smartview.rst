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

Explore interactive visualization of trees 
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
When running in interactive sessions such as IPython or Jupyter Notebooks, 
leave *keep_server* as default *False*.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

Showing node's properties in pop up
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Users can choose to show node's properties in pop up when mouse left-click on the node. 
By setting arguments in *include_props* and *exclude_props* `explore()` method, users can choose to show node's 
properties in pop up when mouse left-click on the node, uses can decide what 
properties to show in interface.

Example using *include_props*::
  
   from ete4 import Tree
   t = Tree()
   t.populate(10, random_branches=True)
   # includes node's properties "name", "dist" and "support" in pop up
   t.explore(include_props=("name", "dist", "support"), keep_server=True)

Or *exclude_props*::

  from ete4 import Tree
   t = Tree()
   t.populate(10, random_branches=True)
   # not showing node's properties "dist" and "support" in pop up
   t.explore(exclude_props=("dist", "support"), keep_server=True)

Control Panel
~~~~~~~~~~~~~
After trigging explore() method on target tree, a local browser will be activated where users can visualize targer tree.
When exploring the tree, a control panel will be shown in the left side of the tree panel.

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/control_panel.png?raw=true
   :alt: alternative text
   :align: center

It consists of the three major tabs:

- **Layout**: overrall setting of the tree layout including tree representation, collapse level, available TreeLayouts, etc.
- **Search & Selection**: to customize search and select nodes in the tree.
- **Advanced**: to control the advanced options of the tree visualization setting.

1) Layout Tab
^^^^^^^^^^^^^
Overrall
""""""""
Layout tab contains most of the general settings of the tree visualization. It includes:

- **tree**, name of the tree.

- **drawer**, drawer of the tree representation, *Rectangular* or *Circular*.

- **collapse**, the threshold of the vertical size in pixel, when the node's vertical size is smaller than the threshold, the node will be collapsed, default value is *10*.

- **ultrametric**, whether to draw ultrametric tree with edge lengths where all leaves are equidistant from the root, default *False*.

- **Layouts**, all available TreeLayouts in the tree, users can choose to activate or deactivate the TreeLayouts.

- **show minimap**, whether to show minimap in the tree interface(bottom-right), default *False*.

- **show tree scale legend**, whether to show tree scale legend in the tree interface(bottom-left), default *True*.

- **tooltip on hover**, whether to show tooltip when mouse hover on the node. If *False*, tooltip will be shown on left-click. Default *False*.

- **zoom around node**, If set to True, SmartView restricts the zoom-out level to maintain the node as the focal point, ensuring it remains clearly visible. The default setting is **True**.

- **zoom in aligned panel**, If set to True, users can zoom in the aligned panel for aligned node faces. The default setting is **False**.

- **select text**, whether is able to select text with cursor in the tree interface, default *False*.

- **Download**, users can download the tree information in **newick**, **svg** or **pdf** file in the tree interface by clicking the download tab from Control Panel.

- **Help**, help page for SmartView, including shortcuts.

Download 
""""""""
Users can download the tree information in **newick**, **svg** or **pdf** file in the tree interface by clicking the download tab from Control Panel.


2) Search & Selection Tab
^^^^^^^^^^^^^^^^^^^^^^^^^
Search & Selection tab contains the search and selection functions of the tree visualization. 
Users can start query with clicking *new search* button, then input the query in the search box. 
Each query will be saved in the search history, users can choose to modtify the visualizing setting for matching nodes or clades.

Simple search
"""""""""""""
Put a text in the search box to find all the nodes whose name matches it.
The search will be case-insensitive if the text is all in lower case, and case-sensitive otherwise.

Regular expression search
""""""""""""""""""""""""""
To search for names mathing a given regular expression, you can prefix your text with the command **/r** (the regexp command) and follow it with the regular expression.

Expression search 
"""""""""""""""""
When prefixing your text with /e (the eval command), you can use a quite general Python expression to search for nodes. This is the most powerful search method available (and the most complex to use).

The expression will be evaluated for every node, and will select those that satisfy it. In the expression you can use (among others) the following variables, with their straightforward interpretation: **node**, **parent**, **is_leaf**, **length** / **dist** / **d**, **properties** / **p**, **children** / **ch**, **size**, **dx**, **dy**, **regex**.

Topological search
""""""""""""""""""
Similar to the expression search, if you prefix your text with **/t** (the topological command), you can write a newick tree with quoted names in each node containing an eval command. This will select the nodes that satisfy the full subtree of expressions that you passed.

Examples of searches and possible matches
"""""""""""""""""""""""""""""""""""""""""

::

  citrobacter		will match nodes named "Citrobacter werkmanii" and "Citrobacter youngae"
      
  UBA		will match "spx UBA2009" but not "Rokubacteriales"
      
  /r sp\d\d		will match any name that contains "sp" followed by (at least) two digits, like "Escherichia sp002965065" and "Citrobacter sp005281345"
      
  /e d > 1		will match nodes with a length > 1
      
  /e is_leaf and p['species'] == 'Homo'		will match leaf nodes with property "species" equal to "Homo"
      
  /t ("is_leaf","d > 1")"name=='AB'"		will match nodes named "AB" that have two children, one that is a leaf and another that has a length > 1


3) Advanced Tab
^^^^^^^^^^^^^^^
For more advance set up for visualization.


Node Panel
~~~~~~~~~~
Interactive tree explorer allows users to perform various editing options on specific node. Once right-click on target node, it trigger node panel for selecting editing options.

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodepanel.png?raw=true
   :alt: alternative text
   :align: center

The node editor panel provides access to node-specific actions, such as creating subtrees, collapsing, pruning, rooting and more.


Customizing the aspect of trees
-------------------------------

Visualization customization is performed through four main elements: *TreeStyle*, *NodeStyle*, *Face*, and *TreeLayout*.

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
Here is the full list of attributtes that can be modified of node style, which is stored in `node.sm_style` :

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

Using `set_style()` method can add the node style of a node. 

Simple tree in which the same style is applied to all nodes::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, NodeStyle

  t = Tree('((A,B),C);')

  # Draw nodes as small red square of diameter equal fo 10 pixels
  triangle_node_style = NodeStyle()
  triangle_node_style["shape"] = "triangle"
  triangle_node_style["size"] = 10
  triangle_node_style["fgcolor"] = "red"

  # brown dashed branch lines with width equal to 2 pixels
  triangle_node_style["hz_line_type"] = 1
  triangle_node_style["hz_line_width"] = 2
  triangle_node_style["hz_line_color"] = "#964B00"

  # Applies the same static style to all nodes in the tree. Note that,
  def modify_node_style(node):
      node.set_style(triangle_node_style)
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

Source code can be found in in ETE4 here: `nodestyle_triangle.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/nodestyle_triangle.py>`_.


If you want to draw nodes with different styles, an independent
:class:`NodeStyle` instance must be created for each node. 

Simple tree in which the different styles are applied to each node::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, NodeStyle

  t = Tree('((a,b),c);')

  # Draw nodes as small red square of diameter equal fo 10 pixels
  # Create an independent node style for each node, which is
  # initialized with a red foreground color.
  leaf_style = NodeStyle()
  leaf_style["shape"] = "square"
  leaf_style["size"] = 10
  leaf_style["fgcolor"] = "red"

  # we set the foreground color to blue and the size to 30 for the root node
  root_style = NodeStyle()
  root_style["fgcolor"] = "blue"
  root_style["size"] = 30
  root_style["vt_line_type"] = 2
  root_style["vt_line_width"] = 10
  root_style["vt_line_color"] = "#964B00"

  # Draw nodes as small red square of diameter equal fo 10 pixels
  def modify_node_style(node):
      # Let's now modify the aspect of the leaf nodes
      if node.is_leaf:
          node.set_style(leaf_style)
      # Let's now modify the aspect of the root node
      # Check if the node is the root node
      elif node.is_root:
          node.set_style(root_style)
      else:
          pass
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
reference page. All node faces example with demonstration code can be found in 
https://github.com/dengzq1234/ete4_gallery. 



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

Example of all face positions

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_all.png?raw=true
   :alt: alternative text
   :align: center
Source code can be found in in ETE4 here: `faceposition_all.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/faceposition_all.py>`_.


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

  # here to modfiy node style directly inside the function
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

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/advance_layout_1.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `advance_layout.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/advance_layout.py>`_.


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
              # here to add text face to node in aligned position
              node.add_face(TextFace('vowel!', color="red"), column=0, position='aligned')

          else:
              node.sm_style['size'] = 5
              node.sm_style['fgcolor'] = 'blue'   
              
              # here to add text face to node in aligned position
              node.add_face(TextFace('not vowel!', color="blue"), column=0, position='aligned')


  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(name="MyTreeLayout", 
      ts=vowel_tree_style, 
      ns=vowel_node_layout,
      active=True, 
      aligned_faces=True)


  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Combined node styles, faces and tree style into one TreeLayout:

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/combinedlayout_basic.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `combinedlayout_basic.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/combinedlayout_basic.py>`_.


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

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/combinedlayout_basic.png?raw=true
   :alt: alternative text
   :align: center

Source code can be found in in ETE4 here: `combinedlayout_object.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/combinedlayout_object.py>`_.

Node Backgrounds
~~~~~~~~~~~~~~~~

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/node_backgrounds.png?raw=true
   :alt: alternative text
   :align: center


::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, NodeStyle, TextFace

  t = Tree('((((a1,a2),a3), ((b1,b2),(b3,b4))), ((c1,c2),c3));')

  # set background color for difference node style
  nst1 = NodeStyle()
  nst1["bgcolor"] = "LightSteelBlue"
  nst2 = NodeStyle()
  nst2["bgcolor"] = "Moccasin"
  nst3 = NodeStyle()
  nst3["bgcolor"] = "DarkSeaGreen"
  nst4 = NodeStyle()
  nst4["bgcolor"] = "Khaki"

  # find common ancestors
  n1 = t.common_ancestor(["a1", "a2", "a3"])
  n2 = t.common_ancestor(["b1", "b2", "b3", "b4"])
  n3 = t.common_ancestor(["c1", "c2", "c3"])
  n4 = t.common_ancestor(["b3", "b4"])

  # set color map dictionary
  colormap = {
      "ancestor_a": "LightSteelBlue",
      "ancestor_b": "Moccasin",
      "ancestor_c": "DarkSeaGreen",
      "ancestor_d": "Khaki"
  }

  def get_tree_style(colormap):
      def add_legend(tree_style):
          tree_style.add_legend(
              title = "MyLegend", 
              variable = "discrete", 
              colormap = colormap
              )
      return add_legend

  def get_background(node):
      # make node name with bigger text
      node.add_face(TextFace(node.name, min_fsize=6, max_fsize=25), column=0, position="branch_right")
      # set node style
      if node == n1:
          node.set_style(nst1)
      elif node == n2:
          node.set_style(nst2)
      elif node == n3:
          node.set_style(nst3)
      elif node == n4:
          node.set_style(nst4)
      return 

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(
      name="MyTreeLayout", 
      ns=get_background, 
      ts=get_tree_style(colormap),
      active=True)

  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Source code can be found in in ETE4 here: `node_backgrounds.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/node_backgrounds.py>`_.


Color Strip
~~~~~~~~~~~

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/colorstrip.png?raw=true
   :alt: alternative text
   :align: center

::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, RectFace, TextFace
  import random

  t = Tree('((((a1,a2),a3), ((b1,b2),(d1,d2))), ((c1,c2),c3));')

  # find common ancestors and annotate them
  n1 = t.common_ancestor(["a1", "a2", "a3"])
  n2 = t.common_ancestor(["b1", "b2"])
  n3 = t.common_ancestor(["c1", "c2", "c3"])
  n4 = t.common_ancestor(["d1", "d2"])
  n1.name = "ancestor_a"
  n2.name = "ancestor_b"
  n3.name = "ancestor_c"
  n4.name = "ancestor_d"

  # set color map dictionary
  colormap = {
      "ancestor_a": "LightSteelBlue",
      "ancestor_b": "Moccasin",
      "ancestor_c": "DarkSeaGreen",
      "ancestor_d": "Brown"
  }

  def get_tree_style(colormap):
      def add_legend(tree_style):
          tree_style.add_legend(
              title = "MyLegend", 
              variable = "discrete", 
              colormap = colormap
              )
          return
      return add_legend

  def get_node_face(colormap):
      def get_background(node):
          # make rectangle face
          if node.name in colormap:
              lca_face = RectFace(
                  width=20, 
                  height=None, # circular  
                  color=colormap.get(node.name),
                  opacity=0.7, 
                  text=node.name, 
                  fgcolor='white',
                  min_fsize=6, 
                  max_fsize=15, 
                  ftype='sans-serif',
                  padding_x=1, 
                  padding_y=1,
                  tooltip=None)
              lca_face.rotate_text = True
              node.add_face(lca_face, position='aligned', column=0)
              
          return
      return get_background
      

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(
      name="MyTreeLayout", 
      ns=get_node_face(colormap), 
      ts=get_tree_style(colormap),
      active=True,
      aligned_faces=True)

  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Source code can be found in in ETE4 here: `colorstrip.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/colorstrip.py>`_.


Outlined Collapsed Clade 
~~~~~~~~~~~~~~~~~~~~~~~~
.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/outline.png?raw=true
   :alt: alternative text
   :align: center

::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, RectFace, TextFace
  import random

  t = Tree('((((a1,a2),a3), ((b1,b2),(d1,d2))), ((c1,c2),c3));')

  # find common ancestors and annotate them
  n1 = t.common_ancestor(["a1", "a2", "a3"])
  n2 = t.common_ancestor(["b1", "b2"])
  n3 = t.common_ancestor(["c1", "c2", "c3"])
  n4 = t.common_ancestor(["d1", "d2"])
  n1.name = "ancestor_a"
  n2.name = "ancestor_b"
  n3.name = "ancestor_c"
  n4.name = "ancestor_d"

  # set color map dictionary
  colormap = {
      "ancestor_a": "LightSteelBlue",
      "ancestor_b": "Moccasin",
      "ancestor_c": "DarkSeaGreen",
      "ancestor_d": "Brown"
  }

  def get_tree_style(colormap):
      def add_legend(tree_style):
          tree_style.add_legend(
              title = "MyLegend", 
              variable = "discrete", 
              colormap = colormap
              )
          return
      return add_legend

  def get_node_face(colormap):
      def get_background(node):
          # make outline face
          if node.name in colormap:
              lca_face = RectFace(
                  width=20, 
                  height=None, # circular  
                  color=colormap.get(node.name),
                  opacity=0.7, 
                  text=node.name, 
                  fgcolor='white',
                  min_fsize=6, 
                  max_fsize=15, 
                  ftype='sans-serif',
                  padding_x=1, 
                  padding_y=1,
                  tooltip=None)
              lca_face.rotate_text = True

              # collapsed nodes
              node.sm_style["draw_descendants"] = False
              node.sm_style["outline_color"] = colormap.get(node.name)

              # show text face
              node.add_face(lca_face, position='aligned', column=0)
              # show text face even for collapsed nodes
              node.add_face(lca_face, position='aligned', collapsed_only=True)
              
          return 
      return get_background
      

  # Create a TreeLayout object, passing in the function
  tree_layout = TreeLayout(
      name="MyTreeLayout", 
      ns=get_node_face(colormap), 
      ts=get_tree_style(colormap),
      active=True,
      aligned_faces=True)

  layouts = []
  layouts.append(tree_layout)
  t.explore(keep_server=True, layouts=layouts)

Source code can be found in in ETE4 here: `outline.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/outline.py>`_.


Bar Plot
~~~~~~~~

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/barplot.png?raw=true
   :alt: alternative text
   :align: center


Example ::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, RectFace, TextFace, ScaleFace
  import random

  t = Tree()
  t.populate(20, random_branches=True)

  # annotate numerical values to each leaf
  for node in t.leaves():
      node.add_prop('count', random.randint(1, 100))

  # define tree style function
  def layout_tree_style(tree_style):
      # add scale bar to footer
      scaleface = ScaleFace(
          name='sample1', 
          width=150, 
          color='black',
          scale_range=(0, 100), 
          tick_width=80, 
          line_width=1,
          formatter='%.0f',
          min_fsize=6, 
          max_fsize=12, 
          ftype='sans-serif',
          padding_x=0, 
          padding_y=0)

      tree_style.aligned_panel_header.add_face(scaleface, column=0)
      tree_style.aligned_panel_footer.add_face(scaleface, column=0)

      # add title to header and footer
      text = TextFace("Count", min_fsize=5, max_fsize=12, width=50, rotation=0)
      tree_style.aligned_panel_header.add_face(text, column=0)    
      return 

  # define node Face layout function
  def layout_barplot(node):
      if node.is_leaf:
          width = node.props.get('count') * 1.5
          rect_face = RectFace(
              width=width, height=70, color='skyblue',
              opacity=0.7, text=None, fgcolor='black',
              min_fsize=6, max_fsize=15, ftype='sans-serif',
              padding_x=0, padding_y=0,
              tooltip=None)
          node.add_face(rect_face, position='aligned', column=0)
          return 

  # Create a TreeLayout object, passing in the function
  barplot_layout = TreeLayout(
      name='BarPlot',
      ns=layout_barplot, 
      ts=layout_tree_style,
      aligned_faces=True)

  # add layout to layouts list
  layouts = []
  layouts.append(barplot_layout)
  t.explore(
      layouts=layouts, 
      include_props=("name", "dist", "length"),
      keep_server=True)



Source code can be found in in ETE4 here: `barplot.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/barplot.py>`_.

Heatmap
~~~~~~~


.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/heatmap.png?raw=true
   :alt: alternative text
   :align: center


Example ::

  import matplotlib as mpl
  import numpy as np

  from ete4 import Tree
  from ete4.smartview import TreeLayout, RectFace, TextFace
  import random


  t = Tree()
  t.populate(20, random_branches=True)

  # annotate numerical values to each leaf
  for node in t.leaves():
      node.add_prop('frequence', random.random())

  # define tree style function
  def layout_tree_style(tree_style):
      # add title to header and footer
      text = TextFace("Frequence", min_fsize=5, max_fsize=12, width=50, rotation=0)
      tree_style.aligned_panel_header.add_face(text, column=0)
      
      tree_style.add_legend(
              title = "Frequence", 
              variable='continuous', 
              value_range=[0, 1],
              color_range=["darkred", "white"]
              )    
      return 

  # define node Face layout function
  def layout_heatmap(mincolor, maxcolor):
      #maxval = max(node.props.get('frequence') for node in t.leaves())
      maxval = 1
      minval = 0

      def color_gradient(c1, c2, mix=0):
          """ Fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1) """
          c1 = np.array(mpl.colors.to_rgb(c1))
          c2 = np.array(mpl.colors.to_rgb(c2))
          return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

      def get_heatmapface(node):
          if node.is_leaf:
              ratio = float(node.props.get('frequence')) / maxval
              gradient_color = color_gradient(mincolor, maxcolor, mix=ratio)
              print_frequnce = f"{node.props.get('frequence'):.2%}"
              rect_face = RectFace(
                  width=50, height=70, color=gradient_color,
                  opacity=0.7, text=print_frequnce, fgcolor='black',
                  min_fsize=6, max_fsize=15, ftype='sans-serif',
                  padding_x=0, padding_y=0,
                  tooltip=None)
              node.add_face(rect_face, position='aligned', column=0)
          return 
      return get_heatmapface

  # Create a TreeLayout object, passing in the function
  barplot_layout = TreeLayout(
      name='HeatMap',
      ns=layout_heatmap(mincolor='white', maxcolor='darkred'), 
      ts=layout_tree_style,
      aligned_faces=True)

  # add layout to layouts list
  layouts = []
  layouts.append(barplot_layout)
  t.explore(
      layouts=layouts, 
      include_props=("name", "dist", "frequence"),
      keep_server=True)

Source code can be found in in ETE4 here: `heatmap.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/heatmap.py>`_.

Visualize Multiple Sequence Alignment and Domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Link to Multiple Sequence Alignment

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/msa_layout.png?raw=true

::


  from ete4 import Tree
  from ete4.smartview import TreeLayout, SeqFace, AlignmentFace


  TREEFILE = 'data/tree.nw'
  MSA = 'data/tree.aln.faa'


  t = Tree(open(TREEFILE))


  def get_seqs(fastafile):
      """Read a fasta file and return a dict with d[description] = sequence.

      Example output: {'Phy003I7ZJ_CHICK': 'TMSQFNFSSAPAGGGFSFSTPKT...', ...}
      """
      name2seq = {}
      seq = ''
      for line in open(fastafile):
          if line.startswith('>'):
              if seq:
                  name2seq[head] = seq
                  seq = ''
                  head = line.lstrip('>').rstrip()
              else:
                  head = line.lstrip('>').rstrip()
          else:
              seq += line.rstrip()
      name2seq[head] = seq
      return name2seq



  # get information alignment 
  name2seq = get_seqs(MSA)


  for leaf in t:
      leaf.add_prop('seq', name2seq[leaf.name])


  def layout_alnface_gray(node):
      if node.is_leaf:
          seq_face = AlignmentFace(
              node.props.get('seq'),
              seqtype='aa', gap_format='line', seq_format='[]',
              width=800, height=None,
              fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
              gap_linewidth=0.2,
              max_fsize=12, ftype='sans-serif',
              padding_x=0, padding_y=0)

          node.add_face(seq_face, position='aligned')
      return

  def layout_alnface_compact(node):
      if node.is_leaf:
          seq_face = AlignmentFace(
              node.props.get('seq'),
              seqtype='aa', gap_format='line', seq_format='compactseq',
              width=800, height=None,
              fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
              gap_linewidth=0.2,
              max_fsize=12, ftype='sans-serif',
              padding_x=0, padding_y=0)

          node.add_face(seq_face, position='aligned')
      return

  def layout_seqface(node):
      if node.is_leaf:
        
          seq_face = SeqFace(
              node.props.get('seq'),
              seqtype='aa', poswidth=1, 
              draw_text=True, max_fsize=15, ftype='sans-serif',
              padding_x=0, padding_y=0)

          node.add_face(seq_face, position='aligned')
      return


  layouts = [
      TreeLayout(name='compact_aln', ns=layout_alnface_compact, aligned_faces=True),
      TreeLayout(name='gray_aln', ns=layout_alnface_gray, aligned_faces=True, active=False),
      TreeLayout(name='seq', ns=layout_seqface, aligned_faces=True,  active=False),
      
  ]

  t.explore(layouts=layouts, keep_server=True)

Source code can be found in in ETE4 here: `msa_layout.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/msa_layout.py>`_.

Domain annotation
~~~~~~~~~~~~~~~~~

.. image:: https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/domain_layout.png?raw=true

::

  from ete4 import Tree
  from ete4.smartview import TreeLayout, SeqFace, SeqMotifFace, AlignmentFace

  # Create a random tree and add to each leaf a random set of motifs
  # from the original set
  t = Tree("((A, B, C, D, E, F, G), H, I);")

  seq = ("-----------------------------------------------AQAK---IKGSKKAIKVFSSA---"
        "APERLQEYGSIFTDA---GLQRRPRHRIQSK-------ALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSN"
        "ISSVSSLLLFNTTENLYKKYVFLDPLAG----THVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPD"
        "LGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTP"
        "AHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIR"
        "QAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHL--MSDLFNKLVMRRKGISGKGPGAGDGPGGAFA"
        "RVSDSIPPLPPPQQPQAEDED----")

  mixed_motifs = [
          # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
          [10, 100, "[]", None, 20, "black", "rgradient:blue", "arial|8|white|long text clipped long text clipped"],
          [101, 150, "o", None, 20, "blue", "pink", None],
          [155, 180, "()", None, 20, "blue", "rgradient:purple", None],
          [160, 190, "^", None, 24, "black", "yellow", None],
          [191, 200, "<>", None, 22, "black", "rgradient:orange", None],
          [201, 250, "o", None, 22, "black", "brown", None],
          [351, 370, "v", None, 25, "black", "rgradient:gold", None],
          [370, 420, "compactseq", 5, 10, None, None, None],
  ]

  simple_motifs = [
          # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
          [10, 60, "[]", None, 20, "black", "rgradient:blue", "arial|8|white|long text clipped long text clipped"],
          [120, 150, "o", None, 20, "blue", "pink", None],
          [200, 300, "()", None, 20, "blue", "red", "arial|8|white|hello"],
  ]

  box_motifs = [
          # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
          [0,  5, "[]", None, 20, "black", "rgradient:blue", "arial|8|white|10"],
          [10, 25, "[]", None, 20, "black", "rgradient:ref", "arial|8|white|10"],
          [30, 45, "[]", None, 20, "black", "rgradient:orange", "arial|8|white|20"],
          [50, 65, "[]", None, 20, "black", "rgradient:pink", "arial|8|white|20"],
          [70, 85, "[]", None, 20, "black", "rgradient:green", "arial|8|white|20"],
          [90, 105, "[]", None, 20, "black", "rgradient:brown", "arial|8|white|20"],
          [110, 125, "[]", None, 20, "black", "rgradient:yellow", "arial|8|white|20"],
  ]

  def layout_domain(node):
      if node.name == 'A':
          seq_face = SeqMotifFace(seq, width=1000, gapcolor="red")
          node.add_face(seq_face, position='aligned')
      elif node.name == 'B':
          seq_face = SeqMotifFace(seq, seq_format="line", width=1000, gap_format="blank")
          node.add_face(seq_face, position='aligned')
      elif node.name == 'C':
          seq_face = SeqMotifFace(seq, seq_format="line", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'D':
          seq_face = SeqMotifFace(seq, seq_format="()", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'E':
          seq_face = SeqMotifFace(seq, motifs=simple_motifs, seq_format="-", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'F':
          seq_face = SeqMotifFace(seq, motifs=simple_motifs, gap_format="blank", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'G':
          seq_face = SeqMotifFace(seq, motifs=mixed_motifs, seq_format="-", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'H':
          seq_face = SeqMotifFace(seq=None, motifs=box_motifs, gap_format="line", width=1000)
          node.add_face(seq_face, position='aligned')
      elif node.name == 'I':
          seq_face = SeqMotifFace(seq[30:60], seq_format="seq")
          node.add_face(seq_face, position='aligned')
      return

  layouts = [
      TreeLayout(name='layout_domain', ns=layout_domain, aligned_faces=True),    
  ]
  t.explore(layouts=layouts, keep_server=True)

Source code can be found in in ETE4 here: `domain_layout.py example <https://github.com/dengzq1234/ete4_gallery/blob/master/smartview/domain_layout.py>`_.
