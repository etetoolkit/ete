.. moduleauthor:: Jaime Huerta-Cepas

.. versionadded:: 2.3

.. currentmodule:: ete2

Overview
================

ETE's `ncbi_taxonomy` module provides utilities to efficiently query a local
copy of the NCBI Taxonomy database. The class :class:`NCBITaxonomy` offers
methods to convert from taxid to names (and vice versa), to fetch pruned
topologies connecting a given set of species, or to download rank, names and lineage
track information.
 
It is also fully integrated with :class:`PhyloTree` instances through the
:func:`tree.annotate_tree` method.

Setting up a local copy of the NCBI taxonomy database
-------------------------------------------------------

The first time you attempt to use :class:`NCBITaxa` ETE will detect that the
database is empty and it will attempt to download the latest NCBI taxonomy
database (~300MB) and store a parsed version in home directory:
`~/.etetoolkit/taxa.sqlite`. All future imports of `NCBITaxa` will detect the local database and skip this step. 

::
   from ete2 import NCBITaxa
   ncbi = NCBITaxa()

Upgrading the local database
------------------------------

Use the method :NCBITaxa:`update_taxonomy_database` to download and parse the
latest database from the NCBI ftp site. Local database will be overwritten. 

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()
   ncbi.update_taxonomy_database()


Converting taxid, species names 
----------------------------------------

Getting taxid information 
-----------------------------

you can fetch species names, ranks and linage track information for your taxids using the following methods: 

 - :func:`NCBITaxa.get_ranks`
 - :func:`NCBITaxa.get_sp_lineage`
 - :func:`NCBITaxa.get_taxid_translator`
 - :func:`NCBITaxa.get_taxid_names`
 - :func:`NCBITaxa.get_name_translator`
 - :func:`NCBITaxa.translate_to_names`


Getting NCBI species tree topology
---------------------------------------

 - :func:`NCBITaxa.get_topology`


Automatic tree annotation using NCBI taxonomy
--------------------------------------------------

NCBI taxonomy annotation consists of adding additional information to all
internal a leaf nodes in a tree based on the species it contains. The annotation
process will add the following features to the nodes:

 - sci_name  
 - taxid
 - named_lineage 
 - lineage 
 - rank

The easiest way to annotate a tree is to use a :class:`PhyloTree` instance where
the species name attribute is bound to taxids.

::

   from ete2 import PhyloTree
   tree = PhyloTree('(proteinA_9606, proteinB_7505)', )
   tree.annotate_ncbi_taxa()


remember that species names in `PhyloTree` instances are automatically extracted from leaf names by
splitting by underscore (`_`). This can be easily customize to fit your tree
format.

::


   from ete2 import PhyloTree

   # load the whole leaf name as species taxid
   tree = PhyloTree('(9606, 7505)', sp_naming_function=lambda name: name)
   tree.annotate_ncbi_taxa()

   # split names by '|' and return the first part as the species taxid 
   tree = PhyloTree('(9606|protA, 7505|protB)', sp_naming_function=lambda name: name.split('|')[0])
   tree.annotate_ncbi_taxa()
      
Alternatively, you can also use the :func:`NCBITaxa.annotate` function to
annotate a custom tree instance.

::

   from ete2 import Tree, NCBITaxa
   ncbi = NCBITaxa()
   tree = Tree("")
   ncbi.annotate_tree(tree, taxid_attr="name")


