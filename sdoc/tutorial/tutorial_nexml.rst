.. moduleauthor:: Jaime Huerta-Cepas

.. versionadded:: 2.1

.. currentmodule:: ete2

NeXML 
************************

NeXML(http://nexml.org) is an exchange standard for representing
phyloinformatic data inspired by the commonly used NEXUS format, but
more robust and easier to process.


Reading NeXML projects
----------------------------

Nexml projects are handled through the :class:`Nexml` base class.  To
load a NexML file, the :func:`Nexml.build_from_file` method can be
used. 

:: 

  from ete2 import Nexml

  nexml_prj = Nexml()
  nexml_prj.build_from_file("/path/to/nexml_example.xml")


Note that the ETE parser will read the provided XML file and convert
all elements into python instances, which will be hierarchically
connected to the Nexml root instance.

Every NeXML XML element has its own python class. Content and
attributes can be handled through the "set_" and "get_" methods
existing in all objects. Nexml classes can be imported from the
:mod:`ete2.nexml` module.

:: 

  from ete2 import Nexml, nexml
  nexml_prj = Nexml()
  nexml_meta = nexml.LiteralMeta(datatype="double", property="branch_support", content=1.0)
  nexml_prj.add_meta(nexml_meta)
  nexml_prj.export()

  # Will produce:
  #
  # <Nexml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Nexml">
  #    <meta datatype="double" content="1.0" property="branch_support" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="LiteralMeta"/>
  # </Nexml>

NeXML trees
==============

NeXML tree elements are automatically converted into
:class:`PhyloTree` instances, containing all ETE functionality
(traversing, drawing, etc) plus normal NeXML attributes.

In the Nexml standard, trees are represented as plain lists of nodes
and edges. ETE will convert such lists into tree topologies, in which
every node will contain a :attr:`nexml_node` and :attr:`nexml_edge`
attribute. In addition, each tree node will have a :attr:`nexml_tree`
attribute (i.e. ``NEXML->FloatTree``) , which can be used to set the
nexml properties of the subtree represented by each node. Note also
that :attr:`node.dist` and :attr:`node.name` features will be linked
to :attr:`node.nexml_edge.length` and :attr:`node.nexml_node.label`,
respectively.

.. literalinclude:: ../../examples/nexml/nexml_parser.py

:download:`[Download tolweb.xml example]  <../../examples/nexml/trees.xml>` ||
:download:`[Download script]  <../../examples/nexml/nexml_parser.py>`

Node meta information is also available:

.. literalinclude:: ../../examples/nexml/nexml_annotated_trees.py 

:download:`[Download tolweb.xml example]  <../../examples/nexml/tolweb.xml>` || 
:download:`[Download script]  <../../examples/nexml/nexml_annotated_trees.py>`

------------------------------------
Creating Nexml project from scratch 
------------------------------------

:class:`Nexml` base class can also be used to create projects from
scratch in a programmatic way. Using the collection of NeXML classes
provided by the:mod:`ete2.nexml` module, you can populate an empty
project and export it as XML.

.. literalinclude:: ../../examples/nexml/nexml_from_scratch.py

:download:`[Download script]  <../../examples/nexml/nexml_from_scratch.py>`

--------------------------------------
Writing NeXML objects
--------------------------------------

Every NexML object has its own :func:`export` method. By calling it,
you can obtain the XML representation of any instance contained in the
Nexml project structure. Usually, all you will need is to export the
whole project, but individual elements can be exported. 

:: 

   import sys
   from ete2 import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()

   # Upload content from file
   nexml_project.build_from_file("nexml_example.xml")
  
   # Extract first collection of trees
   tree_collection =  nexml.get_trees()[0]

   # And export it
   tree_collection.export(output=sys.stdout, level=0)


NeXML tree manipulation and visualization
---------------------------------------------

NeXML trees contain all ETE PhyloTree functionality: orthology
prediction, topology manipulation and traversing methods,
visualization, etc.

For instance, tree changes performed through the visualization GUI are
kept in the NeXML format.

:: 

   from ete2 import nexml
   nexml_tree = nexml.NexMLTree("((hello, nexml):1.51, project):0.6;")
   tree_collection.add_tree(nexml_tree)
   nexml_tree.show()
