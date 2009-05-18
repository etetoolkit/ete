#! /usr/bin/env python
import sys
from pygenomics import PhyloTree

print """ 
This scripts reads an example gene tree and infer the evolutionary
events occurring in such phylogeny by applying a strict reconciliation
algorithm.

"""


# Loads a gene tree
genes_tree = PhyloTree("./genes_tree.nh")
# Roots the tree corretly 
outgroup = genes_tree.search_nodes(name="Ddi0002240")[0]
genes_tree.set_outgroup(outgroup)

# Loads a species reference tree
spcs_tree = PhyloTree("species_tree.nh")

# Reconcile gene_tree with the species tree
t, events = genes_tree.reconcile(spcs_tree)

# t is now the reconcilied tree, in which many nodes (detected as gene
# losses) have been added. This nodes are labeled as 'etype="L"'. 

# When visualize a phylogentic tree, nodes are coloured based on their
# evolutionary type. Gene losses are drawn with dashed lines. 
print t
t.show("phylogeny")

# Moreover, a list of evolutionary events are returend to used at
# convenience
print events

# You can still inspect the topology of the orginial gene tree
print genes_tree
genes_tree.show("phylogeny")
