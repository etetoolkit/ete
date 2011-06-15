.. currentmodule:: ete_dev.nexml

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
attributes. However, XML tree elements will be converted into
:class:`PhyloTree` instances, containing all ETE functionality
(traversing, drawing, etc) plus NeXML attributes.

In Nexml, a trees are represented as plain lists of nodes and
edges. ETE will convert such lists into tree topologies, in which
every node will contain a :attr:`nexml_node` and :attr:`nexml_edge`
attribute. In addition, each tree node has a :attr:`nexml_tree`
attribute (i.e. ``NEXML->FloatTree``) , which can be used to set the
nexml properties of the subtree represented by each node.

Note that :attr:`node.dist` and :attr:`node.name` features are linked
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
provided by the:mod:`ete_dev.nexml` module, you can populate an empty
project and export it as XML.

.. literalinclude:: ../../examples/nexml/nexml_from_scratch.py

:download:`[Download script]  <../../examples/nexml/nexml_from_scratch.py>`


--------------------------------------
Writing NeXML objects
--------------------------------------

Every NexML object has its own :func:`export` method. By calling it,
you can obtain the XML representation of any instance contained in the
Nexml project structure. 

Usually, all you will need is to export the whole project. 

:: 

   from ete_dev import Nexml
   # Create an empty Nexml project 
   nexml_project = Nexml()

   # Upload content from file
   nexml_project.build_from_file("nexml_example.xml")

   nexml_project.export()

