DESC = """
 - ete compare -
 
'compare' is a tool to calculate the distance from one or more trees to a
reference tree. Robinson foulds and strict congruence measures are calculated,
among other stats.

Comparisons between trees with different sizes and containing duplicated
attributes are also supported.  names.

%s
  
"""

def populate_args(compare_args_p):
    compare_args = compare_args_p.add_argument_group("COMPARE GENERAL OPTIONS")
    
    compare_args.add_argument("--min_support_ref",
                              type=float, default=0.0,
                              help=("min support for branches to be considered from the ref tree"))
    compare_args.add_argument("--min_support_src",
                              type=float, default=0.0,
                              help=("min support for branches to be considered from the source tree"))
      
    compare_args.add_argument("--unrooted", dest="unrooted", 
                              action = "store_true",
                              help="""compare trees as unrooted""")

    compare_args.add_argument("--diff", dest="differences", 
                              action = "store_true",
                              help="return differences between pairs of trees ")

def run(args):
    from ete_dev import Tree
    from ete_dev.utils import print_table
    
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

    
    col_sizes = [25, 25] + [8] * 8
            
    print_table([['source', 'ref', 'eff.size', 'nRF',
                 'RF', 'maxRF', "%src_branches",
                  "%ref_branches", "subtrees", "treekoD" ],
                 ["=========================="] * 10],
                fix_col_width=col_sizes, wrap_style="cut")
    

    for stree_name in args.src_tree_iterator:
        stree = Tree(stree_name)
        for rtree_name in args.ref_trees:
            rtree = Tree(rtree_name)
            r = stree.compare(rtree, 
                              ref_tree_attr=args.ref_tree_attr,
                              source_tree_attr=args.src_tree_attr,
                              min_support_ref=args.min_support_ref,
                              min_support_source = args.min_support_src,
                              unrooted=args.unrooted,
                              has_duplications=False)


            print_table([map(as_str, [shorten_str(stree_name,25),
                                      shorten_str(rtree_name,25),
                                      r['effective_tree_size'],
                                      r['norm_rf'], 
                                      r['rf'], r['max_rf'],
                                      r["source_edges_in_ref"],
                                      r["ref_edges_in_source"],
                                      r['source_subtrees'],
                                      r['treeko_dist']])],
                        fix_col_width = col_sizes, wrap_style='cut')

            if args.differences:
                # EXPERIMENTAL
                from pprint import pprint
                import itertools

                mismatches_src = r['source_edges'] - r['ref_edges']
                mismatches_ref = r['ref_edges'] - r['source_edges']
                for part, pairs in iter_differences(mismatches_src,
                                                    mismatches_ref,
                                                    unrooted=args.unrooted):
                    print part
                    for d, r in sorted(pairs):
                        print "  ", d, r
    print
                
def euc_dist(v1, v2):
    if type(v1) != set: v1 = set(v1)
    if type(v2) != set: v2 = set(v2)
   
    return len(v1 ^ v2) / float(len(v1 | v2))

def euc_dist_unrooted(v1, v2):
    a = (euc_dist(v1[0], v2[0]) + euc_dist(v1[1], v2[1])) / 2.0
    b = (euc_dist(v1[1], v2[0]) + euc_dist(v1[0], v2[1])) / 2.0
    return min(a, b)
