import os
import logging
import shutil
log = logging.getLogger("main")

from nprlib.master_task import AlgTask
from nprlib.master_job import Job
from nprlib.utils import (SeqGroup, OrderedDict, checksum, GLOBALS,
                          APP2CLASS, CLASS2MODULE)

import __init__ as task

__all__ = ["MetaAligner"]

def seq_reverser_job(multiseq_file, outfile, trimal_bin, parent_ids):
    """ Returns a job reversing all sequences in MSF or MSA. """
    reversion_args = {"-in": multiseq_file,
                      "-out": outfile,
                      "-reverse": "",
                      "-fasta": "",
                      }
    job = Job(trimal_bin, reversion_args, "TrimalAlgReverser",
              parent_ids=parent_ids)
    return job

class MCoffee(AlgTask):
    def __init__(self, nodeid, seqtype, all_alg_files, confname, parent_ids):
        GLOBALS["citator"].add("Wallace IM, O'Sullivan O, Higgins DG, Notredame C.",
                               "M-Coffee: combining multiple sequence alignment methods with T-Coffee.",
                               "Nucleic Acids Res. 2006 Mar 23;34(6):1692-9.")

        base_args = OrderedDict({
                "-output": "fasta",
                "-aln": ' '.join(all_alg_files)
                })
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Mcoffee", 
                         base_args, GLOBALS["config"][confname])
        self.all_alg_files = all_alg_files
        self.parent_ids = parent_ids
        self.seqtype = seqtype

        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

    def load_jobs(self):
        conf = GLOBALS["config"]
        args = self.args.copy()
        args["-outfile"] = "alg.fasta"
        job = Job(conf["app"]["tcoffee"], args, parent_ids=self.parent_ids)
        self.jobs.append(job)

    def finish(self):
        # Once executed, alignment is converted into relaxed
        # interleaved phylip format.
        alg = SeqGroup(os.path.join(self.jobs[0].jobdir, "alg.fasta"))
        alg.write(outfile=self.alg_fasta_file, format="fasta")
        alg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        self.dump_inkey_file(*self.all_alg_files)
        

class MetaAligner(AlgTask):
    def __init__(self, nodeid, multiseq_file, seqtype, confname):
        self.confname = confname
        # Initialize task
        AlgTask.__init__(self, nodeid, "alg", "Meta-Alg", 
                      OrderedDict(), GLOBALS["config"][confname])

        self.seqtype = seqtype
        self.multiseq_file = multiseq_file
        self.size = GLOBALS["nodeinfo"][nodeid].get("size", 0)
        
        self.init()
        self.alg_fasta_file = os.path.join(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = os.path.join(self.taskdir, "final_alg.iphylip")

        
    def load_jobs(self):
        conf = GLOBALS["config"]
        multiseq_file_r = self.multiseq_file+".reversed"
        first = seq_reverser_job(self.multiseq_file, multiseq_file_r, 
                                 conf["app"]["readal"],
                                 parent_ids=[self.nodeid])
        self.jobs.append(first)
        all_alg_files = []
        mcoffee_parents = []
        
        for aligner_name in conf[self.confname]["_aligners"]:
            _classname = APP2CLASS[conf[aligner_name]["_app"]]
            _module = __import__(CLASS2MODULE[_classname], globals(), locals(), [], -1)
            _aligner = getattr(_module, _classname)

            # Normal alg
            task1 = _aligner(self.nodeid, self.multiseq_file, self.seqtype,
                             aligner_name)
            task1.size = self.size
            self.jobs.append(task1)
            all_alg_files.append(task1.alg_fasta_file)
            
            # Alg of the reverse
            task2 = _aligner(self.nodeid, multiseq_file_r, self.seqtype,
                             aligner_name)
            task2.size = self.size
            task2.dependencies.add(first)
            self.jobs.append(task2)
            
            # Restore reverse alg
            task3 = seq_reverser_job(task2.alg_fasta_file,
                                     task2.alg_fasta_file+".reverse", 
                                     conf["app"]["readal"],
                                     parent_ids=[task2.taskid])
            task3.dependencies.add(task2)
            self.jobs.append(task3)
            
            all_alg_files.append(task2.alg_fasta_file+".reverse")
            mcoffee_parents.extend([task1.taskid, task2.taskid])
            
        # Combine signal from all algs using Mcoffee
        final_task = MCoffee(self.nodeid, self.seqtype, all_alg_files,
                             self.confname, parent_ids=mcoffee_parents)
        final_task.dependencies.update(self.jobs)
        self.jobs.append(final_task)
        
    def finish(self):
        final_task = self.jobs[-1]
        shutil.copy(final_task.alg_fasta_file, self.alg_fasta_file)
        shutil.copy(final_task.alg_fasta_file, self.alg_phylip_file)
        AlgTask.finish(self)
