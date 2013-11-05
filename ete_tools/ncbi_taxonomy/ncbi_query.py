#!/usr/bin/env python 
import sys
import os
from collections import defaultdict, deque
from itertools import permutations
from argparse import ArgumentParser
from string import strip
import logging as log

import operator
import sqlite3
import math
from ete2 import PhyloTree

paired_colors = ['#a6cee3',
                 '#1f78b4',
                 '#b2df8a',
                 '#33a02c',
                 '#fb9a99',
                 '#e31a1c',
                 '#fdbf6f',
                 '#ff7f00',
                 '#cab2d6',
                 '#6a3d9a',
                 '#ffff99',
                 '#b15928']

COLOR_RANKS = {
    "superclass": "#a6cee3",
    "class": "#a6cee3",
    "subclass": "#a6cee3",
    "infraclass": "#a6cee3",
    
    "superfamily": "#1f78b4",
    "family": "#1f78b4",
    "subfamily": "#1f78b4",

    "superkingdom": "#b2df8a",
    "kingdom": "#b2df8a",
    "subkingdom": "#b2df8a",
    
    "superorder": "#33a02c",
    "order": "#33a02c",
    "suborder": "#33a02c",
    "infraorder": "#33a02c",
    "parvorder": "#33a02c",

    "superphylum": "#fdbf6f",
    "phylum": "#fdbf6f",
    "subphylum": "#fdbf6f",

#    "species group": "",
#    "species subgroup": "",
#    "species": "",
#    "subspecies": "",

#    "genus": "",
#    "subgenus": "",

#    "no rank": "",
#    "forma": "",

#    "tribe": "",
#    "subtribe": "",
#    "varietas"
    }


# Loads database
module_path = os.path.split(os.path.realpath(__file__))[0]
c = sqlite3.connect(os.path.join(module_path, 'taxa.sqlite'))

__DESCRIPTION__ = """ 
Query ncbi taxonomy using a local DB
"""

log.basicConfig(level=log.INFO, \
                    format="%(levelname)s - %(message)s" )




def get_fuzzy_name_translation(name, sim=0.9):
    log.info("Trying fuzzy search for %s", name)
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
        log.info("FOUND!                  %s taxid:%s score:%s (%s)", spname, taxid, score, norm_score)

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
    print "merged", len(all_taxids), conversion
    print len(conv_all_taxids)
    return conv_all_taxids, conversion
    
def annotate_tree(t, tax2name=None, tax2track=None):
    leaves = t.get_leaves()
    taxids = set(map(int, [n.taxid for n in leaves]))
    merged_conversion = {}
    
    taxids, merged_conversion = translate_merged(taxids)
       
    if not tax2name or taxids - set(map(int, tax2name.keys())):
        #print "Querying for tax names"
        tax2name = get_taxid_translator([tid for tid in taxids])
    if not tax2track or taxids - set(map(int, tax2track.keys())):
        #print "Querying for tax lineages"
        tax2track = dict([(tid, get_sp_lineage(tid)) for tid in taxids])

    for n in leaves:
        node_taxid = int(n.taxid)
        if node_taxid:
            if node_taxid in merged_conversion:
                node_taxid = merged_conversion[node_taxid]
            
            n.spname = tax2name.get(node_taxid, "Unknown")
            n.lineage = tax2track[node_taxid]
            n.named_lineage = translate_to_names(n.lineage)
        else:
            n.spname = "Unknown"
            n.named_lineage = []
            n.lineage = []
        
    return tax2name, tax2track

def test():
    # TESTS
    get_sp_lineage("9606")
    t = get_topology([9913,31033,7955,9606,7719,9615,44689,10116,7227,9031,13616,7165,8364,99883,10090,9598])
    annotate_tree(t)
    print t.get_ascii(show_internal=True, compact=False)
    t.show()


if __name__ == "__main__":
    parser = ArgumentParser(description=__DESCRIPTION__)
    # name or flags - Either a name or a list of option strings, e.g. foo or -f, --foo.
    # action - The basic type of action to be taken when this argument is encountered at the command line. (store, store_const, store_true, store_false, append, append_const, version)
    # nargs - The number of command-line arguments that should be consumed. (N, ? (one or default), * (all 1 or more), + (more than 1) )
    # const - A constant value required by some action and nargs selections. 
    # default - The value produced if the argument is absent from the command line.
    # type - The type to which the command-line argument should be converted.
    # choices - A container of the allowable values for the argument.
    # required - Whether or not the command-line option may be omitted (optionals only).
    # help - A brief description of what the argument does.
    # metavar - A name for the argument in usage messages.
    # dest - The name of the attribute to be added to the object returned by parse_args().

    parser.add_argument("-t", "--taxid", dest="taxid", nargs="+",  
                        type=int, 
                        help="""taxids (space separated)""")

    parser.add_argument("-tf", "--taxid_file", dest="taxid_file",   
                        type=str, 
                        help="""file containing a list of taxids (one per line)""")

    parser.add_argument("-r", "--reftree", dest="reftree",   
                        type=str, 
                        help="""tree file containing taxids as node names.""")
    
    parser.add_argument("-n", "--name", dest="names", nargs="+",  
                        type=str, 
                        help="""species or taxa names (comma separated)""")

    parser.add_argument("-nf", "--names_file", dest="names_file",   
                        type=str, 
                        help="""file containing a list of taxids (one per line)""")

    parser.add_argument("-x", "--taxonomy", dest="taxonomy",   
                        action="store_true",
                        help=("returns a pruned version of the NCBI taxonomy"
                              " tree containing target species"))

    parser.add_argument("--show_tree", dest="show_tree",   
                        action="store_true",
                        help="""shows the NCBI taxonomy tree of the provided species""")
    
    parser.add_argument("--collapse_subspecies", dest="collapse_subspecies",   
                        action="store_true",
                        help=("When used, all nodes under the the species rank"
                              " are collapsed, so all species and subspecies"
                              " are seen as sister nodes"))

    parser.add_argument("--rank_limit", dest="rank_limit",   
                        type=str,
                        help=("When used, all nodes under the provided rank"
                              " are discarded"))
    
    parser.add_argument("--full_lineage", dest="full_lineage",   
                        action="store_true",
                        help=("When used, topology is not pruned to avoid "
                              " one-child-nodes, so the complete lineage"
                              " track leading from root to tips is kept."))
        
    parser.add_argument("-i", "--info", dest="info",   
                        action="store_true",
                        help="""shows NCBI information about the species""")

    parser.add_argument("--fuzzy", dest="fuzzy", type=float,
                        help=("Tries a fuzzy (and SLOW) search for those"
                              " species names that could not be translated"
                              " into taxids. A float number must be provided"
                              " indicating the minimum string similarity."))
   
    
    args = parser.parse_args()
    
    if args.fuzzy:
        import pysqlite2.dbapi2 as sqlite3
        c = sqlite3.connect(os.path.join(module_path, 'taxa.sqlite'))
        
    all_names = set([])
    all_taxids = []

    if args.names_file:
        all_names.update(map(strip, open(args.names_file, "rU").read().split("\n")))
    if args.names:
        all_names.update(map(strip, " ".join(args.names).split(",")))
    all_names.discard("")
    #all_names = set([n.lower() for n in all_names])
    not_found = set()
    name2realname = {}
    name2score = {}
    if all_names:
        log.info("Dumping name translations:")
        name2id = get_name_translator(all_names)
        not_found = all_names - set(name2id.keys())

        if args.fuzzy and not_found:
            log.info("%s unknown names", len(not_found))
            for name in not_found:
                # enable extension loading
                c.enable_load_extension(True)
                c.execute("select load_extension('%s')" % os.path.join(module_path,
                                            "SQLite-Levenshtein/levenshtein.sqlext"))
                tax, realname, sim = get_fuzzy_name_translation(name, args.fuzzy)
                if tax:
                    name2id[name] = tax
                    name2realname[name] = realname
                    name2score[name] = "Fuzzy:%0.2f" %sim
                    
        for name in all_names:
            taxid = name2id.get(name, "???")
            realname = name2realname.get(name, name)
            score = name2score.get(name, "Exact:1.0")
            print "\t".join(map(str, [score, name, realname.capitalize(), taxid]))
            
    if args.taxid_file:
        all_taxids.extend(map(strip, open(args.taxid_file, "rU").read().split("\n")))
    if args.taxid:
        all_taxids.extend(args.taxid)
        
    reftree = None
    if args.reftree:
        reftree = PhyloTree(args.reftree)
        all_taxids.extend(list(set([n.name for n in reftree.iter_leaves()])))

    if all_taxids:
        all_taxids, merge_conversion = translate_merged(all_taxids)
        print merge_conversion
        
    if all_taxids and args.info:
        all_taxids = set(all_taxids)
        all_taxids.discard("")
        log.info("Dumping %d taxid translations:" %len(all_taxids))
       
        all_taxids.discard("")
        translator = get_taxid_translator(all_taxids)
        for taxid, name in translator.iteritems():
            lineage = get_sp_lineage(taxid)
            named_lineage = ','.join(translate_to_names(lineage))
            lineage = ','.join(map(str, lineage))
            print "\t".join(map(str, [taxid, name, named_lineage, lineage ]))
        for notfound in all_taxids - set(str(k) for k in translator.iterkeys()):
            print >>sys.stderr, notfound, "NOT FOUND"
            
    if all_taxids and args.taxonomy:
        all_taxids = set(all_taxids)
        all_taxids.discard("")
        log.info("Dumping NCBI taxonomy of %d taxa:" %len(all_taxids))

        t = get_topology(all_taxids, args.full_lineage, args.rank_limit)
        id2name = get_taxid_translator([n.name for n in t.traverse()])
        for n in t.traverse():
            n.add_features(taxid=n.name)
            n.add_features(sci_name=str(id2name.get(int(n.name), "?")))
            if n.rank in COLOR_RANKS:
                n.add_features(bgcolor=COLOR_RANKS[n.rank])
            n.name = "%s{%s}" %(id2name.get(int(n.name), n.name), n.name)

        if args.collapse_subspecies:
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
                
        if args.show_tree:
            t.show()
            
        print "\n\n  ===== Newick files saved as 'your_taxa_query.*' ===== "
        t.write(format=9, outfile="your_ncbi_query.nw")
        t.write(format=8, outfile="your_ncbi_query.named.nw")
        t.write(format=9, features=["taxid", "name", "rank", "bgcolor", "sci_name", "collapse_subspecies"],
                outfile="your_ncbi_query.extended.nw")
        for i in t.iter_leaves():
            i.name = i.taxid
        t.write(format=9, outfile="your_ncbi_query.taxids.nw")

    if all_taxids and reftree:
        translator = get_taxid_translator(all_taxids)
        for n in reftree.iter_leaves():
            n.add_features(taxid=n.name)
            n.add_features(sci_name = translator.get(int(n.name), n.name))
            lineage = get_sp_lineage(n.taxid)
            named_lineage = '|'.join(translate_to_names(lineage))
            n.add_features(ncbi_track=named_lineage)
            
        print reftree.write(features=["taxid", "sci_name", "ncbi_track"])
  
