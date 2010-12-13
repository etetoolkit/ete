.. module:: ete_dev.treeview
  :synopsis: Display and rendering capabilities: it provides the programmable tree drawing engine and the Graphical User Interface to interact with trees
.. moduleauthor:: Jaime Huerta-Cepas
:Author: Jaime Huerta-Cepas


************************************
The Programmable Tree Drawing Engine
************************************

ETE's treeview extension provides a highly programmable drawing system to render
any hierarchical tree structure into a custom image. Although a number or
predefined visualization layouts are included with the default installation,
custom styles can be easily created from scratch. To do so, ETE makes use of
there main concepts (node** styles**, node** faces** and **layout** functions),
which allow the user to define the rules in which trees are rendered. Briefly, a
node** style** defines the general aspect of a given tree node (size, color,
background, line type, etc.). Node **faces** are small graphical pieces
(representing, for instance, any node's extra information) that are added to
nodes and that drawn at the same node position. Finally, **layouts functions**
are custom python functions that define the rules on how faces and styles are
added to nodes when they are going to be drawn. By combining this elements, the
aspect of trees can be controlled by custom criteria.

Treeview extension provides an interactive Graphical User Interface (GUI) to
visualize trees using custom layouts. Alternatively, images can be directly
rendered as PNG or PDF files. Every node within a given tree structure has its
own **show() **and** render()** methods, thus allowing to visualize or render
its subtree structure.


Interactive visualization of trees
==================================

ETE's tree drawing engine is fully integrated with a built-in graphical user
interface (GUI). Thus, ETE allows to render tree structures directly on an
interactive interface that can be used to explore and manipulate trees node's
properties and topology. The GUI is based on Qt4 , a cross platform and open
source application and UI framework which allows to handle, virtually, images of
any size. Of course, this will depend on you computer and graphical card
performance.

To start the visualization of a given tree or subtree, you can simply call the
**show() **method present in every node:

One of the advantages of this on-line GUI visualization is that you can use it
to interrupt a given program/analysis, explore trees, manipulate them, and
continuing with the execution thread. Note that **changes made using the GUI
will be kept in the tree structure after quiting the visualization interface
**(Figure :ref:`fig:gui tree manipulation`). This feature is specially useful
for using during python sessions, in which analyses are performed interactively.

The GUI allow many operations to be performed graphically, however it does not
implement all the possibilities of the programming toolkit. These are some of
the allowed GUI options:


Render trees into image files
=============================

Alternatively, images can be directly written info a file. PNG and PDF formats
are supported. While PNG will store only a normal image, PDF will keep vector
graphics format, thus allowing to better edit or resize images using the proper
programs (Such as inkscape in GNU/linux).

To generate an image, the **render()** method should be used instead of
**show()**. The only required argument is the file name, which will determine
the final format of the file (.pdf or .png). By default, the resulting image is
scaled to 7 inches, approximately the width of an A4 paper. However, you can
change this by setting a custom width and height. If only one of this values is
provided, the other is imputed to keep the original aspect ratio.


Customizing tree aspect
=======================

There are three basic elements that control the general aspect of trees:
**node's style**, **node's faces** and **layouts functions**. In brief, layout
functions can be used to set the rules that control the way in which certain
nodes are drawn (setting its style and adding specific faces).


styles
------

A '**style**' is a set of special node attributes that are used by the drawing
algorithm to set the colours, and general aspect of nodes and branches. Styles
are internally encoded as python dictionaries. Each node has its own style
dictionary, which is accessible as **node.img_style**. A default style is
associated to every tree node, but you can modify them at any time. Note that
**nodes styles must only be modified inside a layout function**. Otherwise,
custom settings may be missing or overwritten by default values.


Faces
-----

**Node's faces** are more sophisticated drawing features associated to nodes.
They represent independent images that can be linked to nodes, usually
representing a given node's feature. Faces can be loaded **from external image
files**, **created from scratch** using any drawing library, **or generated as
text labels**.

The complexity of faces may go from simple text tags to complete plots showing
the average expression pattern associated to a given partition in a microarray
clustering tree. Given that faces can be loaded from external images and added
*on the fly*, any way of producing external images could be easily connected to
the drawing engine. For instance, the statistical framework R could be used to
analyze a given node's property, and to generate a plot that can be used as a
node's face.

To create a face, the following general constructors can be used, which are
**available through the face module**:

.. % 

Once a face is created, it can be linked to one or more nodes. To do so, you
must use the **add_face_to_node() **method within the** faces** module. By doing
this, when a node is drawn, their linked faces will be drawn beside it. Since
several faces can be added to the same node, you must specify the relative
position in which they will be placed. Each node reserves a virtual space that
controls how faces are positioned. The position of each face is determined by an
imaginary grid at the right side of each node (Figure :ref:`fig:faces
positions`). Each column from the grid is internally treated as a stack of
faces. Thus, faces can be added to any column and its row position will be
determined by insertion order: **first inserted is first row**. In the case of
trees leaves, nodes can handle an independent list of faces that will be drawn
aligned with the farthest leaf in the tree. To add an aligned face you can use
the **aligned=True **argument** **when calling the **add_face_to_node()**
method. By knowing this rules, you can easily fill virtual node grids with any
external image or text label and the algorithm will take care of positioning.
Note that** add_face_to_node()** must only be used inside a layout function.

.. % 


layouts
-------

**Layout functions** are the key component of the tree drawing customization.
Any python function accepting a node instance as a first argument can be used as
a layout function. Essentially, such function will be called just before drawing
each tree node, so you can use it perform any operation prior to render nodes.
In practice, layout functions are used to define the set of rules that control
nodes style attributes and the faces that will be linked to them. Of course,
such rules can be based on a previous node analysis. For instance: ``if node has
more than 5 descendants, then add a text label, set a different background
color, perform an analysis on leaves and associate an external image`` with
node. As you imagine, rules can be are as sophisticated as you want. Thus, the
advantage of this method is that you can create your own drawing algorithms to
render trees dynamically and fitting very specific needs.

In order to apply your custom layouts functions, function's name (the reference
to it) can be passed to both **render()** and **show()** methods:
``node.render(``\ filename.pdf'', layout=mypythonFn) ``**or**``
node.show(layout=mypythonFn)``.


Example: combining styles, faces and layouts
--------------------------------------------
