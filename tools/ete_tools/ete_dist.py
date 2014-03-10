#!/usr/bin/env python
import os
import sys
import numpy
from time import ctime
from common import __CITATION__, argparse, Tree, PhyloTree, print_table
    
__DESCRIPTION__ = '''
#  - treedist -
# ===================================================================================
#  
# 'treedist' calculates robinson foulds distances between a reference tree and a
# one or more target trees. It also provides the percentage of found branches and o
# other stats summarizing topological differences.
#
%s
#  
# ===================================================================================
'''% __CITATION__


def istr(v):
    if isinstance(v, float):
        return '%0.1f' %v
    else:
        return str(v)

def tree_iterator(fname):
    for line in open(fname):
        if line.strip('\n') and not line.startswith('#'):
            treeid, nw = line.split('\t')
            yield treeid.strip(), nw
        
def main(argv):
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)


    parser.add_argument("target_trees", metavar='target_trees', type=str, nargs="*",
                   help='a list of target tree files')
    
    parser.add_argument("--targets_file", dest="targets_file", 
                        type=str, 
                        help="""path to a file containing target trees, one per line""")
    
    parser.add_argument("-o", dest="output", 
                        type=str,
                        help="""Path to the tab delimited report file""")

    parser.add_argument("-r", dest="reftree", 
                        type=str, required=True,
                        help="""Reference tree""")

    parser.add_argument("--outgroup", dest="outgroup", 
                        nargs = "+",
                        help="""outgroup used to root reference and target trees before distance computation""")
  
    parser.add_argument("--expand_polytomies", dest="polytomies", 
                        action = "store_true",
                        help="""expand politomies if necessary""")
  
    parser.add_argument("--unrooted", dest="unrooted", 
                        action = "store_true",
                        help="""compare trees as unrooted""")

    parser.add_argument("--min_support", dest="min_support", 
                        type=float, default=0.0,
                        help=("min support value for branches to be counted in the distance computation (RF, treeko and refTree/targeGene compatibility)"))
    
    parser.add_argument("--extract_species", dest="extract_species", 
                        action = "store_true",
                        help="""When used, reference tree is assumed to contain species names, while target trees as expected to be gene trees. Species name will be extracted from gene tree nodes and treeko will be used if duplication events are found.""")

    parser.add_argument("--spname_delimiter", dest="spname_delimiter", 
                        type=str, default="_",
                        help=("species code delimiter in node names"))
    
    parser.add_argument("--spname_field", dest="spname_field", 
                        type=int, default=-1,
                        help=("position of the species code extracted from node names. -1 = last field"))
    

    parser.add_argument("--collateral", dest="collateral", 
                        action='store_true', 
                        help=(""))

    
    args = parser.parse_args(argv)
    print __DESCRIPTION__
    reftree = args.reftree
    if args.targets_file and args.target_trees:
        print >>sys.stderr, 'The use of targets_file and targets at the same time is not supported.'
        sys.exit(1)
        
    if args.targets_file:
        target_trees = tree_iterator(args.targets_file)
    else:
        target_trees = args.target_trees
        
    t = Tree(reftree)
    if args.outgroup:
        if len(args.outgroup) > 1:
            out = t.get_common_ancestor(args.outgroup)
        else:
            out = t.search_nodes(name=args.outgroup[0])[0]
        t.set_outgroup(out)

    ref_names = set(t.get_leaf_names())
    reftree_len = len(t)
    reftree_edges = (reftree_len*2)-2
    
    HEADER = ("target tree", 'dups', 'subtrees', 'used trees', 'treeko', "RF", "maxRF", 'normRF', "%reftree", "%genetree", "avgSize", "minSize", "common tips", "refSize", "targetSize")
    if args.output:
        OUT = open(args.output, "w")
        print >>OUT, '# ' + ctime()
        print >>OUT, '# ' + ' '.join(sys.argv) 
        print >>OUT, '#'+'\t'.join(HEADER)
    else:
        print '# ' + ctime()
        print '# ' + ' '.join(sys.argv) 
        COL_WIDTHS = [20, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
        print_table([HEADER], fix_col_width=COL_WIDTHS, wrap_style='wrap')
                
    prev_tree = None

    for counter, tfile in enumerate(target_trees):
        if args.targets_file:
            seedid, tfile = tfile
        else:
            seedid = None
            
        if args.extract_species:
            tt = PhyloTree(tfile, sp_naming_function = lambda name: name.split(args.spname_delimiter)[args.spname_field])
        else:
            tt = Tree(tfile)

        if args.outgroup:
            if len(args.outgroup) > 1:
                out = tt.get_common_ancestor(args.outgroup)
            else:
                out = tt.search_nodes(name=args.outgroup[0])[0]
            tt.set_outgroup(out)
        
        if args.target_trees:
            fname = os.path.basename(tfile)
        else:
            fname = '%05d' %counter

        max_size, min_size, avg_size, common = -1, -1, -1, -1
        total_rf, max_rf, norm_rf = -1, -1, -1
        treeko_d = -1
        ref_branches_in_target, target_branches_in_ref = -1, -1
        target_tree_len = -1
        used_subtrees = -1             
        if args.extract_species:
            orig_target_size = len(tt)
            ntrees, ndups, sp_trees = tt.get_speciation_trees(autodetect_duplications=True, newick_only=True)

            if ntrees < 1000:
                all_rf = []
                ref_found = []
                target_found = []
                tree_sizes = []
                all_max_rf = []
                common_names = 0

                for subtree_nw in sp_trees:
                    if seedid and not args.collateral and (seedid not in subtree_nw):
                        continue
                    subtree = PhyloTree(subtree_nw, sp_naming_function = lambda name: name.split(args.spname_delimiter)[args.spname_field])

                    # only necessary if rf function is going to filter by support value. It slow downs the analysis, obviously
                    if args.min_support:
                        subtree_content = subtree.get_cached_content(store_attr='name')
                        for n in subtree.traverse():
                            if n.children:
                                n.support = tt.get_common_ancestor(subtree_content[n]).support
                                
                    rf, maxr, common, p1, p2, d1, d2 = t.robinson_foulds(subtree, expand_polytomies=args.polytomies, unrooted_trees=args.unrooted,
                                                                         attr_t2='species', min_support_t2=args.min_support)
                    if maxr > 0 and p1 and p2:
                        all_rf.append(rf)
                        tree_sizes.append(len(common))
                        all_max_rf.append(maxr)
                        common_names = max(common_names, len(common))
                        ref_found.append(float(len(p2 & p1)) / reftree_edges)
                        p2 = set([p for p in (p2-d2) if len(p[0])>1 and len(p[1])>1])
                        if p2-d2:
                            incompatible_target_branches = float(len((p2-d2) - p1))
                            target_found.append(1 - (incompatible_target_branches / (len(p2-d2))))

                        
                if all_rf:
                    # Treeko speciation distance
                    alld = [(all_rf[i]/float(all_max_rf[i])) for i in xrange(len(all_rf))]
                    a = numpy.sum([alld[i] * tree_sizes[i] for i in xrange(len(all_rf))])
                    b = float(numpy.sum(tree_sizes))
                    treeko_d  = a/b
                    total_rf = numpy.mean(all_rf)                    
                    norm_rf = numpy.mean([(all_rf[i]/float(all_max_rf[i])) for i in xrange(len(all_rf))])
                    max_rf = numpy.max(all_max_rf)
                    ref_branches_in_target = numpy.mean(ref_found)
                    target_branches_in_ref = numpy.mean(target_found) if target_found else -1
                    target_tree_len = numpy.mean(tree_sizes)
                    used_subtrees = len(all_rf)
        else:
            target_tree_len = len(tt)
            ndups, ntrees, used_subtrees = 0, 1, 1
            treeko_d = -1
            total_rf, max_rf, common, p1, p2, d1, d2 = tt.robinson_foulds(t, expand_polytomies=args.polytomies, unrooted_trees=args.unrooted)
            common_names = len(common)
            if max_rf:
                norm_rf = total_rf / float(max_rf)
            if p1 and p2: 
                sizes = [len(p) for p in p2 ^ p1]
                if sizes: 
                    avg_size = sum(sizes) / float(len(sizes))
                    max_size, min_size = max(sizes), min(sizes)
                else:
                    max_size, min_size, avg_size = 0, 0, 0
                    
                ref_branches_in_target = float(len(p2 & p1)) / reftree_edges
                if p2-d2:
                    incompatible_target_branches = float(len((p2-d2) - p1))
                    target_found.append(1 - (incompatible_target_branches / (len(p2-d2))))
            else:
                ref_branches_in_target = 0.0
                target_branches_in_ref = 0.0
                max_size, min_size, avg_size = -1, -1, -1

        if args.output:
            print >>OUT, '\t'.join(map(str, (fname, ndups, ntrees, used_subtrees, treeko_d, total_rf, max_rf, norm_rf, ref_branches_in_target, target_branches_in_ref,
                                             avg_size, min_size, common_names, reftree_len, target_tree_len)))
        else:
            print_table([map(istr, (fname[-30:], ndups, ntrees, used_subtrees, treeko_d, total_rf, max_rf, norm_rf, '%0.4f' %ref_branches_in_target, '%0.4f' %target_branches_in_ref,
                 avg_size, min_size, common_names, reftree_len, target_tree_len))], fix_col_width = COL_WIDTHS, wrap_style='cut')

    if args.output:
        OUT.close()


if __name__ == '__main__':
    main(sys.argv[1:])
