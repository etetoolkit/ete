import os
from subprocess import Popen
from time import sleep, ctime
from collections import defaultdict
import re
import logging
log = logging.getLogger("main")

from nprlib.logger import set_logindent, logindent
from nprlib.utils import (generate_id, PhyloTree, NodeStyle, Tree,
                          DEBUG, NPR_TREE_STYLE, faces, GLOBALS,
                          basename, read_time_file)
from nprlib.errors import ConfigError, TaskError
from nprlib import db, sge
from nprlib.master_task import isjob

def rpath(fullpath):
    'Returns relative path of a task file (if possible)'
    m = re.search("/(tasks/.+)", fullpath)
    if m:
        return m.groups()[0]
    else:
        return fullpath

def schedule(init_processor, schedule_time, execution, retry, debug):
    config = GLOBALS["config"]

    def sort_tasks(x, y):
        _x = getattr(x, "nseqs", 0)
        _y = getattr(y, "nseqs", 0)
        if _x > _y:
            return -1
        elif _x < _y:
            return 1
        else:
            return 0

    # Clear info from previous runs
    open(os.path.join(GLOBALS["basedir"], "runid"), "w").write(GLOBALS["runid"])

    execution, run_detached = execution
    main_tree = None
    npr_iter = 0
    # Send seed files to processor to generate the initial task
    nodeid2info = GLOBALS["nodeinfo"]
    pending_tasks = init_processor(None)
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
        wait_time = 0.01 # Try to go fast unless we wait for running tasks
        set_logindent(0)
        log.log(28, "CHECK: (%s) %d tasks" % (ctime(), len(pending_tasks)))

        # ask SGE for running jobs
        if execution == "sge":
            sgeid2jobs = db.get_sge_tasks()
            qstat_jobs = sge.qstat()
        else:
            qstat_jobs = None

        # Check task status and compute total cores being used
        for task in pending_tasks:
            if debug and log.level > 10 and task.taskid.startswith(debug):
                log.setLevel(10) #start debugging
                log.debug("ENTERING IN DEBUGGING MODE")

            task.status = task.get_status(qstat_jobs)
            cores_used += task.cores_used
            update_task_states(task)

        db.commit()

        # Process waiting tasks
        for task in sorted(pending_tasks, sort_tasks):
            #if task.nodeid not in nodeid2info:
            #    nodeid2info[task.nodeid] = {}

            #if task.ttype == "msf":
            #    db.add_node(GLOBALS["runid"], task.nodeid,
            #                task.cladeid, task.target_seqs,
            #                task.out_seqs)

            # Shows some task info
            log.log(26, "")
            set_logindent(1)
            log.log(28, "(%s) %s" % (task.status, task))
            logindent(2)
            st_info = ', '.join(["%d(%s)" % (v, k) for k, v in
                                 task.job_status.iteritems()])
            log.log(26, "%d jobs: %s" %(len(task.jobs), st_info))
            tdir = task.taskdir.replace(GLOBALS["basedir"], "")
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
            log.log(26, "Cores in use: %s" %cores_used)
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
                                running_proc = Popen(cmd, shell=True)
                                GLOBALS["running_jobs"].append(j.status_file)
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
                        sge_jobs.append((j, cmd))
                    else:
                        task.status = "R"
                        j.status = "R"
                        print cmd
                if task.status in set("QRL"):
                    wait_time = schedule_time
                    
            elif task.status == "D":
                logindent(3)
                new_tasks = init_processor(task)

                logindent(-3)
                pending_tasks.remove(task)
                for ts in new_tasks:
                    db.add_task2child(task.taskid, ts.taskid)
                    register_task(ts, parentid=task.taskid)
                pending_tasks.extend(new_tasks)
                cladeid = db.get_cladeid(task.nodeid)
                clade2tasks[cladeid].append(task)
                main_tree = task.main_tree
                # If task was a new tree node, update main tree and
                # dump snapshot
                if task.ttype == "treemerger":
                    npr_iter += 1
                    log.log(28, "Saving task tree...")
                    annotate_node(task.task_tree, clade2tasks,
                                  nodeid2info, npr_iter) 
                    db.update_node(task.nodeid, 
                                   GLOBALS["runid"],
                                   newick=db.encode(task.task_tree))
                    db.commit()
                break # Stop processing tasks, so I can sort them by size
                
            elif task.status == "E":
                log.error("Task contains errors")
                if retry and task not in task2retry:
                    log.log(28, "Remarking task as undone to retry")
                    task2retry[task] += 1
                    task.retry()
                    task.init()
                    task.post_init()
                    update_task_states(task)
                    db.commit()
                else:
                    raise TaskError(task)

            else:
                wait_time = schedule_time
                log.error("Unknown task state [%s].", task.status)
                continue
            logindent(-2)

        sge.launch_jobs(sge_jobs, config)
        if wait_time:
            log.log(28, "Wating %s seconds" %wait_time)
            sleep(wait_time)
        log.log(26, "")

    final_tree_file = os.path.join(GLOBALS["basedir"],
                                   "final_tree.nw")

    for n in main_tree.iter_leaves():
        n.name = n.realname
    log.log(28, "writing final_tree")
    main_tree.write(outfile=final_tree_file)
   
    log.log(28, "Done")
    
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
    print task, task.taskid, task.status
    for j in task.jobs:
        if isjob(j):
            start = None
            end = None
            if j.status == "D":
                try:
                    start, end = read_time_file(j.time_file)
                except Exception, e:
                    log.warning("Execution time could not be loaded into DB: %s", j.jobid[:6])
                    log.warning(e)
            db.update_task(j.jobid, status=j.status, tm_start=start, tm_end=end )
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

def annotate_node(t, clade2tasks, nodeid2info, npr_iter):
    cladeid2node = {}
    # Annotate cladeid in the whole tree
    for n in t.traverse():
        if n.is_leaf():
            n.add_feature("realname", db.get_seq_name(n.name))
            #n.name = n.realname
        if hasattr(n, "cladeid"):
            cladeid2node[n.cladeid] = n

    alltasks = clade2tasks[t.cladeid]
    n = cladeid2node[t.cladeid]
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
                           clean_alg_path=rpath(task.clean_alg_fasta_file))
        elif task.ttype == "alg":
            n.add_features(alg_mean_ident=task.mean_ident, 
                           alg_std_ident=task.std_ident, 
                           alg_max_ident=task.max_ident, 
                           alg_min_ident=task.min_ident, 
                           alg_type=task.tname, 
                           alg_cmd=params,
                           alg_path=rpath(task.alg_fasta_file))

        elif task.ttype == "tree":
            n.add_features(tree_model=task.model, 
                           tree_seqtype=task.seqtype, 
                           tree_type=task.tname, 
                           tree_cmd=params,
                           tree_file=rpath(task.tree_file),
                           tree_constrain=task.constrain_tree,
                           npr_iter=npr_iter)
        elif task.ttype == "mchooser":
            n.add_features(modeltester_models=task.models, 
                           modeltester_type=task.tname, 
                           modeltester_params=params, 
                           modeltester_bestmodel=task.get_best_model(), 
                           )
        elif task.ttype == "treemerger":
            n.add_features(treemerger_type=task.tname, 
                           treemerger_rf="RF=%s [%s]" %(task.rf[0], task.rf[1]),
                           treemerger_out_match_dist = task.outgroup_match_dist,
                           treemerger_out_match = task.outgroup_match,
            )

