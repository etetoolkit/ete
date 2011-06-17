from ete_dev import Phyloxml, phyloxml
import random 

project = Phyloxml()

# Creates a random tree
phylo = phyloxml.PhyloXMLTree()
phylo.populate(100, random_dist=True)
phylo.phyloxml_phylogeny.set_name("test_tree")
# Add the tree to the phyloxml project
project.add_phylogeny(phylo)

project.export()
