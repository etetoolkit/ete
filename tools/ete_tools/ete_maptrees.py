#!/usr/bin/env python

import sys
import os
from collections import defaultdict
from common import __CITATION__,  Tree, PhyloTree, argparse, add_face_to_node, TreeStyle, faces, NodeStyle
import numpy
import hashlib
import gc
import cPickle
import time
import commands
md5 = lambda x: hashlib.md5(x).hexdigest()

args = None

__DESCRIPTION__ = '''
#  - maptrees -
# ===================================================================================
#
# 'maptrees' is a program that compares a list of gene-trees against a reference
# topology and calculates the duplication and gene loss rates for every branch
# in the reference tree. In addition, the percentage of gene-trees supporting
# each split in the reference tree (GT support) is calculated. 
#
# Note that this is a duplication aware program, so gene-trees are allowed to
# contain different number of leaves and species content.
#
%s
#
# ===================================================================================
# '''% __CITATION__

def get_first_common_branch(observed_items, reftree_content):
    #first common ancestor of the observed_items in the reftree
    smallest_clade = None
    for node, content in reftree_content.iteritems():
        if observed_items.issubset(content):
            if not min_clade or len(reftree_content[smallest_clade]) < len(content):
                smallest_clade = node
    return smallest_clade
                
def minimize_lost_branches(lost_items, reftree_branches):
    """
    given a set of lost items and a sorted list (preorder) of reference tree
    partitions, returns the min number of lost branches explaining all the
    losses.
    """
    lost_branches = []
    for branch, refcontent in reftree_branches:
        if refcontent.issubset(lost_items):
            lost_branches.append(branch)
            lost_items -= refcontent
    return lost_branches

def get_lost_branches(obs_items, expected_items, ref_branch,
                      sorted_ref_branches):
    """
    Returns the minimum set of lost branches that explain the observed and
    expected set of items, given a reference tree. 
    """
    
    # Calculate lost items in both sides of the duplication
    lost_items = expected_items - obs_items
    if lost_items:
        # Convert list items into the minimum number of branch losses
        lost_branches = minimize_lost_branches(lost_items, sorted_ref_branches)
    else:
        lost_branches = []
    # Group lost branches
    return lost_branches
   
def process_trees(iter_data, reftree, total_trees, thread_name=""):
    # cache some common data
    reftree_content = reftree.get_cached_content(store_attr="name")
    sorted_ref_branches = [(n, reftree_content[n]) for n in reftree.traverse("preorder")]
    refclades = [(n, reftree_content[n.children[0]], reftree_content[n.children[1]])
                 for n in reftree.traverse("preorder") if not n.is_leaf()]

    informed_branches = defaultdict(int)      # How many trees were used to
                                              # inform about each refTree branch
    
    losses_per_branch = defaultdict(int)      # Number of losses in each refTree branch
    coll_losses_per_branch = defaultdict(int) 
    
    losses_per_dup_branch = defaultdict(list) # Number of losses for duplication
                                              # in each refTreeBranch
    coll_losses_per_dup_branch = defaultdict(list) 
    
    dup_per_branch = defaultdict(list)        # dUplication events sorted by
                                              # refTree branch
    coll_dup_per_branch = defaultdict(list)   
                                              
    refbranch_supports = defaultdict(list)    # gene tree support values for
                                              # each refTree branch
    coll_refbranch_supports = defaultdict(list)    

    skipped_trees = 0
        
    time0 = time.time()
    tracked_times = []
    for tree_counter, (treeid, t, tree_content) in enumerate(iter_data):
        if DEBUG:
            print treeid, t
            ts = TreeStyle()
            ts.title.add_face(faces.TextFace("Seedid = %s"%treeid), 1)
            t.render("%s.png"%treeid, tree_style=ts)
                        
        if tree_counter % 100 == 0:
            etime = time.time() - time0
            tracked_times.append(etime)
            total_etime = ((total_trees - tree_counter) / 100.0) * numpy.mean(tracked_times)
            percent = (tree_counter / float(total_trees)) * 100
            print >>sys.stderr, "\r%s% 10d (%0.1f%%) skipped trees:% 5d. Remaining time ~= %d min" %(thread_name, tree_counter, percent, skipped_trees, total_etime/60.)
            time0 = time.time()
            sys.stderr.flush()
            gc.collect()

            
        if tree_counter and MONITOR_STEP and tree_counter % MONITOR_STEP == 0:
            annotate_tree(reftree, informed_branches, dup_per_branch, losses_per_branch,
                          losses_per_dup_branch, refbranch_supports,
                          coll_dup_per_branch, coll_losses_per_branch,
                          coll_losses_per_dup_branch, coll_refbranch_supports)
            
            ts = TreeStyle()
            ts.layout_fn = info_layout
            reftree.render("temp_tree_analysis.png", tree_style=ts)
            
        # Compute support of this tree over the whole refTree
        seedid = None if USE_COLLATERAL else treeid
        seedsp = None if USE_COLLATERAL else extract_species(treeid)
        branch2supports, branch2coll_supports = get_supported_branches(t, tree_content,
                                                                       refclades=refclades, seedid=seedid)
        if branch2supports == {} and branch2coll_supports == {}:
            skipped_trees +=1
            
        # We combine the information of all treeko trees, by averaging the
        # number of subtrees that supported or not a given refTree branch.
        for refbranch, supports in branch2supports.iteritems():
            if IS_VALID_TREEID is None or IS_VALID_TREEID(treeid, extract_species(reftree_content[refbranch])):
                refbranch_supports[refbranch.nid].append(numpy.mean(supports))
        for refbranch, coll_supports in branch2coll_supports.iteritems():
            if IS_VALID_TREEID is None or IS_VALID_TREEID(treeid, extract_species(reftree_content[refbranch])):
                coll_refbranch_supports[refbranch.nid].append(numpy.mean(coll_supports))

        all_observed_sp = extract_species([n.name for n in tree_content[t]])
                
        if REPORT_PER_TREE_SUPPORTS:
            if branch2supports:
                mean_seed_support = numpy.mean([numpy.mean(branch2supports[_b]) for _b in branch2supports])
            else:
                mean_seed_support = 0.0
            if branch2coll_supports:
                mean_coll_support = numpy.mean([numpy.mean(branch2coll_supports[_b]) for _b in branch2coll_supports])
            else:
                mean_coll_support = 0.0
            species_coverage = float(len(all_observed_sp))/len(REFTREE_SPECIES)
            print >>REPORT_SUPPORT_FILE, '\t'.join(map(str, [treeid, species_coverage, mean_seed_support,  mean_coll_support, len(branch2supports), len(branch2coll_supports)]))
                            
        # Here I keep a counter on how many trees were potentially able to
        # inform about specific reftree branches. For instance, if outgroup
        # species X does not appear in a genetree, I dont want to count this
        # tree as a source for duplication in the X branch.
        if len(all_observed_sp) == 1: 
            max_ref_branch = reftree.search_nodes(name=list(all_observed_sp)[0])[0]
        else:
            max_ref_branch = reftree.get_common_ancestor(all_observed_sp)
            
        for refbranch in max_ref_branch.traverse():
            if IS_VALID_TREEID is None or IS_VALID_TREEID(treeid, extract_species(reftree_content[refbranch])):
                informed_branches[refbranch.nid] += 1

        # Start analyzing internal nodes
        for node in t.traverse("preorder"):
            if node.is_leaf():
                continue 

            if len(node.children) != 2:
                print node
                raise ValueError("Binary trees are required")

            # Extract the species set at both sides of the node
            ch_left = node.children[0]
            ch_right = node.children[1]
            seqs_left = set([n.name for n in tree_content[ch_left]])
            seqs_right = set([n.name for n in tree_content[ch_right]])
            species_left = extract_species(seqs_left)
            species_right = extract_species(seqs_right)

            # Decide whether this node is a duplication or not
            if DETECT_DUPLICATIONS:
                if SP_OVERLAP == 0:
                    isdup = True if species_left & species_right else False
                else:
                    #overlap = len(species_left & species_right) / float(max(len(species_left), len(species_right)))
                    overlap = len(species_left & species_right) / float(len(species_left | species_right))

                    isdup = True if overlap >= SP_OVERLAP else False
                    if DEBUG and overlap:
                        print species_left, species_right
                        print len(species_left & species_right),  float(len(species_left | species_right))
                        print overlap, isdup
                
            else:
                isdup = True if n.evoltype == "D" else False

            # if this is a dup or the root of tree, map the to node to its
            # corresponding refTree branch and infer the expected list of
            # species
            if isdup or node is t: 
                observed_sp = species_left | species_right
                if len(observed_sp) == 1: 
                    ref_branch = reftree.search_nodes(name=list(observed_sp)[0])[0]
                else:
                    ref_branch = reftree.get_common_ancestor(observed_sp)
                expected_sp = reftree_content[ref_branch]

            if isdup:
                if IS_VALID_TREEID is None or IS_VALID_TREEID(treeid, extract_species(reftree_content[ref_branch])):
                    # updates duplications per branch in ref tree (dup rate analysis)
                    if USE_COLLATERAL or seedsp in observed_sp:
                        dup_per_branch[ref_branch.nid].append([seqs_left, seqs_right])
                        __seed = True
                    elif not USE_COLLATERAL:
                        coll_dup_per_branch[ref_branch.nid].append([seqs_left, seqs_right])
                        __seed = False
                        
            # Count losses observed after a duplication or at the root of the tree.
            if isdup or node is t:
                # get a list of losses at both sides of the dupli
                if not isdup and node is t:
                    losses_left = get_lost_branches(observed_sp, expected_sp,
                                                    ref_branch, sorted_ref_branches)
                    losses_right = []
                else:
                    losses_left = get_lost_branches(species_left, expected_sp,
                                                    ref_branch, sorted_ref_branches)
                    losses_right = get_lost_branches(species_right, expected_sp,
                                                     ref_branch, sorted_ref_branches)

                if IS_VALID_TREEID is not None:
                    losses_left = [branch for branch in losses_left if IS_VALID_TREEID(treeid, extract_species(reftree_content[branch]))]
                    losses_right = [branch for branch in losses_right if IS_VALID_TREEID(treeid, extract_species(reftree_content[branch]))]
                    
                if USE_COLLATERAL:
                    losses = losses_left + losses_right
                    coll_losses = []
                else:
                    if treeid in seqs_left:
                        # if the seed species is not found at the other side of
                        # the dup, we can assume that its losses will never be
                        # counted, so we combine data from both sides.
                        if seedsp not in species_right: 
                            losses = losses_left + losses_right
                        # otherwise, we wait for info for a different seed tree
                        else: 
                            losses = losses_left
                        # No collateral information as data come from a duplication including the seed
                        coll_losses = [] 
                    elif treeid in seqs_right:
                        # if the seed species is not found at the other side of
                        # the dup, we can assume that its losses will never be
                        # counted, so we combine data from both sides.
                        if seedsp not in species_left: 
                            losses = losses_left + losses_right
                        # otherwise, we wait for info for a different seed tree
                        else:
                            losses = losses_right
                        # No collateral information as data come from a duplication including the seed
                        coll_losses = [] 
                    else:
                        # If this is a collateral duplication, process losses as such
                        losses = []
                        coll_losses = losses_left + losses_right

                if len(reftree_content[ref_branch]) == 1 and losses + coll_losses:
                    raw_input("This should never happen")
                    
                # update gene loss counters
                for lost_branch in losses:
                    losses_per_branch[lost_branch.nid] += 1
                    if isdup: # if losses come from a dup event
                        losses_per_dup_branch[ref_branch.nid].append(lost_branch)
                for lost_branch in coll_losses:
                    coll_losses_per_branch[lost_branch.nid] += 1
                    if isdup: # if losses come from a dup event
                        coll_losses_per_dup_branch[ref_branch.nid].append(lost_branch)

    return (informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
            coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch, coll_refbranch_supports)
        
def get_supported_branches(source_tree, reftree, refclades, seedid=None):
    """
        Given a reference species tree and a rooted gene tree in which
        duplication events are already mapped, this function does the following:
        
          - Split gene tree into all possible species tree (Treeko method)
          
          - Find matches between each subtree branch and all branches in the
            reference tree. 
          
              - Each branch in each species subtree is compared to all branches
                in the reftree. If left/right side of the subtree branch
                coincide with a the left/right side of a reference tree branch,
                this is considered a gene tree support point. Coincidences must
                comply with the following conditions:

                   - All species in the left/right sides of the subtree branch
                     exist in the left/right sides of the reference branch.

                   - Species in the left/right sides of the reference branch are
                     never mixed in the subtree branch.
                     
                   - Missing species are allowed in the subtree split, only if
                     such species are not present in any other part of the
                     original gene tree.
    """
    
    # Run Treeko to get all possible species tree combinations. We assume dups are already mapped
    ntrees, ndups, sp_trees = source_tree.get_speciation_trees(autodetect_duplications=DETECT_DUPLICATIONS, newick_only=True)
    if ntrees > 100000:
        return {}, {}
        
    branches_found = []
    branch2supports = defaultdict(list)
    branch2coll_supports = defaultdict(list)
    for nw in sp_trees:
        # Use all treeko trees or only those subtrees containing the seed?
        if seedid and seedid not in nw:
            container = branch2coll_supports
        else:
            container = branch2supports
            
        subtree = PhyloTree(nw, sp_naming_function = extract_species)
        subtreenode2content = subtree.get_cached_content(store_attr="species")
        #set([phy3(_c.name) for _c in subtreenode2content[subtree]])
        all_sp_in_subtree = subtreenode2content[subtree]
        
        # Visit all nodes in the tree
        for n in subtree.traverse("preorder"):
            if not n.is_leaf():
                c1 = subtreenode2content[n.children[0]]
                c2 = subtreenode2content[n.children[1]]
                #branches_found.append([all_sp_in_subtree, c1, c2])

                for refnode, m1, m2 in refclades:
                    all_expected_sp = m1 | m2

                    # We add one supporting point to every observed split that coincides
                    # with a reference tree branch. This is, seqs in one side and seqs
                    # on the other side of the observed split matches a ref_tree branch
                    # without having extra seqs in any of the sides. However, we allow
                    # for split matches where some seqs are lost in the observed split.
                    
                    #for all_sp_in_subtree, c1, c2 in branches_found:
                    all_seen_sp = c1|c2
                    notfound, found = 0, 0

                    false_missing = (all_expected_sp - all_seen_sp) & all_sp_in_subtree
                    outside_species = (all_seen_sp - all_expected_sp)

                    # Compare expected (m1,m2) splits with observed splits (c1,c2). 
                    a_straight  = m1 & c1
                    b_straight = m2 & c2
                    a_cross = m1 & c2
                    b_cross = m2 & c1

                    # if matches are found for one of the first possible comparison
                    if (a_straight and b_straight):
                        # and the match contains all the observed species, species
                        # from both sides are not mixed and missing species are real
                        if not outside_species and not a_cross and not b_cross and not false_missing:
                            found += 1
                        else:
                            notfound += 1

                    # if matches are found for the second possible comparison (This
                    # would never occur if found variable was increased in the
                    # previous if)
                    if (a_cross and b_cross):
                        # and the match contains all the observed species, species
                        # from both sides are not mixed and missing species are real
                        if not outside_species and not a_straight and not b_straight and not false_missing:
                            found += 1
                        else:
                            notfound += 1

                    if notfound > 0:
                        container[refnode].append(0)
                    elif found > 0:
                        container[refnode].append(1)                    

                    if found == 2:
                        raw_input("Two possible matches? This should never occur!!")
                
    return branch2supports, branch2coll_supports

def dup_iterator(fname):
    for line in open(fname):
        if line.startswith("#") or not line.strip(): continue
        treeid, left, right = map(strip, line.split("\t"))
        seqs_left = set(map(strip, left.split(",")))
        seqs_right = set(map(strip, right.split(",")))
        yield seqs_left, seqs_right, treeid

def extract_species(seq_names):
    if isinstance(seq_names, Tree):
        return seq_names.name.split(SPNAME_DELIMITER)[SPNAME_FIELD]
    elif isinstance(seq_names, str):
        return seq_names.split(SPNAME_DELIMITER)[SPNAME_FIELD]
    else:
        return set(map(lambda name: name.split(SPNAME_DELIMITER)[SPNAME_FIELD], seq_names))
        
def tree_iterator(fname, restrict_species=None, start_line=None, end_line=None):
    for ln, line in enumerate(open(fname)):
        if start_line is not None and ln < start_line:
            continue
        elif end_line is not None and ln >= end_line:
            break

        if line.startswith("#") or not line.strip(): continue
        treeid, newick = line.split("\t")
        t = PhyloTree(newick, sp_naming_function=extract_species)
        if restrict_species:
            t.prune([n for n in t.iter_leaves() if n.species in restrict_species])

        n2content = t.get_cached_content()
        if len(n2content[t]) < 2:
            continue
        yield treeid, t, n2content

def info_layout(node):
    summary_features = [
        "ntrees",
        "nid",
        "ndups",
        "dup_rate",
        "losses",
        "losses_rate",
        "nduplosses",
        "duplosses_rate",
        "gt_support",
        "nsupport_trees",
        "coll_ndups",
        "coll_dup_rate",
        "coll_losses",
        "coll_losses_rate",
        "coll_nduplosses",
        "coll_duplosses_rate",
        "coll_gt_support",
        "coll_nsupport_trees"]

    for f in summary_features:
        if hasattr(node, f):
            try:
                setattr(node, f, float(getattr(node, f)))
            except:
                setattr(node, f, None)
        else:
            setattr(node, f, None)
            
    if node.ndups is not None:
        add_face_to_node(faces.TextFace("Dups=%d(%0.2g dup/tree)" %(node.ndups, node.dup_rate),
                                        fsize=8, fgcolor="orange"), node, 2, position="branch-bottom")
    if node.losses is not None:
        add_face_to_node(faces.TextFace("Losses=%d(%0.2g losses/tree)" %(node.losses, node.losses_rate),
                                    fsize=8, fgcolor="green"), node, 2, position="branch-bottom")

    if node.nduplosses is not None:
        add_face_to_node(faces.TextFace("dupLosses=%d(%0.2g losses/tree)" %(node.nduplosses, node.duplosses_rate),
                                        fsize=8, fgcolor="blue"), node, 2, position="branch-bottom")
    if node.gt_support is not None:
        add_face_to_node(faces.TextFace("GTsupport=%g" %(node.gt_support),
                                        fsize=8, fgcolor="black"), node, 1, position="branch-top")
    if node.nsupport_trees is not None:
        add_face_to_node(faces.TextFace("GTtrees=%d" %(node.nsupport_trees),
                                        fsize=8, fgcolor="grey"), node, 1, position="branch-top")
       
    if node.ntrees is not None:
        add_face_to_node(faces.TextFace("nTrees=%d" %(node.ntrees),
                                        fsize=8, fgcolor="green"), node, 1, position="branch-top")


    # Collateral info
    if node.coll_ndups is not None:
        add_face_to_node(faces.TextFace("Coll_Dups=%d(%0.2g dup/tree)" %(node.coll_ndups, node.coll_dup_rate),
                                        fsize=8, fgcolor="orange"), node, 2, position="branch-bottom")
    if node.coll_losses is not None:
        add_face_to_node(faces.TextFace("Coll_Losses=%d(%0.2g losses/tree)" %(node.coll_losses, node.coll_losses_rate),
                                   fsize=8, fgcolor="green"), node, 2, position="branch-bottom")

    if node.coll_nduplosses is not None:
        add_face_to_node(faces.TextFace("Coll_dupLosses=%d(%0.2g losses/tree)" %(node.coll_nduplosses, node.coll_duplosses_rate),
                                        fsize=8, fgcolor="blue"), node, 2, position="branch-bottom")
    if node.coll_gt_support is not None:
        add_face_to_node(faces.TextFace("Coll_GTsupport=%g" %(node.coll_gt_support),
                                        fsize=8, fgcolor="black"), node, 1, position="branch-top")
    if node.coll_nsupport_trees is not None:
        add_face_to_node(faces.TextFace("Coll_GTtrees=%d" %(node.coll_nsupport_trees),
                                        fsize=8, fgcolor="grey"), node, 1, position="branch-top")
    



        
def annotate_tree(reftree, informed_branches, dup_per_branch, losses_per_branch,
                  losses_per_dup_branch, refbranch_supports,
                  coll_dup_per_branch, coll_losses_per_branch,
                  coll_losses_per_dup_branch, coll_refbranch_supports):
        
    for refbranch_node in reftree.traverse():
        refbranch = refbranch_node.nid
            
        ntrees = informed_branches.get(refbranch, 0)
        dups = dup_per_branch.get(refbranch, [])
        ndups = len(dups) if ntrees else None
        dup_rate = ndups / float(ntrees) if ntrees else None
        losses = losses_per_branch.get(refbranch, 0) if ntrees else None
        losses_rate = losses / float(ntrees) if ntrees else None
        duplosses = losses_per_dup_branch.get(refbranch, [])
        nduplosses = len(duplosses) if ntrees else None
        duplosses_rate = nduplosses / float(ntrees) if ntrees else None
        all_supports = refbranch_supports.get(refbranch, None)
        gt_support = numpy.mean(all_supports) if all_supports else None
        nsupport_trees = len(all_supports) if all_supports else None
        
        refbranch_node.add_features(ntrees=ntrees, dups=dups, ndups=ndups, dup_rate=dup_rate,
                               losses=losses, losses_rate=losses_rate,
                               duplosses=duplosses,
                               nduplosses=nduplosses,
                               duplosses_rate=duplosses_rate,
                               gt_support=gt_support,
                               nsupport_trees=nsupport_trees)

        coll_dups = coll_dup_per_branch.get(refbranch, [])
        coll_ndups = len(coll_dups) if ntrees else None
        coll_dup_rate = coll_ndups / float(ntrees) if ntrees else None
        coll_losses = coll_losses_per_branch.get(refbranch, 0) if ntrees else None
        coll_losses_rate = coll_losses / float(ntrees) if ntrees else None
        coll_duplosses = coll_losses_per_dup_branch.get(refbranch, [])
        coll_nduplosses = len(coll_duplosses) if ntrees else None
        coll_duplosses_rate = coll_nduplosses / float(ntrees) if ntrees else None
        coll_all_supports = coll_refbranch_supports.get(refbranch, None)
        coll_gt_support = numpy.mean(coll_all_supports) if coll_all_supports else None
        coll_nsupport_trees = len(coll_all_supports) if coll_all_supports else None
       
        refbranch_node.add_features(coll_dups=coll_dups, coll_ndups=coll_ndups, coll_dup_rate=coll_dup_rate,
                               coll_losses=coll_losses, coll_losses_rate=coll_losses_rate, coll_duplosses=coll_duplosses,
                               coll_nduplosses=coll_nduplosses,
                               coll_duplosses_rate=coll_duplosses_rate,
                               coll_gt_support=coll_gt_support,
                               coll_nsupport_trees=coll_nsupport_trees)

        # if refbranch == 5:
        #     print refbranch_node.ndups
        #     print refbranch_node.coll_ndups
        #     print CHICK

    
def run_parallel(workernum, queue, f, *args, **kargs):
    kargs["thread_name"] = "Worker%02d" % workernum
    r = f(*args, **kargs)
    #print "Worker done:", workernum, r
    #print
    
    queue.put(r)

    
def dump_results(reftree, informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
                 coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch, coll_refbranch_supports):
        
    # FInal annotation of the refTree
    annotate_tree(reftree, informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
                   coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch, coll_refbranch_supports)
    # Summary newick tree with all features
    if IMG_REPORT:
        print >>sys.stderr, "Generating tree analysis image"
        ts = TreeStyle()
        ts.layout_fn = info_layout
        reftree.render("%s.tree_analysis.png"%args.output, tree_style=ts)
    
    summary_fetaures = [
        "ntrees",
        "nid",
        "ndups",
        "dup_rate",
        "losses",
        "losses_rate",
        "nduplosses",
        "duplosses_rate",
        "gt_support",
        "nsupport_trees",
        "coll_ndups",
        "coll_dup_rate",
        "coll_losses",
        "coll_losses_rate",
        "coll_nduplosses",
        "coll_duplosses_rate",
        "coll_gt_support",
        "coll_nsupport_trees"]
    
    print >>sys.stderr, "Dumping annotated newick..."
    reftree.write(outfile="%s.nwx"%args.output, features=summary_fetaures)
    open("%s.log"%args.output, "w").write(' '.join(sys.argv))

def main(argv):
    global args

    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)

    
    parser.add_argument("-r", dest="reftree", 
                        type=str, required=True,
                        help="""Reference tree""")
    
    parser.add_argument("--source_trees", dest="source_trees", 
                        type=str, required = True,
                        help=("A list of *rooted* genetrees, one per line, in the format: TreeID/SeedID [TAB] newick "))
   
    parser.add_argument("--plot_newick", dest="plot_newick", 
                        type=str,
                        help=(""))
    
    parser.add_argument("--spname_delimiter", dest="spname_delimiter", 
                        type=str, default="_",
                        help=("species code delimiter in node names"))
    
    parser.add_argument("--spname_field", dest="spname_field", 
                        type=int, default=-1,
                        help=("position of the species code extracted from node names. -1 = last field"))

    parser.add_argument("--collateral", dest="use_collateral", 
                        action="store_true",
                        help=("If enabled, collateral information will be used as"
                              " equally qualified data. Otherwise, such data will"
                              " be reported separatedly. Use this if your set of"
                              " trees are not overlaping. "))

    parser.add_argument("--skip_dup_detection", dest="skip_dup_detection", 
                        action="store_true",
                        help=('If used, duplications will be expected to be annotated'
                              ' in the source gene trees with the evoltype="D" tag.'
                              ' Otherwise they will be inferred on the fly using'
                              ' the species overlap algorithm.'))

    parser.add_argument("--spoverlap", dest="species_overlap", 
                        type=float, default=0.0,
                        help=("Species overlap cutoff. A number between 0 and 1 "
                        "representing the percentage of species that should be "
                        "shared between two sister partitions to be considered a"
                        " duplication. 0 = any overlap represents a duplication. "))
    
    parser.add_argument("--debug", dest="debug", 
                        action="store_true",
                        help=("generate an image of every input gene tree tree, so the result can be inspected"))

    parser.add_argument("--snapshot_step", dest="snapshot_step", 
                        type=int, default=1000,
                        help=("How many trees should be processed between snapshots dumps?"))

    parser.add_argument("--reftree_constraint", dest="reftree_constraint", 
                        type=str, 
                        help=("A python module from from which a function called "
                              "*is_valid_treeid(treeid, refbranch)* should be importable. "
                              "The function will be used to decide if the info of a given "
                              "source tree is informative or not for each reftree branch. "))
    
    parser.add_argument("-o", dest="output", 
                        type=str, required=True, 
                        help=("output tag name (extensions will be added)"))

    parser.add_argument("--cpu", dest="cpu", 
                        type=int, default=1, 
                        help=("enable parallel computation"))

    parser.add_argument("--img_report", dest="img_report", 
                        action="store_true", 
                        help=("If true, it generates a summary image results with all the computed data"))

    parser.add_argument("--report_supports", dest="report_supports", 
                        action="store_true", 
                        help=("If used, supported ref tree branches are individually reported for each gene tree "))

    
    args = parser.parse_args(argv)
    if args.plot_newick:
        t = Tree(args.plot_newick)
        ts = TreeStyle()
        ts.layout_fn = info_layout
        t.render("tree_analysis.png", tree_style=ts)
        sys.exit(0)
    
    SPNAME_FIELD, SPNAME_DELIMITER = args.spname_field, args.spname_delimiter
    USE_COLLATERAL = args.use_collateral
    DETECT_DUPLICATIONS = True if not args.skip_dup_detection else False
    REPORT_PER_TREE_SUPPORTS = True if args.report_supports  else False
    SP_OVERLAP = args.species_overlap
    DEBUG = args.debug
    IMG_REPORT = args.img_report
    reftree = PhyloTree(args.reftree, sp_naming_function=None)
    for nid, n in enumerate(reftree.traverse()):
        n.add_features(nid = nid)
    REFTREE_SPECIES = set(reftree.get_leaf_names())
    print __DESCRIPTION__

    if REPORT_PER_TREE_SUPPORTS:
        REPORT_SUPPORT_FILE = open("%s.gentree_supports" %args.output, "w")
        print >>REPORT_SUPPORT_FILE, '#'+'\t'.join(map(str, ["treeId", "spCoverage", "mean_support",  "mean_coll_support", "tested_branches", 'tested_coll_branches']))
    
    TOTAL_TREES = int(commands.getoutput("wc -l %s" %args.source_trees).split()[0]) + 1
    print >>sys.stderr, "Processing %d source trees" %TOTAL_TREES
    if args.reftree_constraint:
        import imp
        constraint = imp.load_source('constraint', args.reftree_constraint)
        IS_VALID_TREEID = constraint.is_valid_treeid
    else:
        IS_VALID_TREEID = None
       
    if args.cpu > 1:
        MONITOR_STEP = 0
        #return (informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
        #       coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch, coll_refbranch_supports)
        # The output of the process_trees function are 9 dictionaries in which keys are refbranches
        target_dicts = [{} for x in range(9)] 
        def merge_dict_results(target, source):
            def merge_dict(target, source):
                for k, v in source.iteritems():
                    if k not in target:
                        target[k] = v
                    elif isinstance(v, list):
                        target[k].extend(v)
                    elif isinstance(v, set):
                        target[k].update(v)
                    elif isinstance(v, int):
                        target[k] += v
                    else:
                        raise ValueError("Impossible to merge str results")
            for index in xrange(len(target)):
                merge_dict(target[index], out[index])

        from multiprocessing import Process, Queue
        from Queue import Empty as QueueEmpty
        outputs_queue = Queue()
        if TOTAL_TREES > args.cpu:
            trees_per_cpu = TOTAL_TREES / args.cpu
            trees_per_cpu += 1 if TOTAL_TREES % args.cpu else 0
        else:
            trees_per_cpu = 1
            args.cpu = TOTAL_TREES
            
        all_workers = set()
        for cpu_num in xrange(args.cpu):
            sline = (cpu_num*trees_per_cpu)
            eline = (cpu_num*trees_per_cpu) + trees_per_cpu
            data_iter = tree_iterator(args.source_trees,
                                      restrict_species=REFTREE_SPECIES,
                                      start_line=sline,
                                      end_line=eline)
            print >>sys.stderr, "Launching worker %d from %d to %d" %(cpu_num, sline, eline)
            worker = Process(target=run_parallel,
                             args=(cpu_num, outputs_queue, process_trees, data_iter, reftree, trees_per_cpu))
            worker.name = "Worker_%d" %cpu_num
            all_workers.add(worker)
            worker.start()
            
        while all_workers:
            # clear done threads
            for w in list(all_workers):
                if not w.is_alive():
                    print >>sys.stderr, "%s thread is done!" %w.name
                    all_workers.discard(w)
            # get and merge results
            while 1:
                try:
                    out = outputs_queue.get(False)
                except QueueEmpty:
                    break
                else:
                    # This merge depends on process_trees return output!!!!!
                    merge_dict_results(target_dicts, out)
                    # Dump a snapshot
                    dump_results(reftree, *target_dicts)
                time.sleep(0.1)
            if all_workers:
                time.sleep(1)
        # collected data
        (informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
         coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch,
         coll_refbranch_supports) = target_dicts
    else:
        MONITOR_STEP = args.snapshot_step
        data_iter = tree_iterator(args.source_trees, restrict_species=REFTREE_SPECIES)
        
        (informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
         coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch,
         coll_refbranch_supports) = process_trees(data_iter, reftree, TOTAL_TREES)

    if REPORT_PER_TREE_SUPPORTS:
        REPORT_SUPPORT_FILE.close()

    dump_results(reftree, informed_branches, dup_per_branch, losses_per_branch, losses_per_dup_branch, refbranch_supports,
                 coll_dup_per_branch, coll_losses_per_branch, coll_losses_per_dup_branch, coll_refbranch_supports)

    print >>sys.stderr, "Dumping full analysis..."
    # Full dump, including duplication details
    cPickle.dump(reftree, open("%s.pkl"%args.output, "w"))
   
    
if __name__ == '__main__':
    main(sys.argv[1:])
