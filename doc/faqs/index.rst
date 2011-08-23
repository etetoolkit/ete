Frequently Asked Questions (FAQs)
**********************************

GENERAL
============

How do I start ETE?
-----------------------------------------------------------------

ETE is not a standalone program, so you cannot just start it. ETE is a
Python library, so you will need to create your own scripts and use
ETE as a module (i.e. from ete2 import Tree).

However, many example files are available. Many can be directly
executed to perform specific actions, while others can be used as
templates to learn how to perform certain actions.

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

All "get_" methods (get_leaves, get_descendants, etc.) return an
independent list of items. This means that tree traversing is fully
performed before returning the result.  In contrast, "iter_" methods
return one item at a time, saving memory and, increasing the
performance of some operations.

Note also that tree topology cannot be modified while iterating
methods are being executed. This limitation does not apply for "get_"
methods.

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


Can ETE draw circular trees?
----------------------------------

Yes, starting from version 2.1, ete can render trees in circular
mode. Currently, ETE version 2.1 is being tested and documented, but
you can download it and use from http://pypi.python.org/pypi/ete2a1 or
by executing "easy_install -U ete2a1".

