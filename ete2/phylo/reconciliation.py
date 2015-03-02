# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################

import copy
from evolevents import EvolEvent


def get_reconciled_tree(node, sptree, events):
    """ Returns the recoliation gene tree with a provided species
    topology """

    if len(node.children) == 2:
        # First visit childs
        morphed_childs = []
        for ch in node.children:
            mc, ev = get_reconciled_tree(ch, sptree, events)
            morphed_childs.append(mc)

        # morphed childs are the reconciled children. I trust its
        # topology. Remember tree is visited on recursive post-order
        sp_child_0 = morphed_childs[0].get_species()
        sp_child_1 = morphed_childs[1].get_species()
        all_species = sp_child_1 | sp_child_0

        # If childs represents a duplication (duplicated species)
        # Check that both are reconciliated to the same species
        if len(sp_child_0 & sp_child_1) > 0:
            newnode = copy.deepcopy(node)
            newnode.up = None
            newnode.children = []
            template = _get_expected_topology(sptree, all_species)
            # replaces child0 partition on the template
            newmorphed0, matchnode = _replace_on_template(template, morphed_childs[0])
            # replaces child1 partition on the template
            newmorphed1, matchnode = _replace_on_template(template, morphed_childs[1])
            newnode.add_child(newmorphed0)
            newnode.add_child(newmorphed1)
            newnode.add_feature("evoltype", "D")
            node.add_feature("evoltype", "D")
            e = EvolEvent()
            e.etype = "D"
            e.inparalogs = node.children[0].get_leaf_names()
            e.outparalogs = node.children[1].get_leaf_names()
            e.in_seqs  = node.children[0].get_leaf_names()
            e.out_seqs = node.children[1].get_leaf_names()
            events.append(e)
            return newnode, events

        # Otherwise, we need to reconciliate species at both sides
        # into a single partition.
        else:
            # gets the topology expected by the observed species
            template = _get_expected_topology(sptree, all_species)
            # replaces child0 partition on the template
            template, matchnode = _replace_on_template(template, morphed_childs[0] )
            # replaces child1 partition on the template
            template, matchnode = _replace_on_template(template, morphed_childs[1])
            template.add_feature("evoltype","S")
            node.add_feature("evoltype","S")
            e = EvolEvent()
            e.etype = "S"
            e.inparalogs = node.children[0].get_leaf_names()
            e.orthologs = node.children[1].get_leaf_names()
            e.in_seqs  = node.children[0].get_leaf_names()
            e.out_seqs = node.children[1].get_leaf_names()
            events.append(e)
            return template, events
    elif len(node.children)==0:
        return copy.deepcopy(node), events
    else:
        raise ValueError("Algorithm can only work with binary trees.")

def _replace_on_template(orig_template, node):
    template = copy.deepcopy(orig_template)
    # detects partition within topo that matchs child1 species
    nodespcs = node.get_species()
    spseed = list(nodespcs)[0]  # any sp name woulbe ok
    # Set an start point
    subtopo = template.search_nodes(children=[], name=spseed)[0]
    # While subtopo does not cover all child species
    while len(nodespcs - set(subtopo.get_leaf_names() ) )>0:
        subtopo= subtopo.up
    # Puts original partition on the expected topology template
    nodecp = copy.deepcopy(node)
    if subtopo.up is None:
        return nodecp, nodecp
    else:
        parent = subtopo.up
        parent.remove_child(subtopo)
        parent.add_child(nodecp)
        return template, nodecp

def _get_expected_topology(t, species):
    missing_sp = set(species) - set(t.get_leaf_names())
    if missing_sp:
        raise KeyError("* The following species are not contained in the species tree: "+ ','.join(missing_sp) )

    node = t.search_nodes(children=[], name=list(species)[0])[0]

    sps = set(species)
    while sps-set(node.get_leaf_names()) != set([]):
        node = node.up
    template = copy.deepcopy(node)
    # make get_species() to work
    #template._speciesFunction = _get_species_on_TOL
    template.set_species_naming_function(_get_species_on_TOL)
    template.detach()
    for n in [template]+template.get_descendants():
        n.add_feature("evoltype","L")
        n.dist = 1
    return template

def _get_species_on_TOL(name):
    return name

def get_reconciled_tree_zmasek(gtree, sptree, inplace=False):
    """ 
    Reconciles the gene tree with the species tree
    using Zmasek and Eddy's algorithm. Details can be
    found in the paper:
    
    Christian M. Zmasek, Sean R. Eddy: A simple algorithm 
    to infer gene duplication and speciation events on a 
    gene tree. Bioinformatics 17(9): 821-828 (2001)
    
    :argument gtree: gene tree (PhyloTree instance)
    
    :argument sptree: species tree (PhyloTree instance)

    :argument False inplace: if True, the provided gene tree instance is
       modified. Otherwise a reconciled copy of the gene tree is returned.
    
    :returns: reconciled gene tree
    """
    # some cleanup operations
    def cleanup(tree):
	for node in tree.traverse(): node.del_feature("M")

    if not inplace:
        gtree = gtree.copy('deepcopy')
        
    # check for missing species
    missing_sp = gtree.get_species() - sptree.get_species()
    if missing_sp:
        raise KeyError("* The following species are not contained in the species tree: "+ ', '.join(missing_sp))

    # initialization
    sp2node = dict()
    for node in sptree.get_leaves(): sp2node[node.species] = node

    # set/compute the mapping function M(g) for the
    # leaf nodes in the gene tree (see paper for details)
    species = sptree.get_species()
    for node in gtree.get_leaves():		
        node.add_feature("M",sp2node[node.species])

    # visit each internal node in the gene tree
    # and detect its event (duplication or speciation)
    for node in gtree.traverse(strategy="postorder"):
        if len(node.children) == 0:
            continue # nothing to do for leaf nodes

        if len(node.children) != 2: 
            cleanup(gtree)
            raise ValueError("Algorithm can only work with binary trees.")

        lca = node.children[0].M.get_common_ancestor(node.children[1].M) # LCA in the species tree
        node.add_feature("M",lca)

        node.add_feature("evoltype","S")
        if id(node.children[0].M) == id(node.M) or id(node.children[1].M) == id(node.M):
                node.evoltype = "D"

    cleanup(gtree)
    return gtree

