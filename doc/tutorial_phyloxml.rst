.. versionadded:: 2.1
.. module:: ete_dev.nexml
  :synopsis: Reading and writing support support for the NexML format
.. moduleauthor:: Jaime Huerta-Cepas

************************************  
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
available in the :mod:`ete_dev.phyloxml` module.

:: 

  from ete2 import Phyloxml, phyloxml
  # create empty project 
  proj = Phyloxml()
  phylogeny = phyloxml.PhyloxmlTree()
  phylogeny.populate(10)
  proj.add_phylogeny(phylogeny)
  
