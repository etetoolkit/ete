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
from collections import defaultdict

from ete2.tools.phylobuild_lib.task import TreeMerger, DummyTree
from ete2.tools.phylobuild_lib.utils import (GLOBALS, tobool, generate_runid, pjoin, rpath, DATATYPES, md5,
                          dict_string, ncbi, colorify)

from ete2.tools.phylobuild_lib.errors import DataError, TaskError
from ete2.tools.phylobuild_lib import db
from ete2.tools.phylobuild_lib.workflow.common import (process_new_tasks, IterConfig,
                                    get_next_npr_node, get_iternumber)
from ete2.tools.phylobuild_lib.logger import logindent

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
        params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                  if not k.startswith("_")]
        params = " ".join(params)

        if task.ttype == "tree":
            n.add_features(tree_model=task.model, 
                           tree_seqtype=task.seqtype, 
                           tree_type=task.tname, 
                           tree_cmd=params,
                           tree_file=rpath(task.tree_file),
                           tree_constrain=task.constrain_tree,
                           npr_iter=npr_iter)
            
        elif task.ttype == "treemerger":
            n.add_features(treemerger_type=task.tname, 
                           treemerger_rf="RF=%s [%s]" %(task.rf[0], task.rf[1]),
                           treemerger_out_match_dist = task.outgroup_match_dist,
                           treemerger_out_match = task.outgroup_match)

        elif task.ttype == "concat_alg":
            n.add_features(concatalg_cogs="%d"%task.used_cogs,
                           alg_path=task.alg_fasta_file)                       

def process_task(task, wkname, npr_conf, nodeid2info):
    cogconf, cogclass = npr_conf.cog_selector
    concatconf, concatclass = npr_conf.alg_concatenator
    treebuilderconf, treebuilderclass = npr_conf.tree_builder
    splitterconf, splitterclass = npr_conf.tree_splitter
    
    threadid, nodeid, seqtype, ttype = (task.threadid, task.nodeid,
                                        task.seqtype, task.ttype)
    cladeid, targets, outgroups = db.get_node_info(threadid, nodeid)

    if not treebuilderclass or task.size < 4:
        # Allows to dump algs in workflows with no tree tasks or if tree
        # inference does not make sense given the number of sequences. DummyTree
        # will produce a fake fully collapsed newick tree.
        treebuilderclass = DummyTree
    
    if outgroups and len(outgroups) > 1:
        constrain_id = nodeid
    else:
        constrain_id = None
        
    node_info = nodeid2info[nodeid]
    conf = GLOBALS[task.configid]
    new_tasks = []    
    if ttype == "cog_selector":
       
        # Generates a md5 id based on the genetree configuration workflow used
        # for the concat alg task. If something changes, concat alg will change
        # and the associated tree will be rebuilt
        config_blocks = set([wkname])
        for key, value in conf[wkname].iteritems():
            if isinstance(value, list) or  isinstance(value, tuple) \
                    or isinstance(value, set):
                for elem in value:
                    config_blocks.add(elem[1:]) if isinstance(elem, str) and elem.startswith("@") else None
            elif isinstance(value, str):
                config_blocks.add(value[1:]) if value.startswith("@") else None
        config_checksum =  md5(''.join(["[%s]\n%s" %(x, dict_string(conf[x]))
                                        for x in sorted(config_blocks)]))

        # THIS PART HAS BEEN MOVED TO COG_SELECTOR TASK
        # Check that current selection of cogs will cover all target and
        # outgroup species
        #cog_hard_limit = int(conf[concatconf]["_max_cogs"])
        #sp_repr = defaultdict(int)
        #for co in task.raw_cogs[:cog_hard_limit]:
        #    for sp, seq in co:
        #        sp_repr[sp] += 1
        #missing_sp = (targets | outgroups) - set(sp_repr.keys())
        #if missing_sp:
        #    raise TaskError("missing species under current cog selection: %s" %missing_sp)
        #else:
        #    log.log(28, "Analysis of current COG selection:")
        #    for sp, ncogs in sorted(sp_repr.items(), key=lambda x:x[1]):
        #        log.log(28, "   % 30s species present in % 6d COGs" %(sp, ncogs))
                
        # register concat alignment task. NodeId associated to concat_alg tasks
        # and all its children jobs should take into account cog information and
        # not only species and outgroups included.
        
        concat_job = concatclass(task.cogs, seqtype, conf, concatconf,
                                 config_checksum)
        db.add_node(threadid,
                    concat_job.nodeid, cladeid,
                    targets, outgroups)

        # Register Tree constrains
        constrain_tree = "(%s, (%s));" %(','.join(sorted(outgroups)), 
                                         ','.join(sorted(targets)))
        _outs = "\n".join(map(lambda name: ">%s\n0" %name, sorted(outgroups)))
        _tars = "\n".join(map(lambda name: ">%s\n1" %name, sorted(targets)))
        constrain_alg = '\n'.join([_outs, _tars])
        db.add_task_data(concat_job.nodeid, DATATYPES.constrain_tree, constrain_tree)
        db.add_task_data(concat_job.nodeid, DATATYPES.constrain_alg, constrain_alg)
        db.dataconn.commit() # since the creation of some Task objects
                             # may require this info, I need to commit
                             # right now.
        concat_job.size = task.size
        new_tasks.append(concat_job)
       
    elif ttype == "concat_alg":
        # register tree for concat alignment, using constraint tree if
        # necessary
        alg_id = db.get_dataid(task.taskid, DATATYPES.concat_alg_phylip)
        try:
            parts_id = db.get_dataid(task.taskid, DATATYPES.model_partitions)
        except ValueError:
            parts_id = None

        nodeid2info[nodeid]["size"] = task.size
        nodeid2info[nodeid]["target_seqs"] = targets
        nodeid2info[nodeid]["out_seqs"] = outgroups
            
        tree_task = treebuilderclass(nodeid, alg_id,
                                     constrain_id, None,
                                     seqtype, conf, treebuilderconf,
                                     parts_id=parts_id)
        tree_task.size = task.size
        new_tasks.append(tree_task)
        
    elif ttype == "tree":
        merger_task = splitterclass(nodeid, seqtype, task.tree_file, conf, splitterconf)
        merger_task.size = task.size
        new_tasks.append(merger_task)

    elif ttype == "treemerger":
        # Lets merge with main tree
        if not task.task_tree:
            task.finish()

        log.log(24, "Saving task tree...")
        annotate_node(task.task_tree, task)
        db.update_node(nid=task.nodeid, runid=task.threadid,
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
                        len(targets), len(outgroups))

                target_cladeids = None
                if tobool(conf[splitterconf].get("_find_ncbi_targets", False)):
                    tcopy = mtree.copy()
                    ncbi.connect_database()
                    tax2name, tax2track = ncbi.annotate_tree_with_taxa(tcopy, None)
                    #tax2name, tax2track = ncbi.annotate_tree_with_taxa(tcopy, "fake") # for testing sptree example
                    n2content = tcopy.get_cached_content()
                    broken_branches, broken_clades, broken_clade_sizes, tax2name = ncbi.get_broken_branches(tcopy, n2content)
                    log.log(28, 'restricting NPR to broken clades: '+
                            colorify(', '.join(map(lambda x: "%s"%tax2name[x], broken_clades)), "wr"))
                    target_cladeids = set()
                    for branch in broken_branches:
                        print branch.get_ascii(attributes=['spname', 'taxid'], compact=True)
                        print map(lambda x: "%s"%tax2name[x], broken_branches[branch])
                        target_cladeids.add(branch.cladeid)

                for node, seqs, outs, wkname in get_next_npr_node(task.configid, ttree,
                                                          task.out_seqs, mtree, None,
                                                          npr_conf, target_cladeids): # None is to avoid alg checks
                    log.log(24, "Adding new node: %s seqs, %s outgroups",
                            len(seqs), len(outs))
                    new_task_node = cogclass(seqs, outs,
                                             source_seqtype, conf, cogconf)
                    new_task_node.target_wkname = wkname
                    new_tasks.append(new_task_node)
                    db.add_node(threadid,
                                new_task_node.nodeid, new_task_node.cladeid,
                                new_task_node.targets,
                                new_task_node.outgroups)
    return new_tasks
     
def pipeline(task, wkname, conf=None):
    logindent(2)
    # Points to npr parameters according to task properties
    
    if not task:
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        npr_conf = IterConfig(conf, wkname,
                              len(GLOBALS["target_species"]),
                              source_seqtype)
        cogconf, cogclass = npr_conf.cog_selector
        initial_task = cogclass(GLOBALS["target_species"], set(),
                                source_seqtype, conf, cogconf)

        initial_task.main_tree = main_tree = None
        initial_task.threadid = generate_runid()
        initial_task.configid = initial_task.threadid
        initial_task.target_wkname = wkname
        # Register node 
        db.add_node(initial_task.threadid, initial_task.nodeid,
                    initial_task.cladeid, initial_task.targets,
                    initial_task.outgroups)
        
        new_tasks = [initial_task]
    else:
        conf = GLOBALS[task.configid]
        npr_conf = IterConfig(conf, wkname, task.size, task.seqtype)
        new_tasks  = process_task(task, wkname, npr_conf, conf['_nodeinfo'])

    process_new_tasks(task, new_tasks, conf)
    logindent(-2)
    
    return new_tasks
    
