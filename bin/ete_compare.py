#!/usr/bin/env python
import os
import sys
import numpy
from time import ctime
from ete_dev import Tree, PhyloTree
from ete_dev.utils import print_table

def compare(args):
    stree_name = args.src_trees[0]
    rtree_name = args.ref_trees[0]
    
    stree = Tree(stree_name)
    rtree = Tree(rtree_name)
    r = stree.compare(rtree, 
                      ref_tree_attr=args.ref_tree_attr,
                      source_tree_attr=args.src_tree_attr,
                      min_support_ref=args.min_support_ref,
                      min_support_source = args.min_support_src,
                      unrooted=args.unrooted,
                      has_duplications=False)
                              
    print_table([map(istr, [stree_name[-30:], rtree_name[-30:], r['effective_tree_size'], r['norm_rf'],
                            r['rf'], r['max_rf'], r["source_edges_in_ref"],
                            r["ref_edges_in_source"], r['source_subtrees'], r['treeko_dist']])],
                fix_col_width = 10, wrap_style='cut')
                          
    if args.differences:
        from pprint import pprint
        import itertools
        
        mismatches_src = r['source_edges'] - r['ref_edges']
        mismatches_ref = r['ref_edges'] - r['source_edges']
        for part, pairs in iter_differences(mismatches_src, mismatches_ref, unrooted=args.unrooted):
            print part
            for d, r in sorted(pairs):
                print "  ", d, r

def istr(v):
    if isinstance(v, float):
        return '%0.2f' %v
    else:
        return str(v)

def tree_iterator(fname):
    for line in open(fname):
        if line.strip('\n') and not line.startswith('#'):
            treeid, nw = line.split('\t')
            yield treeid.strip(), nw
            
def euc_dist(v1, v2):
    if type(v1) != set: v1 = set(v1)
    if type(v2) != set: v2 = set(v2)
    
    return len(v1 ^ v2) / float(len(v1 | v2))


def euc_dist_unrooted(v1, v2):
    a = (euc_dist(v1[0], v2[0]) + euc_dist(v1[1], v2[1])) / 2.0
    b = (euc_dist(v1[1], v2[0]) + euc_dist(v1[0], v2[1])) / 2.0
    return min(a, b)
    
def iter_differences(set1, set2, unrooted=False):
    for s1 in set1:
        pairs = []
        for r1 in set2:
            if unrooted:
                d = euc_dist_unrooted(s1, r1)
            else:
                d = euc_dist(s1, r1)
            if d < 1:
                pairs.append((d,r1))
        yield s1, pairs
    

        
