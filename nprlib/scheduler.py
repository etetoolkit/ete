import os
import signal

import subprocess
from multiprocessing import Process, Queue
from Queue import Empty as QueueEmpty
from time import sleep, ctime, time
from collections import defaultdict, deque
import re
import logging
log = logging.getLogger("main")

from nprlib.logger import set_logindent, logindent, get_logindent
from nprlib.utils import (generate_id, PhyloTree, NodeStyle, Tree,
                          DEBUG, NPR_TREE_STYLE, faces, GLOBALS,
                          basename, pjoin, ask)
from nprlib.errors import ConfigError, TaskError
from nprlib import db, sge
from nprlib.master_task import (isjob, update_task_states_recursively,
                                update_job_status)
from nprlib.template.common import assembly_tree

def debug(_signal, _frame):
    import pdb
    pdb.set_trace()
    
def signal_handler(_signal, _frame):
    if "_background_scheduler" in GLOBALS:
        GLOBALS["_background_scheduler"].terminate()

    signal.signal(signal.SIGINT, lambda s,f: None)
    db.commit()
    ver = {28: "0", 26: "1", 24: "2", 22: "3", 20: "4", 10: "5"}
    ver_level = log.level
    print '\n\nYou pressed Ctrl+C!'
    print 'q) quit'
    print 'v) change verbosity level:', ver.get(ver_level, ver_level)
    print 'd) enter debug mode'
    print 'c) continue execution'
    key = ask("   Choose:", ["q", "v", "d", "c"])
    if key == "q":
        raise KeyboardInterrupt
    elif key == "d":
        signal.signal(signal.SIGALRM, debug)
        signal.alarm(1)
        return
    elif key == "v":
        vl = ask("new level", sorted(ver.values()))
        new_level = sorted(ver.keys(), reverse=True)[int(vl)]
        log.setLevel(new_level)
    elif key == "d":
        import pdb
        pdb.set_trace()
    signal.signal(signal.SIGINT, signal_handler)
    
def sort_tasks(x, y):
    priority = {
        "treemerger": 1,
        "tree": 2,
        "mchooser": 3, 
        "alg": 4,
        "concat_alg": 5,
        "acleaner": 6,
        "msf":7,
        "cog_selector":8}
    
    x_type_prio = priority.get(x.ttype, 100)
    y_type_prio = priority.get(y.ttype, 100)
        
    prio_cmp = cmp(x_type_prio, y_type_prio)
    if prio_cmp == 0: 
        x_size = getattr(x, "size", 0)
        y_size = getattr(y, "size", 0)
        size_cmp = cmp(x_size, y_size) * -1
        if size_cmp == 0:
            return cmp(x.threadid, y.threadid)
        else:
            return size_cmp
    else:
        return prio_cmp
    
def schedule(workflow_task_processor, pending_tasks, schedule_time, execution, retry, debug):

    # Adjust debug mode
    if debug == "all":
        log.setLevel(10)
    pending_tasks = set(pending_tasks)
    
    ## ===================================
    ## INITIALISE BASIC VARS 
    execution, run_detached = execution
    # keeps the count of how many times an error task has been retried
    task2retry = defaultdict(int)
    thread2tasks = defaultdict(list)
    for task in pending_tasks:
        thread2tasks[task.configid].append(task)
    expected_threads = set(thread2tasks.keys())
    past_threads = {}
    thread_errors = defaultdict(list)
    ## END OF VARS AND SHORTCUTS
    ## ===================================

    cores_total = GLOBALS["_max_cores"]
    if cores_total > 2:
        job_queue = Queue()
        back_launcher = Process(target=background_job_launcher,
                                args=(job_queue, run_detached,
                                      schedule_time, cores_total-2))
        GLOBALS["_background_scheduler"] = back_launcher
        back_launcher.start()
    else:
        back_launcher = None

    # Captures Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    BUG = set()
    # Enters into task scheduling
    while pending_tasks:
        wtime = schedule_time/2.0

        # ask SGE for running jobs
        if execution == "sge":
            sgeid2jobs = db.get_sge_tasks()
            qstat_jobs = sge.qstat()
        else:
            qstat_jobs = None

        # Show summary of pending tasks per thread
        thread2tasks = defaultdict(list)
        for task in pending_tasks:
            thread2tasks[task.configid].append(task)
        set_logindent(0)
        log.log(28, "@@13: Updating tasks status:@@1: (%s)" % (ctime()))
        for tid, tlist in thread2tasks.iteritems():
            threadname = GLOBALS[tid]["_name"]
            log.log(28, "  Thread @@13:%s@@1:: pending tasks: @@8:%s@@1:" %(threadname, len(tlist)))
            
        ## ================================
        ## CHECK AND UPDATE CURRENT TASKS
        checked_tasks = set()
        check_start_time = time()
        to_add_tasks = set()
        
        GLOBALS["cached_status"] = {}
        for task in sorted(pending_tasks, sort_tasks):
            # Avoids endless periods without new job submissions
            elapsed_time = time() - check_start_time
            if not back_launcher and pending_tasks and \
                    elapsed_time > schedule_time * 2:
                log.log(26, "@@8:Interrupting task checks to schedule new jobs@@1:")
                db.commit()
                wtime = launch_jobs(sorted(pending_tasks, sort_tasks),
                                    execution, run_detached)
                check_start_time = time()
            
            # Enter debuging mode if necessary
            if debug and log.level > 10 and task.taskid.startswith(debug):
                log.setLevel(10) 
                log.debug("ENTERING IN DEBUGGING MODE")
            thread2tasks[task.configid].append(task)

            # Update tasks and job statuses

            if task.taskid not in checked_tasks:
                try:
                    show_task_info(task)
                    task.status = task.get_status(qstat_jobs)
                    if back_launcher:
                        for j, cmd in task.iter_waiting_jobs():
                            j.status = "Q"
                            GLOBALS["cached_status"][j.jobid] = "Q"
                            if j.jobid not in BUG:
                                log.log(24, "  @@8:Queueing @@1: %s from %s" %(j, task))
                                job_queue.put([j.jobid, j.cores, cmd, j.status_file])
                            BUG.add(j.jobid)

                    update_task_states_recursively(task)
                    db.commit()
                    checked_tasks.add(task.taskid)
                except TaskError, e:
                    log.error("Errors found in %s" %task)
                    pending_tasks.discard(task)
                    thread_errors[task.configid].append([task, e.value, e.msg])
                    continue
            else:
                # Set temporary Queued state to avoids launching
                # jobs from clones
                task.status = "Q" 
                if log.level < 24:
                    show_task_info(task)

            if task.status == "D":
                #db.commit()                
                show_task_info(task)
                logindent(3)
                create_tasks = workflow_task_processor(task)
                logindent(-3)
                to_add_tasks.update(create_tasks)
                pending_tasks.discard(task)
            elif task.status == "E":
                #db.commit()
                log.error("task contains errors: %s " %task)
                if retry and task not in task2retry:
                    log.log(28, "@@8:Remarking task as undone to retry@@1:")
                    task2retry[task] += 1
                    task.retry()
                    task.init()
                    task.post_init()
                    update_task_states_recursively(task)
                    db.commit()
                else:
                    log.error("Errors found in %s")
                    pending_tasks.discard(task)
                    thread_errors[task.configid].append([task, None, "Found (E) task status"])
            
        #db.commit()
        if not back_launcher: 
            wtime = launch_jobs(sorted(pending_tasks, sort_tasks),
                            execution, run_detached)

        # Update global task list with recently added jobs to be check
        # during next cycle
        pending_tasks.update(to_add_tasks)
                
        ## END CHECK AND UPDATE CURRENT TASKS
        ## ================================
        
        if wtime:
            set_logindent(0)
            log.log(28, "@@13:Waiting %s seconds@@1:" %wtime)
            sleep(wtime)
        else:
            sleep(schedule_time)

        # Dump / show ended threads
        for configid, etasks in thread_errors.iteritems(): 
            log.log(28, "Thread @@10:%s@@1: contains errors:" %\
                        (GLOBALS[configid]["_name"]))
            for error in etasks:
                log.error(" ** %s" %error[0])
               
                e_obj = error[1] if error[1] else error[0]
                error_path = e_obj.jobdir if isjob(e_obj) else e_obj.taskdir
                if e_obj is not error[0]: 
                    log.error("      -> %s" %e_obj)
                log.error("      -> %s" %error_path)
                log.error("        -> %s" %error[2])
            
        pending_threads = set([ts.configid for ts in pending_tasks])
        finished_threads = expected_threads - (pending_threads | set(thread_errors.keys()))
        for configid in finished_threads:
            # configid is the the same as threadid in master tasks
            final_tree_file = pjoin(GLOBALS[configid]["_outpath"],
                                    GLOBALS["inputname"] + ".final_tree")
            threadname = GLOBALS[configid]["_name"]
            if configid in past_threads:
                log.log(28, "Done thread @@12:%s@@1: in %d iterations",
                        threadname, past_threads[configid])
            else:
                log.log(28, "Assembling final tree...")
                main_tree, treeiters =  assembly_tree(configid)
                past_threads[configid] = treeiters - 1
                log.log(28, "Writing final tree for @@13:%s@@1: %s",
                        threadname, final_tree_file+".nwx")
                main_tree.write(outfile=final_tree_file+".nw")
                main_tree.write(outfile=final_tree_file+".nwx", features=[])
                log.log(28, "Done thread @@12:%s@@1: in %d iterations",
                        threadname, past_threads[configid])

                
        log.log(26, "")
    if back_launcher:
        back_launcher.terminate()
        
    log.log(28, "Done")
    GLOBALS["citator"].show()

def background_job_launcher(job_queue, run_detached, schedule_time, max_cores):
    running_jobs = {}
    visited_ids = set()
    # job_queue = [jid, cores, cmd, status_file]
    
    finished_states = set("ED")
    cores_used = 0
    dups = set()
    pending_jobs = deque()
    while True:
        launched = 0
        done_jobs = set()
        cores_used = 0
        for jid, (cores, cmd, st_file) in running_jobs.iteritems():
            try:
                st = open(st_file).read(1)
            except IOError:
                st = "?"
            if st in finished_states:
                #cores_used -= cores
                done_jobs.add(jid)
            else:
                cores_used += cores
        for d in done_jobs:
            del running_jobs[d]
            
        cores_avail = max_cores - cores_used       
        for i in xrange(cores_avail):
            try:
                jid, cores, cmd, st_file = job_queue.get(False)
            except QueueEmpty:
                pass
            else:
                pending_jobs.append([jid, cores, cmd, st_file])
                
            if pending_jobs and pending_jobs[0][1] <= cores_avail:
                jid, cores, cmd, st_file = pending_jobs.popleft()
                if jid in visited_ids:
                    dups.add(jid)
                    print "DUPLICATED execution!!!!!!!!!!!!", jid
                    continue
            elif pending_jobs:
                log.log(28, "@@8:waiting for %s cores" %pending_jobs[0][1])
                break
            else:
                break
            
            ST=open(st_file, "w"); ST.write("R"); ST.flush(); ST.close()
            try:
                if run_detached:
                    cmd += " &"
                    subprocess.call(cmd, shell=True)
                else:
                    running_proc = subprocess.Popen(cmd, shell=True)
            except Exception, e:
                print e
                ST=open(st_file, "w"); ST.write("E"); ST.flush(); ST.close()
            else:
                launched += 1
                running_jobs[jid] = [cores, cmd, st_file]
                cores_avail -= cores
                cores_used += cores
                visited_ids.add(jid)
                
        waiting_jobs = job_queue.qsize() + len(pending_jobs)
        log.log(28, "@@8:Launched@@1: %s jobs. Waiting %s jobs. Cores usage: %s/%s",
                launched, waiting_jobs, cores_used, max_cores)
        for _d in dups:
            print "duplicate bug", _d
        
        sleep(schedule_time)

def launch_detached_process(cmd):
    os.system(cmd)

        
    
def launch_jobs(pending_tasks, execution, run_detached):
    if not execution:
        return None
    cores_total = GLOBALS["_max_cores"]
    prev_logindent = get_logindent()
    set_logindent(0)
    log.log(28, "==========================================================")
    log.log(28, "@@13:NEW SCHEDULING CYCLE:@@1: (%s)" % (ctime()))
   
    sge_config = {}# UNUSED SGE CONFIG !!!!  antes GLOBALS["config"]
    
    # Keep number of cores used: if a job has just ended, remove it
    # from the list of running jobs and decrease cores used
    cores_used = 0
    launched_jobs = set()
    for job in list(GLOBALS["running_jobs"]):
        job.get_status() # Quick update for fast jobs that may have ended  
        if job.status in set("DE"):
            log.log(22, "@@8: Releasing %s cores" %job.cores)
            GLOBALS["running_jobs"].discard(job)
        else:
            cores_used += job.cores
        launched_jobs.add(job.jobid)
    db.commit()
    
    del_tasks = set()
    add_tasks = set()
    sge_jobs = []
    launched_tasks = 0
    waiting_jobs = 0
    wait_time = 0.01
    # Process waiting tasks
    for task in pending_tasks:
        if task.status in set("WQRL"):
            exec_type = getattr(task, "exec_type", execution)
            # Tries to send new jobs from this task
            for j, cmd in task.iter_waiting_jobs():
                waiting_jobs += 1
                if not check_cores(j, cores_used, cores_total, execution) or \
                        j.jobid in launched_jobs:
                    continue

                if exec_type == "insitu":
                    log.log(26, "  @@8:Launching@@1: %s from %s" %(j, task))
                    log.debug("Command: %s", j.cmd_file)
                    launched_tasks += 1
                    try:
                        if run_detached:
                            j.status = "R"
                            subjob = Process(target=launch_detached_process, args=[cmd])
                            subjob.daemon = True
                            subjob.start()
                            subjob.join()
                            #launch_detached(cmd)
                        else:
                            running_proc = subprocess.Popen(cmd, shell=True)
                    except Exception:
                        task.save_status("E")
                        task.status = "E"
                        raise
                    else:
                        GLOBALS["running_jobs"].add(j)
                        launched_jobs.add(j.jobid)
                        j.status = "R"
                        task.status = "R"
                        cores_used += j.cores
                elif exec_type == "sge":
                    task.status = "R"
                    j.status = "R"
                    j.sge = sge_config["sge"]
                    sge_jobs.append((j, cmd))
                else:
                    task.status = "R"
                    j.status = "R"
                    print cmd
            if task.status in set("QRL"):
                wait_time = None

        elif task.status == "Q":
            pass # task execution is temporarily blocked
        else:
            wait_time = None
            log.error("Unknown task state [%s].", task.status)
            continue
        logindent(-2)

    sge.launch_jobs(sge_jobs, sge_config)
    log.log(28, "Launched %s of %s waiting jobs", launched_tasks, waiting_jobs)
    log.log(28, "Cores in use: %s/%s", cores_used, cores_total)
    log.log(28, "=======================================================")
    set_logindent(prev_logindent)
    return wait_time 
   

def color_status(status):
    if status == "D":
        stcolor = "@@06:"
    elif status == "E":
        stcolor = "@@03:"
    elif status == "R":
        stcolor = "@@05:"
    else:
        stcolor = ""
    return "%s%s@@1:" %(stcolor, status)

def show_task_info(task):
    log.log(26, "")
    set_logindent(1)
    log.log(28, "(%s) %s" % (color_status(task.status), task))
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
    

def launch_detached(cmd):
    pid1 = os.fork()
    if pid1 == 0:
        pid2 = os.fork()
   
        if pid2 == 0:	
            os.setsid()
            pid3 = os.fork()
            if pid3 == 0:
                os.chdir("/")
                os.umask(0)
                P = subprocess.Popen(cmd, shell=True)
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

