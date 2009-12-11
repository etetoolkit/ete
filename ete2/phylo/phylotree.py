# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
"""
This module defines the PhyloNode dataytype to manage phylogenetic
tree. It inheritates the coretype TreeNode and add some speciall
features to the the node instances.
"""

import sys
import os
import re

from ete_dev import TreeNode, SeqGroup
from reconciliation import get_reconciled_tree
import spoverlap

__all__ = ["PhyloNode", "PhyloTree"]

def _parse_species(name):
    return name[:3]

class PhyloNode(TreeNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def _get_species(self):
        if self._speciesFunction:
            return self._speciesFunction(self.name)
        else:
            return self._species

    def _set_species(self, value):
        if self._speciesFunction:
            pass
        else:
            self._species = value

    # This tweak overwrites the native 'name' attribute to create a
    # property that updates the species code every time name is
    # changed
    species = property(fget = _get_species, fset = _set_species)

    def __init__(self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species):
        # _update names?
        self._name = "NoName"
        self._species = "Unknown"
        self._speciesFunction = None
        # Caution! native __init__ has to be called after setting
        # _speciesFunction to None!!
        TreeNode.__init__(self, newick=newick)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloNode constructor during parsing
        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            self.set_species_naming_function(sp_naming_function)

    def set_species_naming_function(self, fn):
        for n in self.iter_leaves():
            n.features.add("species")
            if fn:
                n._speciesFunction = fn

    def link_to_alignment(self, alignment, alg_format="fasta"):
        missing_leaves = []
        missing_internal = []
        if type(alignment) == SeqGroup:
            alg = alignment
        else:
            alg = SeqGroup(alignment, format=alg_format)
        # sets the seq of
        for n in self.traverse():
            try:
                n.add_feature("sequence",alg.get_seq(n.name))
            except KeyError:
                if n.is_leaf():
                    missing_leaves.append(n.name)
                else:
                    missing_internal.append(n.name)
        if len(missing_leaves)>0:
            print >>sys.stderr, \
                "Warnning: [%d] terminal nodes could not be found in the alignment." %\
                len(missing_leaves)
        # Show warning of not associated internal nodes.
        # if len(missing_internal)>0:
        #     print >>sys.stderr, \
        #       "Warnning: [%d] internal nodes could not be found in the alignment." %\
        #       len(missing_leaves)


    def get_species(self):
        """ Returns the set of species covered by its partition. """
        return set( [ l.species for l in self.iter_leaves() ])

    def iter_species(self):
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
        return self.get_species().issubset(species)
    def get_age(self, species2age):
        return max([species2age[sp] for sp in self.get_species()])
    def reconcile(self, species_tree):
        """ Returns the reconcilied topology with the provided species
        tree, and a list of evolutionary events inferred from such
        reconciliation. """
        return get_reconciled_tree(self, species_tree, [])

    def get_my_evol_events(self, sos_thr=0.0):
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
        return spoverlap.get_evol_events_from_leaf(self, sos_thr=sos_thr)

    def get_descendant_evol_events(self, sos_thr=0.0):
        """ Returns a list of **all** duplication and speciation
        events detected after this node. Nodes are assumed to be
        duplications when a species overlap is found between its child
        linages. Method is described more detail in:

        "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
        T. Genome Biol. 2007;8(6):R109.
        """
        return spoverlap.get_evol_events_from_root(self, sos_thr=sos_thr)

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

# cosmetic alias
PhyloTree = PhyloNode
