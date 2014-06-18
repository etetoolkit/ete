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

from common import PhyloTree, ncbi

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
MODULE_PATH = os.path.split(os.path.realpath(__file__))[0]


__DESCRIPTION__ = """ 
Query ncbi taxonomy using a local DB
"""

log.basicConfig(level=log.INFO, \
                    format="%(levelname)s - %(message)s" )


def test():
    # TESTS
    ncbi.get_sp_lineage("9606")
    t = ncbi.get_topology([9913,31033,7955,9606,7719,9615,44689,10116,7227,9031,13616,7165,8364,99883,10090,9598])
    ncbi.annotate_tree(t)
    print t.get_ascii(show_internal=True, compact=False)
    t.show()


def main(argv):
    
    parser = ArgumentParser(description=__DESCRIPTION__)

    parser.add_argument("--db",  dest="dbfile", default=MODULE_PATH+'/taxa.sqlite',
                        type=str,
                        help="""NCBI sqlite3 db file.""")
    
    parser.add_argument("-t", "--taxid", dest="taxid", nargs="+",  
                        type=int, 
                        help="""taxids (space separated)""")

    parser.add_argument("-tf", "--taxid_file", dest="taxid_file",   
                        type=str, 
                        help="""file containing a list of taxids (one per line)""")

    parser.add_argument("-r", "--reftree", dest="reftree",   
                        type=str, 
                        help="""tree file containing taxids as node names.""")
    
    parser.add_argument("--reftree_attr", dest="reftree_attr",   
                        type=str, default="name",
                        help="""Where taxid should be read from""")
    
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
   
    
    args = parser.parse_args(argv)
    if not args.taxonomy and not args.info and not args.reftree:
        parser.print_usage()
        sys.exit(0)
    
    if args.fuzzy:
        import pysqlite2.dbapi2 as sqlite3
        c = sqlite3.connect(os.path.join(MODULE_PATH, args.dbfile))
    else:
        ncbi.connect_database(args.dbfile)
    

        
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
        name2id = ncbi.get_name_translator(all_names)
        not_found = all_names - set(name2id.keys())

        if args.fuzzy and not_found:
            log.info("%s unknown names", len(not_found))
            for name in not_found:
                # enable extension loading
                c.enable_load_extension(True)
                c.execute("select load_extension('%s')" % os.path.join(module_path,
                                            "SQLite-Levenshtein/levenshtein.sqlext"))
                tax, realname, sim = ncbi.get_fuzzy_name_translation(name, args.fuzzy)
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
        all_taxids.extend(list(set([getattr(n, args.reftree_attr) for n in reftree.iter_leaves()])))

       
    if all_taxids and args.info:
        all_taxids = set(all_taxids)
        all_taxids.discard("")
        all_taxids, merge_conversion = ncbi.translate_merged(all_taxids)
        log.info("Dumping %d taxid translations:" %len(all_taxids))
        all_taxids.discard("")
        translator = ncbi.get_taxid_translator(all_taxids)
        for taxid, name in translator.iteritems():
            lineage = ncbi.get_sp_lineage(taxid)
            named_lineage = ','.join(ncbi.translate_to_names(lineage))
            lineage = ','.join(map(str, lineage))
            print "\t".join(map(str, [merge_conversion.get(int(taxid), taxid), name, named_lineage, lineage ]))
            
        for notfound in set(map(str, all_taxids)) - set(str(k) for k in translator.iterkeys()):
            print >>sys.stderr, notfound, "NOT FOUND"
            
    if all_taxids and args.taxonomy:
        all_taxids = set(all_taxids)
        all_taxids.discard("")
        log.info("Dumping NCBI taxonomy of %d taxa:" %len(all_taxids))

        t = ncbi.get_topology(all_taxids, args.full_lineage, args.rank_limit)
        id2name = ncbi.get_taxid_translator([n.name for n in t.traverse()])
        for n in t.traverse():
            n.add_features(taxid=n.name)
            n.add_features(sci_name=str(id2name.get(int(n.name), "?")))
            if n.rank in COLOR_RANKS:
                n.add_features(bgcolor=COLOR_RANKS[n.rank])
            n.name = "%s{%s}" %(id2name.get(int(n.name), n.name), n.name)
            lineage = ncbi.get_sp_lineage(n.taxid)
            n.add_features(named_lineage = '|'.join(ncbi.translate_to_names(lineage)))
            
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
        t.write(format=9, features=["taxid", "name", "rank", "bgcolor", "sci_name", "collapse_subspecies", "named_lineage"],
                outfile="your_ncbi_query.extended.nw")
        for i in t.iter_leaves():
            i.name = i.taxid
        t.write(format=9, outfile="your_ncbi_query.taxids.nw")

    if all_taxids and reftree:
        translator = ncbi.get_taxid_translator(all_taxids)
        for n in reftree.iter_leaves():
            if not hasattr(n, "taxid"):
                n.add_features(taxid=int(getattr(n, args.reftree_attr)))
            n.add_features(sci_name = translator.get(int(n.taxid), n.name))
            lineage = ncbi.get_sp_lineage(n.taxid)
            named_lineage = '|'.join(ncbi.translate_to_names(lineage))
            n.add_features(ncbi_track=named_lineage)
            
        print reftree.write(features=["taxid", "sci_name", "ncbi_track"])
  
if __name__ == '__main__':
    main(sys.argv[1:])
