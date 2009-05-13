"""
This module defines the PhyloNode dataytype to manage phylogenetic
tree. It inheritates the coretype TreeNode and add some speciall
features to the the node instances.
"""

import sys
import os
import re

from pygenomics.coretype import tree
import reconcile

__all__ = ["EvolEvent", "PhyloNode", "PhyloTree"]

def _parse_species(name):
    return name[:3]

class PhyloNode(tree.TreeNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def _get_name(self):
	return self._name

    def _set_name(self, value):
	self._name = value
	if self._speciesFunction is not None:
	    self.species = self._speciesFunction(self._name)

    # This tweak overwrites the native 'name' attribute to create a
    # property that updates the species code every time name is
    # changed
    name = property(fget = _get_name, fset = _set_name)

    def __init__(self, newick=None, sequences=None):
	# _update names?
	self._name = "NoName"
	self._speciesFunction = _parse_species
	# Caution! native __init__ has to be called after defining
	# _speciesFunction!!
        tree.TreeNode.__init__(self, newick=newick)

	self.add_feature("species","Unknown")
	self.add_feature("lk",0.0)
	self.add_feature("evolModel","unknown")

	# 
	# for node in [t]+t.get_descendants():
	#     node._speciesFunction = speciesFunction
	#     # To update species name
	#     node.name = node.name
	#  
	# if os.path.exists(algFile):
	#     aln = readFasta.read_fasta(algFile)
	#     for node in t.get_leaves():
	#  	seq_id = aln.name2id[node.name]
	#  	node.sequence = aln.id2seq[seq_id]

    def get_leaf_species(self):
        """ Returns the set of species covered by its partition. """ 
        return set( [ l.species for l in self.iter_leaves() ])          

    def iter_leaf_species(self):
        """ Returns an iterator over the species grouped by this node. """ 
	spcs = set([])
	for l in self.iter_leaves():
	    if l.species not in spcs:
		spcs.add(l.species)
		yield l.species

    def is_monophyletic(self, species):
	""" Returns True id species names under this node are all
	included in a given list or set of species names."""
	if type(species) != set:
	    species = set(species)
	return self.get_leaf_species().issubset(species)

    def get_age(self, species2age):
	return max([species2age[sp] for sp in self.get_leaf_species()])

    def get_reconciled_tree(self, species_tree):
	""" Returns the reconcilied topology with the provided species
	tree, and a list of evolutionary events inferred from such
	reconciliation. """
	return reconcile.get_reconciled_tree(self, species_tree, [])

    def get_my_evol_events(self):
        """ Returns a list of duplication and speciation events in
        which the current node has been involved. Scanned nodes are
        also labeled internally as dup=True|False. You can access this
        labels using the 'node.dup' sintaxis.

        Method: the algorithm scans all nodes from the given leafName to
        the root. Nodes are assumed to be duplications when a species
        overlap is found between its child linages. Method is described
        more detail in:

        "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
        T. Genome Biol. 2007;8(6):R109.
        """
        # Get the tree's root
        root = self.get_tree_root()
       
        # Checks that is actually rooted
        outgroups = root.get_childs()
        if len(outgroups) != 2:
            raise "eteError", "Tree is not rooted"

        # Cautch the smaller outgroup (will be stored as the tree
        # outgroup)
        o1 = set([n.name for n in outgroups[0].get_leaves()])
        o2 = set([n.name for n in outgroups[1].get_leaves()])

        if len(o2)<len(o1):
            smaller_outg = outgroups[1]
	else:
            smaller_outg = outgroups[0]


        # Prepare to browse tree from leaf to root
        all_events = []
        current  = self
        ref_spcs = self.species
        sister_leaves  = set([])
        browsed_spcs   = set([current.species])
        browsed_leaves = set([current])
        # get family Size
        fSize =  len([n for n in root.get_leaves() if n.species == ref_spcs])

        # Clean previous analysis 
        for n in root.get_descendants()+[root]:
            n.del_feature("evoltype")

        while current.up:
            # distances control (0.0 distance check)
            d = 0
            for s in current.get_sisters():
                for leaf in s.get_leaves():
                    d += current.get_distance(leaf)
                    sister_leaves.add(leaf)
            # Process sister node only if there is any new sequence.
            # (previene dupliaciones por nombres repetidos)
            sister_leaves = sister_leaves.difference(browsed_leaves)
            if len(sister_leaves)==0:
                current = current.up
                continue
            # Gets species at both sides of event
            sister_spcs     = set([n.species for n in sister_leaves])
            overlaped_spces = browsed_spcs & sister_spcs
            all_spcs        = browsed_spcs | sister_spcs
            score = float(len(overlaped_spces))/len(all_spcs)
            # Creates a new evolEvent
            event = EvolEvent()
            event.fam_size   = fSize
            event.seed      = self.name
            # event.e_newick  = current.up.get_newick()  # high mem usage!!
            event.dup_score = score
            event.outgroup  = smaller_outg.name
            # event.allseqs   = set(current.up.get_leaf_names())
            event.in_seqs = set([n.name for n in browsed_leaves])
            event.out_seqs = set([n.name for n in sister_leaves])
            event.inparalogs  = set([n.name for n in browsed_leaves if n.species == ref_spcs])
            # If species overlap: duplication 
            if score >0.0 and d > 0.0:
                event.etype = "D"
                event.outparalogs = set([n.name for n in sister_leaves  if n.species == ref_spcs])
                event.orthologs   = set([])
                current.up.add_feature("evoltype","D")
		all_events.append(event)

            # If NO species overlap: speciation
            elif score == 0.0:
                event.etype = "S"
                event.orthologs = set([n.name for n in sister_leaves if n.species != ref_spcs])
                event.outparalogs = set([])
                current.up.add_feature("evoltype","S")
		all_events.append(event)
	    else:
		pass # do not add event if distances == 0

            # Updates browsed species  
            browsed_spcs   |= sister_spcs
            browsed_leaves |= sister_leaves
            sister_leaves  = set([])
            # And keep ascending
            current = current.up

        return all_events

    def get_descendant_evol_events(self):
        """ Returns a list of **all** duplication and speciation
        events detected after this node. Nodes are assumed to be
        duplications when a species overlap is found between its child
        linages. Method is described more detail in:

        "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
        T. Genome Biol. 2007;8(6):R109.
        """

        # Get the tree's root
        root = self.get_tree_root()
        
        # Checks that is actually rooted
        outgroups = root.get_childs()
        if len(outgroups) != 2:
            raise "eteError", "Tree is not rooted"

        # Cautch the smaller outgroup (will be stored as the tree outgroup)
        o1 = set([n.name for n in outgroups[0].get_leaves()])
        o2 = set([n.name for n in outgroups[1].get_leaves()])


        if len(o2)<len(o1):
            smaller_outg = outgroups[1]
	else:
            smaller_outg = outgroups[0]

        # Get family size
        fSize = len( [n for n in root.get_leaves()] )

        # Clean previous analysis 
        for n in root.get_descendants()+[root]:
            n.del_feature("evoltype")

        # Gets Prepared to browse the tree from root to leaves
        to_visit = []
        current = root
        all_events = []
        while current: 
            # Gets childs and appends them to the To_visit list
            childs = current.get_childs()
            to_visit += childs
            if len(childs)>2: 
                print >> sys.stderr, "nodes are expected to have two childs."
            elif len(childs)==0: 
                pass # leaf
            else:
                # Get leaves and species at both sides of event
                sideA_leaves= set([n for n in childs[0].get_leaves()])
                sideB_leaves= set([n for n in childs[1].get_leaves()])
                sideA_spcs  = set([n.species for n in childs[0].get_leaves()])
                sideB_spcs  = set([n.species for n in childs[1].get_leaves()])
                # Calculates species overlap
                overlaped_spcs = sideA_spcs & sideB_spcs
                all_spcs       = sideA_spcs | sideB_spcs
                score = float(len(overlaped_spcs))/len(all_spcs)

                # Creates a new evolEvent
                event = EvolEvent()
                event.fam_size   = fSize
		event.branch_supports = [current.support, current.children[0].support, current.children[1].support]
                # event.seed      = leafName
                # event.e_newick  = current.up.get_newick()  # high mem usage!!
                event.dup_score = score
                event.outgroup_spcs  = smaller_outg.get_leaf_species()
                event.in_seqs = set([n.name for n in sideA_leaves])
                event.out_seqs = set([n.name for n in sideB_leaves])
                event.inparalogs  = set([n.name for n in sideA_leaves])
                # If species overlap: duplication 
                if score >0.0:
                    event.etype = "D"
                    event.outparalogs = set([n.name for n in sideB_leaves])
                    event.orthologs   = set([])
                    current.add_feature("evoltype","D")
                # If NO species overlap: speciation
                else:
                    event.etype = "S"
                    event.orthologs = set([n.name for n in sideB_leaves])
                    event.outparalogs = set([])
                    current.add_feature("evoltype","S")

                all_events.append(event)
            # Keep visiting nodes
            try:
                current = to_visit.pop(0)
            except IndexError: 
                current = None
        return all_events

    def get_farthest_oldest_leaf(self, species2age):
        """ Returns the farthest oldest leafnode to the current
        one. It requieres an species2age dictionary with the age
        estimation for all species."""

        root = self.get_tree_root()

        # Get all tree leaves     
        leaves      = root.get_leaves()

        outgroup_dist  = 0
        outgroup_node  = self
        outgroup_age = 0 #species2age[self.species]

        for leaf in leaves:
            if species2age[leaf.species] > outgroup_age: # OJO! Change crocodile to invert the comparison. 
                outgroup_dist = leaf.get_distance(self)
                outgroup_node = leaf
                outgroup_age = species2age[leaf.species]
            elif species2age[leaf.species]==outgroup_age:
                dist = leaf.get_distance(self)
                if dist>outgroup_dist:
                    outgroup_dist  = leaf.get_distance(self)
                    outgroup_node  = leaf
                    outgroup_age = species2age[leaf.species]
            else:
                pass
        return outgroup_node

class EvolEvent:
    """ Basic evolutionary event. It stores all the information about an
    event(node) ocurred in a phylogenetic tree. """
    def __init__(self):
        self.etype         = None   # 'S=speciation D=duplication'
        self.seed          = None   # Seed ID used to start the phylogenetic pipeline
        self.outgroup_spcs = None   # outgroup
        self.e_newick      = None   # 
        self.dup_score     = None   # 
        self.root_age      = None   # estimated time for the outgroup node
        self.inparalogs    = None   
        self.outparalogs   = None 
        self.orthologs     = None 
        self.famSize       = None
        self.allseqs       = []     # all ids grouped by this event
        self.in_seqs       = []
        self.out_seqs      = []
	self.branch_supports  = []

# cosmetic alias
PhyloTree = PhyloNode
