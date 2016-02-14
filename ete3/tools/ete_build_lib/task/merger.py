from __future__ import absolute_import
from __future__ import print_function
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
import logging
import os
import six
log = logging.getLogger("main")

from ..master_task import TreeMergeTask
from ..master_job import Job
from ..utils import (load_node_size, PhyloTree, SeqGroup, generate_id,
                          NPR_TREE_STYLE, NodeStyle, DEBUG,
                          faces, pjoin, GLOBALS)
from ..errors import ConfigError, TaskError
from .. import db

__all__ = ["TreeMerger"]

class TreeMerger(TreeMergeTask):
    def __init__(self, nodeid, seqtype, task_tree, conf, confname):
        # Initialize task
        self.confname = confname
        self.conf = conf
        self.task_tree_file = task_tree
        TreeMergeTask.__init__(self, nodeid, "treemerger", "TreeMerger",
                               None, self.conf[self.confname])

        self.main_tree = None
        self.task_tree = None
        self.seqtype = seqtype
        self.rf = None, None # Robinson foulds to orig partition
        self.outgroup_match_dist = 0.0
        self.outgroup_match = ""
        self.pre_iter_support = None # support of the node pre-iteration
        self.init()

    def finish(self):
        def euc_dist(x, y):
            return len(x.symmetric_difference(y)) / float((len(x) + len(y)))
        dataid = db.get_dataid(*self.task_tree_file.split("."))
        ttree = PhyloTree(db.get_data(dataid))
        mtree = self.main_tree
        ttree.dist = 0
        cladeid, target_seqs, out_seqs = db.get_node_info(self.threadid, self.nodeid)
        self.out_seqs = out_seqs
        self.target_seqs = target_seqs

        ttree_content = ttree.get_cached_content()
        if mtree and not out_seqs:
            mtree_content = mtree.get_cached_content()
            log.log(24, "Finding best scoring outgroup from previous iteration.")
            for _n in mtree_content:
                if _n.cladeid == cladeid:
                    orig_target = _n
            target_left = set([_n.name for _n in mtree_content[orig_target.children[0]]])
            target_right = set([_n.name for _n in mtree_content[orig_target.children[1]]])

            partition_pairs = []
            everything = set([_n.name for _n in ttree_content[ttree]])
            for n, content in six.iteritems(ttree_content):
                if n is ttree:
                    continue
                left = set([_n.name for _n in content])
                right =  everything - left
                d1 = euc_dist(left, target_left)
                d2 = euc_dist(left, target_right)
                best_match = min(d1, d2)
                partition_pairs.append([best_match, left, right, n])

            partition_pairs.sort()

            self.outgroup_match_dist = partition_pairs[0][0]
            #self.outgroup_match = '#'.join( ['|'.join(partition_pairs[0][1]),
            #                      '|'.join(partition_pairs[0][2])] )


            outgroup = partition_pairs[0][3]
            ttree.set_outgroup(outgroup)

            ttree.dist = orig_target.dist
            ttree.support = orig_target.support

            # Merge task and main trees
            parent = orig_target.up
            orig_target.detach()
            parent.add_child(ttree)

        elif mtree and out_seqs:
            log.log(26, "Rooting tree using %d custom seqs" %
                   len(out_seqs))

            self.outgroup_match = '|'.join(out_seqs)

            #log.log(22, "Out seqs:    %s", len(out_seqs))
            #log.log(22, "Target seqs: %s", target_seqs)
            if len(out_seqs) > 1:
                #first root to a single seqs outside the outgroup
                #(should never fail and avoids random outgroup split
                #problems in unrooted trees)
                ttree.set_outgroup(ttree & list(target_seqs)[0])
                # Now tries to get the outgroup node as a monophyletic clade
                outgroup = ttree.get_common_ancestor(out_seqs)
                if set(outgroup.get_leaf_names()) ^ out_seqs:
                    msg = "Monophyly of the selected outgroup could not be granted! Probably constrain tree failed."
                    #dump_tree_debug(msg, self.taskdir, mtree, ttree, target_seqs, out_seqs)
                    raise TaskError(self, msg)
            else:
                outgroup = ttree & list(out_seqs)[0]

            ttree.set_outgroup(outgroup)
            orig_target = self.main_tree.get_common_ancestor(target_seqs)
            found_target = outgroup.get_sisters()[0]

            ttree = ttree.get_common_ancestor(target_seqs)
            outgroup.detach()
            self.pre_iter_support = orig_target.support
            # Use previous dist and support
            ttree.dist = orig_target.dist
            ttree.support = orig_target.support
            parent = orig_target.up
            orig_target.detach()
            parent.add_child(ttree)

        else:
            # ROOTS FIRST ITERATION
            log.log(24, "Getting outgroup for first NPR split")

            # if early split is provided in the command line, it
            # overrides config file
            mainout = GLOBALS.get("first_split_outgroup", "midpoint")

            if mainout.lower() == "midpoint":
                log.log(26, "Rooting to midpoint.")
                best_outgroup = ttree.get_midpoint_outgroup()
                if best_outgroup:
                    ttree.set_outgroup(best_outgroup)
                else:
                    log.warning("Midpoint outgroup could not be set!")
                    ttree.set_outgroup(next(ttree.iter_leaves()))
            else:
                if mainout.startswith("~"):
                    # Lazy defined outgroup. Will trust in the common
                    # ancestor of two or more OTUs
                    strict_common_ancestor = False
                    outs = set(mainout[1:].split())
                    if len(outs) < 2:
                        raise TaskError(self, "First split outgroup error: common "
                                        "ancestor calculation requires at least two OTU names")
                else:
                    strict_common_ancestor = True
                    outs = set(mainout.split())

                if outs - target_seqs:
                    raise TaskError(self, "Unknown seqs cannot be used to set first split rooting:%s" %(outs - target_seqs))

                if len(outs) > 1:
                    anchor = list(set(target_seqs) - outs)[0]
                    ttree.set_outgroup(ttree & anchor)
                    common = ttree.get_common_ancestor(outs)
                    out_seqs = common.get_leaf_names()
                    if common is ttree:
                        msg = "First split outgroup could not be granted:%s" %out_seqs
                        #dump_tree_debug(msg, self.taskdir, mtree, ttree, target_seqs, outs)
                        raise TaskError(self, msg)
                    if strict_common_ancestor and set(out_seqs) ^ outs:
                        msg = "Monophyly of first split outgroup could not be granted:%s" %out_seqs
                        #dump_tree_debug(msg, self.taskdir, mtree, ttree, target_seqs, outs)
                        raise TaskError(self, msg)

                    log.log(26, "@@8:First split rooting to %d seqs@@1:: %s" %(len(out_seqs),out_seqs))
                    ttree.set_outgroup(common)
                else:
                    single_out = outs.pop()
                    common = ttree.set_outgroup(single_out)
                    log.log(26, "@@8:First split rooting to 1 seq@@1:: %s" %(single_out))

            self.main_tree = ttree
            orig_target = ttree

        tn = orig_target.copy()
        self.pre_iter_task_tree = tn
        self.rf = orig_target.robinson_foulds(ttree)
        self.pre_iter_support = orig_target.support

        # Reloads node2content of the rooted tree and generate cladeids
        ttree_content = self.main_tree.get_cached_content()
        for n, content in six.iteritems(ttree_content):
            cid = generate_id([_n.name for _n in content])
            n.add_feature("cladeid", cid)

        #ttree.write(outfile=self.pruned_tree)
        self.task_tree = ttree


def dump_tree_debug(msg, taskdir, mtree, ttree, target_seqs, out_seqs):
    try:
        if out_seqs is None: out_seqs = set()
        if target_seqs is None: target_seqs = set()
        if ttree:
            for n in ttree.get_leaves():
                if n.name in out_seqs:
                    n.name = n.name + " *__OUTGROUP__*"
        if mtree:
            for n in mtree.get_leaves():
                if n.name in out_seqs:
                    n.name = n.name + " *__OUTGROUP__*"
                if n.name in target_seqs:
                    n.name = n.name + " [ TARGET ]"

        OUT = open(pjoin(taskdir, "__debug__"), "w")
        print(msg, file=OUT)
        print("MainTree:", mtree, file=OUT)
        print("TaskTree:", ttree, file=OUT)
        print("Expected outgroups:", out_seqs, file=OUT)
        OUT.close()
    except Exception as e:
        print(e)


