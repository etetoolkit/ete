*****************
The PhylomeDB API
*****************

PhylomeDB is a public database for complete collections of gene phylogenies
(phylomes). It allows users to interactively explore the evolutionary history of
genes through the visualization of phylogenetic trees and multiple sequence
alignments. Moreover, phylomeDB provides genome-wide orthology and paralogy
predictions which are based on the analysis of the phylogenetic trees. The
automated pipeline used to reconstruct trees aims at providing a high-quality
phylogenetic analysis of different genomes , including Maximum Likelihood or
Bayesian tree inference, alignment trimming and evolutionary model testing.
PhylomeDB includes also a public download section with the complete set of
trees, alignments and orthology predictions.

ETE's phylomeDB extension provides an access API to the main PhylomeDB database,
thus allowing to search for and fetch precomputed gene phylogenies.


Basis of the phylomeDB API usage
================================

In order to explore the database resources, you have to create a connector to
the database, which will be used to query it. To do so, you must use the
**PhylomeDBConnector** class and specify the parameters of the DB connection.

The PhylomeDBConnector constructor will return a pointer to the DB that you can
use to perform queries. All methods starting by **get_** can be used to retrieve
information from the database. A complete list of available methods can be found
in the ETE's programming guide (available at
http://etetoolkit.org) or explored by executing
**dir(PhylomeDBConnector)** in a python console.


PhylomeDB structure
===================

A phylome includes thousands of gene trees associated to the different
genes/proteins of a given species. Thus, for example, the human phylome includes
more than 20.000 phylogenetic trees; on per human gene. Moreover, the same gene
may be associated to different trees within the same phylome differing only in
the evolutionary model that assumed to reconstruct the phylogeny.

Given that each phylogenetic tree was reconstructed using a a single gene as the
seed sequence to find homologous in other species, the tree takes the name from
the seed sequence.

You can obtain a full list of phylomes through the **get_phylomes()** and a full
list of seed sequence in a phylome using the **get_seed_ids()** method.
Phylogenetic trees within a given phylome were reconstructed in a context of a
fixed set of species. In order to obtain the list of proteomes included in a
phylome, use the** get_proteomes_in_phylome()** method. PhylomeDB uses its own
sequence identifiers, but you can use the **search_id()** to find a match from
an external sequence ID.

Each phylome is the collection of all trees associated to a given species. Thus,
the human phylome will contain thousands of phylogenetic trees. Each
gene/protein in a phylome may be associated to different trees, testing, for
example, different evolutionary models. Thus when you query the database for a
gene phylogeny you have to specify from which phylome and which specific tree.
Alternatively, you can query for the best tree in a given phylomes, which will
basically return the best likelihood tree for the queried gene/protein. The
get_tree and get_best_tree methods carry out such operations. When trees are
fetched from the phylomeDB database, the are automatically converted to the
PhyloTree class, thus allowing to operate with them as phylogenetic trees.


Going phylogenomic scale
========================

Just to show you how to explore a complete phylome:



