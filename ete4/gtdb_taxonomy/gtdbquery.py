#!/usr/bin/env python3

import sys
import os

import pickle
from collections import defaultdict, Counter

from hashlib import md5

import sqlite3
import math
import tarfile
import warnings
import requests

from ete4 import ETE_DATA_HOME, update_ete_data


__all__ = ["GTDBTaxa", "is_taxadb_up_to_date"]

DB_VERSION = 2
DEFAULT_GTDBTAXADB = ETE_DATA_HOME + '/gtdbtaxa.sqlite'
DEFAULT_GTDBTAXADUMP = ETE_DATA_HOME + '/gtdbdump.tar.gz'


def as_csv(xs):
    """Return sequence xs as comma-separated values, quoted properly for SQL."""
    return ','.join("'%s'" % str(x).replace("'", "''") for x in xs)


def is_taxadb_up_to_date(dbfile=DEFAULT_GTDBTAXADB):
    """Check if a valid and up-to-date gtdbtaxa.sqlite database exists
    If dbfile= is not specified, DEFAULT_TAXADB is assumed
    """
    db = sqlite3.connect(dbfile)
    try:
        r = db.execute('SELECT version FROM stats;')
        version = r.fetchone()[0]
    except (sqlite3.OperationalError, ValueError, IndexError, TypeError):
        version = None

    db.close()

    return version == DB_VERSION


class GTDBTaxa:
    """
    Local transparent connector to the GTDB taxonomy database.
    """

    def __init__(self, dbfile=None, taxdump_file=None, memory=False):

        if not dbfile:
            self.dbfile = DEFAULT_GTDBTAXADB
        else:
            self.dbfile = dbfile

        if taxdump_file:
            self.update_taxonomy_database(taxdump_file)

        if dbfile != DEFAULT_GTDBTAXADB and not os.path.exists(self.dbfile):
            print('GTDB database not present yet (first time used?)', file=sys.stderr)

            update_ete_data(DEFAULT_GTDBTAXADUMP,
                            url='gtdb_taxonomy/gtdblatest/gtdb_latest_dump.tar.gz')

            self.update_taxonomy_database(taxdump_file=DEFAULT_GTDBTAXADUMP)

        if not os.path.exists(self.dbfile):
            raise ValueError("Cannot open taxonomy database: %s" % self.dbfile)

        self.db = None
        self._connect()

        if not is_taxadb_up_to_date(self.dbfile):
            print('GTDB database format is outdated. Upgrading', file=sys.stderr)
            self.update_taxonomy_database(taxdump_file)

        if memory:
            filedb = self.db
            self.db = sqlite3.connect(':memory:')
            filedb.backup(self.db)

    def update_taxonomy_database(self, taxdump_file=None):
        """Update the GTDB taxonomy database.

        It updates it by downloading and parsing the latest
        gtdbtaxdump.tar.gz file.

        :param taxdump_file: Alternative location of gtdbtaxdump.tar.gz.
        """
        update_db(self.dbfile, targz_file=taxdump_file)

    def _connect(self):
        self.db = sqlite3.connect(self.dbfile)

    def _translate_merged(self, all_taxids):
        conv_all_taxids = set((list(map(int, all_taxids))))
        cmd = 'SELECT taxid_old, taxid_new FROM merged WHERE taxid_old IN (%s)' % as_csv(all_taxids)

        result = self.db.execute(cmd)
        conversion = {}
        for old, new in result.fetchall():
            conv_all_taxids.discard(int(old))
            conv_all_taxids.add(int(new))
            conversion[int(old)] = int(new)
        return conv_all_taxids, conversion


    # def get_fuzzy_name_translation(self, name, sim=0.9):
    #     '''
    #     Given an inexact species name, returns the best match in the NCBI database of taxa names.
    #     :argument 0.9 sim: Min word similarity to report a match (from 0 to 1).
    #     :return: taxid, species-name-match, match-score
    #     '''


    #     import sqlite3.dbapi2 as dbapi2
    #     _db = dbapi2.connect(self.dbfile)
    #     _db.enable_load_extension(True)
    #     module_path = os.path.split(os.path.realpath(__file__))[0]
    #     _db.execute("select load_extension('%s')" % os.path.join(module_path,
    #                                                              "SQLite-Levenshtein/levenshtein.sqlext"))

    #     print("Trying fuzzy search for %s" % name)
    #     maxdiffs = math.ceil(len(name) * (1-sim))
    #     cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM species WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
    #     taxid, spname, score = None, None, len(name)
    #     result = _db.execute(cmd)
    #     try:
    #         taxid, spname, score = result.fetchone()
    #     except TypeError:
    #         cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM synonym WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
    #         result = _db.execute(cmd)
    #         try:
    #             taxid, spname, score = result.fetchone()
    #         except:
    #             pass
    #         else:
    #             taxid = int(taxid)
    #     else:
    #         taxid = int(taxid)

    #     norm_score = 1 - (float(score)/len(name))
    #     if taxid:
    #         print("FOUND!    %s taxid:%s score:%s (%s)" %(spname, taxid, score, norm_score))

    #     return taxid, spname, norm_score

    def _get_id2rank(self, internal_taxids):
        """Given a list of numeric ids (each one representing a taxa in GTDB), return a dictionary with their corresponding ranks.
        Examples:
        > gtdb.get_rank([2174, 205487, 610])
        {2174: 'family', 205487: 'order', 610: 'phylum'}

        Note: Numeric taxids are not recognized by the official GTDB taxonomy database, only for internal usage.
        """
        ids = as_csv(set(internal_taxids) - {None, ''})
        result = self.db.execute('SELECT taxid, rank FROM species WHERE taxid IN (%s)' % ids)
        return {tax: spname for tax, spname in result.fetchall()}

    def get_rank(self, taxids):
        """Give a list of GTDB string taxids, return a dictionary with their corresponding ranks.
        Examples:

        > gtdb.get_rank(['c__Thorarchaeia', 'RS_GCF_001477695.1'])
        {'c__Thorarchaeia': 'class', 'RS_GCF_001477695.1': 'subspecies'}
        """

        taxid2rank = {}
        name2ids = self._get_name_translator(taxids)
        overlap_ids = name2ids.values()
        taxids = [item for sublist in overlap_ids for item in sublist]
        ids = as_csv(set(taxids) - {None, ''})
        result = self.db.execute('SELECT taxid, rank FROM species WHERE taxid IN (%s)' % ids)
        for tax, rank in result.fetchall():
            taxid2rank[list(self._get_taxid_translator([tax]).values())[0]] = rank

        return taxid2rank

    def _get_lineage_translator(self, taxids):
        """Given a valid taxid number, return its corresponding lineage track as a
        hierarchically sorted list of parent taxids.
        """
        all_ids = set(taxids)
        all_ids.discard(None)
        all_ids.discard("")
        result = self.db.execute('SELECT taxid, track FROM species WHERE taxid IN (%s);' % as_csv(all_ids))
        id2lineages = {}
        for tax, track in result.fetchall():
            id2lineages[tax] = list(map(int, reversed(track.split(","))))
        return id2lineages

    def get_name_lineage(self, taxnames):
        """Given a valid taxname, return its corresponding lineage track as a
        hierarchically sorted list of parent taxnames.
        """
        name_lineages = []
        name2taxid = self._get_name_translator(taxnames)
        for key, value in name2taxid.items():
            lineage = self._get_lineage(value[0])
            names = self._get_taxid_translator(lineage)
            name_lineages.append({key:[names[taxid] for taxid in lineage]})

        return name_lineages

    def _get_lineage(self, taxid):
        """Given a valid taxid number, return its corresponding lineage track as a
        hierarchically sorted list of parent taxids.
        """
        if not taxid:
            return None
        taxid = int(taxid)
        result = self.db.execute('SELECT track FROM species WHERE taxid=%s' %taxid)
        raw_track = result.fetchone()
        if not raw_track:
            #perhaps is an obsolete taxid
            _, merged_conversion = self._translate_merged([taxid])
            if taxid in merged_conversion:
                result = self.db.execute('SELECT track FROM species WHERE taxid=%s' %merged_conversion[taxid])
                raw_track = result.fetchone()
            # if not raise error
            if not raw_track:
                #raw_track = ["1"]
                raise ValueError("%s taxid not found" %taxid)
            else:
                warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))

        track = list(map(int, raw_track[0].split(",")))
        return list(reversed(track))

    def get_common_names(self, taxids):
        cmd = "select taxid, common FROM species WHERE taxid IN (%s);" % as_csv(taxids)
        result = self.db.execute(cmd)
        id2name = {}
        for tax, common_name in result.fetchall():
            if common_name:
                id2name[tax] = common_name
        return id2name

    def _get_taxid_translator(self, taxids, try_synonyms=True):
        """Given a list of taxids, returns a dictionary with their corresponding
        scientific names.
        """

        all_ids = set(map(int, taxids))
        all_ids.discard(None)
        all_ids.discard("")
        cmd = "select taxid, spname FROM species WHERE taxid IN (%s);" % as_csv(all_ids)
        result = self.db.execute(cmd)
        id2name = {}
        for tax, spname in result.fetchall():
            id2name[tax] = spname

        # any taxid without translation? lets tray in the merged table
        # if len(all_ids) != len(id2name) and try_synonyms:
        #     not_found_taxids = all_ids - set(id2name.keys())
        #     taxids, old2new = self._translate_merged(not_found_taxids)
        #     new2old = {v: k for k,v in old2new.items()}

        #     if old2new:
        #         query = ','.join(['"%s"' %v for v in new2old])
        #         cmd = "select taxid, spname FROM species WHERE taxid IN (%s);" %query
        #         result = self.db.execute(cmd)
        #         for tax, spname in result.fetchall():
        #             id2name[new2old[tax]] = spname

        return id2name

    def _get_name_translator(self, names):
        """
        Given a list of taxid scientific names, returns a dictionary translating them into their corresponding taxids.
        Exact name match is required for translation.
        """

        name2id = {}
        #name2realname = {}
        name2origname = {}
        for n in names:
            name2origname[n.lower()] = n

        names = set(name2origname.keys())

        cmd = 'SELECT spname, taxid FROM species WHERE spname IN (%s)' % as_csv(name2origname.keys())
        result = self.db.execute(cmd)
        for sp, taxid in result.fetchall():
            oname = name2origname[sp.lower()]
            name2id.setdefault(oname, []).append(taxid)
            #name2realname[oname] = sp
        missing =  names - set([n.lower() for n in name2id.keys()])
        if missing:
            result = self.db.execute('SELECT spname, taxid FROM synonym WHERE spname IN (%s)' % as_csv(missing))
            for sp, taxid in result.fetchall():
                oname = name2origname[sp.lower()]
                name2id.setdefault(oname, []).append(taxid)
                #name2realname[oname] = sp
        return name2id

    def _translate_to_names(self, taxids):
        """
        Given a list of taxid numbers, returns another list with their corresponding scientific names.
        """
        id2name = self._get_taxid_translator(taxids)
        names = []
        for sp in taxids:
            names.append(id2name.get(sp, sp))
        return names


    def get_descendant_taxa(self, parent, intermediate_nodes=False, rank_limit=None, collapse_subspecies=False, return_tree=False):
        """
        given a parent taxid or scientific species name, returns a list of all its descendants taxids.
        If intermediate_nodes is set to True, internal nodes will also be dumped.
        """
        try:
            taxid = int(parent)
        except ValueError:
            try:
                taxid = self._get_name_translator([parent])[parent][0]
            except KeyError:
                raise ValueError('%s not found!' %parent)

        # checks if taxid is a deprecated one, and converts into the right one.
        _, conversion = self._translate_merged([taxid]) #try to find taxid in synonyms table
        if conversion:
            taxid = conversion[taxid]

        with open(self.dbfile+".traverse.pkl", "rb") as CACHED_TRAVERSE:
            prepostorder = pickle.load(CACHED_TRAVERSE)
        descendants = {}
        found = 0
        for tid in prepostorder:
            if tid == taxid:
                found += 1
            elif found == 1:
                descendants[tid] = descendants.get(tid, 0) + 1
            elif found == 2:
                break

        if not found:
            raise ValueError("taxid not found:%s" %taxid)
        elif found == 1:
            return [taxid]
        if rank_limit or collapse_subspecies or return_tree:
            descendants_spnames = self._get_taxid_translator(list(descendants.keys()))
            #tree = self.get_topology(list(descendants.keys()), intermediate_nodes=intermediate_nodes, collapse_subspecies=collapse_subspecies, rank_limit=rank_limit)
            tree = self.get_topology(list(descendants_spnames.values()), intermediate_nodes=intermediate_nodes, collapse_subspecies=collapse_subspecies, rank_limit=rank_limit)
            if return_tree:
                return tree
            elif intermediate_nodes:
                return [n.name for n in tree.get_descendants()]
            else:
                return [n.name for n in tree]

        elif intermediate_nodes:
            return self._translate_to_names([tid for tid, count in descendants.items()])
        else:
            self._translate_to_names([tid for tid, count in descendants.items() if count == 1])
            return self._translate_to_names([tid for tid, count in descendants.items() if count == 1])

    def get_topology(self, taxnames, intermediate_nodes=False, rank_limit=None,
                     collapse_subspecies=False, annotate=True):
        """Return minimal pruned GTDB taxonomy tree containing all given taxids.

        :param intermediate_nodes: If True, single child nodes
            representing the complete lineage of leaf nodes are kept.
            Otherwise, the tree is pruned to contain the first common
            ancestor of each group.
        :param rank_limit: If valid NCBI rank name is provided, the
            tree is pruned at that given level. For instance, use
            rank="species" to get rid of sub-species or strain leaf
            nodes.
        :param collapse_subspecies: If True, any item under the
            species rank will be collapsed into the species upper
            node.
        """
        from .. import PhyloTree
        #taxids, merged_conversion = self._translate_merged(taxids)
        tax2id = self._get_name_translator(taxnames) #{'f__Korarchaeaceae': [2174], 'o__Peptococcales': [205487], 'p__Huberarchaeota': [610]}
        taxids = [i[0] for i in tax2id.values()]

        if len(taxids) == 1:
            root_taxid = int(list(taxids)[0])
            with open(self.dbfile+".traverse.pkl", "rb") as CACHED_TRAVERSE:
                prepostorder = pickle.load(CACHED_TRAVERSE)
            descendants = {}
            found = 0
            nodes = {}
            hit = 0
            visited = set()
            start = prepostorder.index(root_taxid)
            try:
            	end = prepostorder.index(root_taxid, start+1)
            	subtree = prepostorder[start:end+1]
            except ValueError:
                # If root taxid is not found in postorder, must be a tip node
            	subtree = [root_taxid]
            leaves = set([v for v, count in Counter(subtree).items() if count == 1])
            tax2name = self._get_taxid_translator(list(subtree))
            name2tax ={spname:taxid for taxid,spname in tax2name.items()}
            nodes[root_taxid] = PhyloTree({'name': str(root_taxid)})
            current_parent = nodes[root_taxid]
            for tid in subtree:
                if tid in visited:
                    current_parent = nodes[tid].up
                else:
                    visited.add(tid)
                    nodes[tid] = PhyloTree({'name': tax2name.get(tid, '')})
                    current_parent.add_child(nodes[tid])
                    if tid not in leaves:
                        current_parent = nodes[tid]
            root = nodes[root_taxid]
        else:
            taxids = set(map(int, taxids))
            sp2track = {}
            elem2node = {}
            id2lineage = self._get_lineage_translator(taxids)
            all_taxids = set()
            for lineage in id2lineage.values():
                all_taxids.update(lineage)
            id2rank = self._get_id2rank(all_taxids)

            tax2name = self._get_taxid_translator(taxids)
            all_taxid_codes = set([_tax for _lin in list(id2lineage.values()) for _tax in _lin])
            extra_tax2name = self._get_taxid_translator(list(all_taxid_codes - set(tax2name.keys())))
            tax2name.update(extra_tax2name)
            name2tax ={spname:taxid for taxid,spname in tax2name.items()}

            for sp in taxids:
                track = []
                lineage = id2lineage[sp]

                for elem in lineage:
                    spanme = tax2name[elem]
                    if elem not in elem2node:
                        node = elem2node.setdefault(elem, PhyloTree())
                        node.name = str(tax2name[elem])
                        node.taxid = str(tax2name[elem])
                        node.add_prop("rank", str(id2rank.get(int(elem), "no rank")))
                    else:
                        node = elem2node[elem]
                    track.append(node)
                sp2track[sp] = track
            # generate parent child relationships
            for sp, track in sp2track.items():
                parent = None
                for elem in track:
                    if parent and elem not in parent.children:
                        parent.add_child(elem)
                    if rank_limit and elem.props.get('rank') == rank_limit:
                        break
                    parent = elem
            root = elem2node[1]
        #remove onechild-nodes

        if not intermediate_nodes:
            for n in root.descendants():
                if len(n.children) == 1 and int(name2tax.get(n.name, n.name)) not in taxids:
                    n.delete(prevent_nondicotomic=False)

        if len(root.children) == 1:
            tree = root.children[0].detach()
        else:
            tree = root

        if collapse_subspecies:
            to_detach = []
            for node in tree.traverse():
                if node.props.get('rank') == 'species':
                    to_detach.extend(node.children)
            for n in to_detach:
                n.detach()

        if annotate:
            self.annotate_tree(tree, ignore_unclassified=False)

        return tree

    def annotate_tree(self, t, taxid_attr='name', tax2name=None,
                        tax2track=None, tax2rank=None, ignore_unclassified=False):
        """Annotate a tree containing taxids as leaf names.

        It annotates by adding the properties 'taxid', 'sci_name',
        'lineage', 'named_lineage' and 'rank'.

        :param t: Tree to annotate.
        :param taxid_attr: Node attribute (property) containing the
            taxid number associated to each node (i.e. species in
            PhyloTree instances).
        :param tax2name, tax2track, tax2rank: Pre-calculated
            dictionaries with translations from taxid number to names,
            track lineages and ranks.
        """
        taxids = set()
        if taxid_attr == "taxid":
            for n in t.leaves():
                if taxid_attr in n.props:
                    taxids.add(n.props[taxid_attr])
        else:
            for n in t.leaves():
                try:
                    # translate gtdb name -> id
                    taxaname = getattr(n, taxid_attr, n.props.get(taxid_attr))
                    tid = self._get_name_translator([taxaname])[taxaname][0]
                    taxids.add(tid)
                except (KeyError, ValueError, AttributeError):
                    pass
        merged_conversion = {}

        taxids, merged_conversion = self._translate_merged(taxids)

        if not tax2name or taxids - set(map(int, list(tax2name.keys()))):
            tax2name = self._get_taxid_translator(taxids)
        if not tax2track or taxids - set(map(int, list(tax2track.keys()))):
            tax2track = self._get_lineage_translator(taxids)

        all_taxid_codes = set([_tax for _lin in list(tax2track.values()) for _tax in _lin])
        extra_tax2name = self._get_taxid_translator(list(all_taxid_codes - set(tax2name.keys())))
        tax2name.update(extra_tax2name)

        tax2common_name = self.get_common_names(tax2name.keys())

        if not tax2rank:
            tax2rank = self._get_id2rank(list(tax2name.keys()))

        name2tax ={spname:taxid for taxid,spname in tax2name.items()}
        n2leaves = t.get_cached_content()

        for node in t.traverse('postorder'):
            if node.is_leaf:
                node_taxid = getattr(node, taxid_attr, node.props.get(taxid_attr))
            else:
                node_taxid = None
            node.add_prop('taxid', node_taxid)
            if node_taxid:
                tmp_taxid = self._get_name_translator([node_taxid]).get(node_taxid, [None])[0]
                if node_taxid in merged_conversion:
                    node_taxid = merged_conversion[node_taxid]

                rank = tax2rank.get(tmp_taxid, 'Unknown')
                if rank != 'subspecies':
                    sci_name = tax2name.get(tmp_taxid, '')
                else:
                    # For subspecies, gtdb taxid (like 'RS_GCF_0062.1') is not informative. Better use the species one.
                    track = tax2track[tmp_taxid]  # like ['root', 'd__Bacteria', ..., 's__Moorella', 'RS_GCF_0062.1']
                    sci_name = tax2name.get(track[-2], '')

                node.add_props(sci_name = sci_name,
                               common_name = tax2common_name.get(node_taxid, ''),
                               lineage = tax2track.get(tmp_taxid, []),
                               rank = tax2rank.get(tmp_taxid, 'Unknown'),
                               named_lineage = [tax2name.get(tax, str(tax)) for tax in tax2track.get(tmp_taxid, [])])
            elif node.is_leaf:
                node.add_props(sci_name = getattr(node, taxid_attr, node.props.get(taxid_attr, 'NA')),
                               common_name = '',
                               lineage = [],
                               rank = 'Unknown',
                               named_lineage = [])
            else:

                if ignore_unclassified:
                    vectors = [lf.props.get('lineage') for lf in n2leaves[node] if lf.props.get('lineage')]
                else:
                    vectors = [lf.props.get('lineage') for lf in n2leaves[node]]
                lineage = self._common_lineage(vectors)

                rank = tax2rank.get(lineage[-1], 'Unknown')

                if lineage[-1]:
                    if rank != 'subspecies':
                        ancestor = self._get_taxid_translator([lineage[-1]])[lineage[-1]]
                    else:
                        ancestor = self._get_taxid_translator([lineage[-2]])[lineage[-2]]
                        lineage = lineage[:-1] # remove subspecies from lineage
                        rank = tax2rank.get(lineage[-1], 'Unknown') # update rank
                else:
                    ancestor = None

                node.add_props(sci_name = tax2name.get(ancestor, str(ancestor)),
                               common_name = tax2common_name.get(lineage[-1], ''),
                               taxid = ancestor,
                               lineage = lineage,
                               rank = rank,
                               named_lineage = [tax2name.get(tax, str(tax)) for tax in lineage])

        return tax2name, tax2track, tax2rank

    def _common_lineage(self, vectors):
        occurrence = defaultdict(int)
        pos = defaultdict(set)
        for v in vectors:
            for i, taxid in enumerate(v):
                occurrence[taxid] += 1
                pos[taxid].add(i)

        common = [taxid for taxid, ocu in occurrence.items() if ocu == len(vectors)]
        if not common:
            return [""]
        else:
            sorted_lineage = sorted(common, key=lambda x: min(pos[x]))
            return sorted_lineage

        # OLD APPROACH:

        # visited = defaultdict(int)
        # for index, name in [(ei, e) for v in vectors for ei, e in enumerate(v)]:
        #     visited[(name, index)] += 1

        # def _sort(a, b):
        #     if a[1] > b[1]:
        #         return 1
        #     elif a[1] < b[1]:
        #         return -1
        #     else:
        #         if a[0][1] > b[0][1]:
        #             return 1
        #         elif a[0][1] < b[0][1]:
        #             return -1
        #     return 0

        # matches = sorted(visited.items(), _sort)

        # if matches:
        #     best_match = matches[-1]
        # else:
        #     return "", set()

        # if best_match[1] != len(vectors):
        #     return "", set()
        # else:
        #     return best_match[0][0], [m[0][0] for m in matches if m[1] == len(vectors)]


    def get_broken_branches(self, t, taxa_lineages, n2content=None):
        """Returns a list of GTDB lineage names that are not monophyletic in the
        provided tree, as well as the list of affected branches and their size.
        CURRENTLY EXPERIMENTAL
        """
        if not n2content:
            n2content = t.get_cached_content()

        tax2node = defaultdict(set)

        unknown = set()
        for leaf in t.iter_leaves():
            if leaf.sci_name.lower() != "unknown":
                lineage = taxa_lineages[leaf.taxid]
                for index, tax in enumerate(lineage):
                    tax2node[tax].add(leaf)
            else:
                unknown.add(leaf)

        broken_branches = defaultdict(set)
        broken_clades = set()
        for tax, leaves in tax2node.items():
            if len(leaves) > 1:
                common = t.get_common_ancestor(leaves)
            else:
                common = list(leaves)[0]
            if (leaves ^ set(n2content[common])) - unknown:
                broken_branches[common].add(tax)
                broken_clades.add(tax)

        broken_clade_sizes = [len(tax2node[tax]) for tax in broken_clades]
        return broken_branches, broken_clades, broken_clade_sizes


    # TODO: See why this code is commented out and comment it properly or remove it.
    #
    # def annotate_tree_with_taxa(self, t, name2taxa_file, tax2name=None, tax2track=None, attr_name="name"):
    #     if name2taxa_file:
    #         names2taxid = dict([map(strip, line.split("\t"))
    #                             for line in open(name2taxa_file)])
    #     else:
    #         names2taxid = dict([(n.name, getattr(n, attr_name)) for n in t.iter_leaves()])

    #     not_found = 0
    #     for n in t.iter_leaves():
    #         n.add_features(taxid=names2taxid.get(n.name, 0))
    #         n.add_features(species=n.taxid)
    #         if n.taxid == 0:
    #             not_found += 1
    #     if not_found:
    #         print >>sys.stderr, "WARNING: %s nodes where not found within NCBI taxonomy!!" %not_found

    #     return self.annotate_tree(t, tax2name, tax2track, attr_name="taxid")


def load_gtdb_tree_from_dump(tar):
    from .. import Tree
    # Download: gtdbdump/gtdbr202dump.tar.z
    parent2child = {}
    name2node = {}
    node2taxname = {}
    synonyms = set()
    name2rank = {}
    node2common = {}
    print("Loading node names...")
    unique_nocase_synonyms = set()
    for line in tar.extractfile("names.dmp"):
        line = str(line.decode())
        fields =  [_f.strip() for _f in line.split("|")]
        nodename = fields[0]
        name_type = fields[3].lower()
        taxname = fields[1]

        # Clean up tax names so we make sure the don't include quotes. See https://github.com/etetoolkit/ete/issues/469
        taxname = taxname.rstrip('"').lstrip('"')

        if name_type == "scientific name":
            node2taxname[nodename] = taxname
        if name_type == "genbank common name":
            node2common[nodename] = taxname
        elif name_type in set(["synonym", "equivalent name", "genbank equivalent name",
                               "anamorph", "genbank synonym", "genbank anamorph", "teleomorph"]):

            # Keep track synonyms, but ignore duplicate case-insensitive names. See https://github.com/etetoolkit/ete/issues/469
            synonym_key = (nodename, taxname.lower())
            if synonym_key not in unique_nocase_synonyms:
                unique_nocase_synonyms.add(synonym_key)
                synonyms.add((nodename, taxname))

    print(len(node2taxname), "names loaded.")
    print(len(synonyms), "synonyms loaded.")

    print("Loading nodes...")
    for line in tar.extractfile("nodes.dmp"):
        line = str(line.decode())
        fields =  line.split("|")
        nodename = fields[0].strip()
        parentname = fields[1].strip()
        try:
            n = Tree()
        except:
            from .. import Tree
            n = Tree()
        n.name = nodename
        #n.taxname = node2taxname[nodename]
        n.add_prop('taxname', node2taxname[nodename])
        if nodename in node2common:
            n.add_prop('common_name', node2taxname[nodename])
        n.add_prop('rank', fields[2].strip())
        parent2child[nodename] = parentname
        name2node[nodename] = n
    print(len(name2node), "nodes loaded.")

    print("Linking nodes...")
    for node in name2node:
       if node == "1":
           t = name2node[node]
       else:
           parent = parent2child[node]
           parent_node = name2node[parent]
           parent_node.add_child(name2node[node])
    print("Tree is loaded.")
    return t, synonyms

def generate_table(t):
    OUT = open("taxa.tab", "w")
    for j, n in enumerate(t.traverse()):
        if j%1000 == 0:
            print("\r",j,"generating entries...", end=' ')
        temp_node = n
        track = []
        while temp_node:
            track.append(temp_node.name)
            temp_node = temp_node.up
        if n.up:
            print('\t'.join([n.name, n.up.name, n.props.get('taxname'), n.props.get("common_name", ''), n.props.get("rank"), ','.join(track)]), file=OUT)
        else:
            print('\t'.join([n.name, "", n.props.get('taxname'), n.props.get("common_name", ''), n.props.get("rank"), ','.join(track)]), file=OUT)
    OUT.close()


def update_db(dbfile, targz_file=None):
    basepath = os.path.split(dbfile)[0]
    if basepath and not os.path.exists(basepath):
        os.mkdir(basepath)

    # if users don't provie targz_file, update the latest version from ete-data
    if not targz_file:
        update_local_taxdump(DEFAULT_GTDBTAXADUMP)
        targz_file = DEFAULT_GTDBTAXADUMP

    tar = tarfile.open(targz_file, 'r')
    t, synonyms = load_gtdb_tree_from_dump(tar)

    prepostorder = [int(node.name) for post, node in t.iter_prepostorder()]

    with open(dbfile+'.traverse.pkl', 'wb') as fout:
        pickle.dump(prepostorder, fout, 2)

    print("Updating database: %s ..." %dbfile)
    generate_table(t)

    upload_data(dbfile)

    os.system("rm taxa.tab")

def update_local_taxdump(fname=DEFAULT_GTDBTAXADUMP):
    # latest version of gtdb taxonomy dump
    url = "https://github.com/etetoolkit/ete-data/raw/main/gtdb_taxonomy/gtdblatest/gtdb_latest_dump.tar.gz"

    if not os.path.exists(fname):
        print(f'Downloading {fname} from {url} ...')
        with open(fname, 'wb') as f:
            f.write(requests.get(url).content)
    else:
        md5_local = md5(open(fname, 'rb').read()).hexdigest()
        md5_remote = requests.get(url + '.md5').text.split()[0]

        if md5_local != md5_remote:
            print(f'Updating {fname} from {url} ...')
            with open(fname, 'wb') as f:
                f.write(requests.get(url).content)
        else:
            print(f'File {fname} is already up-to-date with {url} .')

def upload_data(dbfile):
    print()
    print('Uploading to', dbfile)
    basepath = os.path.split(dbfile)[0]
    if basepath and not os.path.exists(basepath):
        os.mkdir(basepath)

    db = sqlite3.connect(dbfile)

    create_cmd = """
    DROP TABLE IF EXISTS stats;
    DROP TABLE IF EXISTS species;
    DROP TABLE IF EXISTS synonym;
    DROP TABLE IF EXISTS merged;
    CREATE TABLE stats (version INT PRIMARY KEY);
    CREATE TABLE species (taxid INT PRIMARY KEY, parent INT, spname VARCHAR(50) COLLATE NOCASE, common VARCHAR(50) COLLATE NOCASE, rank VARCHAR(50), track TEXT);
    CREATE TABLE synonym (taxid INT,spname VARCHAR(50) COLLATE NOCASE, PRIMARY KEY (spname, taxid));
    CREATE TABLE merged (taxid_old INT, taxid_new INT);
    CREATE INDEX spname1 ON species (spname COLLATE NOCASE);
    CREATE INDEX spname2 ON synonym (spname COLLATE NOCASE);
    """
    for cmd in create_cmd.split(';'):
        db.execute(cmd)
    print()

    db.execute("INSERT INTO stats (version) VALUES (%d);" %DB_VERSION)
    db.commit()

    # for i, line in enumerate(open("syn.tab")):
    #     if i%5000 == 0 :
    #         print('\rInserting synonyms:     % 6d' %i, end=' ', file=sys.stderr)
    #         sys.stderr.flush()
    #     taxid, spname = line.strip('\n').split('\t')
    #     db.execute("INSERT INTO synonym (taxid, spname) VALUES (?, ?);", (taxid, spname))
    # print()
    # db.commit()
    # for i, line in enumerate(open("merged.tab")):
    #     if i%5000 == 0 :
    #         print('\rInserting taxid merges: % 6d' %i, end=' ', file=sys.stderr)
    #         sys.stderr.flush()
    #     taxid_old, taxid_new = line.strip('\n').split('\t')
    #     db.execute("INSERT INTO merged (taxid_old, taxid_new) VALUES (?, ?);", (taxid_old, taxid_new))
    # print()
    # db.commit()

    with open('taxa.tab') as f_taxa:
        for i, line in enumerate(f_taxa):
            if i % 5000 == 0:
                print('\rInserting taxids: %8d' % i, end=' ', file=sys.stderr)
                sys.stderr.flush()
            taxid, parentid, spname, common, rank, lineage = line.strip('\n').split('\t')
            db.execute(('INSERT INTO species          (taxid, parent, spname, common, rank, track) '
                        'VALUES (?, ?, ?, ?, ?, ?)'), (taxid, parentid, spname, common, rank, lineage))
    print()
    db.commit()

if __name__ == "__main__":
    #from .. import PhyloTree
    gtdb = GTDBTaxa()
    gtdb.update_taxonomy_database(DEFAULT_GTDBTAXADUMP)

    descendants = gtdb.get_descendant_taxa('c__Thorarchaeia', collapse_subspecies=True, return_tree=True)
    print(descendants.write(properties=None))
    print(descendants.get_ascii(properties=['sci_name', 'taxid', 'rank']))
    tree = gtdb.get_topology(["p__Huberarchaeota", "o__Peptococcales", "f__Korarchaeaceae", "s__Korarchaeum"], intermediate_nodes=True, collapse_subspecies=True, annotate=True)
    print(tree.get_ascii(properties=["taxid", "sci_name", "rank"]))

    tree = PhyloTree('((c__Thorarchaeia, c__Lokiarchaeia_A), s__Caballeronia udeis);', sp_naming_function=lambda name: name)
    tax2name, tax2track, tax2rank = gtdb.annotate_tree(tree, taxid_attr="name")
    print(tree.get_ascii(properties=["taxid", "name", "sci_name", "rank"]))

    print(gtdb.get_name_lineage(['RS_GCF_006228565.1', 'GB_GCA_001515945.1']))
