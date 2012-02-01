import os
from subprocess import call, Popen
from time import sleep, ctime
from collections import defaultdict
import logging
from logger import set_logindent, logindent
log = logging.getLogger("main")

from nprlib.utils import get_cladeid, render_tree, HOSTNAME
from nprlib.errors import ConfigError, DataError, TaskError
from nprlib import db, sge

def sort_tasks(x, y):
    if getattr(x,"nseqs", 0) > getattr(y,"nseqs", 0):
        return 1
    elif getattr(x,"nseqs", 0) < getattr(y,"nseqs", 0):
        return -1
    else:
        return 0

def schedule(config, processer, schedule_time, execution, retry):
    # Send seed files to processer to generate the initial task
    pending_tasks, main_tree = processer(None, None, 
                                         config)
    clade2tasks = defaultdict(list)
    # Then enters into the pipeline.
    cores_total = config["main"]["_max_cores"]

    while pending_tasks:
        cores_used = 0
        wait_time = 0.1 # Try to go fast unless running tasks
        set_logindent(0)
        log.log(28, ctime())
        log.log(28, "Checking the status of %d tasks" %len(pending_tasks))
        log.log(28, "------------------------------------")

        # Check task status and compute total cores being used
        if execution == "sge":
            sgeid2jobs = db.get_sge_jobids()
            qstat_jobs = sge.qstat()
        else:
            qstat_jobs = None
      
        for task in pending_tasks:
            task.status = task.get_status(qstat_jobs)
            cores_used += task.cores_used
           
            
        sge_jobs = []
        for task in sorted(pending_tasks, sort_tasks):
            print
            set_logindent(1)
            log.log(28, "(%s) %s" %(task.status, task))
            logindent(2)
            st_info = ', '.join(["%d(%s)" %(v,k) for k,v in task.job_status.iteritems()])
            log.log(28, "%d jobs: %s" %(len(task.jobs), st_info))
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
                
            if task.status in set("WQRL"):
                exec_type = getattr(task, "exec_type", execution)
                # shows info about unfinished jobs
                logindent(2)
                for j in task.jobs:
                    if j.status != "D":
                        log.log(24, "%s: %s", j.status, j)
                logindent(-2)

                # Tries to send new jobs from this task
                for j, cmd in task.iter_waiting_jobs():
                    if not check_cores(j, cores_used, cores_total, execution):
                        continue
                    
                    if exec_type == "insitu":
                        log.log(28, "Launching %s" %j)
                        try:
                            launch_detached(j, cmd)
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
                        print cmd
                if task.status in set("QRL"):
                    wait_time = schedule_time
                    
            elif task.status == "D":
                logindent(3)
                new_tasks, main_tree = processer(task, main_tree, config)
                logindent(-3)
                pending_tasks.remove(task)
                pending_tasks.extend(new_tasks)
                clade2tasks[task.cladeid].append(task)

            elif task.status == "E":
                log.error("Task contains errors")
                if retry:
                    log.log(28, "Remarking task as undone to retry")
                    task.retry()
                else:
                    raise TaskError(task)

            else:
                wait_time = schedule_time
                log.error("Unknown task state [%s].", task.status)
                continue
            logindent(-2)
            log.log(26, "Cores in use: %s" %cores_used)

            # If last task processed a new tree node, dump snapshots
            if task.ttype == "treemerger":
                log.info("Annotating tree")
                annotate_tree(main_tree, clade2tasks)
                nw_file = os.path.join(config["main"]["basedir"],
                                       "tree_snapshots", task.cladeid+".nw")
                main_tree.write(outfile=nw_file, features=[])
                
                if config["main"]["render_tree_images"]:
                    log.log(28, "Rendering tree image")
                    img_file = os.path.join(config["main"]["basedir"], 
                                            "gallery", task.cladeid+".svg")
                    render_tree(main_tree, img_file)


        sge.launch_jobs(sge_jobs, config)
        sleep(wait_time)
        print 

    final_tree_file = os.path.join(config["main"]["basedir"], \
                                       "final_tree.nw")
    main_tree.write(outfile=final_tree_file)
    log.debug(str(main_tree))
    main_tree.show()

def annotate_tree(t, clade2tasks):
    n2names = get_node2content(t)
    for n in t.traverse():
        n.add_features(cladeid=get_cladeid(n2names[n]))
    
    clade2node = dict([ (n.cladeid, n) for n in t.traverse()])
    for cladeid, alltasks in clade2tasks.iteritems():
        n = clade2node[cladeid]
        for task in alltasks:

            params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                      if not k.startswith("_")]
            params = " ".join(params)

            if task.ttype == "msf":
                n.add_features(nseqs=task.nseqs, 
                               msf_file=task.seed_file)
            elif task.ttype == "acleaner":
                n.add_features(clean_alg_mean_identn=task.mean_ident, 
                               clean_alg_std_ident=task.std_ident, 
                               clean_alg_max_ident=task.max_ident, 
                               clean_alg_min_ident=task.min_ident, 
                               clean_alg_type=task.tname, 
                               clean_alg_cmd=params)
            elif task.ttype == "alg":
                n.add_features(alg_mean_identn=task.mean_ident, 
                               alg_std_ident=task.std_ident, 
                               alg_max_ident=task.max_ident, 
                               alg_min_ident=task.min_ident, 
                               alg_type=task.tname, 
                               alg_cmd=params)
            elif task.ttype == "tree":
                n.add_features(tree_model=task.model, 
                               tree_seqtype=task.seqtype, 
                               tree_type=task.tname, 
                               tree_cmd=params)
            elif task.ttype == "mchooser":
                n.add_features(modeltester_models=task.models, 
                               modeltester_type=task.tname, 
                               modeltester_params=params, 
                               modeltester_bestmodel=task.get_best_model(), 
                               )
            elif task.ttype == "tree_merger":
                n.add_features(treemerger_type=task.tname, 
                               treemerger_hidden_outgroup=task.outgroup_topology, 
                               )

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
    if pid1 == 0:
        pid2 = os.fork()
   
        if pid2 == 0:	
            os.setsid()
            pid3 = os.fork()
            if pid3 == 0:
                os.chdir("/")
                os.umask(0)
                P = Popen(cmd, shell=True)
                db.update_job(j.jobid, pid=P.pid, host=HOSTNAME)
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
