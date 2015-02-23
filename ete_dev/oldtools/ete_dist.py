#!/usr/bin/env python
import os
import sys
import numpy
from time import ctime
from ete_dev import Tree, PhyloTree
from common import __CITATION__, argparse, print_table
    
__DESCRIPTION__ = '''
#  - treedist -
# ===================================================================================
#  
# 'treedist' is a tool to calculate the distance from one or more trees to a reference
# tree. Robinson foulds and strict congruence measures are calculated, among other stats. 
#
# Notably, comparisons are also allowed between trees with different sizes, containing 
# duplications events and with different sets of overlapping leaf names. 
#
%s
#  
# ===================================================================================
'''% __CITATION__


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


def main(argv):
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)


    input_args = parser.add_argument_group("INPUT OPTIONS")
    input_args.add_argument("source_trees", metavar='source_trees', type=str, nargs="*",
                   help='a list of source tree files')
    
    input_args.add_argument("--source_file", dest="source_file", 
                        type=str, 
                        help="""path to a file containing many source trees, one per line""")

    input_args.add_argument("-r", dest="reftree", 
                        type=str, required=True,
                        help="""Reference tree""")

    input_args.add_argument("--ref_tree_attr", dest="ref_tree_attr", 
                            type=str, default="name",
                            help=("attribute in ref tree used as leaf name"))
    
    input_args.add_argument("--src_tree_attr", dest="src_tree_attr", 
                            type=str, default="name",
                            help=("attribute in source tree used as leaf name"))

    input_args.add_argument("--min_support_ref",
                            type=float, default=0.0,
                        help=("min support for branches to be considered from the ref tree"))
    input_args.add_argument("--min_support_src",
                        type=float, default=0.0,
                        help=("min support for branches to be considered from the source tree"))

    
    output_args = parser.add_argument_group("OUTPUT OPTIONS")
    
    output_args.add_argument("-o", dest="output", 
                            type=str,
                            help="""Path to the tab delimited report file""")

    
    opt_args = parser.add_argument_group("DISTANCE OPTIONS")
    

    opt_args.add_argument("--outgroup", dest="outgroup", 
                        nargs = "+",
                        help="""outgroup used to root reference and source trees before distance computation""")
  
    opt_args.add_argument("--expand_polytomies", dest="polytomies", 
                        action = "store_true",
                        help="""expand politomies if necessary""")
  
    opt_args.add_argument("--unrooted", dest="unrooted", 
                        action = "store_true",
                        help="""compare trees as unrooted""")

    opt_args.add_argument("--min_support", dest="min_support", 
                        type=float, default=0.0,
                        help=("min support value for branches to be counted in the distance computation (RF, treeko and refTree/targeGene compatibility)"))

    opt_args = parser.add_argument_group("PHYLOGENETICS OPTIONS")
    
    opt_args.add_argument("--extract_species",
                        action = "store_true",
                        help="When used, leaf names in the reference and source trees are assumed to represent species."
                          " If target trees are gene-trees whose species information is encoded as a part of the leaf sequence name,"
                          " it can be automatically extracted by providing a Perl regular expression that extract a "
                          " valid species code (see --sp_regexp). Such information will be also used to detect duplication"
                          " events. ")

    opt_args.add_argument("--sp_regexp", 
                          type=str,
                         help=("Specifies a Perl regular expression to automatically extract species names"
                          " from the name string in source trees. If not used, leaf names are assumed to represent species names."
                          " Example: use this expression '[^_]+_(.+)' to extract HUMAN from the string 'P53_HUMAN'."))
        
    opt_args.add_argument("--collateral", 
                        action='store_true', 
                        help=(""))

    
    args = parser.parse_args(argv)
    print __DESCRIPTION__
    reftree = args.reftree
    if args.source_file and args.source_trees:
        print >>sys.stderr, 'The use of targets_file and targets at the same time is not supported.'
        sys.exit(1)
        
    if args.source_file:
        source_trees = tree_iterator(args.source_file)
    else:
        source_trees = args.source_trees
        
    ref_tree = Tree(reftree)

    if args.ref_tree_attr:
        for lf in ref_tree.iter_leaves():
            lf._origname = lf.name
            if args.ref_tree_attr not in lf.features:
                print lf
            lf.name = getattr(lf, args.ref_tree_attr)
    
    if args.outgroup:
        if len(args.outgroup) > 1:
            out = ref_tree.get_common_ancestor(args.outgroup)
        else:
            out = ref_tree.search_nodes(name=args.outgroup[0])[0]
        ref_tree.set_outgroup(out)
                     

    HEADER = ("source tree", 'ref tree', 'common\ntips', 'normRF', 'RF', 'maxRF', "%reftree", "%genetree", "subtrees", "treeko\ndist")
    if args.output:
        OUT = open(args.output, "w")
        print >>OUT, '# ' + ctime()
        print >>OUT, '# ' + ' '.join(sys.argv) 
        print >>OUT, '#'+'\t'.join(HEADER)
    else:
        print '# ' + ctime()
        print '# ' + ' '.join(sys.argv) 
        COL_WIDTHS = [20, 20] + [9] * 10
        print_table([HEADER], fix_col_width=COL_WIDTHS, wrap_style='wrap')
        
                
    prev_tree = None
    ref_fname = os.path.basename(args.reftree)
    for counter, tfile in enumerate(source_trees):
        if args.source_file:
            seedid, tfile = tfile
        else:
            seedid = None
           
        if args.extract_species:

            if args.sp_regexp:
                SPMATCHER = re.compile(args.sp_regexp)
                get_sp_name = lambda x: re.search(SPMATCHER, x).groups()[0]
            else:
                get_sp_name = lambda x: x
                
            tt = PhyloTree(tfile, sp_naming_function = get_sp_name)
        else:
            tt = Tree(tfile)

        if args.src_tree_attr:
            for lf in tt.iter_leaves():
                lf._origname = lf.name
                lf.name = getattr(lf, args.src_tree_attr)
            
        if args.outgroup:
            if len(args.outgroup) > 1:
                out = tt.get_common_ancestor(args.outgroup)
            else:
                out = tt.search_nodes(name=args.outgroup[0])[0]
            tt.set_outgroup(out)
        
        if args.source_trees:
            fname = os.path.basename(tfile)
        else:
            fname = '%05d' %counter                          


            
        r = tt.compare(ref_tree, 
                       ref_tree_attr=args.ref_tree_attr,
                       source_tree_attr=args.src_tree_attr,
                       min_support_ref=args.min_support_ref,
                       min_support_source = args.min_support_src,
                       unrooted=args.unrooted,
                       has_duplications=args.extract_species)

                          

        print_table([map(istr, [fname[-30:], ref_fname[-30:], r['effective_tree_size'], r['norm_rf'],
                               r['rf'], r['max_rf'], r["source_edges_in_ref"],
                               r["ref_edges_in_source"], r['source_subtrees'], r['treeko_dist']])],
                    fix_col_width = COL_WIDTHS, wrap_style='cut')
                          

    if args.output:
        OUT.close()

if __name__ == '__main__':
    main(sys.argv[1:])
