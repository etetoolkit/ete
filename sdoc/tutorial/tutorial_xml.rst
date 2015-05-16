************************************  
Phylogenetic XML standards
************************************
.. versionadded:: 2.1

From version 2.1, ETE provides support for `NeXML
<http://nexml.org/>`_ and `PhyloXML <http://phyloxml.org/>`_
phylogenetic XML standards, both reading and writing. These standards
allow to encode complex phylogenetic data, and therefore they are not
limited to trees. Although ETE is mainly focused on allowing
transparent interaction with trees, it also provides basic I/O methods
to data of different type.

Essentially, NexML and PhyloXML files are intended to encode
collections of phylogenetic data. Such information can be converted to
a collection Python objects sorted in a hierarchical way. A specific
Python class exists for every element encoded documented by the NeXML
and PhyloXML formats. This is possible thanks to the the general
purpose Python drivers available for both formats
(http://etetoolkit.org/phyloxml-and-nexml-python-parsers). ETE will
use such drivers to access XML data, and it will also convert tree
data into PhyloTree objects. In practice, conversions will occur
transparently.  NeXML and PhyloXML files are loaded using their
specific root classes, provided by the main ETE module, and all the
information will become available as a collection of Python objects
internally sorted according to the original XML hierarchy.

.. toctree::
   :maxdepth: 2

   tutorial_nexml
   tutorial_phyloxml

.. note:: 

   NeXML and PhyloXML python parsers are possible thanks to Dave
   Kulhman and his work on the `generateDS.py
   <http://www.rexx.com/~dkuhlman/generateDS.html>`_
   application. Thanks Dave! ;-)



