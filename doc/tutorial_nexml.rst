.. module:: ete_dev.nexml
  :synopsis: Reading and writing support support for the NexML format
.. moduleauthor:: Jaime Huerta-Cepas
.. versionadded:: 2.1

************************
NeXML 
************************

NeXML(http://nexml.org) is an exchange standard for representing
phyloinformatic data inspired by the commonly used NEXUS format, but
more robust and easier to process.

----------------------------
Reading a Nexml project
----------------------------

You can load an external Nexml project by using the :class:`Nexml`
base class and the :func:`Nexml.build_from_file` method. The automatic
parser will read the provided XML file and convert all elements into
python instances, which will be hierarchically connected to the Nexml
root instance.

Note that all Nexml elements have a python class that represent their
attributes. Thus, each element in a Nexml file will be loaded as a
python object that will contain "set" and "get" methods for all their
attributes.

tree instances are mixed objects containing all ETE tree functionality
plus Nexml attributes. 

::

   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()

   # Upload content from file
   nexml_project.build_from_file("nexml_example.xml")

   # All XML elements are within the project instance.
   # exist in each element to access their attributes.
   print nexml_projects.get_otus()

   # Trees can be also accesed 
   trees_collections = nexml_projects.get_trees()
   collection_1 = trees_collection[0]
   tree_1 = collection_1.get_trees()[0]

   # And they are seen as normal ETE tree objects
   print tree_1

In Nexml, a trees are represented as plain lists of nodes and
edges. ETE will convert such lists into tree topologies, in which
every node will contain a :attr:`nexml_node` and :attr:`nexml_edge`
attribute. They will contain all nexml functionality and annotation.

In addition, each tree node has a :attr:`nexml_tree` attribute, which
can be used to set the nexml properties of the subtree represented by
each node. 


--------------------------------------
Writing NeXML objects
--------------------------------------

Every NexML object has its own :func:`export` method. By calling it,
you can obtain the XML representation of any instance contained in the
Nexml project structure. 

Usually, all you will need is to export the whole project. 

::

   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()

   # Upload content from file
   nexml_project.build_from_file("nexml_example.xml")

   # All XML elements are within the project instance.
   # exist in each element to access their attributes.
   print nexml_projects.get_otus()

   # Trees can be also accesed 
   trees_collections = nexml_projects.get_trees()
   collection_1 = trees_collection[0]
   tree_1 = collection_1.get_trees()[0]

   nexml_project.export()




------------------------------------
Creating Nexml project from scratch 
------------------------------------

:class:`Nexml` base class can also be used to create projects from scratch
in a programmatic way. Using the collection of NeXML classes provided
by the **nexml** module, you can populate an empty project and export
it as XML. 

::

   from ete2 import Nexml # Root project class 
   # the module contains all classes representing nexml elements
   from ete2 import nexml 

   # Create an empty Nexml project 
   nexml_project = Nexml()
   tree_collection = nexml.Trees()
   nexml_tree = nexml.NexMLTree()
   nexml_tree.populate(10) # Random tree with 10 leaves
   tree_collection.add_tree(nexml_tree)
   nexml_project.add_trees(tree_collection)


Note that trees can be also read from newick files, allowing the
conversion between both formats.

::

   from ete2 import Nexml # Root project class 
   # the module contains all classes representing nexml elements
   from ete2 import nexml 

   # Create an empty Nexml project 
   nexml_project = Nexml()
   tree_collection = nexml.Trees()
   nexml_tree = nexml.NexMLTree()
   nexml_tree.populate('(((a:0.9,b:0.5),c:1.3):1.2;') # You can also pass a file name
   tree_collection.add_tree(nexml_tree)
   nexml_project.add_trees(tree_collection)
   

