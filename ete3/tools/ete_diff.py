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
# along with ETE.  If not, see <http://www.gnu.org/licenses/>
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
import json
import numpy as np
import numpy.linalg as LA
from scipy.cluster import hierarchy as hcluster
import random
import itertools
import multiprocessing as mp
from ..coretype.tree import Tree
from ..utils import print_table, color
from .ete_diff_lib._lapjv import lapjv
import textwrap
import argparse
import logging
log = logging.Logger("main")



DESC = ""

def SINGLECELL(*args):
    a = args[0]
    b = args[1]
    dist = []

    # Extract and parse pearson dict from first element (could be anyother)
    for p in a[1]:
        pearson = json.loads(p)
        break
    len_axb = 0


    for leaf_a in a[0].iter_leaves():
        for leaf_b in b[0].iter_leaves():
            len_axb += 1
            dist.append(pearson[leaf_a.name][leaf_b.name])
    
    dist = np.percentile(dist,50)
#     dist = sum(dist) / len_axb
    
    return dist


def EUCL_DIST(*args):  
    a = args[0]
    b = args[1]
    return 1 - (float(len(a[1] & b[1])) / max(len(b[1]), len(a[1])))

def EUCL_DIST_B(*args):
    
    a = args[0]
    b = args[1]
    attr1 = args[2]
    attr2 = args[3]

    dist_a = sum([descendant.dist for descendant in a[0].iter_leaves() if getattr(descendant,attr1) in(a[1] - b[1])])
    dist_b = sum([descendant.dist for descendant in b[0].iter_leaves() if getattr(descendant,attr2) in(b[1] - a[1])])
    
    return 1 - (float(len(a[1] & b[1])) / max(len(a[1]), len(b[1]))) + abs(dist_a - dist_b)

def EUCL_DIST_B_ALL(*args): 
    
    a = args[0]
    b = args[1]
    attr1 = args[2]
    attr2 = args[3]

    dist_a = sum([descendant.dist for descendant in a[0].iter_leaves()])
    dist_b = sum([descendant.dist for descendant in b[0].iter_leaves()])
    
    return 1 - (float(len(a[1] & b[1])) / max(len(a[1]), len(b[1]))) + abs(dist_a - dist_b)

def RF_DIST(*args):
    
    a = args[0]
    b = args[1]
    
    if len(a[1] & b[1]) < 2:
        return 1.0
    (a, b) = (b, a) if len(b[1]) > len(a[1]) else (a,b)
    rf, rfmax, names, side1, side2, d1, d2 = a[0].robinson_foulds(b[0])
    return (rf/rfmax if rfmax else 0.0)

def load_matrix(file,separator):
    idx = []
    with open(file, "r") as f:
        headers = f.readline().rstrip().split(separator)[1:] # exclude empty space at the begining
        col2v = { h :[] for h in headers}
        for line in f:
            elements = line.strip().split(separator)
            idx.append(elements.pop(0))
            for i,h in enumerate(headers):
                col2v[h].append(float(elements[i]))
    treedict = {}
    treedict['idx'] = idx
    treedict['headers'] = headers
    treedict['dict'] = col2v
    
    return treedict


def dict2tree(treedict,jobs=1,parallel=None):
    log = logging.getLogger()
#     log.info(treedict['headers'])

    matrix = np.zeros((len(treedict['headers']), len(treedict['headers'])))
    dm = {h : {} for h in treedict['headers']}

    if parallel == 'sync':
        pool = mp.Pool(jobs)
        matrix = [[pool.apply(np.corrcoef,args=(treedict['dict'][col1],treedict['dict'][col2])) for col2 in treedict['headers']] for col1 in treedict['headers']]
        pool.close()    
    
    if parallel == 'async':
        pool = mp.Pool(jobs)
        matrix = [[pool.apply_async(np.corrcoef,args=(treedict['dict'][col1],treedict['dict'][col2])) for col2 in treedict['headers']] for col1 in treedict['headers']]
        pool.close()
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                matrix[i][j] = matrix[i][j].get()[0][1]
    
    else:
        matrix = [[(np.corrcoef(treedict['dict'][col1],treedict['dict'][col2]))[0][1] for col2 in treedict['headers']] for col1 in treedict['headers']]

    Z = hcluster.linkage(matrix, "average") #"single" for default, "average" for UPGMA
    T = hcluster.to_tree(Z)


    root = Tree()
    root.dist = 0
    root.name = "root"
    item2node = {T.get_id(): [T, root]}

    to_visit = [T]
    while to_visit:
        node = to_visit.pop()
        cl_dist = node.dist /2.0
        for ch_node in [node.left, node.right]:
            if ch_node:
                ch = Tree()
                ch.dist = cl_dist
                ch.name = str(ch_node.get_id())
                item2node[node.get_id()][1].add_child(ch)
                item2node[ch_node.get_id()] = [ch_node, ch]
                to_visit.append(ch_node)


    # This is your ETE tree structure
    tree = root

    for leaf in tree:
        leaf.name = treedict['headers'][int(leaf.name)]
        
    return tree

def tree_from_matrix(matrix,sep=",",dictionary=False,jobs=1,parallel=None):
    tree_dict = load_matrix(matrix,sep)

    if dictionary == True:
        return dict2tree(tree_dict,jobs,parallel), tree_dict
    else:
        return dict2tree(tree_dict,jobs,parallel)
    
def pearson_corr(rdict,tdict):
    # Select only common genes by gene name y both dictionaries
    log = logging.getLogger()
    log.info("Getting shared genes...")
    rfilter = [i for i,value in enumerate(rdict['idx']) if value in tdict['idx']]
    tfilter = [i for i,value in enumerate(tdict['idx']) if value in rdict['idx']]
    log.info("Total Genes Shared = " + str(len(rfilter)))

    rdict['dict'] = {header : [rdict['dict'][header][element] for element in rfilter] for header in rdict['headers']}

    tdict['dict'] = {header : [tdict['dict'][header][element] for element in tfilter] for header in tdict['headers']}

    leaves = np.concatenate((rdict['headers'],tdict['headers']))
    pearson = {x: {} for x in leaves}
    for a in rdict['headers']:
        for b in tdict['headers']:
            pearson[a][b] = pearson[b][a] = 1 - np.corrcoef(rdict['dict'][a],tdict['dict'][b])[0][1]

    return pearson

def be_distance(t1,t2):
    """Branch-Extended Distance"""
    
    # Get total distance from leaf to root
    def _get_leaves_paths(t):
        leaves = t.get_leaves()
        leave_branches = set()

        for n in leaves:
            if n.is_root():
                continue
            movingnode = n
            length = 0
            while not movingnode.is_root():
                length += movingnode.dist
                movingnode = movingnode.up
            leave_branches.add((n.name,length))

        return leave_branches

    # Get difference of distances from unique leaves in tree 1 - unique leaves in tree 2
    def _get_distances(leaf_distances1,leaf_distances2):

        unique_leaves1 = leaf_distances1 - leaf_distances2
        unique_leaves2 = leaf_distances2 - leaf_distances1
        
        return abs(sum([leaf[1] for leaf in unique_leaves1]) - sum([leaf[1] for leaf in unique_leaves2]))

    return _get_distances(_get_leaves_paths(t1),_get_leaves_paths(t2))    


def cc_distance(t1,t2):
    """Cophenetic-Compared Distance"""
    def cophenetic_compared_matrix(t_source,t_compare):

        leaves = t_source.get_leaves()
        paths = {x.name: set() for x in leaves}

        # get the paths going up the tree
        # we get all the nodes up to the last one and store them in a set

        for n in leaves:
            if n.is_root():
                continue
            movingnode = n
            while not movingnode.is_root():
                paths[n.name].add(movingnode)
                movingnode = movingnode.up

        # We set the paths for leaves not in the source tree as empty to indicate they are non-existent

        for i in (set(x.name for x in t_compare.get_leaves()) - set(x.name for x in t_source.get_leaves())):
            paths[i] = set()

        # now we want to get all pairs of nodes using itertools combinations. We need AB AC etc but don't need BA CA

        leaf_distances = {x: {} for x in paths.keys()}

        for (leaf1, leaf2) in itertools.combinations(paths.keys(), 2):
            # figure out the unique nodes in the path
            if len(paths[leaf1]) > 0 and len(paths[leaf2]) > 0:
                uniquenodes = paths[leaf1] ^ paths[leaf2]
                distance = sum(x.dist for x in uniquenodes)
            else:
                distance = 0
            leaf_distances[leaf1][leaf2] = leaf_distances[leaf2][leaf1] = distance

        allleaves = sorted(leaf_distances.keys()) # the leaves in order that we will return

        output = [] # the two dimensional array that we will return

        for i, n in enumerate(allleaves):
            output.append([])
            for m in allleaves:
                if m == n:
                    output[i].append(0) # distance to ourself = 0
                else:
                    output[i].append(leaf_distances[n][m])
        return np.asarray(output)

    ccm1 = cophenetic_compared_matrix(t1,t2)
    ccm2 = cophenetic_compared_matrix(t2,t1)
    
    return LA.norm(ccm1-ccm2)


def sepstring(items, sep=", "):
    return sep.join(sorted(map(str, items)))



### Treediff ###

def treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, reduce_matrix=False,extended=None, jobs=1, parallel=None):
    log = logging.getLogger()
    log.info("Computing distance matrix...")
    for index, n in enumerate(t1.traverse('preorder')):
        n._nid = index
    for index, n in enumerate(t2.traverse('preorder')):
        n._nid = index
    t1_cached_content = t1.get_cached_content(store_attr=attr1)
    t1 = None
    t2_cached_content = t2.get_cached_content(store_attr=attr2)
    t2 = None

#     parts1 = [(k, v) for k, v in t1_cached_content.items() if k.children]
#     parts2 = [(k, v) for k, v in t2_cached_content.items() if k.children]

    parts1 = [(k, v) for k, v in t1_cached_content.items()]
    t1_cached_content = None
    parts2 = [(k, v) for k, v in t2_cached_content.items()]
    t2_cached_content = None

    parts1 = sorted(parts1, key = lambda x : len(x[1]))
    parts2 = sorted(parts2, key = lambda x : len(x[1]))
   
    if parallel == 'sync':
        pool = mp.Pool(jobs)
        matrix = [[pool.apply(dist_fn,args=((n1,x),(n2,y),attr1,attr2)) for n2,y in parts2] for n1,x in parts1]
        pool.close()
    
    elif parallel == 'async':
        pool = mp.Pool(jobs)
        matrix = [[pool.apply_async(dist_fn,args=((n1,x),(n2,y),attr1,attr2)) for n2,y in parts2] for n1,x in parts1]
        pool.close()
    
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                matrix[i][j] = matrix[i][j].get()

    else:
        matrix = [[dist_fn((n1,x),(n2,y),attr1,attr2) for n2,y in parts2] for n1,x in parts1]
    
    # Reduce matrix to avoid useless comparisons
    if reduce_matrix:
        log.info( "Reducing distance matrix...")
        cols_to_include = set(range(len(matrix[0])))
        rows_to_include = []
        for i, row in enumerate(matrix):
            try:
                cols_to_include.remove(row.index(0.0))
            except ValueError:
                rows_to_include.append(i)
            except KeyError:
                pass
        
        cols_to_include = sorted(cols_to_include)

        parts1 = [parts1[row] for row in rows_to_include]
        parts2 = [parts2[col] for col in cols_to_include]
        
        new_matrix = []
        for row in rows_to_include:
            new_matrix.append([matrix[row][col] for col in cols_to_include])
 
        if len(new_matrix) < 1:
            return new_matrix
        
        log.info("Distance matrix reduced from %dx%d to %dx%d" %\
                (len(matrix), len(matrix[0]), len(new_matrix), len(new_matrix[0])))
            
        matrix = new_matrix

    log.info("Comparing trees...")
    
    difftable = []
    b_dist = -1
    matrix = np.asarray(matrix, dtype=np.float32)
    
    if dist_fn != SINGLECELL:
        
        cols , _ = lapjv(matrix,extend_cost=True)

        for r in range(len(matrix)):
            c = cols[r]
            
            if extended:
                b_dist = extended(parts1[r][0], parts2[c][0])
            else:
                pass

            dist, side1, side2, diff, n1, n2 = (matrix[r][c], 
                                                parts1[r][1], parts2[c][1],
                                                parts1[r][1].symmetric_difference(parts2[c][1]),
                                                parts1[r][0], parts2[c][0])
            difftable.append([dist, b_dist, side1, side2, diff, n1, n2])

        return difftable
    
    # Show only best match
    elif dist_fn == SINGLECELL:
        for r in range(len(matrix)):
            c = np.argmin(matrix[r])

            if extended:
                b_dist = extended(parts1[r][0], parts2[c][0])
            else:
                pass
            
            dist, side1, side2, diff, n1, n2 = (matrix[r][c], 
                                                [l.name for l in parts1[r][0].iter_leaves()], [l.name for l in parts2[r][0].iter_leaves()],
                                                parts1[r][1].symmetric_difference(parts2[c][1]),
                                                parts1[r][0], parts2[c][0])
            difftable.append([dist, b_dist, side1, side2, diff, n1, n2])

        return difftable

### REPORTS ###

def show_difftable_summary(difftable, rf=-1, rf_max=-1, extended=None):
    total_dist = 0
    total_bdist = 0
    for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
        total_dist += dist
        total_bdist += b_dist
  
    if extended:
        print("\n"+"\t".join(["Dist", "branchDist", "Mismatches", "RF", "maxRF"]))
        print("%0.6f\t%0.6f\t%10d\t%d\t%d" %(total_dist,total_bdist, len(difftable), rf, rf_max))
    else:
        print("\n"+"\t".join(["Dist", "Mismatches", "RF", "maxRF"]))
        print("%0.6f\t%10d\t%d\t%d" %(total_dist, len(difftable), rf, rf_max))

def show_difftable(difftable, extended=False):
    showtable = []
    
    if extended:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
            showtable.append([dist, b_dist, len(side1), len(side2), len(diff), sepstring(side1), sepstring(side2), sepstring(diff)])
        print_table(showtable, header=["Dist", "branchDist", "Size1", "Size2", "ndiffs", "refTree", "targetTree", "Diff"],
                    max_col_width=80, wrap_style="wrap", row_line=True)
    else:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
            showtable.append([dist, len(side1), len(side2), len(diff), sepstring(side1), sepstring(side2), sepstring(diff)])
        print_table(showtable, header=["Dist", "Size1", "Size2", "ndiffs", "refTree", "targetTree", "Diff"],
                    max_col_width=80, wrap_style="wrap", row_line=True)

def show_difftable_tab(difftable, extended=None):
    showtable = []
    
    if extended:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
            showtable.append([dist, b_dist, len(side1), len(side2), len(diff),
                              sepstring(side1, "|"), sepstring(side2, "|"),
                              sepstring(diff, "|")])
        print('#' + '\t'.join(["Dist", "branchDist", "Size1", "Size2", "ndiffs", "refTree", "targetTree", "Diff"]))
    else:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
            showtable.append([dist, len(side1), len(side2), len(diff),
                              sepstring(side1, "|"), sepstring(side2, "|"),
                              sepstring(diff, "|")])
        print('#' + '\t'.join(["Dist", "Size1", "Size2", "ndiffs", "refTree", "targetTree", "Diff"]))
        
    print('\n'.join(['\t'.join(map(str, items)) for items in showtable]))
    
    
def show_difftable_topo(difftable, attr1, attr2, usecolor=False, extended=None):
    log = logging.getLogger()
    if not difftable:
        return
    showtable = []
    maxcolwidth = 80
    total_dist = 0
    for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True):
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
        
        if extended:
            showtable.append([dist, b_dist, "%d/%d (%d)" %(len(side1), len(side2),len(diff)), topo1, topo2])
        else:
            showtable.append([dist, "%d/%d (%d)" %(len(side1), len(side2),len(diff)), topo1, topo2])
    
    if extended:
        print_table(showtable, header=["Dist", "branchDist", "#Diffs", "refTree", "targetTree"],
                    max_col_width=maxcolwidth, wrap_style="wrap", row_line=True)
    else:
        print_table(showtable, header=["Dist", "#Diffs", "refTree", "targetTree"],
                    max_col_width=maxcolwidth, wrap_style="wrap", row_line=True)    
        
    log.info("Total euclidean distance:\t%0.4f\tMismatching nodes:\t%d" %(total_dist, len(difftable)))
    
    
    
    
    
### SCA REPORTS ###
    
def show_difftable_summary_SCA(difftable, rf=-1, rf_max=-1, extended=None):
    total_dist = 0
    total_bdist = 0
    for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
        total_dist += dist
        total_bdist += b_dist
  
    if extended:
        print("\n"+"\t".join(["Dist", "branchDist", "Mismatches", "RF", "maxRF"]))
        print("%0.6f\t%0.6f\t%10d\t%d\t%d" %(total_dist,total_bdist, len(difftable), rf, rf_max))
    else:
        print("\n"+"\t".join(["Dist", "Mismatches", "RF", "maxRF"]))
        print("%0.6f\t%10d\t%d\t%d" %(total_dist, len(difftable), rf, rf_max))
        
def show_difftable_SCA(difftable, extended=False):
    showtable = []
    
    if extended:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
            showtable.append([dist, b_dist, len(side1), len(side2), sepstring(side1), sepstring(side2)])
        print_table(showtable, header=["Dist", "branchDist", "Size1", "Size2","refTree", "targetTree"],
                    max_col_width=80, wrap_style="wrap", row_line=True)
    else:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
            showtable.append([dist, len(side1), len(side2), sepstring(side1), sepstring(side2)])
        print_table(showtable, header=["Dist", "Size1", "Size2", "refTree", "targetTree"],
                    max_col_width=80, wrap_style="wrap", row_line=True)    
    
def show_difftable_tab_SCA(difftable, extended=None):
    showtable = []
    
    if extended:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
            showtable.append([dist, b_dist, len(side1), len(side2), sepstring(side1, "|"), sepstring(side2, "|")])
        print('#' + '\t'.join(["Dist", "branchDist", "Size1", "Size2", "refTree", "targetTree"]))
    else:
        for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
            showtable.append([dist, len(side1), len(side2),
                              sepstring(side1, "|"), sepstring(side2, "|")])
        print('#' + '\t'.join(["Dist", "Size1", "Size2", "refTree", "targetTree"]))
        
    print('\n'.join(['\t'.join(map(str, items)) for items in showtable]))    
    
def show_difftable_topo_SCA(difftable, attr1, attr2, usecolor=False, extended=None):
    if not difftable:
        return
    showtable = []
    maxcolwidth = 80
    total_dist = 0

    for dist, b_dist, side1, side2, diff, n1, n2 in sorted(difftable, reverse=True,key = lambda x : x[0]):
        log = logging.getLogger()
        total_dist += dist
        n1 = Tree(n1.write())
        n2 = Tree(n2.write())
        n1.ladderize()
        n2.ladderize()

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
        
        if extended:
            showtable.append([dist, b_dist, "%d/%d (%d)" %(len(side1), len(side2),len(diff)), topo1, topo2])
        else:
            showtable.append([dist, "%d/%d (%d)" %(len(side1), len(side2),len(diff)), topo1, topo2])
    
    if extended:
        print_table(showtable, header=["Dist", "branchDist", "#Diffs", "refTree", "targetTree"],
                    max_col_width=maxcolwidth, wrap_style="wrap", row_line=True)
    else:
        print_table(showtable, header=["Dist", "#Diffs", "refTree", "targetTree"],
                    max_col_width=maxcolwidth, wrap_style="wrap", row_line=True)    
        
    log.info("Total euclidean distance:\t%0.4f\tMismatching nodes:\t%d" %(total_dist, len(difftable)))
       
        
        
        
        
        
        
        
### ARGUMENTS ###        
        
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
                           type=str, choices= ['e', 'rf', 'eb','eb-all'], default='e',
                           help=('Distance measure (e by default): e = Euclidean distance, rf = Robinson-Foulds symetric distance'
                                 ' eb = Euclidean distance + branch length difference between disjoint leaves'))
    
    diff_args_r = diff_args_p.add_argument_group("DIFF RESEARCH OPTIONS")
    
    diff_args_r.add_argument("--extended", dest="extended",
                           type=str, choices= [None,'cc','be'], default=None,
                           help=('Extend with branch distance after node comparison (None by default). cc = Branch distance based in cophenetic-like distance between trees '
                                'be = branch extended distance based on the distance from unique leaves to root between source tree and target tree'))
    
    diff_args_r.add_argument("--ref-matrix", dest="rmatrix",
                           type=str,
                           help=('For Single Cell Analysis data, csv/tsv (see --extension option) with cell IDs as columns headers and their '
                                 'expresion values below. If given, --dist will be ignored'))
    
    diff_args_r.add_argument("--target-matrix", dest="tmatrix",
                           type=str,
                           help=('For Single Cell Analysis data, csv/tsv (see --extension option) with cell IDs as columns headers and their '
                                 'expresion values below. If given, --dist will be ignored'))
    
    diff_args_r.add_argument("--extension", dest="ext",
                           type=str, choices= ['tsv','csv'], default='csv',
                           help=('Data separator for Single Cell Analysis data expression matrix (csv by default)'))
    
    diff_args_r.add_argument("--parallelism", dest="parallelism",
                           type=str, choices= [None,'sync','async'], default=None,
                           help=('Distance matrix computation parallelism (None by default). sync form syncronous and asyncc for asyncronous parallelism. '
                                'CAUTION: Only for research purpose as the wall time will be higher for all functions'))
    
    diff_args_r.add_argument("-C", "--cpu", dest="maxjobs", type=int,
                            default=1, help="CAUTION: only for non linear parallelism (see --parallelism option). "
                            " Maximum number of CPU/jobs"
                            " available in the execution host. If higher"
                            " than 1, tasks with multi-threading"
                            " capabilities will enabled. Note that this"
                            " number will work as a hard limit for all applications,"
                            "regardless of their specific configuration.")
    
def run(args):
    
    if (not args.ref_trees or not args.src_trees) and (not args.rmatrix or not args.tmatrix):
        logging.warning("Target tree/matrix or reference tree/matrix weren't introduced. You can find the arguments in the help command (-h)")
        
    else:
        if args.quiet:
            logging.basicConfig(format='%(message)s', level=logging.WARNING)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)
        log = logging

        # Set maximun number of jobs
        if args.maxjobs == -1:
            maxjobs = mp.cpu_count()
        else:
            maxjobs = args.maxjobs          
        
        if args.ncbi:
            from common import ncbi
            ncbi.connect_database()

        rattr, tattr = args.ref_attr, args.target_attr

        log.info("Loading trees...")
        if args.ref_trees and args.src_trees:
            rtree = args.ref_trees[0]
            ttree = args.src_trees[0]
            t1 = Tree(rtree,format=args.ref_newick_format)
            t2 = Tree(ttree,format=args.src_newick_format)
            
        elif args.rmatrix and args.tmatrix:
            sepdict = {'tsv' : "\t", "csv" : ","}
            sep_ = sepdict[args.ext]
            
            log.info("Reference Tree...")
            t1, rdict = tree_from_matrix(args.rmatrix,sep_,dictionary=True,jobs=maxjobs,parallel=args.parallelism)
            
            log.info("Target Tree...")
            t2, tdict = tree_from_matrix(args.tmatrix,sep_,dictionary=True,jobs=maxjobs,parallel=args.parallelism)


        if args.ncbi:

            taxids = set([getattr(leaf, rattr) for leaf in t1.iter_leaves()])
            taxids.update([getattr(leaf, tattr) for leaf in t2.iter_leaves()])
            taxid2name = ncbi.get_taxid_translator(taxids)
            for leaf in  t1.get_leaves()+t2.get_leaves():
                try:
                    leaf.name=taxid2name.get(int(leaf.name), leaf.name)
                except ValueError:
                    pass

        # Report extension
        if args.extended == 'cc':
            extend = cc_distance
        elif args.extended == 'be':
            extend = be_distance
        else:
            extend = None
            
        # Single cell
        if args.rmatrix and args.tmatrix:
            
            pearson = pearson_corr(rdict,tdict)

            for leaf in t1.iter_leaves():
                # we can't pass dicts or lists due to an incompatibility with get_cached_content so we give a string and then parse it
                leaf.pearson=json.dumps(pearson)

            for leaf in t2.iter_leaves():
                # we can't pass dicts or lists due to an incompatibility with get_cached_content so we give a string and then parse it
                leaf.pearson=json.dumps(pearson)

            rattr, tattr = 'pearson', 'pearson'
            dist_fn = SINGLECELL

        else:
            if args.distance == 'e':
                dist_fn = EUCL_DIST
            elif args.distance == 'rf':
                dist_fn = RF_DIST
            elif args.distance == 'eb':
                dist_fn = EUCL_DIST_B
            elif args.distance == 'eb-all':
                dist_fn = EUCL_DIST_B_ALL
            else:
                pass
            
                

        difftable = treediff(t1, t2, rattr, tattr, dist_fn, args.fullsearch, extended=extend,jobs=maxjobs, parallel=args.parallelism)

        if len(difftable) != 0:
            if dist_fn != SINGLECELL:
                if args.report == "topology":
                    show_difftable_topo(difftable, rattr, tattr, usecolor=args.color,extended=extend)
                elif args.report == "diffs":
                    show_difftable(difftable, extended=extend)
                elif args.report == "diffs_tab":
                    show_difftable_tab(difftable, extended=extend)
                elif args.report == 'summary':
                    rf, rf_max, _, _, _, _, _ = t1.robinson_foulds(t2, attr_t1=rattr, attr_t2=tattr)
                    show_difftable_summary(difftable, rf, rf_max, extended=extend)
                    
            elif dist_fn == SINGLECELL:
                if args.report == "topology":
                    show_difftable_topo_SCA(difftable, rattr, tattr, usecolor=args.color,extended=extend)
                elif args.report == "diffs":
                    show_difftable_SCA(difftable, extended=extend)
                elif args.report == "diffs_tab":
                    show_difftable_tab_SCA(difftable, extended=extend)
                elif args.report == 'summary':
                    rf, rf_max, _, _, _, _, _ = t1.robinson_foulds(t2, attr_t1='name', attr_t2='name')
                    show_difftable_summary_SCA(difftable, rf, rf_max, extended=extend)

        else:
            log.info("Difference between (Reference) %s and (Target) %s returned no results" % (rtree, ttree))


