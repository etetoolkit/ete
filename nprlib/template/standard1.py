import numpy 
import re
import commands
import logging
import numpy
from collections import defaultdict

from nprlib.utils import del_gaps, GENCODE, PhyloTree, SeqGroup, TreeStyle
from nprlib.task import (MetaAligner, Mafft, Muscle, Uhire, Dialigntx, FastTree,
                   Clustalo, Raxml, Phyml, JModeltest, Prottest, Trimal,
                   TreeMerger, Msf)
from nprlib.errors import DataError

log = logging.getLogger("main")

n2class = {
    "none": None, 
    "meta_aligner":MetaAligner, 
    "mafft":Mafft, 
    "muscle":Muscle, 
    "uhire":Uhire, 
    "dialigntx":Dialigntx, 
    "fasttree":FastTree, 
    "clustalo": Clustalo, 
    "raxml": Raxml,
    "phyml": Phyml,
    "jmodeltest": JModeltest,
    "prottest": Prottest,
    "trimal": Trimal
    }

def get_trimal_conservation(alg_file, trimal_bin):
    output = commands.getoutput("%s -ssc -in %s" %\
                                    (trimal_bin, alg_file))
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = map(float, line.split())
        conservation.append(b)
    mean = numpy.mean(conservation)
    std =  numpy.std(conservation)
    return mean, std

def get_trimal_identity(alg_file, trimal_bin):
    #print "%s -sident -in %s" %\
    #    (trimal_bin, alg_file)
    output = commands.getoutput("%s -sident -in %s" %\
                                    (trimal_bin, alg_file))
    #print output
    conservation = []
    for line in output.split("\n"):
        m = re.search("#MaxIdentity\s+(\d+\.\d+)", line)
        if m: 
            max_identity = float(m.groups()[0])
    return max_identity

def get_identity(fname): 
    log.log(28, "Calculating alg stats...")
    s = SeqGroup(fname)
    seqlen = len(s.id2seq.itervalues().next())
    ident = list()
    for i in xrange(seqlen):
        states = defaultdict(int)
        for seq in s.id2seq.itervalues():
            if seq[i] != "-":
                states[seq[i]] += 1
        values = states.values()
        if values:
            ident.append(float(max(values))/sum(values))
    return (numpy.min(ident), numpy.max(ident), 
            numpy.mean(ident), numpy.std(ident))

         
def switch_to_codon(alg_fasta_file, alg_phylip_file, nt_seed_file, 
                    kept_columns=[]):
    GAP_CHARS = set(".-")
    NUCLEOTIDES = set("ATCG") 
    # Check conservation of columns. If too many identities,
    # switch to codon alignment and make the tree with DNA. 
    # Mixed models is another possibility.
    kept_columns = set(map(int, kept_columns))
    all_nt_alg = SeqGroup(nt_seed_file)
    aa_alg = SeqGroup(alg_fasta_file)
    nt_alg = SeqGroup()

    for seqname, aaseq, comments in aa_alg.iter_entries():
        ntseq = all_nt_alg.get_seq(seqname).upper()
        ntalgseq = []
        nt_pos = 0
        for pos, ch in enumerate(aaseq):
            if ch in GAP_CHARS:
                codon = "---"
            else:
                codon = ntseq[nt_pos:nt_pos+3]
                nt_pos += 3

            if not kept_columns or pos in kept_columns: 
                ntalgseq.append(codon)
                # If codon does not contain unknown symbols, check
                # that translation is correct
                if not (set(codon) - NUCLEOTIDES) and GENCODE[codon] != ch:
                    log.error("[%s] CDS does not match protein sequence:"
                              " %s = %s not %s at pos %d" %\
                                  (seqname, codon, GENCODE[codon], ch, nt_pos))
                    raise ValueError()

        ntalgseq = "".join(ntalgseq)
        nt_alg.set_seq(seqname, ntalgseq)

    alg_fasta_filename = alg_fasta_file + ".nt"
    alg_phylip_filename = alg_phylip_file + ".nt"
    nt_alg.write(outfile=alg_fasta_filename, format="fasta")
    nt_alg.write(outfile=alg_phylip_filename, format="iphylip_relaxed")
        
    return alg_fasta_filename, alg_phylip_filename

def process_task(task, main_tree, conf):
    aa_seed_file = conf["main"]["aa_seed"]
    nt_seed_file = conf["main"]["nt_seed"]
    seqtype = task.seqtype
    nodeid = task.nodeid
    nseqs = task.nseqs
    sst = conf["main"]["DNA_sst"]
    sit = conf["main"]["DNA_sit"]
    sct = conf["main"]["DNA_sct"]
    ttype = task.ttype

    # Loads application handlers according to current task size
    index = None
    index_slide = 0
    while index is None: 
        try: 
            max_seqs = conf["main"]["npr_max_seqs"][index_slide]
        except IndexError:
            raise DataError("Number of seqs [%d] not considered"
                             " in current config" %nseqs)
        else:
            if nseqs <= max_seqs:
                index = index_slide
            else:
                index_slide += 1

    if seqtype == "nt": 
        _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_nt_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
    elif seqtype == "aa": 
        _aligner = n2class[conf["main"]["npr_aa_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_aa_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_aa_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_aa_tree_builder"][index]]

    #print (nseqs, index, _alg_cleaner, _model_tester, _aligner, _tree_builder)
    
    new_tasks = []
    if ttype == "msf":
        alg_task = _aligner(nodeid, task.multiseq_file,
                           seqtype, conf)
        alg_task.nseqs = nseqs
        new_tasks.append(alg_task)

    elif ttype == "alg" or ttype == "acleaner":
        alg_fasta_file = getattr(task, "clean_alg_fasta_file", 
                                 task.alg_fasta_file)
        alg_phylip_file = getattr(task, "clean_alg_phylip_file", 
                                  task.alg_phylip_file)

        # Calculate alignment stats           
        # cons_mean, cons_std = get_trimal_conservation(task.alg_fasta_file, 
        #                                        conf["app"]["trimal"])
        #  
        # max_identity = get_trimal_identity(task.alg_fasta_file, 
        #                                 conf["app"]["trimal"])
        # log.info("Conservation: %0.2f +-%0.2f", cons_mean, cons_std)
        # log.info("Max. Identity: %0.2f", max_identity)


        mx, mn, mean, std = get_identity(task.alg_fasta_file)
        log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
                 mx, mn, mean, std)
        task.max_ident = mx
        task.min_ident = mx
        task.mean_ident = mean
        task.std_ident = std

        if ttype == "alg" and _alg_cleaner:
            next_task = _alg_cleaner(nodeid, seqtype, alg_fasta_file, 
                                     alg_phylip_file, conf)
        else:
            # Converts aa alignment into nt if necessary
            if seqtype == "aa" and nt_seed_file and \
                    task.nseqs <= sst and task.mean_ident > sit:

                    log.log(26, "switching to codon alignment")
                    # Change seqtype config 
                    seqtype = "nt"
                    _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
                    _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
                    _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
                    alg_fasta_file, alg_phylip_file = switch_to_codon(
                        task.alg_fasta_file, task.alg_phylip_file, 
                        nt_seed_file)

            if _model_tester:
                next_task = _model_tester(nodeid,
                                         alg_fasta_file, 
                                         alg_phylip_file, 
                                         conf)
            else:
                next_task = _tree_builder(nodeid, alg_phylip_file, None, 
                                          seqtype, conf)

        next_task.nseqs = nseqs
        new_tasks.append(next_task)

    elif ttype == "mchooser":
        alg_fasta_file = task.alg_fasta_file
        alg_phylip_file = task.alg_phylip_file
        model = task.get_best_model()

        tree_task = _tree_builder(nodeid, alg_phylip_file, model, 
                                  seqtype, conf)
        tree_task.nseqs = nseqs
        new_tasks.append(tree_task)

    elif ttype == "tree":
        treemerge_task = TreeMerger(nodeid, seqtype, task.tree_file, main_tree, conf)
        treemerge_task.nseqs = nseqs
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        if not task.set_a: 
            task.finish()
        main_tree = task.main_tree

        if conf["main"]["aa_seed"]:
            source = SeqGroup(conf["main"]["aa_seed"])
            source_seqtype = "aa"
        else:
            source = SeqGroup(conf["main"]["nt_seed"])
            source_seqtype = "nt"

        for seqs, outs in [task.set_a, task.set_b]:
            if len(seqs) >= int(conf["tree_merger"]["_min_size"]):
                msf_task = Msf(seqs, outs, seqtype=source_seqtype, source=source)
                new_tasks.append(msf_task)
           
    return new_tasks, main_tree

def pipeline(task, main_tree, conf):
    if not task:
        if conf["main"]["aa_seed"]:
            source = SeqGroup(conf["main"]["aa_seed"])
            source_seqtype = "aa"
        else:
            source = SeqGroup(conf["main"]["nt_seed"])
            source_seqtype = "nt"

        new_tasks = [Msf(set(source.id2name.values()), set(),
                         seqtype=source_seqtype,
                         source = source)]
    else:
        new_tasks, main_tree = process_task(task, main_tree, conf)

    return new_tasks, main_tree

