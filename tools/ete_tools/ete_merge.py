#!/usr/bin/env python
import sys
import os
from collections import defaultdict
from common import __CITATION__,  Tree, argparse, print_table

__DESCRIPTION__ = '''
#  - ete combine -
# ===================================================================================
#  
# 'ete combine' allows to merge the annotation of two or more trees, producing a single 
# newick that contains all the targeted annotations. 
#  
%s
#  
# ===================================================================================
'''% __CITATION__

def main(argv):
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("-r", dest="reftree", 
                        type=str, required=True,
                        help="""Reference tree""")

    parser.add_argument("source_trees", metavar='source_trees',
                        type=str, nargs="+", 
                        help='A list of newick tree files used as a source for node annotations')

    parser.add_argument("--discard", dest="discard",
                        type=str, nargs="+", default=[],
                        help=("A list of attributes that should be ignored from source trees. "
                              "Node dist, name and support values are always ignored unless they"
                              " are explicitly passed as target features"))

    parser.add_argument("--features", dest="features",
                        type=str, nargs="+", default = [],
                        help=("A list of attributes that should be transferred from source trees."))
    
    parser.add_argument("-o", dest="output", 
                        type=str, required=True, 
                        help=("output file name for the annotated tree"))

    args = parser.parse_args(argv)
    ref = Tree(args.reftree)
    TARGET_FEATURES = args.features
    DISCARD_FEATURES = args.discard + ["support", "name", "dist"]

    key2node = {}
    for node in ref.traverse():
        nodekey = frozenset(node.get_leaf_names())
        key2node[nodekey] = node
    
    out = ref.children[0].get_leaf_names()
    out2 = ref.children[1].get_leaf_names()
    transferred_features = defaultdict(int)
    for target in args.source_trees:
        print target
        tt = Tree(target)
        tt.prune(ref.get_leaf_names())
        if len(out) > 1:
            try:
                tt.set_outgroup(tt.get_common_ancestor(out))
            except ValueError:
                tt.set_outgroup(tt.get_common_ancestor(out2))
        else:
            tt.set_outgroup(tt.search_nodes(name=out[0])[0])

        for node in tt.traverse():
            nodekey = frozenset([n.name for n in node.get_leaves()])
            target_node = key2node.get(nodekey, None)
            if target_node:
                for f in node.features:
                    if f in DISCARD_FEATURES and not TARGET_FEATURES:
                        continue
                    elif TARGET_FEATURES and f not in TARGET_FEATURES:
                        continue
                    else:
                        transferred_features[f] += 1
                        target_node.add_feature(f, getattr(node, f))

    ref.write(outfile=args.output, features=[], format_root_node=True)
    print
    print_table(transferred_features.items(), header=["feature name", "#nodes"])

if __name__ == '__main__':
    main(sys.argv[1:])
