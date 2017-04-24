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
import re
from subprocess import check_output
import logging

from ..task import TreeMerger, Msf, DummyTree, ManualAlg
from ..errors import DataError
from ..utils import (GLOBALS, rpath, pjoin, pexist, generate_runid,
                                  DATATYPES, GAP_CHARS, DEBUG, SeqGroup, _min, _max, _std, _mean, _median)
from .. import db
from ..master_task import register_task_recursively
from ..workflow.common import (IterConfig, get_next_npr_node,
                               process_new_tasks, get_iternumber)
from ..logger import logindent
import six
from six.moves import map
log = logging.getLogger("main")

def annotate_node(t, final_task):
    cladeid2node = {}
    # Annotate cladeid in the whole tree
    for n in t.traverse():
        if n.is_leaf():
            n.add_feature("realname", db.get_seq_name(n.name))
            #n.name = n.realname
        if hasattr(n, "cladeid"):
            cladeid2node[n.cladeid] = n

    alltasks = GLOBALS[final_task.configid]["_nodeinfo"][final_task.nodeid]["tasks"]
    npr_iter = get_iternumber(final_task.threadid)
    n = cladeid2node[t.cladeid]
    n.add_features(size=final_task.size)
    for task in alltasks:
        params = ["%s %s" %(k,v) for k,v in  six.iteritems(task.args)
                  if not k.startswith("_")]
        params = " ".join(params)

        if task.ttype == "msf":
            n.add_features(msf_outseqs=task.out_seqs,
                           msf_file=task.multiseq_file)

        elif task.ttype == "acleaner":
            n.add_features(clean_alg_mean_ident=task.mean_ident,
                           clean_alg_std_ident=task.std_ident,
                           clean_alg_max_ident=task.max_ident,
                           clean_alg_min_ident=task.min_ident,
                           clean_alg_type=task.tname,
                           clean_alg_cmd=params,
                           clean_alg_path=task.clean_alg_fasta_file)
        elif task.ttype == "alg":
            n.add_features(alg_mean_ident=task.mean_ident,
                           alg_std_ident=task.std_ident,
                           alg_max_ident=task.max_ident,
                           alg_min_ident=task.min_ident,
                           alg_type=task.tname,
                           alg_cmd=params,
                           alg_path=task.alg_fasta_file)

        elif task.ttype == "tree":
            n.add_features(tree_model=task.model,
                           tree_seqtype=task.seqtype,
                           tree_type=task.tname,
                           tree_cmd=params,
                           tree_path=task.tree_file,
                           tree_constrain=task.constrain_tree,
                           tree_phylip_alg=task.alg_phylip_file,
                           npr_iter=npr_iter)
        elif task.ttype == "mchooser":
            n.add_features(modeltester_models=task.models,
                           modeltester_type=task.tname,
                           modeltester_params=params,
                           modeltester_bestmodel=task.best_model,
                           )
        elif task.ttype == "treemerger":
            n.add_features(treemerger_type=task.tname,
                           treemerger_rf="RF=%s [%s]" %(task.rf[0], task.rf[1]),
                           treemerger_out_match_dist = task.outgroup_match_dist,
                           treemerger_out_match = task.outgroup_match,
            )

def get_trimal_conservation(alg_file, trimal_bin):
    output = bytes.decode(check_output("%s -ssc -in %s" % (trimal_bin,
                                                    alg_file), shell=True))
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = list(map(float, line.split()))
        conservation.append(b)
    mean = _mean(conservation)
    std = _std(conservation)
    return mean, std


def get_statal_identity(alg_file, statal_bin):
    output = bytes.decode(check_output("%s -scolidentt -in %s" % (statal_bin, alg_file), shell=True))

    ## Columns Identity Descriptive Statistics
    #maxColIdentity	1
    #minColIdentity	0.428571
    #avgColIdentity	0.781853
    #stdColIdentity	0.2229
    #print output

    maxi, mini, avgi, stdi = [None] * 4
    for line in output.splitlines():
        if line.startswith("#maxColIdentity"):
            maxi = float(line.split()[1])
        elif line.startswith("#minColIdentity"):
            mini = float(line.split()[1])
        elif line.startswith("#avgColIdentity"):
            avgi = float(line.split()[1])
        elif line.startswith("#stdColIdentity"):
            stdi = float(line.split()[1])
            break
    return maxi, mini, avgi, stdi


def get_trimal_identity(alg_file, trimal_bin):
    #print "%s -sident -in %s" %\
    #    (trimal_bin, alg_file)
    output = byets.decode(check_output("%s -sident -in %s" %\
                                    (trimal_bin, alg_file), shell=True))
    #print output
    conservation = []
    for line in output.split("\n"):
        m = re.search("#MaxIdentity\s+(\d+\.\d+)", line)
        if m:
            max_identity = float(m.groups()[0])
    return max_identity

def switch_to_codon(alg_fasta_file,  kept_columns=None):
    # Check conservation of columns. If too many identities,
    # switch to codon alignment and make the tree with DNA.
    # Mixed models is another possibility.
    if kept_columns:
        kept_columns = set(map(int, kept_columns))
    else:
        kept_columns = []

    #all_nt_alg = SeqGroup(nt_seed_file)
    aa_alg = SeqGroup(alg_fasta_file)
    nt_alg = SeqGroup()

    for seqname, aaseq, comments in aa_alg.iter_entries():
        #ntseq = all_nt_alg.get_seq(seqname).upper()
        ntseq = db.get_seq(seqname, "nt").upper()
        ntalgseq = []
        nt_pos = 0
        for pos, ch in enumerate(aaseq):
            if ch in GAP_CHARS:
                codon = "---"
            else:
                codon = ntseq[nt_pos:nt_pos+3]
                nt_pos += 3

            if not kept_columns or pos in kept_columns:
                # we trust the sequence in DB, consistency should have been
                # checked during the start up
                ntalgseq.append(codon)

        ntalgseq = "".join(ntalgseq)
        nt_alg.set_seq(seqname, ntalgseq)

    return nt_alg

def process_task(task, wkname, npr_conf, nodeid2info):
    alignerconf, alignerclass = npr_conf.aligner
    cleanerconf, cleanerclass = npr_conf.alg_cleaner
    mtesterconf, mtesterclass = npr_conf.model_tester
    treebuilderconf, treebuilderclass = npr_conf.tree_builder
    if not treebuilderclass:
        # Allows to dump algs in workflows with no tree tasks
        treebuilderclass = DummyTree

    splitterconf, splitterclass = npr_conf.tree_splitter

    conf = GLOBALS[task.configid]
    seqtype = task.seqtype
    nodeid = task.nodeid
    ttype = task.ttype
    taskid = task.taskid
    threadid = task.threadid
    node_info = nodeid2info[nodeid]
    size = task.size#node_info.get("size", 0)
    target_seqs = node_info.get("target_seqs", [])
    out_seqs = node_info.get("out_seqs", [])

    if not treebuilderclass or size < 4:
        # Allows to dump algs in workflows with no tree tasks or if tree
        # inference does not make sense given the number of sequences. DummyTree
        # will produce a fake fully collapsed newick tree.
        treebuilderclass = DummyTree
        mtesterclass = None


    # If more than one outgroup are used, enable the use of constrain
    if out_seqs and len(out_seqs) > 1:
        constrain_id = nodeid
    else:
        constrain_id = None

    new_tasks = []
    if ttype == "msf":
        # Register Tree constrains
        constrain_tree = "(%s, (%s));" %(','.join(sorted(task.out_seqs)),
                                         ','.join(sorted(task.target_seqs)))
        _outs = "\n".join([">%s\n0" %name for name in sorted(task.out_seqs)])
        _tars = "\n".join([">%s\n1" %name for name in sorted(task.target_seqs)])
        constrain_alg = '\n'.join([_outs, _tars])
        db.add_task_data(nodeid, DATATYPES.constrain_tree, constrain_tree)
        db.add_task_data(nodeid, DATATYPES.constrain_alg, constrain_alg)
        db.dataconn.commit() # since the creation of some Task
                               # objects may require this info, I need
                               # to commit right now.

        # Register node
        db.add_node(task.threadid,
                    task.nodeid, task.cladeid,
                    task.target_seqs,
                    task.out_seqs)

        nodeid2info[nodeid]["size"] = task.size
        nodeid2info[nodeid]["target_seqs"] = task.target_seqs
        nodeid2info[nodeid]["out_seqs"] = task.out_seqs
        
        if alignerclass:
            alg_task = alignerclass(nodeid, task.multiseq_file,
                                    seqtype, conf, alignerconf)
        else:
            log.warning("Skipping alignment phase, using original sequences")
            alg_task = ManualAlg(nodeid, task.multiseq_file,
                                 seqtype, conf, alignerconf)
            
        alg_task.size = task.size
        new_tasks.append(alg_task)


    elif ttype == "alg" or ttype == "acleaner":
        if ttype == "alg":
            nodeid2info[nodeid]["alg_path"] = task.alg_fasta_file
        elif ttype == "acleaner":
            nodeid2info[nodeid]["alg_clean_path"] = task.clean_alg_fasta_file

        alg_fasta_file = getattr(task, "clean_alg_fasta_file",
                                 task.alg_fasta_file)
        alg_phylip_file = getattr(task, "clean_alg_phylip_file",
                                  task.alg_phylip_file)

        # Calculate alignment stats
        # cons_mean, cons_std = get_trimal_conservation(task.alg_fasta_file,
        #                                        conf["app"]["trimal"])
        #
        # max_identity = get_trimal_identity(task.alg_fasta_file,
        #                                 conf["app"]["trimal"])
        # log.info("Conservation: %0.2f +-%0.2f", cons_mean, cons_std)
        # log.info("Max. Identity: %0.2f", max_identity)
        #import time
        #t1 = time.time()
        #mx, mn, mean, std = get_identity(task.alg_fasta_file)
        #print time.time()-t1
        #log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
        #        mx, mn, mean, std)
        #t1 = time.time()

        if seqtype == "aa" and npr_conf.switch_aa_similarity < 1:
            try:
                alg_stats = db.get_task_data(taskid, DATATYPES.alg_stats)
            except Exception as e:
                alg_stats = {}

            if ttype == "alg":
                algfile = pjoin(GLOBALS["input_dir"], task.alg_phylip_file)
                dataid = DATATYPES.alg_phylip
            elif ttype == "acleaner":
                algfile = pjoin(GLOBALS["input_dir"], task.clean_alg_phylip_file)
                dataid = DATATYPES.clean_alg_phylip

            if "i_mean" not in alg_stats:
                log.log(24, "Calculating alignment stats...")
                # dump data if necesary
                algfile = pjoin(GLOBALS["input_dir"], task.alg_phylip_file)
                if not pexist(algfile):
                    # dump phylip alg
                    open(algfile, "w").write(db.get_data(db.get_dataid(taskid, dataid)))

                mx, mn, mean, std = get_statal_identity(algfile,
                                                        conf["app"]["statal"])
                alg_stats = {"i_max":mx, "i_mean":mean, "i_min":mn, "i_std":std}
                db.add_task_data(taskid, DATATYPES.alg_stats, alg_stats)

            log.log(22, "Alignment stats (sequence similarity):")
            log.log(22, "   max: %(i_max)0.2f, min:%(i_min)0.2f, avg:%(i_mean)0.2f+-%(i_std)0.2f" %
                    (alg_stats))

        else:
            alg_stats = {"i_max":-1, "i_mean":-1, "i_min":-1, "i_std":-1}

        #print time.time()-t1
        #log.log(24, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
        #        mx, mn, mean, std)
        task.max_ident = alg_stats["i_max"]
        task.min_ident = alg_stats["i_min"]
        task.mean_ident = alg_stats["i_mean"]
        task.std_ident = alg_stats["i_std"]
        next_task = None

        if ttype == "alg" and cleanerclass:
            next_task = cleanerclass(nodeid, seqtype, alg_fasta_file,
                                     alg_phylip_file,
                                     conf, cleanerconf)
        else:
            # Converts aa alignment into nt if necessary
            if  seqtype == "aa" and \
                    "nt" in GLOBALS["seqtypes"] and \
                    task.mean_ident >= npr_conf.switch_aa_similarity:
                log.log(28, "@@2:Switching to codon alignment!@@1: amino-acid sequence similarity: %0.2f >= %0.2f" %\
                        (task.mean_ident, npr_conf.switch_aa_similarity))
                alg_fasta_file = "%s.%s" %(taskid, DATATYPES.alg_nt_fasta)
                alg_phylip_file = "%s.%s" %(taskid, DATATYPES.alg_nt_phylip)
                try:
                    alg_fasta_file = db.get_dataid(taskid, DATATYPES.alg_nt_fasta)
                    alg_phylip_file = db.get_dataid(taskid, DATATYPES.alg_nt_phylip)
                except ValueError:
                    log.log(22, "Calculating codon alignment...")

                    source_alg = pjoin(GLOBALS["input_dir"], task.alg_fasta_file)
                    if ttype == "alg":
                        kept_columns = []
                    elif ttype == "acleaner":
                        # if original alignment was trimmed, use it as reference
                        # but make the nt alignment only on the kept columns
                        kept_columns = db.get_task_data(taskid, DATATYPES.kept_alg_columns)

                    if not pexist(source_alg):
                        open(source_alg, "w").write(db.get_task_data(taskid, DATATYPES.alg_fasta))

                    nt_alg = switch_to_codon(source_alg, kept_columns=kept_columns)
                    
                    db.add_task_data(taskid, DATATYPES.alg_nt_fasta, nt_alg.write())
                    db.add_task_data(taskid, DATATYPES.alg_nt_phylip, nt_alg.write(format='iphylip_relaxed'))

                npr_conf = IterConfig(conf, wkname, task.size, "nt")
                seqtype = "nt"
                
                # This is necessary for connecting to supermatrix workflows
                task.alg_nt_fasta_file = alg_fasta_file
                task.alg_nt_phylip_file = alg_phylip_file
                    

            if mtesterclass:
                next_task = mtesterclass(nodeid, alg_fasta_file,
                                         alg_phylip_file,
                                         constrain_id, seqtype,
                                         conf, mtesterconf)
            elif treebuilderclass:
                next_task = treebuilderclass(nodeid, alg_phylip_file,
                                             constrain_id,
                                             None, seqtype,
                                             conf, treebuilderconf)
        if next_task:
            next_task.size = task.size
            new_tasks.append(next_task)

    elif ttype == "mchooser":
        if treebuilderclass:
            alg_fasta_file = task.alg_fasta_file
            alg_phylip_file = task.alg_phylip_file
            model = task.best_model
            tree_task = treebuilderclass(nodeid, alg_phylip_file,
                                         constrain_id,
                                         model, seqtype,
                                         conf, treebuilderconf)
            tree_task.size = task.size
            if task.seqtype != seqtype:
                tree_task.alg_phylip_file = task.alg_phylip_file
            new_tasks.append(tree_task)

    elif ttype == "tree":
        treemerge_task = splitterclass(nodeid, seqtype,
                                       task.tree_file, conf, splitterconf)
            #if conf["tree_splitter"]["_outgroup_size"]:
            #    treemerge_task = TreeSplitterWithOutgroups(nodeid, seqtype, task.tree_file, main_tree, conf)
            #else:
            #    treemerge_task = TreeSplitter(nodeid, seqtype, task.tree_file, main_tree, conf)

        treemerge_task.size = task.size
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        if not task.task_tree:
            task.finish()

        log.log(24, "Saving task tree...")
        annotate_node(task.task_tree, task)
        db.update_node(nid=task.nodeid,
                       runid=task.threadid,
                       newick=db.encode(task.task_tree))
        db.commit()

        if not isinstance(treebuilderclass, DummyTree) and npr_conf.max_iters > 1:
            current_iter = get_iternumber(threadid)
            if npr_conf.max_iters and current_iter >= npr_conf.max_iters:
                log.warning("Maximum number of iterations reached!")
            else:
                # Add new nodes
                source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
                ttree, mtree = task.task_tree, task.main_tree
                log.log(26, "Processing tree: %s seqs, %s outgroups",
                        len(target_seqs), len(out_seqs))
                alg_path = node_info.get("clean_alg_path", node_info["alg_path"])
                for node, seqs, outs, wkname in get_next_npr_node(threadid, ttree,
                                                          task.out_seqs, mtree,
                                                          alg_path, npr_conf):
                    log.log(24, "Registering new node: %s seqs, %s outgroups",
                            len(seqs), len(outs))
                    new_task_node = Msf(seqs, outs, seqtype=source_seqtype)
                    new_task_node.target_wkname = wkname
                    new_tasks.append(new_task_node)
    return new_tasks

def pipeline(task, wkname, conf=None):
    logindent(2)

    if not task: # in this case, conf is expected
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        all_seqs = GLOBALS["target_sequences"]
        initial_task = Msf(set(all_seqs), set(),
                           seqtype=source_seqtype)

        initial_task.main_tree = None
        initial_task.threadid = generate_runid()
        initial_task.configid = initial_task.threadid
        initial_task.target_wkname = wkname
        # Register node
        db.add_node(initial_task.threadid, initial_task.nodeid,
                    initial_task.cladeid, initial_task.target_seqs,
                    initial_task.out_seqs)

        new_tasks = [initial_task]
    else:
        conf = GLOBALS[task.configid]
        npr_conf = IterConfig(conf, wkname, task.size, task.seqtype)
        new_tasks  = process_task(task, wkname, npr_conf, conf["_nodeinfo"])

    process_new_tasks(task, new_tasks, conf)
    logindent(-2)

    return new_tasks
