#!/usr/bin/python


import time

import numpy as np
import lap
import random
import time
import sys
import itertools

from ..coretype.tree import Tree
from ..utils import print_table, color

import textwrap
import argparse
import logging
log = logging.Logger("main")


DESC = ""

EUCL_DIST = lambda a,b: 1 - (float(len(a[1] & b[1])) / max(len(a[1]), len(b[1]))) # 24

def EUCL_DIST_B(a,b):    
    dist_a = 0
    dist_b = 0
    
    for diff_a in (a[1] ^ b[1] & a[1]):
        dist_a +=[i for i in a[0].iter_search_nodes(name=diff_a)][0].dist
    
    for diff_b in (b[1] ^ a[1] & b[1]):
        dist_b +=[i for i in b[0].iter_search_nodes(name=diff_b)][0].dist     
    
    return 1 - (float(len(a[1] & b[1])) / max(len(a[1]), len(b[1]))) + abs(dist_a - dist_b)

def RF_DIST(a, b):
    if len(a[1] & b[1]) < 2:
        return 1
    (a, b) = (b, a) if len(b[1]) > len(a[1]) else (a,b)
    rf, rfmax, names, side1, side2, d1, d2 = a[0].robinson_foulds(b[0])
    return (rf/rfmax if rfmax else 0)

def sepstring(items, sep=", "):
    return sep.join(sorted(map(str, items)))

def treediff(t1, t2, attr1, attr2, dist_fn=EUCL_DIST, reduce_matrix=False):
    log.info("Computing distance matrix...")
    t1_cached_content = t1.get_cached_content(store_attr=attr1)
    t2_cached_content = t2.get_cached_content(store_attr=attr2)

    parts1 = [(k, v) for k, v in t1_cached_content.items() if k.children]
    parts2 = [(k, v) for k, v in t2_cached_content.items() if k.children]

    # Should I include tips?
    # parts1.extend([(leaf, set([getattr(leaf, attr1)])) for leaf in t1.iter_leaves()])
    # parts2.extend([(leaf, set([getattr(leaf, attr2)])) for leaf in t2.iter_leaves()])

    def sortSecond(val):
        return len(val[1])

    parts1 = sorted(parts1, key = sortSecond)#, reverse=True)
    parts2 = sorted(parts2, key = sortSecond)#, reverse=True)
    
    log.info( "Calculating distance matrix...")

    matrix = [[dist_fn((n1,a), (n2,b)) for n2,b in parts2] for n1,a in parts1]


    # Reduce matrix to avoid useless comparisons
    if reduce_matrix:
        log.info( "Reducing distance matrix...")
        cols_to_include = set(range(len(matrix[0])))
        rows_to_include = []
        for i, row in enumerate(matrix):
            try:
                cols_to_include.remove(row.index(0))
            except ValueError:
                rows_to_include.append(i)
        
        cols_to_include = sorted(cols_to_include)
        new_matrix = []
        parts1 = [parts1[row] for row in rows_to_include]
        parts2 = [parts2[col] for col in cols_to_include]
        
        if len(new_matrix) < 1:
            return new_matrix
        
        for row in rows_to_include:
            new_matrix.append([matrix[row][col] for col in cols_to_include])
            
        log.info("Distance matrix reduced from %dx%d to %dx%d" %\
                (len(matrix), len(matrix[0]), len(new_matrix), len(new_matrix[0])))
            
        matrix = new_matrix
    
    log.info("Comparing trees...")
    
    matrix = np.asarray(matrix, dtype=np.float32)
    _ , row, col = lap.lapjv(matrix)
    indexes= zip(row,col)

    difftable = []
    for r, c in indexes:
        if matrix[r][c] != 0:
            dist, side1, side2, diff, n1, n2 = (matrix[r][c], parts1[r][1], parts2[c][1],
                                                parts1[r][1].symmetric_difference(parts2[c][1]),
                                                parts1[r][0], parts2[c][0])
            difftable.append([dist, side1, side2, diff, n1, n2])
            
            
    return difftable

def show_difftable_summary(difftable, rf=-1, rf_max=-1):
    total_dist = 0
    for dist, side1, side2, diff, n1, n2 in difftable:
        total_dist += dist
    log.info("\n"+"\t".join(["Distance", "mismatches", "RF", "maxRF"]))
    print("%0.6f\t% 10d\t%d\t%d" %(total_dist, len(difftable), rf, rf_max))

def show_difftable(difftable):
    showtable = []
    for dist, side1, side2, diff, n1, n2 in difftable:
        showtable.append([dist, len(side1), len(side2), len(diff), sepstring(diff)])
    print_table(showtable, header=["distance", "size1", "size2", "ndiffs", "diff"],
                max_col_width=80, wrap_style="wrap", row_line=True)

def show_difftable_tab(difftable):
    showtable = []
    for dist, side1, side2, diff, n1, n2 in difftable:
        showtable.append([dist, len(side1), len(side2), len(diff),
                          sepstring(side1, "|"), sepstring(side2, "|"),
                          sepstring(diff, "|")])
    print('#' + '\t'.join(["distance", "size1", "size2", "ndiffs", "diff", "refTree", "targetTree"]))
    print('\n'.join(['\t'.join(map(str, items)) for items in showtable]))
    
def show_difftable_topo(difftable, attr1, attr2, usecolor=False):
    if not difftable:
        return
    showtable = []
    maxcolwidth = 80
    total_dist = 0
    for dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
        total_dist += dist
        n1 = Tree(n1.write(features=[attr1]))
        n2 = Tree(n2.write(features=[attr2]))
        n1.ladderize()
        n2.ladderize()
        for leaf in n1.iter_leaves():
            leaf.name = getattr(leaf, attr1)
            if leaf.name in diff:
                leaf.name += " ***"
                if usecolor:
                    leaf.name = color(leaf.name, "red")
        for leaf in n2.iter_leaves():
            leaf.name = getattr(leaf, attr2)
            if leaf.name in diff:
                leaf.name += " ***"
                if usecolor:
                    leaf.name = color(leaf.name, "red")

        topo1 = n1.get_ascii(show_internal=False, compact=False)
        topo2 = n2.get_ascii(show_internal=False, compact=False)

        # This truncates too large topology strings pretending to be
        # scrolled to the right margin
        topo1_lines = topo1.split("\n")
        topowidth1 = max([len(l) for l in topo1_lines])
        if topowidth1 > maxcolwidth:
            start = topowidth1 - maxcolwidth
            topo1 = '\n'.join([line[start+1:] for line in topo1_lines])
        
        topo2_lines = topo2.split("\n")
        topowidth2 = max([len(l) for l in topo2_lines])
        if topowidth2 > maxcolwidth:
            start = topowidth2 - maxcolwidth
            topo2 = '\n'.join([line[start+1:] for line in topo2_lines])
                
        showtable.append([dist, "%d/%d (%d)" %(len(side1), len(side2),len(diff)), topo1, topo2])
    print_table(showtable, header=["Dist", "#diffs", "Tree1", "Tree2"],
                max_col_width=maxcolwidth, wrap_style="wrap", row_line=True)
    
    log.info("Total euclidean distance:\t%0.4f\tMismatching nodes:\t%d" %(total_dist, len(difftable)))
       
def populate_args(diff_args_p):

    diff_args = diff_args_p.add_argument_group("DIFF GENERAL OPTIONS")
        
    diff_args.add_argument("--ref_attr", dest="ref_attr",
                        default = "name", 
                        help=("Defines the attribute in REFERENCE tree that will be used"
                              " to perform the comparison"))
    
    diff_args.add_argument("--target_attr", dest="target_attr",
                        default = "name",
                        help=("Defines the attribute in TARGET tree that will be used"
                              " to perform the comparison"))
    
    diff_args.add_argument("--fullsearch", dest="fullsearch",
                        action="store_true",
                        help=("Enable this option if duplicated attributes (i.e. name)"
                              "exist in reference or target trees."))
    
    diff_args.add_argument("--quiet", dest="quiet",
                        action="store_true",
                        help="Do not show process information")
    
    diff_args.add_argument("--report", dest="report",
                        choices=["topology", "diffs", "diffs_tab", "summary"],
                        default = "topology",
                        help="Different format for the comparison results")

    diff_args.add_argument("--ncbi", dest="ncbi",
                        action="store_true",
                        help="If enabled, it will use the ETE ncbi_taxonomy module to for ncbi taxid translation")

    diff_args.add_argument("--color", dest="color",
                        action="store_true",
                        help="If enabled, it will use colors in some of the report")
    
    diff_args.add_argument("--dist", dest="distance",
                           type=str, choices= ['e', 'rf', 'eb'], default='e',
                           help=('Distance measure: e = Euclidean distance, rf = Robinson-Foulds symetric distance'
                                 ' eb = Euclidean distance + branch length difference between disjoint leaves'))
    
def run(args):
        
    if not args.ref_trees or not args.src_trees:
        logging.warning("Target tree (-t argument) or source tree (-s argument) were not specified")
        
    else:
        if args.quiet:
            logging.basicConfig(format='%(message)s', level=logging.WARNING)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)
        log = logging

        if args.ncbi:
            from common import ncbi
            ncbi.connect_database()



        for rtree in args.ref_trees:
            t1 = Tree(rtree)

            for ttree in args.src_trees:
                t2 = Tree(ttree)

                if args.ncbi:

                    taxids = set([getattr(leaf, args.ref_attr) for leaf in t1.iter_leaves()])
                    taxids.update([getattr(leaf, args.target_attr) for leaf in t2.iter_leaves()])
                    taxid2name = ncbi.get_taxid_translator(taxids)
                    for leaf in  t1.get_leaves()+t2.get_leaves():
                        try:
                            leaf.name=taxid2name.get(int(leaf.name), leaf.name)
                        except ValueError:
                            pass

                if args.distance == 'e':
                    dist_fn = EUCL_DIST
                elif args.distance == 'rf':
                    dist_fn = RF_DIST
                elif args.distance == 'eb':
                    dist_fn = EUCL_DIST_B
                
                difftable = treediff(t1, t2, args.ref_attr, args.target_attr, dist_fn, args.fullsearch)

                if len(difftable) != 0:
                    if args.report == "topology":
                        show_difftable_topo(difftable, args.ref_attr, args.target_attr, usecolor=args.color)
                    elif args.report == "diffs":
                        show_difftable(difftable)
                    elif args.report == "diffs_tab":
                        show_difftable_tab(difftable)
                    elif args.report == 'table':
                        rf, rf_max, _, _, _, _, _ = t1.robinson_foulds(t2, attr_t1=args.ref_attr, attr_t2=args.target_attr)[:2]
                        show_difftable_summary(difftable, rf, rf_max)
                else:
                    log.info("Difference between (Reference) %s and (Target) %s returned no results" % (rtree, ttree))
