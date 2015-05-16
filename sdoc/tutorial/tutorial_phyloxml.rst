.. moduleauthor:: Jaime Huerta-Cepas

.. versionadded:: 2.1

.. currentmodule:: ete2

PhyloXML
************************************

PhyloXML (http://www.phyloxml.org/) is a novel standard used to encode
phylogenetic information. In particular, phyloXML is designed to
describe phylogenetic trees (or networks) and associated data, such as
taxonomic information, gene names and identifiers, branch lengths,
support values, and gene duplication and speciation events.

----------------------------------------
Loading PhyloXML projects from files 
----------------------------------------

ETE provides full support for phyloXML projects through the
:class:`Phyloxml` object. Phylogenies are integrated as ETE's tree
data structures as :class:`PhyloxmlTree` instances, while the rest of
features are represented as simple classes (:mod:`ete2.phyloxml`)
providing basic reading and writing operations.


.. literalinclude:: ../../examples/phyloxml/phyloxml_parser.py

:download:`[Download script]  <../../examples/phyloxml/phyloxml_parser.py>`
:download:`[Download example]  <../../examples/phyloxml/apaf.xml>`


Each tree node contains two phyloxml elements, :attr:`phyloxml_clade`
and :attr:`phyloxml_phylogeny`. The first attribute contains clade
information referred to the node, while ``phyloxml_phylogeny``
contains general data about the subtree defined by each node. This
way, you can split, or copy any part of a tree and it will be exported
as a separate phyloxml phylogeny instance.

Note that :attr:`node.dist`, :attr:`node.support` and
:attr:`node.name` features are linked to
:attr:`node.phyloxml_clade.branch_length`,
:attr:`node.phyloxml_clade.confidence` and
:attr:`node.phyloxml_clade.name`, respectively.

----------------------------------------
Creating PhyloXML projects from scratch
----------------------------------------

In order to create new PhyloXML projects, a set of classes is
available in the :mod:`ete2.phyloxml` module.

.. literalinclude:: ../../examples/phyloxml/phyloxml_from_scratch.py

:download:`[Download script]  <../../examples/phyloxml/phyloxml_from_scratch.py>`
  
