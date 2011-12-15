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
trees. It inheritates the coretype TreeNode and add some special
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
    """ 
    .. currentmodule:: ete_dev
    Extends the standard :class:`TreeNode` instance. It adds
    specific attributes and methods to work with phylogentic trees.

    :argument newick: Path to the file containing the tree or, alternatively,
      the text string containing the same information.

    :argument alignment: file containing a multiple sequence alignment. 

    :argument alg_format:  "fasta", "phylip" or "iphylip" (interleaved)

    :argument format: sub-newick format 

      .. table::                                               

          ======  ============================================== 
          FORMAT  DESCRIPTION                                    
          ======  ============================================== 
          0        flexible with support values                  
          1        flexible with internal node names             
          2        all branches + leaf names + internal supports 
          3        all branches + all names                      
          4        leaf branches + leaf names                    
          5        internal and leaf branches + leaf names       
          6        internal branches + leaf names                
          7        leaf branches + all names                     
          8        all names                                     
          9        leaf names                                    
          100      topology only                                 
          ======  ============================================== 

    :argument sp_naming_function: Pointer to a parsing python
       function that receives nodename as first argument and returns
       the species name (see
       :func:`PhyloNode.set_species_naming_function`. By default, the
       3 first letter of nodes will be used as species identifiers.



    :returns: a tree node object which represents the base of the tree.
    """

    def _get_species(self):
        if self._speciesFunction:
            try:
                return self._speciesFunction(self.name)
            except:
                return self._speciesFunction(self)
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

    #: .. currentmodule:: ete_dev
    #:
    #Species code associated to the node. This property can be
    #automatically extracted from the TreeNode.name attribute or
    #manually set (see :func:`PhyloNode.set_species_naming_function`).
    species = property(fget = _get_species, fset = _set_species)

    def __init__(self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species, format=0):


        # _update names?
        self._name = "NoName"
        self._species = "Unknown"
        self._speciesFunction = None
        # Caution! native __init__ has to be called after setting
        # _speciesFunction to None!!
        TreeNode.__init__(self, newick=newick, format=format)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloNode constructor during parsing
        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            self.set_species_naming_function(sp_naming_function)

    def __repr__(self):
        return "PhyloTree node '%s' (%s)" %(self.name, hex(self.__hash__()))

    def show(self, layout="phylogeny", tree_style=None):
        super(PhyloNode, self).show(layout=layout, tree_style=tree_style)

    def set_species_naming_function(self, fn):
        """ 
        Sets the parsing function used to extract species name from a
        node's name.

        :argument fn: Pointer to a parsing python function that
          receives nodename as first argument and returns the species
          name.
        
        :: 

          # Example of a parsing function to extract species names for
          # all nodes in a given tree.
          def parse_sp_name(node_name):
              return node_name.split("_")[1]
          tree.set_species_naming_function(parse_sp_name)

        """
        if fn:
            for n in self.traverse():
                n._speciesFunction = fn
                if n.is_leaf():
                    n.features.add("species")

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
        return set([l.species for l in self.iter_leaves()])

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

    def get_farthest_oldest_leaf(self, species2age, is_leaf_fn=None):
        """ Returns the farthest oldest leaf to the current
        one. It requires an species2age dictionary with the age
        estimation for all species. 

        :argument None is_leaf_fn: A pointer to a function that
          receives a node instance as unique argument and returns True
          or False. It can be used to dynamically collapse nodes, so
          they are seen as leaves.

        """

        root = self.get_tree_root()
        outgroup_dist  = 0
        outgroup_node  = self
        outgroup_age = 0 # self.get_age(species2age)

        for leaf in root.iter_leaves(is_leaf_fn=is_leaf_fn):
            if leaf.get_age(species2age) > outgroup_age:
                outgroup_dist = leaf.get_distance(self)
                outgroup_node = leaf
                outgroup_age = species2age[leaf.get_species().pop()]
            elif leaf.get_age(species2age) == outgroup_age:
                dist = leaf.get_distance(self)
                if dist>outgroup_dist:
                    outgroup_dist  = leaf.get_distance(self)
                    outgroup_node  = leaf
                    outgroup_age = species2age[leaf.get_species().pop()]
        return outgroup_node

    def get_farthest_oldest_node(self, species2age):
        """ 
        .. versionadded:: 2.1

        Returns the farthest oldest node (leaf or internal). The
        difference with get_farthest_oldest_leaf() is that in this
        function internal nodes grouping seqs from the same species
        are collapsed.
        """

        # I use a custom is_leaf() function to collapse nodes groups
        # seqs from the same species
        is_leaf = lambda node: len(node.get_species())==1
        return self.get_farthest_oldest_leaf(species2age, is_leaf_fn=is_leaf)

    def get_age_balanced_outgroup(self, species2age):
        """ 
        .. versionadded:: 2.x
        
        Returns the best outgroup according to topological ages and
        node sizes.
        
        Currently Experimental !!

        """
        root = self
        all_seqs = set(self.get_leaf_names())
        outgroup_dist  = 0
        best_balance = max(species2age.values())
        outgroup_node  = self
        outgroup_size = 0

        for leaf in root.iter_descendants():
            leaf_seqs = set(leaf.get_leaf_names())
            size = len(leaf_seqs)
            
            leaf_species =[self._speciesFunction(s) for s in leaf_seqs]
            out_species = [self._speciesFunction(s) for s in all_seqs-leaf_seqs]

            leaf_age_min = min([species2age[sp] for sp in leaf_species])
            out_age_min = min([species2age[sp] for sp in out_species])
            leaf_age_max = max([species2age[sp] for sp in leaf_species])
            out_age_max = max([species2age[sp] for sp in out_species])
            leaf_age = leaf_age_max - leaf_age_min
            out_age = out_age_max - out_age_min

            age_inbalance = abs(out_age - leaf_age)

            # DEBUG ONLY
            # leaf.add_features(age_inbalance = age_inbalance, age=leaf_age)

            update = False
            if age_inbalance < best_balance:
                update = True
            elif age_inbalance == best_balance:
                if size > outgroup_size: 
                    update = True
                elif size == outgroup_size:
                    dist = self.get_distance(leaf)
                    outgroup_dist = self.get_distance(outgroup_node)
                    if dist > outgroup_dist:
                        update = True
       
            if update:
                best_balance = age_inbalance
                outgroup_node = leaf
                outgroup_size = size

        return outgroup_node


#: .. currentmodule:: ete_dev
#
PhyloTree = PhyloNode
