************************************  
Phylogenetic XML standards
************************************
.. versionadded:: 2.1

From version 2.1, ETE has support for NeXML and PhyloXML phylogenetic
XML standards, both reading and writing.

These standards provide a way to encode complex phylogenetic data,
therefore they are not limited to phylogenetic trees. Although ETE is
focused on allowing transparent interaction with the trees encoded by
such data formats, it also has basic support for other features. Thus,
while any phylogenetic tree encoded using NeXML or PhyloXML formats
will be seen as a normal ETE tree object, other elements (otus information )

, enabling tree drawing,
browsing and manipulation options.




are not limited to phylogenetic tree data, but ETE
provides handlers to deal with most of their features.

Consequently, these standards are not treated as simple tree formats
(like newick), but as phylogenetic data projects, containing or not
phylogenetic trees.  In practice, you will notice that not Nexml nor
PhyloXML are included as core parser, but as independent ETE modules.

Nexml and PhyloXML modules follow a similar design. A base class
exists for each standard. 

By creating instances of such classes, you can create empty
projects. Subsequently, the project can be built using external data
from xml files, or manually populated.

=============
Nexml
=============

NeXML is a novel standard whose design allows to encode many
phylogenetic data, which is highly integrated with ETE tree
features. This is, when a NeXML project is loaded, any available tree
is converted into a ETE tree, thus enabling all drawing, and browsing
options. Note that, although NeXML tree definition does not follow a
hierarchical design, tree objects will transparently be perceived as
hierarchical.

Other available data encoded in the project will be converted into
Python instances that can also be operated. Thus, each element found
in given XML file will have a python instance that can be used to set
or read their attributes.


----------------------------
Reading Nexml projects
----------------------------

You can load an external Nexml project by using the :class:`Nexml` base
class and the :func:`build_from_file` method. The automatic parser will
read the provided XML file and convert all elements into python
instances, which :will: be hierarchilly connected to the Nexml root
object.

::

   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()

   # Upload content from file
   nexml_project.build_from_file("../nexml_example.xml")

   # All XML elements hang from the root element. get and set methods
   # exist in each element to access their attributes.
   print   nexml_projects.get_otus()

   # Trees can be also accesed 
   trees_collections = nexml_projects.get_trees()
   collection_1 = trees_collection[0]
   tree_1 = collection_1.get_trees()[0]

   # And they are seen as normal ETE tree objects
   print tree_1


----------------------------
Creating Nexml projects
----------------------------

:class:`Nexml` base class can also be used to create projects from scractch
in a programmatic way. Using the collection of NeXML classes provided
by the **nexml** module, you can populate an empty project and export
it as XML. 


::

   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()
   


You can export your project using NeXML format at any time by using
the :func:`export` function


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
  proj.add_phylogeny()






.. automodule:: ete_dev.phyloxml._phyloxml
   :members:

##   :undoc-members:

# Example of how to add images

.. figure:: ./reconcilied_tree.png
   :alt: map to buried treasure



