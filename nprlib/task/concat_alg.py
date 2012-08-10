from os.path import join as pjoin 
import logging
from collections import defaultdict
log = logging.getLogger("main")

from nprlib.task import Msf
from nprlib.master_task import ConcatAlgTask
from nprlib.master_job import Job
from nprlib.utils import SeqGroup, GLOBALS, generate_runid, strip
from nprlib import db
from nprlib.errors import TaskError

__all__ = ["ConcatAlg"]

class ConcatAlg(ConcatAlgTask):
    def __init__(self, nodeid, cogs, seqtype):
        self.cogs_hard_limit = conf["alg_concat"]["_max_cogs"]
        base_args = {}
        base_args["_max_cogs"] = self.cogs_hard_limit
        
        ConcatAlgTask.__init__(self, nodeid, "concat_alg", "ConcatAlg", 
                      base_args)
        self.cogs = cogs
        self.seqtype = seqtype
        self.cog_ids = set()
        self.job2alg = {}
        self.job2model = {}
        self.default_model = "JTT"
        self.init()
        
        self.alg_fasta_file = pjoin(self.taskdir, "final_alg.fasta")
        self.alg_phylip_file = pjoin(self.taskdir, "final_alg.iphylip")
        self.partitions_file = pjoin(self.taskdir, "final_alg.regions")


        
    def load_jobs(self):
        # I want a single phylognetic tree for each cog
        from nprlib.template.genetree import pipeline
        
        for co in self.cogs[:self.cogs_hard_limit]:
            # Register a new msf task for each COG
            job = Msf(set(co), set(),
                      seqtype = self.seqtype)
            job.main_tree = None
            job.threadid = generate_runid()
            
            # This converts the job in a workflow job. As soon as a
            # task is done, it will be automatically processed and the
            # new tasks will be registered as new jobs.
            job.task_processor = pipeline
            self.jobs.append(job)
            self.cog_ids.add(job.nodeid)

    def finish(self):
        # Assumes tasks resulting from genetree workflow, in which
        # only Alg and Acleaner tasks could contain the results
        for job in self.jobs: 
            if job.ttype == "alg" and job.nodeid not in self.job2alg:
                self.job2alg[job.nodeid] = job.alg_fasta_file
            elif job.ttype == "acleaner":
                self.job2alg[job.nodeid] = job.clean_alg_fasta_file
            elif job.ttype == "mchooser":
                self.job2model[job.nodeid] = job.best_model
        if self.cog_ids - set(self.job2alg):
            log.error("Missing %s algs", len(self.cog_ids -
                                             set(self.job2alg)))
            raise TaskError(self)

        alg_data = [(self.job2alg[nid], self.job2model.get(nid, self.default_model)) for nid in self.job2alg]
        filenames, models = zip(*alg_data)

        mainalg, partitions, sp2alg, species = get_concatanted_alg(filenames,
                                    models, sp_field=0,
                                    sp_delimiter=GLOBALS["spname_delimiter"])
        mainalg.write(outfile=self.alg_fasta_file, format="fasta")
        mainalg.write(outfile=self.alg_phylip_file, format="iphylip_relaxed")
        open(self.partitions_file, "w").write('\n'.join(partitions))
        print '\n'.join(partitions)
                        
def get_species_code(name, splitter, field):
    # By default, taxid is the first par of the seqid, separated by
    # underscore
    return map(strip, name.split(splitter))[field]

def get_concatanted_alg(alg_filenames, models=None, 
                        sp_field=0, sp_delimiter="_", 
                        kill_thr=0.0, 
                        keep_species=set()):
    # Concat alg container 
    concat = SeqGroup()
    # Used to store different model partitions
    concat.id2partition = {}

    if not models: 
        models = ["None"]*len(alg_filenames)
    else:
        if len(models) != len(alg_filenames):
            raise ValueError("Different number of algs and model names was found!")

    expected_total_length = 0
    # Check algs and gets the whole set of species
    alg_objects = []
    sp2alg = defaultdict(list)
    
    for algfile, matrix in zip(alg_filenames, models):
        alg = SeqGroup(algfile, "fasta")
        alg_objects.append(alg)
        lenseq = None
        browsed_species = set()
        alg.sp2seq = {}
        # Set best matrix for this alignment
        alg.matrix = matrix
        # Change seq names to contain only species names
        for i, seq in alg.id2seq.iteritems():
            name = db.get_seq_name(alg.id2name[i])
            taxid = get_species_code(name, splitter=sp_delimiter, field=sp_field)
            if lenseq is not None and len(seq) != lenseq:
                raise Exception("Inconsistent alignment when concatenating: Unequal length")
            elif lenseq is None:
                lenseq = len(seq)
                alg.seqlength = len(seq)
                expected_total_length += len(seq)
            if taxid in browsed_species:
                raise Exception("Inconsistent alignment when concatenating: Repeated species")
            browsed_species.add(taxid) # Check no duplicated species in the same alg
            sp2alg[taxid].append(alg) # Records all species seen in all algs.
            alg.sp2seq[taxid] = seq

    valid_species = [sp for sp in sp2alg.iterkeys() \
                         if sp in keep_species or \
                         len(sp2alg[sp])/float(len(alg_objects)) > kill_thr]

    log.info("%d out of %d will be kept (missing factor threshold=%g, %d species forced to kept)" %\
                 (len(valid_species), len(sp2alg), kill_thr, len(keep_species)))
          
    sorted_algs = sorted(alg_objects, lambda x,y: cmp(x.matrix, y.matrix))
    model2win = {}
    model2size = {}
    for alg in sorted_algs:
        model2size[alg.matrix] = model2size.get(alg.matrix, 0) + alg.seqlength

    # Create concat alg
    concat.id2seq = defaultdict(list)
    for sp in sorted(valid_species):
        log.log(20, "Concatenating sequences of [%s]" %sp)
        for alg in sorted_algs:
            seq = alg.sp2seq.get(sp, "-" * alg.seqlength)
            concat.id2seq[sp].append(seq)
            #current_seq = concat.id2seq.get(sp, "")
            #concat.id2seq[sp] = current_seq + seq.strip()
            concat.id2name[sp] = sp 
            concat.name2id[sp] = sp
            concat.id2comment[sp] = [""]
        concat.id2seq[sp] = ''.join(concat.id2seq[sp])

    current_pos = 0
    partitions = []
    for model in sorted(model2size.keys()):
        size = model2size[model]
        part = "%s, %s = %d-%d" % (model, model+"_genes", \
                                       current_pos + 1,\
                                       current_pos + size)
        current_pos += size
        partitions.append(part)

    # Basic Checks
    seq_sizes = [len(seq) for seq in concat.id2seq.values()]
    if len(set(seq_sizes)) != 1:
        raise Exception("Concatenated alignment is not consistent: unequal seq length ")
    if seq_sizes[0] != expected_total_length:
        raise Exception("The size of concatenated alg is not what expected")
    return concat, partitions, sp2alg, valid_species

        
