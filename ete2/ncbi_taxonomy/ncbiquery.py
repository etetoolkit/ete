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
#!/usr/bin/env python 
import sys
import os
from collections import defaultdict, deque
from string import strip

import sqlite3
import math

c = None

__all__ = ["NCBITaxa"]

class NCBITaxa(object):
    """
    versionadded: 2.3

    Provides a local transparent connector to the NCBI taxonomy database.

    """
    
    def __init__(self, dbfile = None):
        if not dbfile:
            self.dbfile = os.path.join(os.environ.get('HOME', '/'), '.etetoolkit', 'taxa.sqlite')
        else:
            self.dbfile = dbfile
                
        if not os.path.exists(self.dbfile):
            raise ValueError("NCBI taxonomy database was not found in %s" %self.dbfile)
                            
        self.db = None
        self._connect()
            
    def _connect(self):
        self.db = sqlite3.connect(self.dbfile)

    def _update_database(self):
        pass

    def _translate_merged(self, all_taxids):
        conv_all_taxids = set((map(int, all_taxids)))
        cmd = 'select taxid_old, taxid_new FROM merged WHERE taxid_old IN (%s)' %','.join(map(str, all_taxids))
        result = self.db.execute(cmd)
        conversion = {}
        for old, new in result.fetchall():
            conv_all_taxids.discard(int(old))
            conv_all_taxids.add(int(new))
            conversion[int(old)] = int(new)
        return conv_all_taxids, conversion

    
    def get_fuzzy_name_translation(self, name, sim=0.9):
        '''
        Given an inexact species name, returns the best match in the NCBI database of taxa names.

        :argument 0.9 sim: Min word similarity to report a match (from 0 to 1).

        :return: taxid, species-name-match, match-score
        '''


        import pysqlite2.dbapi2 as sqlite2
        _db = sqlite2.connect(self.dbfile)
        _db.enable_load_extension(True)
        module_path = os.path.split(os.path.realpath(__file__))[0]
        _db.execute("select load_extension('%s')" % os.path.join(module_path,
                                                                 "SQLite-Levenshtein/levenshtein.sqlext"))

        print "Trying fuzzy search for %s" % name
        maxdiffs = math.ceil(len(name) * (1-sim))
        cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM species WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
        taxid, spname, score = None, None, len(name)
        result = _db.execute(cmd)
        try:
            taxid, spname, score = result.fetchone()
        except TypeError:
            cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM synonym WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
            result = _db.execute(cmd)
            try:
                taxid, spname, score = result.fetchone()
            except:
                pass
            else:
                taxid = int(taxid)
        else:
            taxid = int(taxid)

        norm_score = 1 - (float(score)/len(name))
        if taxid: 
            print "FOUND!    %s taxid:%s score:%s (%s)" %(spname, taxid, score, norm_score)

        return taxid, spname, norm_score

    def get_ranks(self, taxids):
        all_ids = set(taxids)
        all_ids.discard(None)
        all_ids.discard("")
        query = ','.join(['"%s"' %v for v in all_ids])
        cmd = "select taxid, rank FROM species WHERE taxid IN (%s);" %query
        result = self.db.execute(cmd)
        id2rank = {}
        for tax, spname in result.fetchall():
            id2rank[tax] = spname
        return id2rank
    
    def get_sp_lineage(self, taxid):
        """
        Given a valid taxid number, return its corresponding lineage track as a hierarchical list of parent taxids. 
 
        """
        if not taxid:
            return None
        result = self.db.execute('SELECT track FROM species WHERE taxid=%s' %taxid)
        raw_track = result.fetchone()
        if not raw_track:
            raw_track = ["1"]
            #raise ValueError("%s taxid not found" %taxid)
        track = map(int, raw_track[0].split(","))
        return list(reversed(track))
    
    def get_taxid_translator(self, taxids):
        """
        Given a list of taxid numbers, returns a dictionary of their corresponding scientific names.
        """
       
        all_ids = set(map(int, taxids))
        all_ids.discard(None)
        all_ids.discard("")
        query = ','.join(['"%s"' %v for v in all_ids])
        cmd = "select taxid, spname FROM species WHERE taxid IN (%s);" %query
        result = self.db.execute(cmd)
        id2name = {}
        for tax, spname in result.fetchall():
            id2name[tax] = spname

        # any taxid without translation? lets tray in the merged table
        if len(all_ids) != len(id2name):
            not_found_taxids = all_ids - set(id2name.keys())
            taxids, old2new = self._translate_merged(not_found_taxids)
            new2old = dict([(v,k) for k,v in old2new.iteritems()])
            
            if old2new:                
                query = ','.join(['"%s"' %v for v in new2old])
                cmd = "select taxid, spname FROM species WHERE taxid IN (%s);" %query
                result = self.db.execute(cmd)
                for tax, spname in result.fetchall():
                    id2name[new2old[tax]] = spname
            
        return id2name


    def get_name_translator(self, names):
        """
        Given a list of taxid scientific names, returns a dictionary translating them into their corresponding taxids. 

        Exact name match is required for translation.
        """
        
        name2id = {}
        name2realname = {}
        name2origname = {}
        for n in names:
            name2origname[n.lower()] = n
            
        names = set(name2origname.keys())
        
        query = ','.join(['"%s"' %n for n in name2origname.iterkeys()])
        cmd = 'select spname, taxid from species where spname IN (%s)' %query
        result = self.db.execute('select spname, taxid from species where spname IN (%s)' %query)
        for sp, taxid in result.fetchall():
            oname = name2origname[sp.lower()]
            name2id[oname] = taxid
            name2realname[oname] = sp
        missing =  names - set(name2id.keys())
        if missing:
            query = ','.join(['"%s"' %n for n in missing])
            result = self.db.execute('select spname, taxid from synonym where spname IN (%s)' %query)
            for sp, taxid in result.fetchall():
                oname = name2origname[sp.lower()]
                name2id[oname] = taxid
                name2realname[oname] = sp
        return name2id

    def translate_to_names(self, taxids):
        """
        given a list of taxid numbers, returns a list with their corresponding scientific names.
        """
        id2name = self.get_taxid_translator(taxids)
        names = []
        for sp in taxids: 
            names.append(id2name.get(sp, sp))
        return names


    def get_topology(self, taxids, intermediate_nodes=False, rank_limit=None, collapse_subspecies=False):
        """Given a list of taxid numbers, return the minimal pruned NCBI taxonomy tree
        containing all of them.

        :param False intermediate_nodes: If True, single child nodes
        representing the complete lineage of leaf nodes are kept. Otherwise, the
        tree is pruned to contain the first common ancestor of each group.

        :param None rank_limit: If valid NCBI rank name is provided, the tree is
        pruned at that given level. For instance, use rank="species" to get rid
        of sub-species or strain leaf nodes.

        """
        from ete2 import PhyloTree
        sp2track = {}
        elem2node = {}
        for sp in taxids:
            track = deque()
            lineage = self.get_sp_lineage(sp)
            id2rank = self.get_ranks(lineage)

            for elem in lineage:
                node = elem2node.setdefault(elem, PhyloTree())
                node.name = str(elem)
                node.add_feature("rank", str(id2rank.get(int(elem), "?")))
                track.append(node)
            sp2track[sp] = track

        # generate parent child relationships
        for sp, track in sp2track.iteritems():
            parent = None
            for elem in track:
                if parent and elem not in parent.children:
                    parent.add_child(elem)
                if rank_limit and elem.rank == rank_limit:
                    break
                parent = elem
        root = elem2node[1]

        # This fixes cases in which requested taxids are internal nodes
        #for x in set(sp2track) - set([n.name for n in root.iter_leaves()]):
        #    new_leaf = sp2track[x][-1].copy()
        #    for ch in new_leaf.get_children():
        #        ch.detach()
        #    sp2track[x][-1].add_child(new_leaf)

        #remove onechild-nodes
        if not intermediate_nodes:
            for n in root.get_descendants():
                if len(n.children) == 1 and int(n.name) not in taxids: 
                    n.delete(prevent_nondicotomic=False)

        if collapse_subspecies:
            species_nodes = [n for n in t.traverse() if n.rank == "species"
                             if int(n.taxid) in all_taxids]
            for sp_node in species_nodes:
                bellow = sp_node.get_descendants()
                if bellow:
                    # creates a copy of the species node
                    connector = sp_node.__class__()
                    for f in sp_node.features:
                        connector.add_feature(f, getattr(sp_node, f))
                    connector.name = connector.name + "{species}"
                    for n in bellow:
                        n.detach()
                        n.name = n.name + "{%s}" %n.rank
                        sp_node.add_child(n)
                    sp_node.add_child(connector)
                    sp_node.add_feature("collapse_subspecies", "1")
                    
        if len(root.children) == 1:
            return root.children[0].detach()
        else:
            return root


    def annotate_tree(self, t, taxid_attr="name", tax2name=None, tax2track=None, tax2rank=None):
        """Annotate a tree containing taxids as leaf names by adding the  'taxid',
        'sci_name', 'lineage', 'named_lineage' and 'rank' additional attributes.

        :param name taxid_attr: if taxid number is encoded under a different
        attribute rather than node.name, specify which. For instance, in
        PhyloTree objectd, you may want to use taxid_attr="species"

        :param tax2name,tax2track,tax2rank: Use these arguments to provide
        pre-calculated dictionaries providing translation from taxid number and
        names,track lineages and ranks.

        """

        leaves = t.get_leaves()
        taxids = set(map(int, [getattr(n, taxid_attr) for n in leaves]))
        merged_conversion = {}

        taxids, merged_conversion = self._translate_merged(taxids)

        if not tax2name or taxids - set(map(int, tax2name.keys())):
            #print "Querying for tax names"
            tax2name = self.get_taxid_translator([tid for tid in taxids])
        if not tax2track or taxids - set(map(int, tax2track.keys())):
            #print "Querying for tax lineages"
            tax2track = dict([(tid, self.get_sp_lineage(tid)) for tid in taxids])

        all_taxid_codes = set([_tax for _lin in tax2track.values() for _tax in _lin])
        extra_tax2name = self.get_taxid_translator(list(all_taxid_codes - set(tax2name.keys())))
        tax2name.update(extra_tax2name)

        if not tax2rank:
            tax2rank = self.get_ranks(tax2name.keys())

        n2leaves = t.get_cached_content()

        for n in t.traverse('postorder'):
            if n.is_leaf():
                node_taxid = int(getattr(n, taxid_attr))
                n.add_features(taxid = node_taxid)
                if node_taxid:
                    if node_taxid in merged_conversion:
                        node_taxid = merged_conversion[node_taxid]

                    n.add_features(sci_name = tax2name.get(node_taxid, "Unknown"),
                                   lineage = tax2track[node_taxid], 
                                   rank = tax2rank.get(node_taxid, 'Unknown'),
                                   named_lineage = self.translate_to_names(tax2track[node_taxid]))
                else:
                    n.add_features(sci_name = "Unknown",
                                   lineage = [], 
                                   rank = 'Unknown',
                                   named_lineage = [])
            else:
                ancestor, lineage = self._first_common_ocurrence([lf.lineage for lf in n2leaves[n]])

                #node_name, named_lineage = first_common_ocurrence([lf.named_lineage for lf in n2leaves[n]])
                n.add_features(sci_name = tax2name.get(ancestor, str(ancestor)),
                               taxid = ancestor,
                               lineage = lineage, 
                               rank = tax2rank.get(ancestor, 'Unknown'),
                               named_lineage = [tax2name.get(tax, str(tax)) for tax in lineage])

        return tax2name, tax2track, tax2rank

    def _first_common_ocurrence(self, vectors):
        visited = defaultdict(int)
        for index, name in [(ei, e) for v in vectors for ei,e in enumerate(v)]:
            visited[(name, index)] += 1

        def _sort(a, b):
            if a[1] > b[1]:
                return 1
            elif a[1] < b[1]:
                return -1
            else:
                if a[0][1] > b[0][1]:
                    return 1
                elif a[0][1] < b[0][1]:
                    return -1
            return 0

        matches = sorted(visited.items(), _sort)
        if matches:
            best_match = matches[-1]
        else:
            return "", set()

        if best_match[1] != len(vectors):
            return "", set()
        else:
            return best_match[0][0], [m[0][0] for m in matches if m[1] == len(vectors)]


    def get_broken_branches(self, t, taxa_lineages, n2content=None):
        """Returns a list of NCBI lineage names that are not monophyletic, the list of affected
        branches and their size.


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
        for tax, leaves in tax2node.iteritems():
            if len(leaves) > 1:
                common = t.get_common_ancestor(leaves)
            else:
                common = list(leaves)[0]
            if (leaves ^ set(n2content[common])) - unknown:
                broken_branches[common].add(tax)
                broken_clades.add(tax)

        broken_clade_sizes = [len(tax2node[tax]) for tax in broken_clades]
        return broken_branches, broken_clades, broken_clade_sizes


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


