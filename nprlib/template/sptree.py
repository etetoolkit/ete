import os
import logging
from collections import defaultdict

from nprlib.task import TreeMerger
from nprlib.utils import GLOBALS, generate_runid, pjoin, rpath

from nprlib.errors import DataError
from nprlib import db
from nprlib.template.common import (process_new_tasks, IterConfig,
                                    get_next_npr_node, get_iternumber)
from nprlib.logger import logindent

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

    alltasks = GLOBALS["nodeinfo"][final_task.nodeid]["tasks"]
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
                           treemerger_out_match = task.outgroup_match,)


def process_task(task, npr_conf, nodeid2info):
    conf = GLOBALS["config"]
    threadid, nodeid, seqtype, ttype = (task.threadid, task.nodeid,
                                        task.seqtype, task.ttype)
    cladeid, targets, outgroups = db.get_node_info(threadid, nodeid)
    node_info = nodeid2info[nodeid]
    
    new_tasks = []    
    if ttype == "cog_selector":
        # register concat alignment task
        concat_job = npr_conf.alg_concatenator(nodeid, task.cogs,
                                               seqtype, conf)
        concat_job.size = task.size
        new_tasks.append(concat_job)
       
    elif ttype == "concat_alg":
        # register tree for concat alignment, using constraint tree if
        # necessary
        constrain_tree_path = None 
        if outgroups and len(outgroups) > 1 and len(targets) > 1:
            constrain_tree_path = pjoin(task.taskdir,
                                        "constrain_tree.nw")
            newick = "(%s, (%s));" %(','.join(outgroups), ','.join(targets))
            open(constrain_tree_path, "w").write(newick)
           
        tree_task = npr_conf.tree_builder(nodeid,
                                          task.alg_phylip_file,
                                          constrain_tree_path, "JTT",
                                          seqtype, conf)
        tree_task.size = task.size
        new_tasks.append(tree_task)
        
    elif ttype == "tree":
        merger_task = TreeMerger(nodeid, seqtype, task.tree_file, conf)
        merger_task.size = task.size
        new_tasks.append(merger_task)

    elif ttype == "treemerger":
        # Lets merge with main tree
        if not task.task_tree:
            task.finish()

        log.log(28, "Saving task tree...")
        annotate_node(task.task_tree, task) 
        db.update_node(nid=task.nodeid, runid=task.threadid,
                       newick=db.encode(task.task_tree))
        db.commit()

        # Add new nodes
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        ttree, mtree = task.task_tree, task.main_tree
        log.log(28, "Processing tree: %s seqs, %s outgroups",
                len(targets), len(outgroups))
        for node, seqs, outs in get_next_npr_node(threadid, ttree,
                                                  mtree, None, npr_conf):
            log.log(28, "Adding new node: %s seqs, %s outgroups",
                    len(seqs), len(outs))
            new_task_node = npr_conf.cog_selector(seqs, outs,
                                                  source_seqtype, conf)
            new_tasks.append(new_task_node)
            db.add_node(threadid,
                        new_task_node.nodeid, new_task_node.cladeid,
                        new_task_node.targets,
                        new_task_node.outgroups)
        
    return new_tasks
      

def pipeline(task):
    logindent(2)
    # Points to npr parameters according to task properties
    nodeid2info = GLOBALS["nodeinfo"]
    if not task:
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        npr_conf = IterConfig("sptree",
                              len(GLOBALS["target_species"]),
                              source_seqtype)
        initial_task = npr_conf.cog_selector(GLOBALS["target_species"],
                                             set(), source_seqtype, GLOBALS["config"])
        initial_task.main_tree = main_tree = None
        initial_task.threadid = generate_runid()
        # Register node 
        db.add_node(initial_task.threadid, initial_task.nodeid,
                    initial_task.cladeid, initial_task.targets,
                    initial_task.outgroups)
        
        new_tasks = [initial_task]
    else:
        npr_conf = IterConfig("sptree", task.size, task.seqtype)
        new_tasks  = process_task(task, npr_conf, nodeid2info)

    process_new_tasks(task, new_tasks)
    logindent(-2)
    return new_tasks
    
