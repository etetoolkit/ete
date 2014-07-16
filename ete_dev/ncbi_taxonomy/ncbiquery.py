#!/usr/bin/env python 
import sys
import os
from collections import defaultdict, deque
from string import strip

import sqlite3
import math

c = None

# Loads database
def connect_database(dbfile=None):
    global c
    if not dbfile:
        module_path = os.path.split(os.path.realpath(__file__))[0]
        dbfile = os.path.join(module_path, 'taxa.sqlite')
        if not os.path.exists(dbfile):
            dbfile = os.path.join(os.environ.get('HOME', '/'), '.etetoolkit', 'taxa.sqlite')
        
    c = sqlite3.connect(dbfile)

def get_fuzzy_name_translation(name, sim=0.9):
    print "Trying fuzzy search for %s" % name
    maxdiffs = math.ceil(len(name) * (1-sim))
    cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM species WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
    taxid, spname, score = None, None, len(name)
    result = c.execute(cmd)
    try:
        taxid, spname, score = result.fetchone()
    except TypeError:
        cmd = 'SELECT taxid, spname, LEVENSHTEIN(spname, "%s") AS sim  FROM synonym WHERE sim<=%s ORDER BY sim LIMIT 1;' % (name, maxdiffs)
        result = c.execute(cmd)
        try:
            taxid, spname, score = result.fetchone()
        except:
            pass
        else:
            taxid = int(taxid)
    else:
        taxid = int(taxid)

    norm_score = 1-(float(score)/len(name))
    if taxid: 
        print "FOUND!                  %s taxid:%s score:%s (%s)" %(spname, taxid, score, norm_score)

    return taxid, spname, norm_score
    
def get_sp_lineage(taxid):
    if not taxid:
        return None
    result = c.execute('SELECT track FROM species WHERE taxid=%s' %taxid)
    raw_track = result.fetchone()
    if not raw_track:
        raw_track = ["1"]
        #raise ValueError("%s taxid not found" %taxid)
    track = map(int, raw_track[0].split(","))
    return list(reversed(track))

def get_taxid_translator(taxids):
    all_ids = set(taxids)
    all_ids.discard(None)
    all_ids.discard("")
    query = ','.join(['"%s"' %v for v in all_ids])
    cmd = "select taxid, spname FROM species WHERE taxid IN (%s);" %query
    result = c.execute(cmd)
    id2name = {}
    for tax, spname in result.fetchall():
        id2name[tax] = spname
    return id2name

def get_ranks(taxids):
    all_ids = set(taxids)
    all_ids.discard(None)
    all_ids.discard("")
    query = ','.join(['"%s"' %v for v in all_ids])
    cmd = "select taxid, rank FROM species WHERE taxid IN (%s);" %query
    result = c.execute(cmd)
    id2rank = {}
    for tax, spname in result.fetchall():
        id2rank[tax] = spname
    return id2rank

def get_name_translator(names):
    name2id = {}
    name2realname = {}
    name2origname = {}
    for n in names:
        name2origname[n.lower()] = n
    query = ','.join(['"%s"' %n for n in name2origname.iterkeys()])
    cmd = 'select spname, taxid from species where spname IN (%s)' %query
    result = c.execute('select spname, taxid from species where spname IN (%s)' %query)
    for sp, taxid in result.fetchall():
        oname = name2origname[sp.lower()]
        name2id[oname] = taxid
        name2realname[oname] = sp
    missing =  names - set(name2id.keys())
    if missing:
        query = ','.join(['"%s"' %n for n in missing])
        result = c.execute('select spname, taxid from synonym where spname IN (%s)' %query)
        for sp, taxid in result.fetchall():
            oname = name2origname[sp.lower()]
            name2id[oname] = taxid
            name2realname[oname] = sp
    return name2id
    
  
def translate_to_names(taxids):
    def get_name(taxid):
        result = c.execute('select spname from species where taxid=%s' %taxid)
        try:
            return result.fetchone()[0]
        except TypeError:
            raise ValueError("%s taxid not found" %taxid)
    id2name = {}
    names = []
    for sp in taxids: 
        names.append(id2name.setdefault(sp, get_name(sp)))
    return names

    
def get_topology(taxids, intermediate_nodes=False, rank_limit=None):
    from ete2 import PhyloTree
    sp2track = {}
    elem2node = {}
    for sp in taxids:
        track = deque()
        lineage = get_sp_lineage(sp)
        id2rank = get_ranks(lineage)

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
       
    if len(root.children) == 1:
        return root.children[0].detach()
    else:
        return root

def translate_merged(all_taxids):
    conv_all_taxids = set((map(int, all_taxids)))
    cmd = 'select taxid_old, taxid_new FROM merged WHERE taxid_old IN (%s)' %','.join(map(str, all_taxids))
    result = c.execute(cmd)
    conversion = {}
    for old, new in result.fetchall():
        conv_all_taxids.discard(int(old))
        conv_all_taxids.add(int(new))
        conversion[int(old)] = int(new)
    return conv_all_taxids, conversion
    
def annotate_tree(t, tax2name=None, tax2track=None, attr_name="name"):
    leaves = t.get_leaves()
    taxids = set(map(int, [getattr(n, attr_name) for n in leaves]))
    merged_conversion = {}
    
    taxids, merged_conversion = translate_merged(taxids)
       
    if not tax2name or taxids - set(map(int, tax2name.keys())):
        #print "Querying for tax names"
        tax2name = get_taxid_translator([tid for tid in taxids])
    if not tax2track or taxids - set(map(int, tax2track.keys())):
        #print "Querying for tax lineages"
        tax2track = dict([(tid, get_sp_lineage(tid)) for tid in taxids])

    n2leaves = t.get_cached_content()
        
    for n in t.traverse('postorder'):
        if n.is_leaf():
            node_taxid = int(getattr(n, attr_name))
            n.add_features(taxid = node_taxid)
            if node_taxid:
                if node_taxid in merged_conversion:
                    node_taxid = merged_conversion[node_taxid]

                n.add_features(spname = tax2name.get(node_taxid, "Unknown"),
                               lineage = tax2track[node_taxid], 
                               named_lineage = translate_to_names(tax2track[node_taxid]))
            else:
                n.add_features(spname = "Unknown",
                               lineage = [], 
                               named_lineage = [])
        else:
            n.name, n.named_lineage = first_common_ocurrence([lf.named_lineage for lf in n2leaves[n]])
            
    return tax2name, tax2track

def first_common_ocurrence(vectors):
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

    
def get_broken_branches(t, n2content):
    tax2node = defaultdict(set)
    tax2name = {}
    unknown = set()
    for leaf in t.iter_leaves():
        if leaf.spname.lower() != "unknown":
            for index, tax in enumerate(leaf.lineage):
                tax2node[tax].add(leaf)
                tax2name[tax] = leaf.named_lineage[index]
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
    return broken_branches, broken_clades, broken_clade_sizes, tax2name
   

def annotate_tree_with_taxa(t, name2taxa_file, tax2name=None, tax2track=None, attr_name="name"):
    if name2taxa_file: 
        names2taxid = dict([map(strip, line.split("\t"))
                            for line in open(name2taxa_file)])
    else:
        names2taxid = dict([(n.name, getattr(n, attr_name)) for n in t.iter_leaves()])
        
    not_found = 0
    for n in t.iter_leaves():
        n.add_features(taxid=names2taxid.get(n.name, 0))
        n.add_features(species=n.taxid)
        if n.taxid == 0:
            not_found += 1
    if not_found:
        print >>sys.stderr, "WARNING: %s nodes where not found within NCBI taxonomy!!" %not_found
      
    return annotate_tree(t, tax2name, tax2track, attr_name="taxid")
    

    
