.. currentmodule:: ete4

Connecting with Taxonomy Databases
==================

.. contents::

Overview
--------
ETE4 contains *ncbi_taxonomy* and *gtdb_taxonomy* modules which provide 
utilities to efficiently query a local copy of the NCBI or GTDB taxonomy 
databases. The class ``NCBITaxa`` and ``GTDBTaxa`` offer methods to convert 
from taxid to names (and vice versa), to fetch pruned topologies connecting 
a given set of species, or to download rank, names and lineage track information.

It is also fully integrated with PhyloTree instances through the 
``PhyloNode.annotate_ncbi_taxa()`` and ``PhyloNode.annotate_gtdb_taxa()``method.

