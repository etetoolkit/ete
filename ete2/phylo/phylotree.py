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


"""
This module defines the PhyloNode dataytype to manage phylogenetic
trees. It inheritates the coretype TreeNode and add some special
features to the the node instances.
"""

import sys
import os
import re
import itertools
from collections import defaultdict
from ete2 import TreeNode, SeqGroup, NCBITaxa
from reconciliation import get_reconciled_tree
import spoverlap

__all__ = ["PhyloNode", "PhyloTree"]

def _parse_species(name):
    return name[:3]

def is_dup(n):
    return getattr(n, "evoltype", None) == "D"

def get_subtrees(tree, full_copy=False, features=None, newick_only=False):
    """Calculate all possible species trees within a gene tree. I
    tested several recursive and iterative approaches to do it and
    this is the most efficient way I found. The method is now fast and
    light enough to deal with very large gene trees, and it scales
    linearly instead of exponentially. For instance, a tree with ~8000
    nodes, ~100 species and ~400 duplications returns ~10,000 sptrees
    that could be loaded in few minutes.

    To avoid memory overloads, this function returns a tuple containing the
    total number of trees, number of duplication events, and an iterator for the
    species trees. Real trees are not actually computed until the iterator is
    first accessed. This allows to filter out cases producing astronomic numbers
    of sptrees.

    """
    ntrees, ndups = calc_subtrees(tree)
    return ntrees, ndups, _get_subtrees(tree, full_copy, features, newick_only)
    
def _get_subtrees(tree, full_copy=False, features=None, newick_only=False):
    # First I need to precalculate all the species trees in tuple (newick) format
    nid = 0
    n2nid = {}
    nid2node = {}
    n2subtrees = defaultdict(list)
    for n in tree.traverse("postorder"):
        n2nid[n] = nid
        nid2node[nid] = n
        nid += 1
        if n.children: 
            if is_dup(n):
                subtrees = []
                for ch in n.children: 
                    subtrees.extend(n2subtrees[n2nid[ch]])
            else:
                subtrees = tuple([val for val in
                                  itertools.product(n2subtrees[n2nid[n.children[0]]],
                                                    n2subtrees[n2nid[n.children[1]]])])
        else:
            subtrees = tuple([n2nid[n]])
       
        n2subtrees[n2nid[n]] = subtrees
        for ch in n.children:
            del n2subtrees[n2nid[ch]]
            
    sp_trees = n2subtrees[n2nid[tree]]
    
    # Second, I yield a tree per iteration in newick or ETE format
    features = set(features) if features else set()
    features.update(["name"])

    def _nodereplacer(match):
        pre, b, post =  match.groups()
        pre = '' if not pre else pre
        post = '' if not post else post
        node = nid2node[int(b)]
        fstring = ""
        if features: 
            fstring = "".join(["[&&NHX:",
                               ':'.join(["%s=%s" %(f, getattr(node, f))
                                         for f in features if hasattr(node, f)])
                               , "]"])

        return ''.join([pre, node.name, fstring, post])
    
    if newick_only:
        id_match = re.compile("([^0-9])?(\d+)([^0-9])?")
        for nw in sp_trees:
            yield re.sub(id_match, _nodereplacer, str(nw)+";")
    else:
        for nw in sp_trees:
            # I take advantage from the fact that I generated the subtrees
            # using tuples, so str representation is actually a newick :)
            t = PhyloTree(str(nw)+";")
            # Map features from original tree
            for leaf in t.iter_leaves():
                _nid = int(leaf.name)
                for f in features:
                    leaf.add_feature(f, getattr(nid2node[_nid], f))
            yield t

def calc_subtrees(tree):
    '''
    Computes the total number of species trees that TreeKO algorithm would produce for a given gene tree

    returns: ntrees, ndups
    ''' 
    n2subtrees = {}
    dups = 0
    for n in tree.traverse("postorder"):
        if n.children: 
            if is_dup(n):
                dups += 1
                subtrees = 0
                for ch in n.children: 
                    subtrees += n2subtrees[ch]
            else:
                subtrees = n2subtrees[n.children[0]] * n2subtrees[n.children[1]]
        else:
            subtrees = 1
        n2subtrees[n] = subtrees
    return n2subtrees[tree], dups
    
def iter_sptrees(sptrees, nid2node, features=None, newick_only=False):
    """ Loads and map the species trees returned by get_subtrees"""
    
    features = set(features) if features else set()
    features.update(["name"])

    def _nodereplacer(match):
        pre, b, post =  match.groups()
        node = nid2node[int(b)]
        fstring = ""
        if features: 
            fstring = "".join(["[&&NHX:",
                               ','.join(["%s=%s" %(f, getattr(node, f))
                                         for f in features if hasattr(node, f)])
                               , "]"])

        return ''.join([pre, node.name, fstring, post])
    
    if newick_only:
        id_match = re.compile("([^0-9])(\d+)([^0-9])")
        for nw in sptrees:
            yield re.sub(id_match, _nodereplacer, str(nw)+";")
    else:
        for nw in sptrees:
            # I take advantage from the fact that I generated the subtrees
            # using tuples, so str representation is actually a newick :)
            t = PhyloTree(str(nw)+";")
            # Map features from original tree
            for leaf in t.iter_leaves():
                _nid = int(leaf.name)
                for f in features:
                    leaf.add_feature(f, getattr(nid2node[_nid], f))
            yield t
        
def _get_subtrees_recursive(node, full_copy=True):
    if is_dup(node):
        sp_trees = []
        for ch in node.children:
            sp_trees.extend(_get_subtrees_recursive(ch, full_copy=full_copy))
        return sp_trees

    # saves a list of duplication nodes under current node
    dups = []
    for _n in node.iter_leaves(is_leaf_fn=is_dup):
        if is_dup(_n):
            dups.append(_n)

    if dups: 
        # detach inner duplication nodes and stores their anchor point
        subtrees = []
        for dp in dups:
            # The real node to attach sibling subtress
            anchor = dp.up
            dp.detach()
            
            duptrees = []
            #get all sibling sptrees in each side of the
            #duplication. Each subtree is pointed to its anchor
            for ch in dp.children:
                for subt in _get_subtrees_recursive(ch, full_copy=full_copy):
                    if not full_copy:
                        subt = node.__class__(subt)
                    subt.up = anchor
                    duptrees.append(subt)

            #all posible sptrees under this duplication are stored
            subtrees.append(duptrees)
            
        # Generates all combinations of subtrees in sibling duplications
        sp_trees = []
        for comb in itertools.product(*subtrees):
            #each subtree is attached to its anchor point and make a copy
            #of the final sp tree
            for subt in comb:
                #anchor = subt2anchor[subt]
                if subt.up:
                    subt.up.children.append(subt)
                    #print subt.up
                else:
                    sp_trees.append(subt)
            if full_copy:
                 back_up = node.up
                 node.up = None
                 _node = node.copy()
                 node.up = back_up
            else:
                _node = node.write(format=9, features=["name", "evoltype"])
            sp_trees.append(_node)
            # Clear current node
            for subt in comb:
                subt.up.children.pop(-1)
    else:
        if full_copy:
            back_up = node.up
            node.up = None
            _node = node.copy()
            node.up = back_up
        else:
            _node = node.write(format=9, features=["name", "evoltype"])
        #node.detach()
        sp_trees = [_node]
        
    return sp_trees
               
def get_subparts(n):
    def is_dup(n):
        return getattr(n, "evoltype", None) == "D"
        
    subtrees = []
    if is_dup(n):
        for ch in n.get_children():
            ch.detach()
            subtrees.extend(get_subparts(ch))
    else:
        to_visit = []
        for _n in n.iter_leaves(is_leaf_fn=is_dup):
            if is_dup(_n):
                to_visit.append(_n)

        for _n in to_visit:
            _n.detach()

        freaks = [_n for _n in n.iter_descendants() if
                  len(_n.children)==1 or (not hasattr(_n, "_leaf") and not _n.children)]
        for s in freaks:
            s.delete(prevent_nondicotomic=True)

        # Clean node structure to prevent nodes with only one child
        while len(n.children) == 1:
            n = n.children[0]
            n.detach()
            
        if not n.children and not hasattr(n, "_leaf"): 
            pass
        else:
            subtrees.append(n)
            
        for _n in to_visit:
            subtrees.extend(get_subparts(_n))
                
    return subtrees
    
    
class PhyloNode(TreeNode):
    """ 
    .. currentmodule:: ete2
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

    #: .. currentmodule:: ete2
    #:
    #Species code associated to the node. This property can be
    #automatically extracted from the TreeNode.name attribute or
    #manually set (see :func:`PhyloNode.set_species_naming_function`).
    species = property(fget = _get_species, fset = _set_species)

    def __init__(self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species, format=0, **kargs):

        # _update names?
        self._name = "NoName"
        self._species = "Unknown"
        self._speciesFunction = None
        # Caution! native __init__ has to be called after setting
        # _speciesFunction to None!!
        TreeNode.__init__(self, newick=newick, format=format, **kargs)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloNode constructor during parsing
        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            self.set_species_naming_function(sp_naming_function)

    def __repr__(self):
        return "PhyloTree node '%s' (%s)" %(self.name, hex(self.__hash__()))

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

    def link_to_alignment(self, alignment, alg_format="fasta", **kwargs):
        missing_leaves = []
        missing_internal = []
        if type(alignment) == SeqGroup:
            alg = alignment
        else:
            alg = SeqGroup(alignment, format=alg_format, **kwargs)
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
    
    def get_age(self, species2age):
        """
        Implements the phylostratigrafic method described in:
        
        Huerta-Cepas, J., & Gabaldon, T. (2011). Assigning duplication events to
        relative temporal scales in genome-wide studies. Bioinformatics, 27(1),
        38-45.
        """
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
        .. versionadded:: 2.2
        
        Returns the node better balance current tree structure
        according to the topological age of the different leaves and
        internal node sizes.

        :param species2age: A dictionary translating from leaf names
          into a topological age. 
                
        .. warning: This is currently an experimental method!!
        
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

    def get_speciation_trees(self, map_features=None, autodetect_duplications=True,
                             newick_only=False, target_attr='species'):
        """
        .. versionadded: 2.2
        
        Calculates all possible species trees contained within a
        duplicated gene family tree as described in `Treeko
        <http://treeko.cgenomics.org>`_ (see `Marcet and Gabaldon,
        2011 <http://www.ncbi.nlm.nih.gov/pubmed/21335609>`_ ).


        :argument True autodetect_duplications: If True, duplication
        nodes will be automatically detected using the Species Overlap
        algorithm (:func:`PhyloNode.get_descendants_evol_events`. If
        False, duplication nodes within the original tree are expected
        to contain the feature "evoltype=D".

        :argument None features: A list of features that should be
        mapped from the original gene family tree to each species
        tree subtree.

        :returns: (number_of_sptrees, number_of_dups, species_tree_iterator)

        """
        t = self
        if autodetect_duplications:
            #n2content, n2species = t.get_node2species()
            n2content = t.get_cached_content()
            n2species = t.get_cached_content(store_attr=target_attr)
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.add_features(evoltype="D")
               
        sp_trees = get_subtrees(t, features=map_features, newick_only=newick_only)
        
        return sp_trees

    def __get_speciation_trees_recursive(self):
        """ experimental and testing """
        t = self.copy()
        if autodetect_duplications:
            dups = 0
            #n2content, n2species = t.get_node2species()
            n2content = t.get_cached_content()
            n2species = t.get_cached_content(store_attr="species")

            #print "Detecting dups"
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if  len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.add_features(evoltype="D")
                    dups += 1
                elif node.is_leaf():
                    node._leaf = True
            #print dups
        else:
            for node in t.iter_leaves():
                node._leaf = True
        subtrees = _get_subtrees_recursive(t)
        return len(subtrees), 0, subtrees

    def split_by_dups(self, autodetect_duplications=True):
        """
        .. versionadded: 2.2
        
        Returns the list of all subtrees resulting from splitting
        current tree by its duplication nodes.

        :argument True autodetect_duplications: If True, duplication
        nodes will be automatically detected using the Species Overlap
        algorithm (:func:`PhyloNode.get_descendants_evol_events`. If
        False, duplication nodes within the original tree are expected
        to contain the feature "evoltype=D".

        :returns: species_trees
        """
        try:
            t = self.copy()
        except Exception:
            t = self.copy("deepcopy")
            
        if autodetect_duplications:
            dups = 0
            #n2content, n2species = t.get_node2species()
            n2content = t.get_cached_content()
            n2species = t.get_cached_content(store_attr="species")

            #print "Detecting dups"
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if  len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.add_features(evoltype="D")
                    dups += 1
                elif node.is_leaf():
                    node._leaf = True
            #print dups
        else:
            for node in t.iter_leaves():
                node._leaf = True
        sp_trees = get_subparts(t)
        return sp_trees
    
    def collapse_lineage_specific_expansions(self, species=None, return_copy=True):
        """ Converts lineage specific expansion nodes into a single
        tip node (randomly chosen from tips within the expansion).

        :param None species: If supplied, only expansions matching the
           species criteria will be pruned. When None, all expansions
           within the tree will be processed.

        """
        if species and type(species) not in set(["set", "frozenset"]):
            raise ValueError("species argument should be a set, frozenset")

        prunned = self.copy("deepcopy") if return_copy else self
        n2sp = prunned.get_cached_content(store_attr="species")
        n2leaves = prunned.get_cached_content()
        is_expansion = lambda n: (len(n2sp[n])==1 and len(n2leaves[n])>1
                                  and (species is None or species & n2sp[n]))
        for n in prunned.get_leaves(is_leaf_fn=is_expansion):
            repre = list(n2leaves[n])[0]
            repre.detach()
            if n is not prunned:
                n.up.add_child(repre)
                n.detach()
            else:
                return repre
            
        return prunned
   

    def annotate_ncbi_taxa(self, taxid_attr='species', tax2name=None, tax2track=None, tax2rank=None, dbfile=None):
        """Add NCBI taxonomy annotation to all descendant nodes. Leaf nodes are
        expected to contain a feature (name, by default) encoding a valid taxid
        number.

        All descendant nodes (including internal nodes) are annotated with the
        following new features:

        `Node.spname`: scientific spcies name as encoded in the NCBI taxonomy database

        `Node.named_lineage`: the NCBI lineage track using scientific names 

        `Node.taxid`: NCBI taxid number 

        `Node.lineage`: same as named_lineage but using taxid codes. 
        

        Note that for internal nodes, NCBI information will refer to the first
        common lineage of the grouped species.

        :param name taxid_attr: the name of the feature that should be used to access the taxid number associated to each node. 

        :param None tax2name: A dictionary where keys are taxid numbers and
        values are their translation into NCBI scientific name. Its use is
        optional and allows to avoid database queries when annotating many trees
        containing the same set of taxids.

        :param None tax2track: A dictionary where keys are taxid numbers and
        values are their translation into NCBI lineage tracks (taxids). Its use is
        optional and allows to avoid database queries when annotating many trees
        containing the same set of taxids.

        :param None tax2rank: A dictionary where keys are taxid numbers and
        values are their translation into NCBI rank name. Its use is optional
        and allows to avoid database queries when annotating many trees
        containing the same set of taxids.

        :param None dbfile : If provided, the provided file will be used as a
        local copy of the NCBI taxonomy database.

        :returns: tax2name (a dictionary translating taxid numbers into
        scientific name), tax2lineage (a dictionary translating taxid numbers
        into their corresponding NCBI lineage track) and tax2rank (a dictionary translating taxid numbers into
        rank names).

        """
        
        ncbi = NCBITaxa(dbfile=dbfile)        
        return ncbi.annotate_tree(self, taxid_attr=taxid_attr, tax2name=tax2name, tax2track=tax2track, tax2rank=tax2rank)


    def ncbi_compare(self, autodetect_duplications=True, cached_content=None):
        if not cached_content:
            cached_content = self.get_cached_content()
        cached_species = set([n.species for n in cached_content[self]])
        
        if len(cached_species) != len(cached_content[self]):
            print cached_species
            ntrees, ndups, target_trees = self.get_speciation_trees(autodetect_duplications=autodetect_duplications, map_features=["taxid"])
        else:
            target_trees = [self]


        ncbi = NCBITaxa()        
        for t in target_trees: 
            ncbi.get_broken_branches(t, cached_content)
        


#: .. currentmodule:: ete2
#
PhyloTree = PhyloNode
