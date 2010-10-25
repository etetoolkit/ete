**************  
Phylogenetic XML standards
**************

==============
Description
==============

From version 2.1, ETE provides support for NeXML and PhyloXML
phylogenetic XML standards, both reading and writing. 

These standards are not limited to phylogenetic tree data, but ETE
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


--------------
Reading Nexml projects
--------------

You can load an external Nexml project by using the **Nexml** base
class and the **build_from_file()** method. The automatic parser will
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


--------------
Creating Nexml projects
--------------

**Nexml** base class can also be used to create projects from scractch
in a programmatic way. Using the collection of NeXML classes provided
by the **nexml** module, you can populate an empty project and export
it as XML. 


::

   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()
   


You can export your project using NeXML format at any time by using
the **export()** function




.. figure:: ./reconcilied_tree.png
   :alt: map to buried treasure

=============
PhyloXML
=============

PhyloXML is a novel standard whose design allows to encode many
phylogenetic data. 
