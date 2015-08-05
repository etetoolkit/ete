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
import sys
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

from ete2.tools.phylobuild_lib.logger import set_logindent, logindent, get_logindent
from ete2.tools.phylobuild_lib.utils import (generate_id, PhyloTree, NodeStyle, Tree,
                          DEBUG, NPR_TREE_STYLE, faces, GLOBALS,
                          basename, pjoin, ask, send_mail, pid_up, SeqGroup)
from ete2.tools.phylobuild_lib.errors import ConfigError, TaskError
from ete2.tools.phylobuild_lib import db, sge
from ete2.tools.phylobuild_lib.master_task import (isjob, update_task_states_recursively,
                                store_task_data_recursively,
                                remove_task_dir_recursively,
                                update_job_status)
from ete2.tools.phylobuild_lib.workflow.common import assembly_tree, get_cmd_log

def debug(_signal, _frame):
    import pdb
    pdb.set_trace()

def control_c(_signal, _frame):    
    signal.signal(signal.SIGINT, signal.SIG_IGN)
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
    signal.signal(signal.SIGINT, control_c)
    
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

def get_stored_data(fileid):
    try:
        _tid, _did = fileid.split(".")
        _did = int(_did)
    except (IndexError, ValueError): 
        dataid = fileid
    else:
        dataid = db.get_dataid(_tid, _did)
    return db.get_data(dataid)
    
def schedule(workflow_task_processor, pending_tasks, schedule_time, execution, debug, norender):    
    # Adjust debug mode
    if debug == "all":
        log.setLevel(10)
    pending_tasks = set(pending_tasks)
    
    ## ===================================
    ## INITIALIZE BASIC VARS 
    execution, run_detached = execution
    thread2tasks = defaultdict(list)
    for task in pending_tasks:
        thread2tasks[task.configid].append(task)
    expected_threads = set(thread2tasks.keys())
    past_threads = {}
    thread_errors = defaultdict(list)
    ## END OF VARS AND SHORTCUTS
    ## ===================================

    cores_total = GLOBALS["_max_cores"]
    if cores_total > 0:
        job_queue = Queue()
        
        back_launcher = Process(target=background_job_launcher,
                                args=(job_queue, run_detached,
                                      GLOBALS["launch_time"], cores_total))
        back_launcher.start()
    else:
        job_queue = None
        back_launcher = None

    GLOBALS["_background_scheduler"] = back_launcher
    GLOBALS["_job_queue"] = job_queue

        
    # Captures Ctrl-C for debuging DEBUG 
    #signal.signal(signal.SIGINT, control_c)
    

    
    last_report_time = None
    
    BUG = set()
    try:
        # Enters into task scheduling
        while pending_tasks:
            wtime = schedule_time

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
            info_lines = []
            for tid, tlist in thread2tasks.iteritems():
                threadname = GLOBALS[tid]["_name"]
                sizelist = ["%s" %getattr(_ts, "size", "?") for _ts in tlist]
                info = "Thread @@13:%s@@1:: pending tasks: @@8:%s@@1: of sizes: %s" %(
                    threadname, len(tlist), ', '.join(sizelist))
                info_lines.append(info)

            for line in info_lines:
                log.log(28, line)

            if GLOBALS["email"]  and last_report_time is None:
                last_report_time = time()
                send_mail(GLOBALS["email"], "Your NPR process has started", '\n'.join(info_lines))

            ## ================================
            ## CHECK AND UPDATE CURRENT TASKS
            checked_tasks = set()
            check_start_time = time()
            to_add_tasks = set()

            GLOBALS["cached_status"] = {}
            for task in sorted(pending_tasks, sort_tasks):
                # Avoids endless periods without new job submissions
                elapsed_time = time() - check_start_time
                #if not back_launcher and pending_tasks and \
                #        elapsed_time > schedule_time * 2:
                #    log.log(26, "@@8:Interrupting task checks to schedule new jobs@@1:")
                #    db.commit()
                #    wtime = launch_jobs(sorted(pending_tasks, sort_tasks),
                #                        execution, run_detached)
                #    check_start_time = time()

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
                        db.dataconn.commit()
                        if back_launcher and task.status not in set("DE"):
                            for j, cmd in task.iter_waiting_jobs():
                                j.status = "Q"
                                GLOBALS["cached_status"][j.jobid] = "Q"
                                if j.jobid not in BUG:
                                    if not os.path.exists(j.jobdir):
                                        os.makedirs(j.jobdir)
                                    for ifile, outpath in j.input_files.iteritems():
                                        try:
                                            _tid, _did = ifile.split(".")
                                            _did = int(_did)
                                        except (IndexError, ValueError): 
                                            dataid = ifile
                                        else:
                                            dataid = db.get_dataid(_tid, _did)

                                        if not outpath:
                                            outfile = pjoin(GLOBALS["input_dir"], ifile)
                                        else:
                                            outfile = pjoin(outpath, ifile)

                                        if not os.path.exists(outfile): 
                                            open(outfile, "w").write(db.get_data(dataid))
                                            
                                    log.log(24, "  @@8:Queueing @@1: %s from %s" %(j, task))
                                    if execution: 
                                        job_queue.put([j.jobid, j.cores, cmd, j.status_file])
                                BUG.add(j.jobid)

                        update_task_states_recursively(task)
                        db.commit()
                        checked_tasks.add(task.taskid)
                    except TaskError, e:
                        log.error("Errors found in %s" %task)
                        import traceback
                        traceback.print_exc()
                        if GLOBALS["email"]:
                            threadname = GLOBALS[task.configid]["_name"]
                            send_mail(GLOBALS["email"], "Errors found in %s!" %threadname,
                                      '\n'.join(map(str, [task, e.value, e.msg])))
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


                    # Log commands of every task
                    if 'cmd_log_file' not in GLOBALS[task.configid]:
                         GLOBALS[task.configid]['cmd_log_file'] = pjoin(GLOBALS[task.configid]["_outpath"], "cmd.log")
                         O = open(GLOBALS[task.configid]['cmd_log_file'], "w")
                         O.close()

                    cmd_lines =  get_cmd_log(task)
                    CMD_LOG = open(GLOBALS[task.configid]['cmd_log_file'], "a")
                    print >>CMD_LOG, task
                    for c in cmd_lines:
                        print >>CMD_LOG, '   '+'\t'.join(map(str, c))
                    CMD_LOG.close()
                    # 

                    try:
                        #wkname = GLOBALS[task.configid]['_name']
                        create_tasks = workflow_task_processor(task, task.target_wkname)
                    except TaskError, e:
                        log.error("Errors found in %s" %task)
                        pending_tasks.discard(task)
                        thread_errors[task.configid].append([task, e.value, e.msg])
                        continue
                    else: 
                        logindent(-3)

                        to_add_tasks.update(create_tasks)
                        pending_tasks.discard(task)

                elif task.status == "E":
                    log.error("task contains errors: %s " %task)
                    log.error("Errors found in %s")
                    pending_tasks.discard(task)
                    thread_errors[task.configid].append([task, None, "Found (E) task status"])

            #db.commit()
            #if not back_launcher: 
            #    wtime = launch_jobs(sorted(pending_tasks, sort_tasks),
            #                    execution, run_detached)

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
            error_lines = []
            for configid, etasks in thread_errors.iteritems(): 
                error_lines.append("Thread @@10:%s@@1: contains errors:" %\
                            (GLOBALS[configid]["_name"]))
                for error in etasks:
                    error_lines.append(" ** %s" %error[0])
                    e_obj = error[1] if error[1] else error[0]
                    error_path = e_obj.jobdir if isjob(e_obj) else e_obj.taskid
                    if e_obj is not error[0]: 
                        error_lines.append("      -> %s" %e_obj)
                    error_lines.append("      -> %s" %error_path)
                    error_lines.append("        -> %s" %error[2])
            for eline in error_lines:
                log.error(eline)

            pending_threads = set([ts.configid for ts in pending_tasks])
            finished_threads = expected_threads - (pending_threads | set(thread_errors.keys()))
            just_finished_lines = []
            finished_lines = []
            for configid in finished_threads:
                # configid is the the same as threadid in master tasks
                final_tree_file = pjoin(GLOBALS[configid]["_outpath"],
                                        GLOBALS["inputname"] + ".final_tree")
                threadname = GLOBALS[configid]["_name"]

                if configid in past_threads:
                    log.log(28, "Done thread @@12:%s@@1: in %d iteration(s)",
                            threadname, past_threads[configid])
                    finished_lines.append("Finished %s in %d iteration(s)" %(
                            threadname, past_threads[configid]))
                else:

                    log.log(28, "Assembling final tree...")
                    main_tree, treeiters =  assembly_tree(configid)
                    past_threads[configid] = treeiters - 1

                    log.log(28, "Done thread @@12:%s@@1: in %d iteration(s)",
                            threadname, past_threads[configid])


                    log.log(28, "Writing final tree for @@13:%s@@1:\n   %s\n   %s",
                            threadname, final_tree_file+".nw",
                            final_tree_file+".nwx (newick extended)")
                    main_tree.write(outfile=final_tree_file+".nw")
                    main_tree.write(outfile=final_tree_file+ ".nwx", features=[],
                                    format_root_node=True)

                    if hasattr(main_tree, "alg_path"):
                        log.log(28, "Writing root node alignment @@13:%s@@1:\n   %s",
                                threadname, final_tree_file+".fa")

                        alg = SeqGroup(get_stored_data(main_tree.alg_path))
                        OUT = open(final_tree_file+".fa", "w")
                        for name, seq, comments in alg:
                            realname = db.get_seq_name(name)
                            print >>OUT, ">%s\n%s" %(realname, seq)
                        OUT.close()

                    if hasattr(main_tree, "clean_alg_path"):
                        log.log(28, "Writing root node trimmed alignment @@13:%s@@1:\n   %s",
                                threadname, final_tree_file+".trimmed.fa")

                        alg = SeqGroup(get_stored_data(main_tree.clean_alg_path))
                        OUT = open(final_tree_file+".trimmed.fa", "w")
                        for name, seq, comments in alg:
                            realname = db.get_seq_name(name)
                            print >>OUT, ">%s\n%s" %(realname, seq)
                        OUT.close()

                    if norender == False:
                        log.log(28, "Generating tree image for @@13:%s@@1:\n   %s",
                                threadname, final_tree_file+".png")
                        for lf in main_tree:
                            lf.add_feature("sequence", alg.get_seq(lf.safename))
                        try:
                            from ete2.tools.phylobuild_lib.visualize import draw_tree
                            draw_tree(main_tree, GLOBALS[configid], final_tree_file+".png")
                        except Exception, e:
                            log.warning('@@8:something went wrong when generating the tree image. Try manually :(@@1:')
                            if DEBUG:
                                import traceback, sys
                                traceback.print_exc(file=sys.stdout)

                    just_finished_lines.append("Finished %s in %d iteration(s)" %(
                            threadname, past_threads[configid]))
            if GLOBALS["email"]:
                if not pending_tasks:
                    all_lines = finished_lines + just_finished_lines + error_lines
                    send_mail(GLOBALS["email"], "Your NPR process has ended", '\n'.join(all_lines))

                elif GLOBALS["email_report_time"] and time() - last_report_time >= \
                        GLOBALS["email_report_time"]:
                    all_lines = info_lines + error_lines + just_finished_lines
                    send_mail(GLOBALS["email"], "Your NPR report", '\n'.join(all_lines))
                    last_report_time = time()

                elif just_finished_lines:
                    send_mail(GLOBALS["email"], "Finished threads!",
                              '\n'.join(just_finished_lines))

            log.log(26, "")
    except:
        raise 
        
    if thread_errors:
        log.error("Done with ERRORS")
    else:
        log.log(28, "Done")

    return thread_errors

    
def background_job_launcher(job_queue, run_detached, schedule_time, max_cores):
    running_jobs = {}
    visited_ids = set()
    # job_queue = [jid, cores, cmd, status_file]
    GLOBALS["myid"] = 'back_launcher'
    finished_states = set("ED")
    cores_used = 0
    dups = set()
    pending_jobs = deque()
    try:
        while True:
            launched = 0
            done_jobs = set()
            cores_used = 0
            for jid, (cores, cmd, st_file, pid) in running_jobs.iteritems():
                process_done = pid.poll() if pid else None
                try:
                    st = open(st_file).read(1)
                except IOError:
                    st = "?"
                #print pid.poll(), pid.pid, st
                if st in finished_states:
                     done_jobs.add(jid)
                elif process_done is not None and st == "R":
                    # check if a running job is actually running
                    print "LOST PROCESS", pid, jid
                    ST=open(st_file, "w"); ST.write("E"); ST.flush(); ST.close()
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
                        print "DUPLICATED execution!!!!!!!!!!!! This should not occur!", jid
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
                        running_proc = None
                        subprocess.call(cmd, shell=True)
                    else:
                        # create a process group, so I can kill the thread if necessary
                        running_proc = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
                        
                except Exception, e:
                    print e
                    ST=open(st_file, "w"); ST.write("E"); ST.flush(); ST.close()
                else:
                    launched += 1
                    running_jobs[jid] = [cores, cmd, st_file, running_proc]
                    cores_avail -= cores
                    cores_used += cores
                    visited_ids.add(jid)
            try:
                waiting_jobs = job_queue.qsize() + len(pending_jobs)
            except NotImplementedError: # OSX does not support qsize
                waiting_jobs = len(pending_jobs)
                
            log.log(28, "@@8:Launched@@1: %s jobs. %d(R), %s(W). Cores usage: %s/%s",
                    launched, len(running_jobs), waiting_jobs, cores_used, max_cores)
            for _d in dups:
                print "duplicate bug", _d

            sleep(schedule_time)
    except:
        if len(running_jobs):
            print >>sys.stderr, ' Killing %s running jobs...' %len(running_jobs)
            for jid, (cores, cmd, st_file, pid) in running_jobs.iteritems():
                if pid:
                    #print >>sys.stderr, ".",
                    #sys.stderr.flush()
                    try:
                        os.killpg(pid.pid, signal.SIGTERM)
                    except:
                        print "Ooops, the process", pid.pid, "could not be terminated!"
                        pass
                    try:
                        open(st_file, "w").write("E")
                    except:
                        print "Ooops,", st_file, "could not be labeled as Error task. Please remove file before resuming the analysis."
            
    sys.exit(0)

        
def launch_detached_process(cmd):
    os.system(cmd)
    
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
    tdir = task.taskid
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

