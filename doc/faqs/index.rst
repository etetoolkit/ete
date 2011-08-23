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
 

How do I visit all leaves within a tree?
-----------------------------------------------------------------
:: 

  for node in t.iter_leaves():
      print node.name


What's the difference between **get_leaves()** and **iter_leaves()**?
-----------------------------------------------------------------------

