************************************  
Phylogenetic XML standards
************************************
.. versionadded:: 2.1

From version 2.1, ETE has support for NeXML and PhyloXML phylogenetic
XML standards, both for reading and writing.

These standards allow to encode complex phylogenetic data, and they
are not limited to trees. However, although ETE is mainly focused on
allowing transparent interaction with the trees encoded in such data
formats, it also provides basic support for many other features.

Essentially, NexML and PhyloXML formats are internally represented as
projects. Each XML instance can be loaded into ETE as a python object
using the corresponding module. Project objects are expected to follow
the hierarchical structure of the original XML schema. Trees within
projects will be represented as fully functional ETE tree objects.

Thus, while phylogenetic trees encoded using NeXML or PhyloXML formats
can be accessed as a normal ETE tree objects, other elements
(i.e. otus, metadata, annotation.) will be also accessible as basic
python instances.

NeXML and PhyloXML python parsers are possible thanks to the work of
Dave Kulhman on the generateDS.py application. 

=============
Nexml
=============

NeXML(http://nexml.org) is an exchange standard for representing
phyloinformatic data inspired by the commonly used NEXUS format, but
more robust and easier to process.

----------------------------
Reading a Nexml project
----------------------------

You can load an external Nexml project by using the :class:`Nexml`
base class and the :func:`build_from_file` method. The automatic
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
Export projects to XML format
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
   


=============
PhyloXML
=============

PhyloXML (http://www.phyloxml.org/) is a novel standard used to encode
phylogenetic information. In particular, phyloXML is designed to
describe phylogenetic trees (or networks) and associated data, such as
taxonomic information, gene names and identifiers, branch lengths,
support values, and gene duplication and speciation events.

----------------------------------------
Loading PhyloXML projects from files 
----------------------------------------

ETE provides full support for phyloXML projects. Phylogenies are
integrated as ETE's tree data structures, while the rest of features
are represented as simple classes handling basic reading and writing
operations.

:: 

   from ete2 import Phyloxml
   project = Phyloxml()
   project.build_from_tree("phyloxml_example.xml")

   # Each tree contains the same methods as a PhyloTree object
   for tree in project.phylogenies: 
       print tree
       # you can even use rendering options
       tree.show()
       # PhyloXML features are stored in the phyloxml_clade attribute
       print tree.phyloxml_clade

Each tree node contains two phyloxml elements, :attr:`phyloxml_clade`
and :attr:`phyloxml_phylogeny`. The first attribute contains clade
information referred to the node, while phyloxml_phylogeny contains
general data about the subtree defined by each node. This way, you can
split, or copy any part of a tree and it will be exported as a
separate phyloxml phylogeny instance.

:: 
 
   from ete2 import Phyloxml
   import random 

   project = Phyloxml()
   phylo = PhyloXMLTree()
   phylo.populate(100)
   phylo.phyloxml_phylogeny.add
   project.add_phylogeny(phylo)

   # Let's now add another phylogeny bases on a subtree of the original "phylo" tree
   all_internal_nodes =  [n for n in phylo.get_descendants() if not n.is_leaf()]
   random_node = random.sample(all_internal_nodes, 1)[0]

   random_node.phyloxml_phylogeny.add_
   project.add_phylogeny(random_node)


----------------------------------------
Creating PhyloXML projects from scratch
----------------------------------------

In order to create new PhyloXML projects, a set of classes is
available in the :mod:`phyloxml` module.

:: 

  from ete2 import Phyloxml, phyloxml
  # create empty project 
  proj = Phyloxml()
  phylogeny = phyloxml.PhyloxmlTree()
  phylogeny.populate(10)
  proj.add_phylogeny(phylogeny)
  
