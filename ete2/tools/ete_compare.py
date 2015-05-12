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
from common import as_str, shorten_str
import re

DESC = """
 - ete compare -
 
'compare' is a tool to calculate distances from one or more trees to a
reference tree. 

It provides Robinson foulds and tree compatibility measures. Comparisons between
trees with different sizes and containing duplicated attributes are also
supported.

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

    compare_args.add_argument("--show_mismatches", dest="show_mismatches", 
                              action = "store_true",
                              help="")

    compare_args.add_argument("--show_matches", dest="show_matches", 
                              action = "store_true",
                              help="")
    compare_args.add_argument("--show_edges", dest="show_edges", 
                              action = "store_true",
                              help="")

    compare_args.add_argument("--taboutput", dest="taboutput", 
                              action = "store_true",
                              help="ouput results in tab delimited format")
    
    compare_args.add_argument("--treeko", dest="treeko", 
                              action = "store_true",
                              help="activates the TreeKO duplication aware comparison method")


def run(args):
    from ete2 import Tree
    from ete2.utils import print_table
    
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

    header = ['source', 'ref', 'eff.size', 'nRF',
              'RF', 'maxRF', "%src_branches",
              "%ref_branches", "subtrees", "treekoD" ]

    if args.taboutput:
        print '# ' + '\t'.join(header)
    elif args.show_mismatches or args.show_matches or args.show_edges:
        pass
    else: 
        print_table([header,
                     ["=========================="] * 10],
                    fix_col_width=col_sizes, wrap_style="cut")
    

    if args.treeko:
        from ete2 import PhyloTree
        tree_class = PhyloTree
    else:
        tree_class = Tree
        
    for stree_name in args.src_tree_iterator:
        stree = tree_class(stree_name)

        # Parses attrs if necessary
        src_tree_attr = args.src_tree_attr
        if args.src_attr_parser:
            for leaf in stree:
                leaf.add_feature('tempattr', re.search(
                    args.src_attr_parser, getattr(leaf, args.src_tree_attr)).groups()[0])
            src_tree_attr = 'tempattr'
  
        for rtree_name in args.ref_trees:
            rtree = tree_class(rtree_name)

            # Parses attrs if necessary
            ref_tree_attr = args.ref_tree_attr
            if args.ref_attr_parser:
                for leaf in rtree:
                    leaf.add_feature('tempattr', re.search(
                        args.ref_attr_parser, getattr(leaf, args.ref_tree_attr)).groups()[0])
                ref_tree_attr = 'tempattr'

            r = stree.compare(rtree, 
                              ref_tree_attr=ref_tree_attr,
                              source_tree_attr=src_tree_attr,
                              min_support_ref=args.min_support_ref,
                              min_support_source = args.min_support_src,
                              unrooted=args.unrooted,
                              has_duplications=args.treeko)
            
            
            
            if args.show_mismatches or args.show_matches or args.show_edges:
                if args.show_mismatches:
                    src = r['source_edges'] - r['ref_edges']
                    ref = r['ref_edges'] - r['source_edges']
                elif args.show_matches:
                    src = r['source_edges'] & r['ref_edges']
                    ref = r['ref_edges'] & r['source_edges']
                elif args.show_edges:
                    src = r['source_edges']
                    ref = r['ref_edges']

                if args.unrooted:
                    for tag, part in [("src: %s"%stree_name, src), ("ref: %s"%rtree_name, ref)]:
                        print "%s\t%s" %(tag, '\t'.join(
                            map(lambda x: '%s|%s' %(','.join(x[0]), ','.join(x[1])), part)))
                else:
                    for tag, part in [("src: %s"%stree_name, src), ("ref: %s"%rtree_name, ref)]:
                        print "%s\t%s" %(tag, '\t'.join([','.join(p) for p in part]))
            else:
                data = [shorten_str(stree_name,25),
                        shorten_str(rtree_name,25),
                        r['effective_tree_size'],
                        r['norm_rf'], 
                        r['rf'], r['max_rf'],
                        r["source_edges_in_ref"],
                        r["ref_edges_in_source"],
                        r['source_subtrees'],
                        r['treeko_dist']]

                if r['effective_tree_size'] == 0:
                    for i in xrange(3, len(data)):
                        data[i] = -1
                
                if args.taboutput:                    
                    print '\t'.join(map(str, data))
                else:    
                    print_table([map(as_str, data)],
                                fix_col_width = col_sizes, wrap_style='cut')
                        

                
def euc_dist(v1, v2):
    if type(v1) != set: v1 = set(v1)
    if type(v2) != set: v2 = set(v2)
   
    return len(v1 ^ v2) / float(len(v1 | v2))

def euc_dist_unrooted(v1, v2):
    a = (euc_dist(v1[0], v2[0]) + euc_dist(v1[1], v2[1])) / 2.0
    b = (euc_dist(v1[1], v2[0]) + euc_dist(v1[0], v2[1])) / 2.0
    return min(a, b)
