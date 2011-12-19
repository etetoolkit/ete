Frequently Asked Questions (FAQs)
**********************************

GENERAL
============

How do I use ETE?
-----------------------------------------------------------------

From 2.1 version, ETE includes a basic standalone program that can be
used to quickly visualize your trees. Type ``ete2`` in a terminal to
access the program.

However, ETE is not a standalone program. The ``ete2`` script is a
very simple implementation and does not allow for fancy customization. 

The main goal of ETE is to provide a Python programming library, so
you can create your own scripts to manipulate and visualize
phylogenetic trees. Many examples are available `here
<http:://ete.cgenomics.org/releases/ete2/examples-ete2.tar.gz>`_ and
along the ETE tutorial.


Can ETE draw circular trees?
----------------------------------

Yes, starting from version 2.1, ete can render trees in circular
mode. Install the latest version from
http://pypi.python.org/pypi/ete_dev or by executing ``easy_install -U
ete_dev``.

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
-----------------------------------------------------------------

There are many ways, but this is the easiest one:

:: 

  for node in t.traverse():
      print node.name

Can I control the order in which nodes are visited?
-----------------------------------------------------------------

Yes, currently 3 strategies are implemented: pre-order, post-order and
level-over. You can check the differences at
http://packages.python.org/ete2/tutorial/tutorial_trees.html#traversing-browsing-trees
      

How do I visit all leaves within a tree?
-----------------------------------------------------------------
:: 

  for node in t.iter_leaves():
      print node.name


What's the difference between **get_leaves()** and **iter_leaves()**?
-----------------------------------------------------------------------

All get\_ methods (get_leaves, get_descendants, etc.) return an
independent list of items. This means that tree traversing is fully
performed before returning the result.  In contrast, iter\_ methods
return one item at a time, saving memory and, increasing the
performance of some operations.

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


How do I export tree images as SVG
-----------------------------------------------------------------

Image format is automatically detected from the filename extension.
The following code will automatically render the tree as a vector
image.

::
                
        tree.render("mytree.svg")

