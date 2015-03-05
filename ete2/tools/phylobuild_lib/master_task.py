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
import os
import logging
import traceback
log = logging.getLogger("main")
from collections import defaultdict

from ete2.tools.phylobuild_lib.logger import logindent
from ete2.tools.phylobuild_lib.utils import (md5, merge_arg_dicts, PhyloTree, SeqGroup,
                          checksum, read_time_file, generate_runid,
                          GLOBALS, DATATYPES)
from ete2.tools.phylobuild_lib.master_job import Job
from ete2.tools.phylobuild_lib.errors import TaskError
from ete2.tools.phylobuild_lib import db
import shutil

isjob = lambda j: isinstance(j, Job)
istask = lambda j: isinstance(j, Task)

def thread_name(task):
    tid = getattr(task, "threadid", None)
    if hasattr(task, 'target_wkname'):
        name = getattr(task, 'target_wkname')
    else:
        name = GLOBALS.get(tid, {}).get("_name", "?")

    if GLOBALS.get('verbosity', 4) < 2:
        if len(name)>23:
            name = "%s...%s" %(name[:10], name[-10:])
    return "@@13:%s@@1:" %name

def genetree_class_repr(cls, cls_name):
    """ Human readable representation of NPR genetree tasks.""" 
    return "%s (%s %s seqs, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or "", getattr(cls, "seqtype", None) or 0,
         cls.tname, 
         "", #(getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def sptree_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s species, %s, %s/%s)" %\
        (cls_name,
         getattr(cls, "size", None) or 0,
         cls.tname,
         "", #(getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def concatalg_class_repr(cls, cls_name):
    """ Human readable representation of NPR  concat alg tasks.""" 
    return "%s (%s species, %s COGs, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or 0,
         getattr(cls, "used_cogs", None) or "?",
         cls.tname, 
         "", #(getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

def generic_class_repr(cls, cls_name):
    """ Human readable representation of NPR sptree tasks.""" 
    return "%s (%s %s seqs, %s, %s/%s)" %\
        (cls_name, getattr(cls, "size", None) or 0, getattr(cls, "seqtype", None) or "",
         cls.tname, 
         "", #(getattr(cls, "taskid", None) or "?")[:6],
         thread_name(cls))

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
        
    def __init__(self, nodeid, task_type, task_name, base_args=None,
                 extra_args=None):

        if not base_args: base_args = {}
        if not extra_args: extra_args = {}

        self.taskid = None
        
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

        # Path to the file containing task status: (D)one, (R)unning
        # or (W)aiting or (Un)Finished
        #self.status_file = None
        #self.inkey_file = None
        #self.info_file = None
        self.status = "W"
        self.all_status = None

        # keeps a counter of how many cores are being used by running jobs
        self.cores_used = 0
        
        self.job_status = {}
        
        # Set arguments that could be sent to jobs
        self.args = merge_arg_dicts(extra_args, base_args, parent=self)
        
        # extract all internal config values associated to this task
        # and generate its unique id (later used to generate taskid)
        self._config_id = md5(','.join(sorted(["%s %s" %(str(pair[0]),str(pair[1])) for pair in
                                       extra_args.iteritems() if pair[0].startswith("_")])))
        self.dependencies = set()
        
    def get_status(self, sge_jobs=None):
        # If another tasks with the same id (same work to be done) has
        # been checked in the same cycle, reuse its information
        if self.taskid in GLOBALS["cached_status"]:
            return GLOBALS["cached_status"][self.taskid]

        # Otherwise check the status or all its children jobs and
        # tasks
        logindent(2)

        #last_status = db.get_last_task_status(self.taskid)
        task_saved = db.task_is_saved(self.taskid)

        # If task is processed and saved, just return its state
        # without checking children
        if task_saved and self.status == "D":
            log.log(24, "@@8:Task is done and processed@@1:")
            self.status = "D"
        # If I have just noticed the task is done and saved, load its
        # stored data.
        elif task_saved and self.status != "D":
            log.log(26, "@@8:Loading pre-computed data@@1:")
            self.status = "D"
            self.load_stored_data()
        else:
            # Otherwise, we need to check for all children
            self.job_status = self.get_jobs_status(sge_jobs)
            job_statuses = set(self.job_status.keys())
            # If all children jobs have just finished, we process the
            # task, and save it into the database
            if job_statuses == set("D"):
                logindent(-2)
                log.log(22, "Processing done task: %s", self)
                logindent(2)
                try:
                    self.finish()
                except Exception, e:
                    print traceback.print_exc()
                    raise TaskError(self, e)
                else:
                    #store in database .......
                    if self.check():
                        self.status = "D"
                    elif self.status == "!":
                        #this means the finish procedure has generate
                        #new jobs associated to the task, so it
                        #requires relaunching
                        self.status = "W"
                    else:
                        # Otherwise, everything point to errors when
                        # processing
                        raise TaskError(self, "Task check not passed")
            # Otherwise, update the ongoing task status, but do not
            # store result yet.
            else: 
                # Order matters
                if "E" in job_statuses:
                    self.status = "E"
                elif "L" in job_statuses:
                    self.status = "L"
                elif "R" in job_statuses: 
                    self.status =  "R"
                elif "Q" in job_statuses: 
                    self.status =  "Q"
                elif "W" in job_statuses: 
                    self.status = "W"
                else:
                    log.error("unknown task state %s" %(job_statuses))

        logindent(-2)
        
        GLOBALS["cached_status"][self.taskid] = self.status
        return self.status

    def init(self):
        # List of associated jobs necessary to complete the task. Job
        # and Task classes are accepted as elements in the list.
        self.jobs = []
       
        self._donejobs = set()
        self._running_jobs = set()
       
        # Prepare required jobs
        self.load_jobs()
        
        # Set task information, such as taskid
        self.load_task_info()

        # Now taskid is set, so we can save output file ids
        self.init_output_info()
        
    def get_saved_status(self):
        try:
            return open(self.status_file, "ru").read(1)
        except IOError: 
            return "?"
       
    def get_jobs_status(self, sge_jobs=None):
        ''' Check the status of all children jobs. '''
        self.cores_used = 0
        all_states = defaultdict(int)
        jobs_to_check = set(reversed(self.jobs))
        while jobs_to_check:
            j = jobs_to_check.pop()
            logindent(1)
            jobid = j.taskid if istask(j) else j.jobid
            
            if jobid in GLOBALS["cached_status"]:
                log.log(22, "@@8:Recycling status@@1: %s" %j)
                st = GLOBALS["cached_status"][jobid]
                all_states[st] += 1
                
            elif j not in self._donejobs:
                st = j.get_status(sge_jobs)
                GLOBALS["cached_status"][jobid] = st
                all_states[st] += 1
                if st == "D":
                    self._donejobs.add(j)
                    # If task has an internal worflow processor,
                    # launch it and populate with new jobs
                    if istask(j) and j.task_processor:
                        pipeline = j.task_processor
                        target_workflow = j.target_wkname
                        for new_job in pipeline(j, target_workflow):
                            jobs_to_check.add(new_job)
                            self.jobs.append(new_job)

                elif st in set("QRL"):
                    if isjob(j) and not j.host.startswith("@sge"):
                        self.cores_used += j.cores
                    elif istask(j):
                        self.cores_used += j.cores_used
                elif st == "E":
                    errorpath = j.jobdir if isjob(j) else j.taskid
                    raise TaskError(j, "Job execution error %s" %errorpath)
            else:
                all_states["D"] += 1
                
            logindent(-1)              
        if not all_states:
            all_states["D"] +=1

        return all_states

    def load_task_info(self):
        ''' Initialize task information. It generates a unique taskID based on
        the sibling jobs and sets task working directory.''' 

        # Creates a task id based on its target node and job arguments. The same
        # tasks, including the same parameters would raise the same id, so it is
        # easy to check if a task is already done in the working path.
        if not self.taskid:
            args_id = md5(','.join(sorted(["%s %s" %(str(pair[0]), str(pair[1]))
                                           for pair in self.args.iteritems()])))
             
            unique_id = md5(','.join([self.nodeid, self._config_id, args_id] +\
                                         sorted([getattr(j, "jobid", "taskid")
                                                 for j in self.jobs])))
            self.taskid = unique_id

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
            st = j.status
            if st == "W" and not (j.dependencies - self._donejobs):
                if hasattr(j, "_post_dependencies_hook"):
                    j._post_dependencies_hook()
                    
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
        pointing to the resulting file'''

    def check(self):
        ''' Customizable function. Return true if task is done and
        expected results are available. '''
        return True

    def post_init(self):
        '''Customizable function. Put here or the initialization steps
        that must run after init (load_jobs, taskid, etc). 
        '''
    def store_data(self, DB):
        ''' This should store in the database all relevant data
        associated to the task '''
        pass
    def init_output_info(self):
        ''' This should set the expected file ids of task output '''
        pass
    def load_stored_data(self):
        ''' Restore data from DB if available '''
        pass

class MsfTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@6:MultiSeqTask@@1:")

    def init_output_info(self):
        self.multiseq_file = "%s.%s" %(self.taskid, DATATYPES.msf)
    
    def load_stored_data(self):
        pass
            
    def store_data(self, msf):
        db.add_task_data(self.taskid, DATATYPES.msf, msf)
        
    def check(self):
        if self.multiseq_file:
            return True
        return False
        
class AlgTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@5:AlgTask@@1:")
   
    def check(self):
        if self.alg_fasta_file and self.alg_phylip_file:
            return True
        return False
    
    def init_output_info(self):
        self.alg_fasta_file = "%s.%s" %(self.taskid, DATATYPES.alg_fasta)
        self.alg_phylip_file = "%s.%s" %(self.taskid, DATATYPES.alg_phylip)
        
    def store_data(self, fasta, phylip):
        # self.alg_fasta_file = db.add_task_data(self.taskid, DATATYPES.alg_fasta,
        #                                        fasta)
        # self.alg_phylip_file = db.add_task_data(self.taskid,
        #                                         DATATYPES.alg_phylip, phylip)
        db.add_task_data(self.taskid, DATATYPES.alg_fasta, fasta)
        db.add_task_data(self.taskid, DATATYPES.alg_phylip, phylip)
                
class AlgCleanerTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@4:AlgCleanerTask@@1:")
   
    def check(self):
        if self.clean_alg_fasta_file and \
                self.clean_alg_phylip_file: 
            return True
        return False

    def init_output_info(self):
        self.clean_alg_fasta_file = "%s.%s" %(self.taskid,
                                                  DATATYPES.clean_alg_fasta)
        self.clean_alg_phylip_file = "%s.%s" %(self.taskid,
                                               DATATYPES.clean_alg_phylip)
        self.kept_columns = []
       
    def load_stored_data(self):
        self.kept_columns[:] = [] # clear list
        self.kept_columns.append(
            db.get_task_data(self.taskid, DATATYPES.kept_alg_columns))

    def store_data(self, fasta, phylip, kept_columns):
        db.add_task_data(self.taskid, DATATYPES.clean_alg_fasta, fasta)
        db.add_task_data(self.taskid, DATATYPES.clean_alg_phylip, phylip)
        db.add_task_data(self.taskid, DATATYPES.kept_alg_columns, kept_columns)
        self.kept_columns[:] = [] # security clear
        self.kept_columns.extend(kept_columns)
        
class ModelTesterTask(Task):
    def __repr__(self):
        return genetree_class_repr(self, "@@2:ModelTesterTask@@1:")

    def check(self):
        if self.best_model and self.model_ranking:
            return True
        return False

    def init_output_info(self):
        self.best_model = ""
        self.model_ranking = []
            
    def store_data(self, best_model, ranking):
        db.add_task_data(self.taskid, DATATYPES.best_model, best_model)
        db.add_task_data(self.taskid, DATATYPES.model_ranking, ranking)
        self.best_model = best_model
        self.model_ranking[:] = []
        self.model_ranking.extend(ranking)
        
    def load_stored_data(self):
        self.best_model = db.get_task_data(self.taskid, DATATYPES.best_model)
        self.model_ranking = db.get_task_data(self.taskid, DATATYPES.model_ranking)
        #print self.best_model, self.model_ranking
        
class TreeTask(Task):
    def __init__(self, nodeid, task_type, task_name, base_args=None, 
                 extra_args=None):
        if not base_args: base_args = {}
        extra_args = {} if not extra_args else dict(extra_args)
        extra_args["_alg_checksum"] = self.alg_phylip_file
        extra_args["_constrain_checksum"] = getattr(self, "constrain_tree", None)
        extra_args["_partitions_checksum"] = getattr(self, "partitions_file", None)

        Task.__init__(self, nodeid, task_type, task_name, base_args, 
                      extra_args)
        
    def __repr__(self):
        return generic_class_repr(self, "@@3:TreeTask@@1:")

    def check(self):
        if self.tree_file: 
            return True
        return False

    def init_output_info(self):
        self.tree_file = "%s.%s" %(self.taskid, DATATYPES.tree)
    
    def load_stored_data(self):
        # self.tree_file = db.get_dataid(self.taskid, DATATYPES.tree)
        self.stats = db.get_task_data(self.taskid, DATATYPES.tree_stats)
        
    def store_data(self, newick, stats):
        db.add_task_data(self.taskid, DATATYPES.tree, newick)
        db.add_task_data(self.taskid, DATATYPES.tree_stats, stats)
        self.stats = stats
    
class TreeMergeTask(Task):
    def __init__(self, nodeid, task_type, task_name, base_args=None, 
                 extra_args=None):
        # I want every tree merge instance to be unique (avoids recycling and
        # undesired collisions between trees from different threads containing
        # the same topology, so I create a random checksum to compute taskid
        extra_args = {} if not extra_args else dict(extra_args)
        extra_args["_treechecksum"] = generate_runid()
        Task.__init__(self, nodeid, task_type, task_name, base_args, 
                      extra_args)

    def __repr__(self):
        return generic_class_repr(self, "@@7:TreeMergeTask@@1:")
       

class ConcatAlgTask(Task):
    def __init__(self, nodeid, task_type, task_name, workflow_checksum,
                 base_args=None, extra_args=None,):
        if not base_args: base_args = {}
        extra_args = {} if not extra_args else dict(extra_args)
        extra_args["_workflow_checksum"] = workflow_checksum
        Task.__init__(self, nodeid, task_type, task_name, base_args, 
                      extra_args)
           
    def __repr__(self):
        return concatalg_class_repr(self, "@@5:ConcatAlgTask@@1:")

    def check(self):
        if self.alg_fasta_file and self.alg_phylip_file: 
            return True
        return False

    def init_output_info(self):
        self.partitions_file = "%s.%s" %(self.taskid, DATATYPES.model_partitions)
        self.alg_fasta_file = "%s.%s"  %(self.taskid, DATATYPES.concat_alg_fasta)
        self.alg_phylip_file = "%s.%s" %(self.taskid, DATATYPES.concat_alg_phylip)
        
    def store_data(self, fasta, phylip, partitions):
        db.add_task_data(self.taskid, DATATYPES.model_partitions, partitions)
        db.add_task_data(self.taskid, DATATYPES.concat_alg_fasta, fasta)
        db.add_task_data(self.taskid, DATATYPES.concat_alg_phylip, phylip)
        
        
class CogSelectorTask(Task):
    def __repr__(self):
        return sptree_class_repr(self, "@@6:CogSelectorTask@@1:")

    def check(self):
        if self.cogs:
            return True
        return False

    def load_stored_data(self):
        self.cogs = db.get_task_data(self.taskid, DATATYPES.cogs)
        self.cog_analysis = db.get_task_data(self.taskid,
                                             DATATYPES.cog_analysis)
    
    def store_data(self, cogs, cog_analysis):
        db.add_task_data(self.taskid, DATATYPES.cogs, cogs)
        db.add_task_data(self.taskid, DATATYPES.cog_analysis, cog_analysis)
        self.cogs = cogs
        self.cog_analysis = cog_analysis
        
def register_task_recursively(task, parentid=None):
    db.add_task(tid=task.taskid, nid=task.nodeid,
                parent=parentid, status=task.status, type="task",
                subtype=task.ttype, name=task.tname)
    for j in task.jobs:
        if isjob(j):
            db.add_task(tid=j.jobid, nid=task.nodeid,
                        parent=task.taskid, status="W", type="job",
                        name=j.jobname)
        else:
            register_task_recursively(j, parentid=task.taskid)
    
def update_task_states_recursively(task):
    task_start = 0
    task_end = 0
    for j in task.jobs:
        if isjob(j):
            start, end = update_job_status(j)
        else:
            start, end = update_task_states_recursively(j)
        task_start = min(task_start, start) if task_start > 0 else start
        task_end = max(task_end, end)
        
    db.update_task(task.taskid, status=task.status, tm_start=task_start, tm_end=task_end)
    return task_start, task_end

def store_task_data_recursively(task):
    # store task data
    task.store_data(db)
    for j in task.jobs:
        if isjob(j):
            pass
        else:
            store_task_data_recursively(j)

def remove_task_dir_recursively(task):
    # store task data
    for j in task.jobs:
        if isjob(j):
            shutil.rmtree(j.jobdir)
        else:
            remove_task_dir_recursively(j)
    shutil.rmtree(task.taskdir)
            
def update_job_status(j):
    start = None
    end = None
    if j.status == "D":
        try:
            start, end = read_time_file(j.time_file)
        except Exception, e:
            log.warning("Execution time could not be loaded into DB: %s", j.jobid[:6])
            log.warning(e)
    db.update_task(j.jobid, status=j.status, tm_start=start, tm_end=end)
    return start, end
