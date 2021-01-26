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
from __future__ import absolute_import
from __future__ import print_function

import sys
import re
from collections import defaultdict 
import numpy

from .common import as_str, shorten_str, src_tree_iterator, ref_tree_iterator
from ..utils import print_table

from six.moves import map

DESC = """
 - ete maptrees -

'maptrees' is a tool that maps branches and support values from multiple
(gene)trees into a single reference (species)topology.

%s

"""

def populate_args(maptrees_args_p):
    maptrees_args = maptrees_args_p.add_argument_group("COMPARE GENERAL OPTIONS")

    maptrees_args.add_argument("--treeko", dest="treeko",
                              action = "store_true",
                              help="activates the TreeKO mode: duplication aware comparisons")

    # Output options    
    maptrees_args.add_argument("--image", dest="image",
                              type=str,
                              help="activates the TreeKO duplication aware comparison method")

    maptrees_args.add_argument("--outtree", dest="outtree",
                              type=str, 
                              help="output results as an annotated reference tree ")

    maptrees_args.add_argument("--tab", dest="taboutput",
                              action = "store_true",
                              help="output results in tab delimited format")
    
    maptrees_args.add_argument("--dump_matches", dest="dump_matches",
                              type=str,
                              help="dump the branches from source trees matching each branch in the reference trees")

    maptrees_args.add_argument("--min_support_src",
                              type=float, default=0.0,
                              help=("min support for branches to be considered from the source tree"))

    maptrees_args.add_argument("--discard_incomplete", dest="discard_incomplete",
                               action="store_true",
                               help=("discard source trees missing any reference species"))

    maptrees_args.add_argument("--discard-root", dest="discard_root",
                               action="store_true",
                               help=(""))

def get_splits(tree, min_support=None, target_attr="name", discard_root=False, ignore_multifurcations=False, target_species=None):
    branches = []
    node2content = tree.get_cached_content()
    all_species = set([getattr(_n, target_attr) for _n in node2content[tree]])
    for node in tree.traverse("preorder"):
        if discard_root and node is tree:
            continue
        if not node.is_leaf():
            if len(node.children) != 2:
                if ignore_multifurcations:
                    continue
                else:
                    raise ValueError('multifurcations and single child branches not supported')

            b1 = set([getattr(_c, target_attr) for _c in node2content[node.children[0]]])
            b2 = set([getattr(_c, target_attr) for _c in node2content[node.children[1]]])
            if target_species:
                b1 = b1 & target_species
                b2 = b2 & target_species
            if b1 and b2:
                branches.append([node, b1, b2])
    return all_species, branches

def map_branches(ref_branches, source_branches, ref_species, src_species):   
    for refnode, r1, r2 in ref_branches:
        all_expected_sp = r1 | r2

        if not (r1 & src_species) or not (r2 & src_species):
            continue
        
        # Now we scan branches from the source trees and we add one
        # supporting point for every observed split that coincides with a
        # reference tree split. This is, that seqs in one side and seqs on
        # the other side of the observed split matches a ref_tree branch
        # without having extra seqs in any of the sides. However, we allow
        # for split matches when some seqs are lost in the observed split.
        matches = []
        for srcnode, s1, s2 in source_branches:                                
            all_seen_sp = s1 | s2

            # Check if any of the observed species should not be present in
            # the ref branch.
            if (all_seen_sp - all_expected_sp):
                continue

            # check if an expected species is not observed in this branch,
            # but it actually exists in other branches of the same tree. If
            # so, this is not missing species that we can ignore, but a mismatch.
            false_missing = (all_expected_sp - all_seen_sp) & src_species
            if false_missing:
                continue           
            
            # let's check if the split is correct
            if not (s1-r1) and not (s2-r2):
                matches.append(srcnode)
            elif not (s2-r1) and not (s1-r2):
                matches.append(srcnode)
            else:
                pass

        yield refnode, matches
              

def map_dup_and_losses(reftree, source_branches, ref_leaves):    
    for srcnode, s1, s2 in source_branches:
        all_sp = s1 | s2
        if len(all_sp) == 1: 
            refnode = ref_leaves[list(all_sp)[0]]
        else:
            refnode = reftree.get_common_ancestor([ref_leaves[sp] for sp in all_sp])
        isdup = 1 if s1 & s2 else 0
        # if isdup:
        #     print(isdup, srcnode, refnode)
        #     raw_input()
        yield srcnode, refnode, isdup
        
def run(args):
    if args.treeko:
        from .. import PhyloTree
        tree_class = PhyloTree
    else:
        from .. import Tree
        tree_class = Tree

    for rtree_nw in ref_tree_iterator(args):
        rtree = tree_class(rtree_nw, format=args.src_newick_format)

        # Parses attrs if necessary
        ref_tree_attr = args.ref_tree_attr
        if args.ref_attr_parser:
            for leaf in rtree:                
                leaf.add_feature('_tempattr', re.search(args.ref_attr_parser, getattr(leaf, args.ref_tree_attr)).groups()[0])
            ref_tree_attr = '_tempattr'
        else:
            ref_tree_attr = args.ref_tree_attr                        
        
        ref_leaves = {getattr(_n, ref_tree_attr): _n for _n in rtree}
        refnode2supports = defaultdict(list)
        reftree_species, reftree_branches = get_splits(rtree, target_attr=ref_tree_attr, ignore_multifurcations=True)

        refnode2visited = defaultdict(int)
        refnode2dups = defaultdict(list)
        refnode2losses = defaultdict(list)
        trees_scanned = 0
        for stree_count, stree_name in enumerate(src_tree_iterator(args)):
            print ("\r%s" %stree_count, end="", file=sys.stderr)
            sys.stderr.flush()
            refnode2matches = defaultdict(list)

            stree = tree_class(stree_name, format=args.ref_newick_format)
            # Parses attrs if necessary
            src_tree_attr = args.src_tree_attr
            if args.src_attr_parser:
                for leaf in stree:
                    leaf.add_feature('name', re.search(
                        args.src_attr_parser, getattr(leaf, args.src_tree_attr)).groups()[0])
                src_tree_attr = 'name'
            elif args.src_tree_attr:
                for leaf in stree:
                    leaf.name = getattr(leaf, args.src_tree_attr)
                src_tree_attr = 'name'

            # Computes dup and gene losses (treeko independent)
            srctree_species, srctree_branches = get_splits(stree, target_attr=src_tree_attr, discard_root=args.discard_root, target_species=reftree_species)

            if args.discard_incomplete:
                if reftree_species - srctree_species:
                    #print(reftree_species - srctree_species)
                    continue

            trees_scanned += 1 
            # intialized visited nodes with the observed leaves, as they are not
            # taken into account when processing splits
            visited_refnodes = set([_rnode for _rnode in rtree if getattr(_rnode, ref_tree_attr) in srctree_species])
            ref2dups = defaultdict(int)
            for srcnode, refnode, isdup in map_dup_and_losses(rtree, srctree_branches, ref_leaves):
                visited_refnodes.add(refnode)
                if isdup:
                    ref2dups[refnode] += 1
                    
            for refnode in visited_refnodes:
                refnode2visited[refnode] += 1
                refnode2dups[refnode].append(ref2dups[refnode])
                
            if args.treeko:
                # Count matches (treeko)
                ntrees, ndups, sp_trees = stree.get_speciation_trees(
                    autodetect_duplications=True, newick_only=True,
                    target_attr=src_tree_attr, map_features=["support"])

                refnodes = defaultdict(list)
                for i, subnw in enumerate(sp_trees):
                    if i>100:
                        break
                    subtree = tree_class(subnw)
                    treeko_srctree_species, treeko_srctree_branches = get_splits(subtree, target_attr=src_tree_attr)
                    for rbranch, matches in map_branches(reftree_branches,
                                                         treeko_srctree_branches,
                                                         reftree_species,
                                                         treeko_srctree_species):                        
                        refnodes[rbranch].append(len(matches))
                        if args.dump_matches and len(matches):
                            refnode2matches[rbranch].extend(matches)
                        
                for rbranch, support in refnodes.items():
                    refnode2supports[rbranch].append(numpy.mean(support))

            else:
                # Count matches (flat)
                for rbranch, matches in map_branches(reftree_branches, srctree_branches, reftree_species, srctree_species):
                    refnode2supports[rbranch].append(len(matches))                    
                    if args.dump_matches and len(matches):
                        refnode2matches[rbranch].extend(matches)
            
                        
            if refnode2matches:
                print('# %s\t%s' %("refbranch", "match"))
                for refbranch in rtree.traverse():
                    ref_nw = rbranch.write(format=9)
                    for m in refnode2matches.get(refbranch, []):
                        print('\t'.join([ref_nw, m.write(format=9)]))
                    
        data = []
        header=["ref branch", "data trees", "matches", "support (%)", "treeko matches", "treeko support (%)", "visited_trees", "duplications", "dup/tree", "dup/tree dev."]
        for node in rtree.traverse("levelorder"):

            has_support_data = node in refnode2supports 
            supports = refnode2supports[node] if has_support_data else "NA"
            observed = float(len([s for s in supports if s>0])) if has_support_data else "NA"
            total = float(len(supports)) if has_support_data else "NA"
            avg_observed = ((observed / total) * 100) if has_support_data else "NA"
            if args.treeko and has_support_data:
                treeko_observed = sum(supports)
                avg_treeko_observed = (treeko_observed / total) * 100
            else:
                treeko_observed = "NA"
                avg_treeko_observed = "NA"

            has_dup_data = node in refnode2visited
            #trees_visited = refnode2visited[node] if has_dup_data else "NA"
            trees_visited = len(refnode2dups[node])
            
            dups_observed = sum(refnode2dups[node]) if has_dup_data else "NA"
            #dup_rate = dups_observed/float(times_visited) if has_dup_data else "NA"
            dup_rate = numpy.mean(refnode2dups[node]) if has_dup_data else "NA"
            dup_dev = numpy.std(refnode2dups[node]) if has_dup_data else "NA"

            node.add_features(
                maptrees_total = total,
                maptrees_observerd = observed,
                maptrees_support = avg_observed,
                maptrees_treeko_observerd = treeko_observed,
                maptrees_treeko_support = avg_treeko_observed,
                maptrees_observed_dups = dups_observed,
                maptrees_visited = trees_visited,
                maptrees_dup_rate = dup_rate,

            )                
            data.append([node.write(format=9),
                         #str(node),
                         total,
                         observed,
                         avg_observed,
                         treeko_observed,
                         avg_treeko_observed,
                         trees_visited,
                         dups_observed,
                         dup_rate,
                         dup_dev,
                         ])

        if args.outtree:
            t.write(outfile=args.outtree, features=[])
            
        if args.image:
            from . import ete_view
            ts = ete_view.TreeStyle()
            ts.layout_fn = ete_view.maptrees_layout
            ts.show_scale = False
            ts.tree_width = 400
            rtree.render(args.image, tree_style=ts)
                        
        if args.taboutput:
            print('#'+'\t'.join(header))
            for row in data:
                print('\t'.join([str(v) for v in row]))               
        else:
            print()
            print_table(data, header=header, wrap_style="cut")
            rtree.write(features=[], outfile="outtree")
          
        print("Source trees used: %d" %trees_scanned)
