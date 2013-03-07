import os
import logging
log = logging.getLogger("main")
from collections import defaultdict

from nprlib.logger import logindent
from nprlib.utils import (md5, merge_arg_dicts, PhyloTree, SeqGroup,
                          checksum, read_time_file, GLOBALS)
from nprlib.master_job import Job
from nprlib.errors import RetryException
from nprlib import db

isjob = lambda j: isinstance(j, Job)
istask = lambda j: isinstance(j, Task)

def genetree_class_repr(cls, cls_name):
    """ Human readable representation of NPR genetree tasks.""" 
    return "%s (%s seqs, %s, %s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6])

def sptree_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s species, %s, %s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6])
    
def generic_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s tips, %s, %s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         cls.tname, 
         (getattr(cls, "taskid", None) or "?")[:6])

    
class Task(object):
    def _get_max_cores(self):
        return max([j.cores for j in self.jobs]) or 1
            
    cores = property(_get_max_cores,None)
    
    def __repr__(self):
        return generic_class_repr(self, "Task")

    def print_summary(self):
        print "Type:", self.ttype
        print "Name:", self.tname
        print "Id:", self.taskid
        print "Dir:", self.taskdir
        print "Jobs", len(self.jobs)
        print "Status", self.status
        for tag, value in self.args.iteritems():
            print tag,":", value

    def __init__(self, nodeid, task_type, task_name, base_args={}, 
                 extra_args={}):
        
        # This define which task-processor should be used
        # (i.e. genetree, sptree).
        self.task_processor = None
        
        # Nodeid is used to identify the tree node associated with
        # the task. It is calculated as a hash string based on the
        # list of sequence IDs grouped by the node.
        self.nodeid = nodeid

        # task type: "alg|tree|acleaner|mchooser|etc."
        self.ttype = task_type

        # Used only to name directories and identify task in log
        # messages
        self.tname = task_name

        # Working directory for the task
        self.taskdir = None

        # Unique id based on the parameters set for each task
        self.taskid = None

        # Path to the file containing task status: (D)one, (R)unning
        # or (W)aiting or (Un)Finished
        self.status_file = None
        self.inkey_file = None
        self.info_file = None
        self.status = "W"
        self.all_status = None

        # keeps a counter of how many cores are being used by running jobs
        self.cores_used = 0
        
        self.job_status = {}
        
        # Initialize job arguments 
        self.args = merge_arg_dicts(extra_args, base_args, parent=self)

    def get_status(self, sge_jobs=None):
        logindent(2)
        saved_status = db.get_task_status(self.taskid)
        self.job_status = self.get_jobs_status(sge_jobs)
        job_status = set(self.job_status.keys())
        if job_status == set("D") and saved_status != "D":
            logindent(-2)
            log.log(20, "Processing done task: %s", self)
            logindent(2)
            try:
                self.finish()
            except RetryException:
                logindent(-2)
                return "W"
            else:
                st = "D"
        elif job_status == set("D") and saved_status == "D":
            st = "D"
        else:
            # Order matters
            if "E" in job_status:
                st = "E"
            elif "L" in job_status:
                st = "L"
            elif "R" in job_status: 
                st =  "R"
            elif "Q" in job_status: 
                st =  "Q"
            elif "W" in job_status: 
                st = "W"
            else:
                st = "?"

        if st == "D":
            if not self.check():
                log.error("Task check not passed")
                st = "E"
                
        #self.save_status(st)
        #db.update_task(self.taskid, status=st)
        self.status = st
        logindent(-2)
        return st

    def dump_inkey_file(self, *files):
        input_key = checksum(*files)
        open(self.inkey_file, "w").write(input_key)

    def init(self):

        # List of associated jobs necessary to complete the task. Job
        # and Task classes are accepted as elements in the list.
        self.jobs = []
       
        self._donejobs = set()
        self._running_jobs = set()
        self.dependencies = set()
       
        # Prepare required jobs
        self.load_jobs()
        
        # Set task information, such as task working dir and taskid
        self.load_task_info()
        # Set the working dir for all jobs
        # self.set_jobs_wd(self.taskdir)
        self.set_jobs_wd()

        OUT = open(self.info_file, "w")
        for j in self.jobs:
            if isjob(j):
                print >>OUT, j, j.jobdir
            elif istask(j):
                print >>OUT, j, j.taskdir
        OUT.close()
        
        #if db.get_task_status(self.taskid) is None:
        #    db.add_task(tid=self.taskid, nid=self.nodeid, parent=self.nodeid,
        #                status="W", type="task", subtype=self.ttype, name=self.tname)
        #for j in self.jobs:
        #    if isjob(j) and db.get_task_status(j.jobid) is None:
        #        db.add_task(tid=j.jobid, nid=self.nodeid, parent=self.taskid,
        #                    status="W", type="job", name=j.jobname)
        
    def get_saved_status(self):
        try:
            return open(self.status_file, "ru").read(1)
        except IOError: 
            return "?" 

    def get_jobs_status(self, sge_jobs=None):
        ''' Check the status of all children jobs. '''
        self.cores_used = 0
        all_states = defaultdict(int)
        jobs_to_check = list(reversed(self.jobs))
        while jobs_to_check:
            j = jobs_to_check.pop()
            logindent(1)
            if j not in self._donejobs:
                st = j.get_status(sge_jobs)
                all_states[st] += 1
                if st == "D":
                    self._donejobs.add(j)
                    # If task has an internal worflow processor,
                    # launch it and populate with new jobs
                    if istask(j) and j.task_processor:
                        for new_job in j.task_processor(j):
                            jobs_to_check.append(new_job)
                            self.jobs.append(new_job)
                elif st in set("QRL"):
                    if isjob(j) and not j.host.startswith("@sge"):
                        self.cores_used += j.cores
                    elif istask(j):
                        self.cores_used += j.cores_used
                elif st == "E":
                    log.log(20, "Error found in: %s", j)
                    errorpath = j.jobdir if isjob(j) else j.taskdir
                    log.log(20, "  %s", errorpath)
            else:
                all_states["D"] += 1
            logindent(-1)              

                
        if not all_states:
            all_states["D"] +=1
        return all_states

    def load_task_info(self):
        ''' Initialize task information. It generates a unique taskID
        based on the sibling jobs and sets task working directory. ''' 

        # Creates a task id based on its target node and job
        # arguments. The same tasks, including the same parameters
        # would raise the same id, so it is easy to check if a task is
        # already done in the working path. Note that this prevents
        # using.taskdir before calling task.init()
        if not self.taskid:
            args_id = md5(','.join(sorted(["%s %s" %(str(pair[0]),str(pair[1])) for pair in
                       self.args.iteritems()])))

            unique_id = md5(','.join([self.nodeid, args_id]+sorted(
                        [getattr(j, "jobid", "taskid") for j in self.jobs])))
            
            self.taskid = unique_id
            
        self.taskdir = os.path.join(GLOBALS["taskdir"], self.taskid)
            

        if not os.path.exists(self.taskdir):
            os.makedirs(self.taskdir)

        self.status_file = os.path.join(self.taskdir, "__status__")
        self.inkey_file = os.path.join(self.taskdir, "__inkey__")
        self.info_file = os.path.join(self.taskdir, "__info__")
        
    def save_status(self, status):
        open(self.status_file, "w").write(status)

    def set_jobs_wd(self):
        ''' Sets working directory of all sibling jobs '''
        for j in self.jobs:
            # Only if job is not another Task instance
            if isjob(j):
                path = os.path.join(GLOBALS["taskdir"], j.jobid)
                j.set_jobdir(path)

    def retry(self):
        for job in self.jobs:
            if job.get_status() == "E":
                if isjob(job):
                    job.clean()
                elif istask(job):
                    job.retry()
        self.status = "W"
        #self.post_init()

    def iter_waiting_jobs(self):
        for j in self.jobs:
            # Process only  jobs whose dependencies are satisfied
            if j.status == "W" and not (j.dependencies - self._donejobs): 
                if isjob(j):
                    j.dump_script()
                    cmd = "sh %s >%s 2>%s" %\
                        (j.cmd_file, j.stdout_file, j.stderr_file)
                    yield j, cmd
                elif istask(j):
                    for subj, cmd in j.iter_waiting_jobs():
                        yield subj, cmd

    def load_jobs(self):
        ''' Customizable function. It must create all job objects and add
        them to self.jobs'''

    def finish(self):
        ''' Customizable function. It must process all jobs and set
        the resulting values of the task. For instance, set variables
        pointing to the resulting file '''

    def check(self):
        ''' Customizable function. Return true if task is done and
        expected results are available. '''
        return True

    def post_init(self):
        '''Customizable function. Put here or the initialization steps
        that must run after init (load_jobs, taskid, etc). 
        '''

class MsfTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@6:MultiSeqTask@@1:")
        
class AlgTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@5:AlgTask@@1:")

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file) and \
                os.path.getsize(self.alg_fasta_file) and \
                os.path.getsize(self.alg_phylip_file):
            return True
        return False

    def finish(self):
        self.dump_inkey_file(self.alg_fasta_file, 
                             self.alg_phylip_file)

class AlgCleanerTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@4:AlgCleanerTask@@1:")

    def check(self):
        if os.path.exists(self.clean_alg_fasta_file) and \
                os.path.exists(self.clean_alg_phylip_file) and \
                os.path.getsize(self.clean_alg_fasta_file) and \
                os.path.getsize(self.clean_alg_phylip_file):
            return True
        return False

    def finish(self):
        self.dump_inkey_file(self.alg_fasta_file, 
                             self.alg_phylip_file)


class ModelTesterTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@2:ModelTesterTask@@1:")

    def get_best_model(self):
        return open(self.best_model_file, "ru").read()

    def check(self):
        if not os.path.exists(self.best_model_file) or\
                not os.path.getsize(self.best_model_file):
            return False
        elif self.tree_file:
            if not os.path.exists(self.tree_file) or\
                    not os.path.getsize(self.tree_file):
                return False
        return True

    def finish(self):
        self.dump_inkey_file(self.alg_fasta_file, 
                             self.alg_phylip_file)

class TreeTask(Task):
    def __repr__(self):
        return generic_class_repr(self, "@@3:TreeTask@@1:")

    def check(self):
        if os.path.exists(self.tree_file) and \
                os.path.getsize(self.tree_file):
            return True
        return False

    def finish(self):
        self.dump_inkey_file(self.alg_phylip_file)

class TreeMergeTask(Task):
    def __repr__(self):
        return generic_class_repr(self, "@@3:TreeMergeTask@@1:")
       

class ConcatAlgTask(Task):
    def __repr__(self):
        return sptree_class_repr(self, "@@5:ConcatAlgTask@@1:")

    def check(self):
        if os.path.exists(self.alg_fasta_file) and \
                os.path.exists(self.alg_phylip_file) and \
                os.path.getsize(self.alg_fasta_file) and \
                os.path.getsize(self.alg_phylip_file):
            return True
        return False

class CogSelectorTask(Task):
    def __repr__(self):
        return sptree_class_repr(self, "@@6:CogSelectorTask@@1:")

    def check(self):
        if len(self.cogs) > 1:
            return True
        return False
        
    
def register_task_recursively(task, parentid=None):
    db.add_task(tid=task.taskid, nid=task.nodeid, parent=parentid,
                status=task.status, type="task", subtype=task.ttype, name=task.tname)
    for j in task.jobs:
        if isjob(j):
            db.add_task(tid=j.jobid, nid=task.nodeid, parent=task.taskid,
                        status="W", type="job", name=j.jobname)
            
        else:
            register_task_recursively(j, parentid=parentid)

def update_task_states_recursively(task):
    task_start = 0
    task_end = 0
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
                else:
                    task_start = min(task_start, start) if task_start > 0 else start
                    task_end = max(task_end, end)
            db.update_task(j.jobid, status=j.status, tm_start=start, tm_end=end)
        else:
            update_task_states_recursively(j)
    db.update_task(task.taskid, status=task.status)

        
