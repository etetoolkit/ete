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
                          basename)
from nprlib.errors import ConfigError, TaskError
from nprlib import db, sge
from nprlib.master_task import isjob, update_task_states_recursively

def sort_tasks(x, y):
    _x = getattr(x, "size", 0)
    _y = getattr(y, "size", 0)
    if _x > _y:
        return -1
    elif _x < _y:
        return 1
    else:
        return 0
        
def schedule(workflow_task_processor, schedule_time, execution, retry, debug):
    # Adjust debug mode
    if debug == "all":
        log.setLevel(10)

    ## ===================================
    ## INITIALIZE BASIC VARS AND SHORTCUTS
    config = GLOBALS["config"]
    cores_total = GLOBALS["_max_cores"]
    execution, run_detached = execution
    # keeps the count of how many times an error task has been retried
    task2retry = defaultdict(int) 
    npr_iter = 0
    main_tree = None   
    ## END OF VARS AND SHORTCUTS
    ## ===================================
   
    # Feeds pending task with the first task of the workflow 
    pending_tasks = workflow_task_processor(None)
    main_thread_id = pending_tasks[0].threadid
    # Clear info from previous runs
    open(os.path.join(GLOBALS["basedir"], "runid"), "a").write('\t'.join([main_thread_id, ctime()+"\n"]))
    
    # Enters into task scheduling
    while pending_tasks:
        cores_used = 0
        sge_jobs = []
        wait_time = 0.01

        ## ================================
        ## CHECK AND UPDATE CURRENT TASKS
        set_logindent(0)
        log.log(28, "CHECKING: (%s) %d tasks" % (ctime(), len(pending_tasks)))

        # ask SGE for running jobs
        if execution == "sge":
            sgeid2jobs = db.get_sge_tasks()
            qstat_jobs = sge.qstat()
        else:
            qstat_jobs = None

        # Check task status, update new states and compute total cores
        # being used
        for task in pending_tasks:
            show_task_info(task)
            if debug and log.level > 10 and task.taskid.startswith(debug):
                log.setLevel(10) #start debugging
                log.debug("ENTERING IN DEBUGGING MODE")
            task.status = task.get_status(qstat_jobs)
            cores_used += task.cores_used
            update_task_states_recursively(task)
        db.commit()
        ## END CHECK AND UPDATE CURRENT TASKS
        ## ================================
        
        # Process waiting tasks
        launched_tasks = 0
        
        for task in sorted(pending_tasks, sort_tasks):

            log.log(28, "Cores in use: %s/%s", cores_used, cores_total)
            
            if task.status in set("WQRL"):
                exec_type = getattr(task, "exec_type", execution)
                # Tries to send new jobs from this task
                for j, cmd in task.iter_waiting_jobs():
                    if not check_cores(j, cores_used, cores_total, execution):
                        continue
                    
                    if exec_type == "insitu":
                        log.log(24, "Launching %s" %j)
                        launched_tasks += 1
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
                log.log(28, "Launched %s tasks. Busy cores %s", launched_tasks, cores_used)
                
            elif task.status == "D":
                logindent(3)
                new_tasks = workflow_task_processor(task)
                logindent(-3)
                
                main_tree = task.main_tree
                # Update list of tasks
                pending_tasks.remove(task)
                pending_tasks.extend(new_tasks)
                # Stop processing tasks, so I can sort new and old
                # tasks by size
                break 
                
            elif task.status == "E":
                log.error("Task contains errors")
                if retry and task not in task2retry:
                    log.log(28, "Remarking task as undone to retry")
                    task2retry[task] += 1
                    task.retry()
                    task.init()
                    task.post_init()
                    update_task_states_recursively(task)
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
    if main_tree: 
        for n in main_tree.iter_leaves():
            n.name = n.realname
        log.log(28, "Writing final tree: %s", final_tree_file)
        main_tree.write(outfile=final_tree_file)

    log.log(28, "Done")
    GLOBALS["citator"].show()
   
      
def show_task_info(task):
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
    # Shows details about jobs
    for j in task.jobs:
        if j.status == "D":
            log.log(20, "(%s): %s", j.status, j)
        else:
            log.log(24, "(%s): %s", j.status, j)
    logindent(-2)

    
def check_cores(j, cores_used, cores_total, execution):
    if j.cores > cores_total:
        raise ConfigError("Job [%s] is trying to be executed using [%d] cores."
                          " However, the program is limited to [%d] core(s)."
                          " Use the --multicore option to enable more cores." %
                          (j, j.cores, cores_total))
    elif execution =="insitu" and j.cores > cores_total-cores_used:
        log.log(22, "Job [%s] awaiting [%d] core(s)" 
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

