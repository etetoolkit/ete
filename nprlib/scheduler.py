import os
import time
from subprocess import call, Popen
from time import sleep, ctime
from collections import defaultdict
import logging
log = logging.getLogger("main")

from nprlib.logger import set_logindent, logindent
from nprlib.utils import (generate_id, print_as_table, HOSTNAME, md5,
                          get_node2content, PhyloTree, NodeStyle, Tree, DEBUG,
                          NPR_TREE_STYLE, faces)
from nprlib.errors import ConfigError, DataError, TaskError
from nprlib import db, sge
from nprlib.master_task import isjob

def schedule(config, processer, schedule_time, execution, retry, debug):
    def sort_tasks(x, y):
        _x = getattr(x, "nseqs", 0)
        _y = getattr(y, "nseqs", 0)
        if _x > _y:
            return -1
        elif _x < _y:
            return 1
        else:
            return 0
            
    execution, run_detached = execution
    main_tree = None
    npr_iter = 0
    # Send seed files to processer to generate the initial task
    nodeid2info = {}
    pending_tasks, main_tree = processer(None, main_tree,
                              config, nodeid2info)
    initial_task = pending_tasks[0]
    register_task(initial_task)
    if debug == "all":
        log.setLevel(10)
   
    clade2tasks = defaultdict(list)
    # Then enters into the scheduling.
    cores_total = config["main"]["_max_cores"]
    task2retry = defaultdict(int)
        
    while pending_tasks:
        cores_used = 0
        sge_jobs = []
        wait_time = 0.01 # Try to go fast unless running tasks
        set_logindent(0)
        log.log(28, "CHECK: (%s) %d tasks" %(ctime(), len(pending_tasks)))

        # ask SGE for running jobs
        if execution == "sge":
            sgeid2jobs = db.get_sge_tasks()
            qstat_jobs = sge.qstat()
        else:
            qstat_jobs = None

        # Check task status and compute total cores being used            
        for task in pending_tasks:
            if debug and log.level>10 and task.taskid.startswith(debug):
                log.setLevel(10) #start debugging
                
            task.status = task.get_status(qstat_jobs)
            cores_used += task.cores_used
            update_task_states(task)
        db.commit()
        
        # Process waiting tasks
        for task in sorted(pending_tasks, sort_tasks):
            if task.nodeid not in nodeid2info:
                nodeid2info[task.nodeid] = {}
                
            if task.ttype == "msf":
                seqs = task.target_seqs
                out_seqs = task.out_seqs
                try:
                    db.add_node(task.nodeid, task.cladeid,
                                task.target_seqs, task.out_seqs)
                except db.sqlite3.IntegrityError:
                    log.log(20, "node was registered previously.")

            # Shows some task info
            log.log(26, "")
            set_logindent(1)
            log.log(28, "(%s) %s" %(task.status, task))
            logindent(2)
            st_info = ', '.join(["%d(%s)" %(v,k) for k,v in task.job_status.iteritems()])
            log.log(26, "%d jobs: %s" %(len(task.jobs), st_info))
            tdir = task.taskdir.replace(config["main"]["basedir"], "")
            tdir = tdir.lstrip("/")
            log.log(20, "TaskDir: %s" %tdir)
            
            if task.status == "L":
                logindent(-2)
                log.warning("Some jobs within the task [%s] are marked as (L)ost,"
                            " meaning that although they look as running,"
                            " its execution could not be tracked. NPR will"
                            " continue execution with other pending tasks."
                            %task)
                logindent(2)

            logindent(2)
            for j in task.jobs:
                if j.status == "D":
                    log.log(20, "%s: %s", j.status, j)
                else:
                    log.log(24, "%s: %s", j.status, j)
            logindent(-2)
                
            if task.status in set("WQRL"):
                exec_type = getattr(task, "exec_type", execution)
                # Tries to send new jobs from this task
                for j, cmd in task.iter_waiting_jobs():
                    if not check_cores(j, cores_used, cores_total, execution):
                        continue
                    
                    if exec_type == "insitu":
                        log.log(28, "Launching %s" %j)
                        try:
                            if run_detached:
                                launch_detached(j, cmd)
                            else:
                                P = Popen(cmd, shell=True)
                            log.debug("Command: %s", j.cmd_file)
                        except Exception:
                            task.save_status("E")
                            task.status = "E"
                            raise
                        else:
                            j.status = "R"
                            task.status = "R"
                            cores_used += j.cores
                    elif exec_type == "sge":
                        task.status = "R"
                        j.status = "R"
                        j.sge = config["sge"]
                        sge_jobs.append((j,cmd))
                    else:
                        task.status = "R"
                        j.status = "R"
                        print cmd
                if task.status in set("QRL"):
                    wait_time = schedule_time
                    
            elif task.status == "D":
                logindent(3)
                new_tasks, main_tree = processer(task, main_tree, config,
                                                 nodeid2info)
                logindent(-3)
                pending_tasks.remove(task)
                for ts in new_tasks:
                    db.add_task2child(task.taskid, ts.taskid)
                    register_task(ts, parentid=task.taskid)
                pending_tasks.extend(new_tasks)
                cladeid = db.get_cladeid(task.nodeid)
                clade2tasks[cladeid].append(task)

            elif task.status == "E":
                log.error("Task contains errors")
                if retry and task not in task2retry:
                    log.log(28, "Remarking task as undone to retry")
                    task2retry[task] += 1
                    task.retry()
                    update_task_states(task)
                    db.commit()
                else:
                    raise TaskError(task)

            else:
                wait_time = schedule_time
                log.error("Unknown task state [%s].", task.status)
                continue
            logindent(-2)
            log.log(26, "Cores in use: %s" %cores_used)

            # If task was a new tree node, update main tree and dump snapshot
            if task.ttype == "treemerger":
                npr_iter += 1
                log.info("Dump iteration snapshot.")
                #main_tree = assembly_tree(config["main"]["basedir"],
                #                          clade2tasks, initial_task.taskid)

                #main_tree = assembly_tree(config["main"]["basedir"],
                #                          initial_task.taskid, clade2tasks)

                # we change node names here
                annotate_tree(main_tree, clade2tasks, nodeid2info, npr_iter)
                if DEBUG():
                    NPR_TREE_STYLE.title.clear()
                    NPR_TREE_STYLE.title.add_face(faces.TextFace("Current iteration tree. red=optimized node", fgcolor="blue"), 0)
                    main_tree.show(tree_style=NPR_TREE_STYLE)
                    
                snapshot_tree = main_tree.copy()
                for n in snapshot_tree.iter_leaves():
                    n.name = n.realname
                nout= len(task.out_seqs)
                ntarget = len(task.target_seqs)
                nw_file = os.path.join(config["main"]["basedir"],
                                       "tree_snapshots", "Iter_%06d_%s_S_%s_O.nw" %
                                       (npr_iter, ntarget, nout))
                snapshot_tree.write(outfile=nw_file, features=[])

        sge.launch_jobs(sge_jobs, config)
        sleep(wait_time)
        log.log(26, "")

    final_tree_file = os.path.join(config["main"]["basedir"], \
                                       "final_tree.nw")
    snapshot_tree.write(outfile=final_tree_file)
    log.log(28, "Done")
    log.debug(str(snapshot_tree))
   
def register_task(task, parentid=None):
 
    db.add_task(tid=task.taskid, nid=task.nodeid, parent=parentid,
                status=task.status, type="task", subtype=task.ttype, name=task.tname)
    for j in task.jobs:
        if isjob(j):
            db.add_task(tid=j.jobid, nid=task.nodeid, parent=task.taskid,
                        status="W", type="job", name=j.jobname)
            
        else:
            register_task(j, parentid=parentid)

def update_task_states(task):
    for j in task.jobs:
        if isjob(j):
            db.update_task(j.jobid, status=j.status)
        else:
            update_task_states(j)
    db.update_task(task.taskid, status=task.status)
        

def check_cores(j, cores_used, cores_total, execution):
    if j.cores > cores_total:
        raise ConfigError("Job [%s] is trying to be executed using [%d] cores."
                          " However, the program is limited to [%d] core(s)."
                          " Use the --multicore option to enable more cores." %
                          (j, j.cores, cores_total))
    elif execution =="insitu" and j.cores > cores_total-cores_used:
        log.log(22, "Job [%s] is waiting for [%d] core(s)" 
                 % (j, j.cores))
        return False
    else:
        return True
    
def get_node2content(node, store={}):
    for ch in node.children:
        get_node2content(ch, store=store)

    if node.children:
        val = []
        for ch in node.children:
            val.extend(store[ch])
        store[node] = val
    else:
        store[node] = [node.name]
    return store

def launch_detached(j, cmd):
    pid1 = os.fork()
    j.status = "R"
    if pid1 == 0:
        pid2 = os.fork()
   
        if pid2 == 0:	
            os.setsid()
            pid3 = os.fork()
            if pid3 == 0:
                os.chdir("/")
                os.umask(0)
                P = Popen(cmd, shell=True)
                P.wait()
                os._exit(0)
            else:
                # exit() or _exit()?  See below.
                os._exit(0)
        else:
            # exit() or _exit()?
            # _exit is like exit(), but it doesn't call any functions registered
            # with atexit (and on_exit) or any registered signal handlers.  It also
            # closes any open file descriptors.  Using exit() may cause all stdio
            # streams to be flushed twice and any temporary files may be unexpectedly
            # removed.  It's therefore recommended that child branches of a fork()
            # and the parent branch(es) of a daemon use _exit().
            os._exit(0)
    else:
        return

def assembly_tree(base_dir, init_task, clade2tasks):

    noimaginationtoday = db.get_task2child_tree()

    current_tasks = set()
    for tasks in clade2tasks.itervalues():
        current_tasks.update([_task.taskid for _task in tasks])
    
    tid2node = defaultdict(Tree)
    for tid, ch, ttype, tsubtype, tname, tstatus, clade in noimaginationtoday:
        #print tid, ch, clade, tsubtype
        if ch in current_tasks:
            tid2node[tid].add_child(tid2node[ch])
            tid2node[ch].name = str(ch)
            tid2node[ch].add_features(ttype=str(ttype),
                                  tsubtype=str(tsubtype),
                                      tstatus=str(tstatus), cladeid=str(clade))
    
    tasks_hierarchy = tid2node[init_task]
    #print tasks_hierarchy 
    #if DEBUG():
    #    tasks_hierarchy.show()
    base_tree = None
    if DEBUG():
        highlight = NodeStyle()
        highlight["fgcolor"]= "red"
        highlight["size"]= 12

    clade2node = {}
    for tnode in tasks_hierarchy.get_descendants():
        if tnode.name in current_tasks and tnode.tsubtype == "treemerger" and \
           tnode.tstatus == "D":
                
            task_tree = PhyloTree(os.path.join(base_dir, "tasks", tnode.name, "pruned_tree.nw"))
            # print tnode.name, tnode.tsubtype
            #n2content = get_node2content(task_tree)
            # 
            #for n, content in n2content.iteritems():
            #    n.cladeid = generate_id(content)
                            
            if base_tree:
                #target_node = base_tree.search_nodes(cladeid=tnode.cladeid)[0]
                target_node = clade2node[tnode.cladeid]
                # Set the distance to this partition from the prev iteration
                task_tree.dist = target_node.dist
                parent_node = target_node.up
                target_node.detach()
                parent_node.add_child(task_tree)
                
            else:
                base_tree = task_tree
                base_tree.dist = 0.0

            ch0 = task_tree.children[0]
            ch1 = task_tree.children[1]
            ch0.add_features(cladeid=generate_id(ch0.get_leaf_names()))
            ch1.add_features(cladeid=generate_id(ch0.get_leaf_names()))
            clade2node[tnode.cladeid] = task_tree
            clade2node[ch0.cladeid] = ch0
            clade2node[ch1.cladeid] = ch1
                
            if DEBUG(): 
                task_tree.set_style(highlight)
    return base_tree
       
    
def annotate_tree(t, clade2tasks, nodeid2info, npr_iter):
    n2names = get_node2content(t)
    cladeid2node = {}
    # Annotate cladeid in the whole tree
    for n in t.traverse():
        n.add_feature("realname", db.get_seq_name(n.name))
        cladeid2node[n.cladeid] = n

    for cladeid, alltasks in clade2tasks.iteritems():
        n = cladeid2node[cladeid]
        
        for task in alltasks:
            
            params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                      if not k.startswith("_")]
            params = " ".join(params)

            n.add_features(nseqs=nodeid2info[task.nodeid]["nseqs"])

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
                               tree_file=task.tree_file,
                               tree_constrain=task.constrain_tree,
                               npr_iter=npr_iter)
            elif task.ttype == "mchooser":
                n.add_features(modeltester_models=task.models, 
                               modeltester_type=task.tname, 
                               modeltester_params=params, 
                               modeltester_bestmodel=task.get_best_model(), 
                               )
            elif task.ttype == "treemerger":
                n.add_features(treemerger_type = task.tname, 
                               treemerger_out_policy = task.out_policy,
                               treemerger_min_outs =task.min_outs,
                               treemerger_rf = "RF=%s (%s)" %task.rf
                               )
               


# def assembly_tree_old(base_dir, clade2tasks, init_cid):
#     thread = set()
#     for tasks in clade2tasks.values():
#         thread.update(set([t.taskid for t in tasks]))
    
#     tid2child = defaultdict(set)
#     info = {}
#     for fields in db.report(max_records=0):
#         tid, nid, pid, cid, status, ttype, tstype = fields[:7]
#         info[tid] = {
#             "status": status,
#             "type": ttype,
#             "stype": tstype, 
#             "cladeid": cid, 
#         }
#         tid2child[pid].add(tid)
#     child_tasks = [init_cid]
#     base_tree = None
#     cladeid2node = {}
#     highlight = NodeStyle()
#     highlight["fgcolor"]= "red"
#     highlight["size"]= 20
#     while child_tasks:
#         tid = child_tasks.pop(0)
#         if tid not in thread:
#             continue
            
#         if info[tid]["type"] == "task" and info[tid]["stype"] == "treemerger" and info[tid]["status"] == "D":
#             task_tree = PhyloTree(os.path.join(base_dir, "tasks", tid, "pruned_tree.nw"))
#             n2content = get_node2content(task_tree)
        
#             for n, content in n2content.iteritems():
#                 n.cladeid = generate_id(content)
#             cid = info[tid]["cladeid"]
#             task_tree.set_style(highlight)            
#             if base_tree:
#                 target_node = base_tree.search_nodes(cladeid=cid)[0]
#                 parent_node = target_node.up

#                 target_node.detach()
#                 parent_node.add_child(task_tree)
#             else:
#                 base_tree = task_tree
#                 base_tree.dist = 0.0
#             #base_tree.show()
#         child_tasks.extend(list(tid2child.get(tid, set())))
#        
#    return base_tree
