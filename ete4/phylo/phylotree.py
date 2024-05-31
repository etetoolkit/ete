"""
This module defines the PhyloTree class to manage phylogenetic trees.
It inherits from Tree and adds some special features to the the node
instances.
"""

import sys
import re
import warnings
import itertools
from collections import defaultdict
from ete4 import Tree, SeqGroup, NCBITaxa, GTDBTaxa
from .reconciliation import get_reconciled_tree
from . import spoverlap

__all__ = ["PhyloTree"]


def is_dup(n):
    return n.props.get("evoltype") == "D"

def get_subtrees(tree, full_copy=False, properties=None, newick_only=False):
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
    return ntrees, ndups, _get_subtrees(tree, full_copy, properties, newick_only)

def _get_subtrees(tree, full_copy=False, properties=None, newick_only=False):
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
    properties = set(properties) if properties else set()
    properties.update(["name"])

    def _nodereplacer(match):
        pre, b, post =  match.groups()
        pre = '' if not pre else pre
        post = '' if not post else post
        node = nid2node[int(b)]
        fstring = ""
        if properties:
            fstring = "".join(["[&&NHX:",
                               ':'.join(["%s=%s" %(p, node.props.get(p))
                                         for p in properties if node.props.get(p)])
                               , "]"])

        return ''.join([pre, node.name, fstring, post])

    if newick_only:
        id_match = re.compile(r"([^0-9])?(\d+)([^0-9])?")
        for nw in sp_trees:
            yield re.sub(id_match, _nodereplacer, str(nw)+";")
    else:
        for nw in sp_trees:
            # I take advantage from the fact that I generated the subtrees
            # using tuples, so str representation is actually a newick :)
            t = PhyloTree(str(nw)+";")
            # Map properties from original tree
            for leaf in t.leaves():
                _nid = int(leaf.name)
                for p in properties:
                    leaf.add_prop(p, getattr(nid2node[_nid], p))
            yield t

def calc_subtrees(tree):
    """Return the number of species and duplications for the given tree.

    The ones that the TreeKO algorithm would produce.
    """
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

def iter_sptrees(sptrees, nid2node, properties=None, newick_only=False):
    """ Loads and map the species trees returned by get_subtrees"""

    properties = set(properties) if properties else set()
    properties.update(["name"])

    def _nodereplacer(match):
        pre, b, post =  match.groups()
        node = nid2node[int(b)]
        fstring = ""
        if properties:
            fstring = "".join(["[&&NHX:",
                               ','.join(["%s=%s" %(p, node.props.get(p))
                                         for p in properties if node.props.get(p)])
                               , "]"])

        return ''.join([pre, node.name, fstring, post])

    if newick_only:
        id_match = re.compile(r"([^0-9])(\d+)([^0-9])")
        for nw in sptrees:
            yield re.sub(id_match, _nodereplacer, str(nw)+";")
    else:
        for nw in sptrees:
            # I take advantage from the fact that I generated the subtrees
            # using tuples, so str representation is actually a newick :)
            t = PhyloTree(str(nw)+";")
            # Map properties from original tree
            for leaf in t.leaves():
                _nid = int(leaf.name)
                for p in properties:
                    leaf.add_prop(p, getattr(nid2node[_nid], p))
            yield t

def _get_subtrees_recursive(node, full_copy=True):
    if is_dup(node):
        sp_trees = []
        for ch in node.children:
            sp_trees.extend(_get_subtrees_recursive(ch, full_copy=full_copy))
        return sp_trees

    # saves a list of duplication nodes under current node
    dups = []
    for _n in node.leaves(is_leaf_fn=is_dup):
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
                _node = node.write(format=9, properties=["name", "evoltype"])
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
            _node = node.write(format=9, properties=["name", "evoltype"])
        #node.detach()
        sp_trees = [_node]

    return sp_trees

def get_subparts(n):
    subtrees = []
    if is_dup(n):
        for ch in n.get_children():
            ch.detach()
            subtrees.extend(get_subparts(ch))
    else:
        to_visit = []
        for _n in n.leaves(is_leaf_fn=is_dup):
            if is_dup(_n):
                to_visit.append(_n)

        for _n in to_visit:
            _n.detach()

        freaks = [_n for _n in n.descendants() if
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


class PhyloTree(Tree):
    """
    Class to store a phylogenetic tree.

    Extends the standard :class:`Tree` instance by adding
    specific properties and methods to work with phylogentic trees.
    """

    def __init__(self, newick=None, children=None, alignment=None,
                 alg_format="fasta", sp_naming_function=None,
                 parser=None):
        """
        :param newick: If not None, initializes the tree from a newick,
            which can be a string or file object containing it.
        :param children: If not None, the children to add to this node.
        :param alignment: File containing a multiple sequence alignment.
        :param alg_format: "fasta", "phylip" or "iphylip" (interleaved).
        :param parser: Parser to read the newick.
        :param sp_naming_function: Function that gets a node name and
            returns the species name (see
            :func:`PhyloTree.set_species_naming_function`). By default,
            the 3 first letters of node names will be used as species
            identifier.
        """
        super().__init__(data=newick, children=children, parser=parser)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloTree constructor during parsing.
        if alignment:
            self.link_to_alignment(alignment, alg_format)

        if newick:
            self.set_species_naming_function(sp_naming_function)

    @property
    def species(self):
        if self.props.get('_speciesFunction'):
            if 'species' in self.props:
                warnings.warn('Ambiguous species: both species and _speciesFunction'
                             'defined. You can remove "species" from this node.')
            try:
                return self.props.get('_speciesFunction')(self.name)
            except:
                return self.props.get('_speciesFunction')(self)
        else:
            return self.props.get('species')

    @species.setter
    def species(self, value):
        assert self.props.get('_speciesFunction') is None, \
            ('Species naming function present, cannot set species manually. '
             'Maybe call set_species_naming_function() first?')
        self.props['species'] = value

    def __repr__(self):
        return "PhyloTree '%s' (%s)" % (self.name, hex(self.__hash__()))

    def write(self, outfile=None, props=(), parser=None,
              format_root_node=False, is_leaf_fn=None):
        if props is None:
            props = sorted(set(p for node in self.traverse()
                               for p in node.props if not p.startswith('_')))
        return super().write(outfile, props, parser, format_root_node, is_leaf_fn)

    def set_species_naming_function(self, fn):
        """Set the function used to get the species from the node's name.

        :param fn: Function that takes a nodename and returns the species name.

        Example of a parsing function::

          def parse_sp_name(node_name):
              return node_name.split("_")[1]
          tree.set_species_naming_function(parse_sp_name)
        """
        for n in self.traverse():
            if fn is not None:
                n.props['_speciesFunction'] = fn
            else:
                n.props.pop('_speciesFunction', None)

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
                n.add_prop("sequence",alg.get_seq(n.name))
            except KeyError:
                if n.is_leaf:
                    missing_leaves.append(n.name)
                else:
                    missing_internal.append(n.name)
        if len(missing_leaves)>0:
            print("Warnning: [%d] terminal nodes could not be found in the alignment." %\
                len(missing_leaves), file=sys.stderr)
        # Show warning of not associated internal nodes.
        # if len(missing_internal)>0:
        #     print >>sys.stderr, \
        #       "Warnning: [%d] internal nodes could not be found in the alignment." %\
        #       len(missing_leaves)

    def get_species(self):
        """ Returns the set of species covered by its partition. """
        return set([l.species for l in self.leaves()])

    def iter_species(self):
        """ Returns an iterator over the species grouped by this node. """
        spcs = set([])
        for l in self.leaves():
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
        """Return list of duplication and speciation events involving this node.

        Scanned nodes are also labeled internally as dup=True|False.
        You can access these labels using ``node.dup``.

        The algorithm scans all nodes from the given leafName to the
        root. Nodes are assumed to be duplications when a species
        overlap is found between its child linages. The method is
        described in more detail in:

        :Citation:
            *The Human Phylome*. T. Genome Biol. 2007;8(6):R109.
        """
        return spoverlap.get_evol_events_from_leaf(self, sos_thr=sos_thr)

    def get_descendant_evol_events(self, sos_thr=0.0):
        """ Returns a list of all duplication and speciation
        events detected after this node. Nodes are assumed to be
        duplications when a species overlap is found between its child
        linages. Method is described more detail in:

        "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
        T. Genome Biol. 2007;8(6):R109.
        """
        return spoverlap.get_evol_events_from_root(self, sos_thr=sos_thr)

    def get_farthest_oldest_leaf(self, species2age, is_leaf_fn=None):
        """Return the farthest oldest leaf to the current one.

        It requires an species2age dictionary with the age estimation
        for all species.

        :param None is_leaf_fn: A pointer to a function that receives
            a node instance as unique argument and returns True or
            False. It can be used to dynamically collapse nodes, so
            they are seen as leaves.
        """
        root = self.root
        outgroup_dist  = 0
        outgroup_node  = self
        outgroup_age = 0 # self.get_age(species2age)

        for leaf in root.leaves(is_leaf_fn=is_leaf_fn):
            if leaf.get_age(species2age) > outgroup_age:
                outgroup_dist = leaf.get_distance(self, leaf)
                outgroup_node = leaf
                outgroup_age = species2age[leaf.get_species().pop()]
            elif leaf.get_age(species2age) == outgroup_age:
                dist = leaf.get_distance(self, leaf)
                if dist>outgroup_dist:
                    outgroup_dist  = leaf.get_distance(self, leaf)
                    outgroup_node  = leaf
                    outgroup_age = species2age[leaf.get_species().pop()]
        return outgroup_node

    def get_farthest_oldest_node(self, species2age):
        """Return the farthest oldest node (leaf or internal).

        The difference with get_farthest_oldest_leaf() is that in this
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
        all_seqs = set(self.leaf_names())
        outgroup_dist  = 0
        best_balance = max(species2age.values())
        outgroup_node  = self
        outgroup_size = 0

        for leaf in root.descendants():
            leaf_seqs = set(leaf.leaf_names())
            size = len(leaf_seqs)

            leaf_species =[self.props.get('_speciesFunction')(s) for s in leaf_seqs]
            out_species = [self.props.get('_speciesFunction')(s) for s in all_seqs-leaf_seqs]

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
                    dist = self.get_distance(self, leaf)
                    outgroup_dist = self.get_distance(self, outgroup_node)
                    if dist > outgroup_dist:
                        update = True

            if update:
                best_balance = age_inbalance
                outgroup_node = leaf
                outgroup_size = size

        return outgroup_node

    def get_speciation_trees(self, map_properties=None, autodetect_duplications=True,
                             newick_only=False, prop='species'):
        """Return number of species trees, of duplications, and an iterator.

        Calculates all possible species trees contained within a
        duplicated gene family tree as described in `Treeko
        <http://treeko.cgenomics.org>`_ (see `Marcet and Gabaldon,
        2011 <http://www.ncbi.nlm.nih.gov/pubmed/21335609>`_ ).

        :param map_properties: List of properties that should be
            mapped from the original gene family tree to each species
            tree subtree.
        :param autodetect_duplications: If True, duplication nodes
            will be automatically detected using the Species Overlap
            algorithm (:func:`PhyloTree.get_descendants_evol_events`).
            If False, duplication nodes within the original tree are
            expected to contain the property "evoltype='D'".
        """
        t = self
        if autodetect_duplications:
            n2content = t.get_cached_content()
            n2species = t.get_cached_content(prop)
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.props['evoltype'] = 'D'

        sp_trees = get_subtrees(t, properties=map_properties, newick_only=newick_only)

        return sp_trees

    def __get_speciation_trees_recursive(self):
        # NOTE: This function is experimental and for testing.
        t = self.copy()
        if autodetect_duplications:
            dups = 0
            n2content = t.get_cached_content()
            n2species = t.get_cached_content('species')

            #print "Detecting dups"
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if  len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.props['evoltype'] = 'D'
                    dups += 1
                elif node.is_leaf:
                    node._leaf = True
            #print dups
        else:
            for node in t.leaves():
                node._leaf = True
        subtrees = _get_subtrees_recursive(t)
        return len(subtrees), 0, subtrees

    def split_by_dups(self, autodetect_duplications=True):
        """Return the list of subtrees when splitting by its duplication nodes.

        :param True autodetect_duplications: If True, duplication
            nodes will be automatically detected using the Species
            Overlap algorithm
            (:func:`PhyloTree.get_descendants_evol_events`. If False,
            duplication nodes within the original tree are expected to
            contain the feature "evoltype=D".
        """
        try:
            t = self.copy()
        except Exception:
            t = self.copy("deepcopy")

        if autodetect_duplications:
            dups = 0
            n2content = t.get_cached_content()
            n2species = t.get_cached_content('species')

            #print "Detecting dups"
            for node in n2content:
                sp_subtotal = sum([len(n2species[_ch]) for _ch in node.children])
                if  len(n2species[node]) > 1 and len(n2species[node]) != sp_subtotal:
                    node.props['evoltype'] = 'D'
                    dups += 1
                elif node.is_leaf:
                    node._leaf = True
        else:
            for node in t.leaves():
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
        if species and isinstance(species, (list, tuple)):
            species = set(species)
        elif species and (not isinstance(species, (set, frozenset))):
            raise TypeError("species argument should be a set (preferred), list or tuple")

        prunned = self.copy("deepcopy") if return_copy else self
        n2sp = prunned.get_cached_content('species')
        n2leaves = prunned.get_cached_content()
        is_expansion = lambda n: (len(n2sp[n])==1 and len(n2leaves[n])>1
                                  and (species is None or species & n2sp[n]))
        for n in prunned.leaves(is_leaf_fn=is_expansion):
            repre = list(n2leaves[n])[0]
            repre.detach()
            if n is not prunned:
                n.up.add_child(repre)
                n.detach()
            else:
                return repre

        return prunned


    def annotate_ncbi_taxa(self, taxid_attr='species', tax2name=None, tax2track=None, tax2rank=None, dbfile=None, ignore_unclassified=False):
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

        :param None tax2name: A dictionary where keys are taxid
            numbers and values are their translation into NCBI
            scientific name. Its use is optional and allows to avoid
            database queries when annotating many trees containing the
            same set of taxids.

        :param None tax2track: A dictionary where keys are taxid
            numbers and values are their translation into NCBI lineage
            tracks (taxids). Its use is optional and allows to avoid
            database queries when annotating many trees containing the
            same set of taxids.

        :param None tax2rank: A dictionary where keys are taxid
            numbers and values are their translation into NCBI rank
            name. Its use is optional and allows to avoid database
            queries when annotating many trees containing the same set
            of taxids.

        :param None dbfile : If provided, the provided file will be
            used as a local copy of the NCBI taxonomy database.

        :returns: tax2name (a dictionary translating taxid numbers
            into scientific name), tax2lineage (a dictionary
            translating taxid numbers into their corresponding NCBI
            lineage track) and tax2rank (a dictionary translating
            taxid numbers into rank names).

        """

        ncbi = NCBITaxa(dbfile=dbfile)
        return ncbi.annotate_tree(self, taxid_attr=taxid_attr, tax2name=tax2name, tax2track=tax2track, tax2rank=tax2rank, ignore_unclassified=ignore_unclassified)

    def annotate_gtdb_taxa(self, taxid_attr='species', tax2name=None, tax2track=None, tax2rank=None, dbfile=None, ignore_unclassified=False):
        gtdb = GTDBTaxa(dbfile=dbfile)
        return gtdb.annotate_tree(self, taxid_attr=taxid_attr, tax2name=tax2name, tax2track=tax2track, tax2rank=tax2rank, ignore_unclassified=ignore_unclassified)

    def ncbi_compare(self, autodetect_duplications=True, cached_content=None):
        if not cached_content:
            cached_content = self.get_cached_content()
        cached_species = set([n.props.get('species') for n in cached_content[self]])

        if len(cached_species) != len(cached_content[self]):
            ntrees, ndups, target_trees = self.get_speciation_trees(
                    autodetect_duplications=autodetect_duplications,
                    map_properties=["taxid"])
        else:
            target_trees = [self]


        ncbi = NCBITaxa()
        for t in target_trees:
            ncbi.get_broken_branches(t, cached_content)
