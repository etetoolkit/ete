#!/usr/bin/env python
import os
import sys
from math import sqrt
from common import __CITATION__, argparse, Tree, print_table
    
__DESCRIPTION__ = '''
#  - treedist -
# ===================================================================================
#  
# treestats provides basic information about one or more trees
#  
# %s
#  
# ===================================================================================
'''% __CITATION__

def mean_std_dev(durations):
    """ Calculate mean and standard deviation of data durations[]: """
    length, mean, std = len(durations), 0, 0
    for duration in durations:
        mean = mean + duration
    mean = mean / float(length)
    for duration in durations:
        std = std + (duration - mean) ** 2
    std = sqrt(std / float(length))
    mean = int(round(mean))
    std = int(round(std))
    return mean, std

def itertrees(trees, treefile):
    if trees:
        for nw in trees:
            yield nw
    if treefile:
        for line in open(treefile): 
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            else:
                yield line

def main(argv):
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tf", dest='target_trees_file', type=str, help='target_trees')

    parser.add_argument("-t", dest='target_trees', type=str, nargs="+",
                   help='target_trees')

    parser.add_argument("--unique", dest='unique', type=str,
                   help='When used, all the provided trees are compared and unique topologies are dumped in the specified file.')

    parser.add_argument("--stats", dest='stats', type=str,
                   help='Show general stats for the provided trees')

    parser.add_argument("--distmatrix", dest='distmatrix', type=str,
                   help='Dump a distance matrix (robinson foulds) among all topologies')

    
    args = parser.parse_args(argv)
    
    print __DESCRIPTION__

    unique_topo = {}
    stats_table = []
    for tfile in itertrees(args.target_trees, args.target_trees_file):
        t = Tree(tfile)
        if args.unique:
            tid = t.get_topology_id()
            if tid not in unique_topo:
                unique_topo[tid] = t
        if args.stats:
            most_distance_node, tree_length = t.get_farthest_leaf()
            supports = []
            names = []
            distances = []
            leaves = 0
            for n in t.traverse():
                names.append(n.name)
                if n.up:
                    supports.append(n.support)
                    distances.append(n.dist)
                    if n.is_leaf():
                        leaves += 1 
            min_support, max_support = min(supports), max(supports)
            mean_support, std_support =  mean_std_dev(supports)
            min_dist, max_dist = min(distances), max(distances)
            mean_dist, std_dist =  mean_std_dev(distances)

            stats_table.append([str(t.children<=2),
                                 leaves,
                                 tree_length,
                                 most_distance_node.name,
                                 min_support, max_support, mean_support, std_support,
                                 min_dist, max_dist, mean_dist, std_dist, ])

    if stats_table:
        header = ['rooted', '#tips', 'tree length', 'most distant tip', 'min support', 'max support', 'min support' , 'std support', 'max dist', 'min dist' , 'mean dist', 'std dist']
        print_table(stats_table, header=header, max_col_width=12)

    if unique_topo:
        print '%d unique topologies found' %len(unique_topo)
        topos = unique_topo.values()
        open(args.unique+'.trees', 'w').write('\n'.join([topo.write(format=9) for topo in topos ])+'\n')
   
        import itertools
        for a,b in itertools.product(topos, topos):
            print a.diff(b, output='diffs_tab')
            
            
if __name__ == '__main__':
    main(sys.argv[1:])

