import os
import logging
from collections import defaultdict

from nprlib.task import TreeMerger
from nprlib.utils import GLOBALS, generate_runid, SeqGroup, pjoin

from nprlib.errors import DataError
from nprlib import db
from nprlib.template.common import process_new_tasks, IterConfig

log = logging.getLogger("main")

def process_task(task, npr_conf, nodeid2info):
    conf = GLOBALS["config"]
    
    new_tasks = []
    threadid, nodeid, seqtype, ttype = (task.threadid, task.nodeid,
                                        task.seqtype, task.ttype)
    cladeid, targets, outgroups = db.get_node_info(threadid, nodeid)
    
    if ttype == "cog_selector":
        # register concat alignment task
        concat_job = npr_conf.alg_concatenator(nodeid, task.cogs, seqtype)
        concat_job.size = task.size
        new_tasks.append(concat_job)
       
    elif ttype == "concat_alg":
        # register tree for concat alignment, using constraint tree if
        # necessary
        constrain_tree_path = None 
        if outgroups and len(outgroups) > 1:
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
        new_tasks.append(merger_task)

    elif ttype == "treemerger":
        # Lets merge with main tree
        if not task.task_tree:
            task.finish()

        log.log(28, "Saving task tree...")
        annotate_node(task.task_tree, task) 
        db.update_node(nid=task.nodeid, 
                       runid=task.threadid,
                       newick=db.encode(task.task_tree))
        db.commit()

        # Add new nodes
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        ttree, mtree = task.task_tree, task.main_tree
        current_iter = get_iternumber(task.threadid)
        # Loads information about sequence similarity in each internal
        # node. This info will be used by processable_node()
        alg_path = node_info.get("clean_alg_path", node_info["alg_path"])
        if current_iter < conf["genetree"].get("max_iters", current_iter + 1):
            for node, seqs, outs in split_tree(ttree, mtree, alg_path, npr_conf):
                if current_iter < conf["genetree"].get("max_iters", current_iter + 1):
                    new_node = npr_conf.cog_selector(seqs, outs, source_seqtype)
                    if new_task_node.nodeid not in nodeid2info:
                        new_tasks.append(new_task_node)
                        current_iter =  inc_iternumber(task.threadid) # Register node
                        db.add_node(task.threadid,
                                    new_task_node.nodeid, new_task_node.cladeid,
                                    new_task_node.target_seqs,
                                    new_task_node.out_seqs)

                        if DEBUG():
                            NPR_TREE_STYLE.title.clear()
                            NPR_TREE_STYLE.title.add_face( faces.TextFace("MainTree:"
                                                                      "Gold color:Newly generated task nodes ",
                                                                      fgcolor="blue"), 0)
                            node.img_style["fgcolor"] = "Gold"
                            node.img_style["size"] = 30
        if DEBUG():
            task.main_tree.show(tree_style=NPR_TREE_STYLE)
            for _n in task.main_tree.traverse():
                _n.img_style = None
        
    return new_tasks
      


def pipeline(task):
    # Points to npr parameters according to task properties
    nodeid2info = GLOBALS["nodeinfo"]
    if not task:
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        npr_conf = IterConfig("sptree",
                              len(GLOBALS["target_species"]),
                              source_seqtype)
        initial_task = npr_conf.cog_selector(GLOBALS["target_species"],
                                             set(), source_seqtype)
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
    return new_tasks
    
