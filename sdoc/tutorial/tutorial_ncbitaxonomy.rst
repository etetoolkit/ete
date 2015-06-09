.. moduleauthor:: Jaime Huerta-Cepas

.. versionadded:: 2.3

.. currentmodule:: ete2

Dealing with the NCBI Taxonomy database
=================================================

ETE's `ncbi_taxonomy` module provides utilities to efficiently query a local
copy of the NCBI Taxonomy database. The class :class:`NCBITaxa` offers
methods to convert from taxid to names (and vice versa), to fetch pruned
topologies connecting a given set of species, or to download rank, names and
lineage track information.
 
It is also fully integrated with :class:`PhyloTree` instances through the
:func:`PhyloNode.annotate_ncbi_taxa` method.

Setting up a local copy of the NCBI taxonomy database
-------------------------------------------------------

The first time you attempt to use :class:`NCBITaxa`, ETE will detect that your
local database is empty and it will attempt to download the latest NCBI taxonomy
database (~300MB) and will store a parsed version of it in your home directory:
`~/.etetoolkit/taxa.sqlite`. All future imports of _`NCBITaxa` will detect the
local database and will skip this step.

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()

Upgrading the local database
------------------------------

Use the method :NCBITaxa:`update_taxonomy_database` to download and parse the
latest database from the NCBI ftp site. Your current local database will be
overwritten.

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()
   ncbi.update_taxonomy_database()


Getting taxid information 
-----------------------------

you can fetch species names, ranks and linage track information for your taxids
using the following methods:

 - :func:`NCBITaxa.get_rank`
 - :func:`NCBITaxa.get_lineage`
 - :func:`NCBITaxa.get_taxid_translator`
 - :func:`NCBITaxa.get_name_translator`
 - :func:`NCBITaxa.translate_to_names`

The so called get-translator-functions will return a dictionary converting
between taxids and species names. Either species or linage names/taxids are
accepted as input.

::
 
   from ete2 import NCBITaxa
   ncbi = NCBITaxa()
   taxid2name = ncbi.get_taxid_translator([9606, 9443])
   print taxid2name
   # {9443: u'Primates', 9606: u'Homo sapiens'}
   
   name2taxid = ncbi.get_name_translator(["Homo sapiens", "primates"])
   print name2taxid
   # {'Homo sapiens': 9606, 'primates': 9443}

Other functions allow to extract further information using taxid numbers as a query. 

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()

   print ncbi.get_rank([9606, 9443])
   # {9443: u'order', 9606: u'species'}

   print ncbi.get_lineage(9606) 

   # [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742,
   # 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347,
   # 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605,
   # 9606]


And you can combine combine all at once:

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()

   lineage = ncbi.get_lineage(9606) 
   print lineage

   # [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742,
   # 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347,
   # 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605,
   # 9606]

   names = ncbi.get_taxid_translator(lineage)
   print [names[taxid] for taxid in lineage]
 
   # [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa',
   # u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata',
   # u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi',
   # u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota',
   # u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires',
   # u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea',
   # u'Hominidae', u'Homininae', u'Homo', u'Homo sapiens']


Getting descendant taxa
-----------------------------

Given a taxid or a taxa name from an internal node in the NCBI taxonomy tree,
their descendants can be retrieved as follows:

::

   from ete2 import NCBITaxa
   ncbi = NCBITaxa()

   descendants = ncbi.get_descendant_taxa('Homo')
   print ncbi.translate_to_names(descendants)

   # [u'Homo heidelbergensis', u'Homo sapiens ssp. Denisova', u'Homo sapiens neanderthalensis']

   # you can easily ignore subspecies, so only taxa labeled as "species" will be reported:
   descendants = ncbi.get_descendant_taxa('Homo', collapse_subspecies=True)
   print ncbi.translate_to_names(descendants)

   # [u'Homo sapiens', u'Homo heidelbergensis']

   # or even returned as an annotated tree
   tree = ncbi.get_descendant_taxa('Homo', collapse_subspecies=True, return_tree=True)
   print tree.get_ascii(attributes=['sci_name', 'taxid'])

   #           /-Homo sapiens, 9606
   # -Homo, 9605
   #           \-Homo heidelbergensis, 1425170


Getting NCBI species tree topology
---------------------------------------

Getting the NCBI taxonomy tree for a given set of species is one of the most
useful ways to get all information at once. The method
:func:`NCBITaxa.get_topology` allows to query your local NCBI database and
extract the smallest tree that connects all your query taxids. It returns a
normal ETE tree in which all nodes, internal or leaves, are annotated for
lineage, scientific names, ranks, and so on.

::


   from ete2 import NCBITaxa
   ncbi = NCBITaxa()
   
   tree = ncbi.get_topology([9606, 9598, 10090, 7707, 8782])
   print tree.get_ascii(attributes=["sci_name", "rank"])

   #                     /-Dendrochirotida, order
   #                    |
   #                    |                                                                /-Pan troglodytes, species
   # -Deuterostomia, no rank                                           /Homininae, subfamily
   #                    |                /Euarchontoglires, superorder                   \-Homo sapiens, species
   #                    |               |                           |
   #                     \Amniota, no rank                           \-Mus musculus, species
   #                                    |
   #                                     \-Aves, class


If needed, all intermediate nodes connecting the species can also be kept in the tree: 

::


   from ete2 import NCBITaxa
   ncbi = NCBITaxa()
   
   tree = ncbi.get_topology([2, 33208], intermediate_nodes=True)
   print tree.get_ascii(attributes=["sci_name"])

   #                  /Eukaryota - Opisthokonta - Metazoa
   # -cellular organisms
   #                  \-Bacteria



Automatic tree annotation using NCBI taxonomy
--------------------------------------------------

NCBI taxonomy annotation consists of adding additional information to any
internal a leaf node in a give user tree. Only an attribute containing the taxid
associated to each node is required for the nodes in the query tree. The
annotation process will add the following features to the nodes:

 - sci_name  
 - taxid
 - named_lineage 
 - lineage 
 - rank

Note that, for internal nodes, taxid can be automatically inferred based on
their sibling nodes. The easiest way to annotate a tree is to use a
:class:`PhyloTree` instance where the species name attribute is transparently
used as the taxid attribute.  Note that the :PhyloNode:`annotate_ncbi_taxa`:
function will also return the used name, lineage and rank translators.

Remember that species names in `PhyloTree` instances are automatically extracted
from leaf names. The parsing method can be easily adapted to any formatting:

::


   from ete2 import PhyloTree

   # load the whole leaf name as species taxid
   tree = PhyloTree('((9606, 9598), 10090);', sp_naming_function=lambda name: name)
   tax2names, tax2lineages, tax2rank = tree.annotate_ncbi_taxa()

   # split names by '|' and return the first part as the species taxid 
   tree = PhyloTree('((9606|protA, 9598|protA), 10090|protB);', sp_naming_function=lambda name: name.split('|')[0])
   tax2names, tax2lineages, tax2rank = tree.annotate_ncbi_taxa()

   print tree.get_ascii(attributes=["name", "sci_name", "taxid"])


   #                                             /-9606|protA, Homo sapiens, 9606
   #                          /, Homininae, 207598
   #-, Euarchontoglires, 314146                  \-9598|protA, Pan troglodytes, 9598
   #                         |
   #                          \-10090|protB, Mus musculus, 10090


Alternatively, you can also use the :func:`NCBITaxa.annotate_tree` function to
annotate a custom tree instance.

::

   from ete2 import Tree, NCBITaxa
   ncbi = NCBITaxa()
   tree = Tree("")
   ncbi.annotate_tree(tree, taxid_attr="name")


