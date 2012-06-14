import os
import numpy 
import re
import commands
import logging
import numpy
from collections import defaultdict

from nprlib.utils import (del_gaps, GENCODE, PhyloTree, SeqGroup,
                          TreeStyle, generate_node_ids, DEBUG,
                          NPR_TREE_STYLE, faces)
from nprlib.task import (MetaAligner, Mafft, Muscle, Uhire, Dialigntx,
                         FastTree, Clustalo, Raxml, Phyml, JModeltest,
                         Prottest, Trimal, TreeMerger, select_outgroups,
                         Msf)
from nprlib.errors import DataError

log = logging.getLogger("main")

n2class = {
    "none": None, 
    "meta_aligner": MetaAligner, 
    "mafft": Mafft, 
    "muscle": Muscle, 
    "uhire": Uhire, 
    "dialigntx": Dialigntx, 
    "fasttree": FastTree, 
    "clustalo": Clustalo, 
    "raxml": Raxml,
    "phyml": Phyml,
    "jmodeltest": JModeltest,
    "prottest": Prottest,
    "trimal": Trimal
    }


def get_trimal_conservation(alg_file, trimal_bin):
    output = commands.getoutput("%s -ssc -in %s" % (trimal_bin,
                                                    alg_file))
    conservation = []
    for line in output.split("\n")[3:]:
        a, b = map(float, line.split())
        conservation.append(b)
    mean = numpy.mean(conservation)
    std = numpy.std(conservation)
    return mean, std

    
def get_statal_identity(alg_file, statal_bin):
    output = commands.getoutput("%s -scolidentt -in %s" % (statal_bin,
                                                           alg_file))
    ## Columns Identity Descriptive Statistics
    #maxColIdentity	1
    #minColIdentity	0.428571
    #avgColIdentity	0.781853
    #stdColIdentity	0.2229
    #print output
    maxi, mini, avgi, stdi = [None] * 4
    for line in output.split("\n"):
        if line.startswith("#maxColIdentity"):
            maxi = float(line.split()[1])
        elif line.startswith("#minColIdentity"):
            mini = float(line.split()[1])
        elif line.startswith("#avgColIdentity"):
            avgi = float(line.split()[1])
        elif line.startswith("#stdColIdentity"):
            stdi = float(line.split()[1])
            break
    return maxi, mini, avgi, stdi

    
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
    return (numpy.max(ident), numpy.min(ident), 
            numpy.mean(ident), numpy.std(ident))

    
def get_seqs_identity(alg, seqs):
    ''' Returns alg statistics regarding a set of sequences'''
    seqlen = len(alg.get_seq(seqs[0]))
    ident = list()
    for i in xrange(seqlen):
        states = defaultdict(int)
        for seq_id in seqs:
            seq = alg.get_seq(seq_id)
            if seq[i] != "-":
                states[seq[i]] += 1
        values = states.values()
        if values:
            ident.append(float(max(values))/sum(values))
    return (numpy.max(ident), numpy.min(ident), 
            numpy.mean(ident), numpy.std(ident))
   
         
def switch_to_codon(alg_fasta_file, alg_phylip_file, nt_seed_file,
                    kept_columns=None):
    GAP_CHARS = set(".-")
    NUCLEOTIDES = set("ATCG") 
    # Check conservation of columns. If too many identities,
    # switch to codon alignment and make the tree with DNA. 
    # Mixed models is another possibility.
    if kept_columns:
        kept_columns = set(map(int, kept_columns))
    else:
        kept_columns = []

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

                # NOT WORKING ON ALTERNATIVE TABLES
                # if not (set(codon) - NUCLEOTIDES) and GENCODE[codon] != ch:
                #     log.error("[%s] CDS does not match protein sequence:"
                #               " %s = %s not %s at pos %d" %\
                #                   (seqname, codon, GENCODE[codon], ch, nt_pos))
                #     raise ValueError()

        ntalgseq = "".join(ntalgseq)
        nt_alg.set_seq(seqname, ntalgseq)

    alg_fasta_filename = alg_fasta_file + ".nt"
    alg_phylip_filename = alg_phylip_file + ".nt"
    nt_alg.write(outfile=alg_fasta_filename, format="fasta")
    nt_alg.write(outfile=alg_phylip_filename, format="iphylip_relaxed")
        
    return alg_fasta_filename, alg_phylip_filename

def process_task(task, main_tree, conf, nodeid2info):
    aa_seed_file = conf["main"]["aa_seed"]
    nt_seed_file = conf["main"]["nt_seed"]
    seqtype = task.seqtype
    nodeid = task.nodeid
    ttype = task.ttype
    node_info = nodeid2info[nodeid]
    nseqs = task.nseqs#node_info.get("nseqs", 0)
    target_seqs = node_info.get("target_seqs", [])
    out_seqs = node_info.get("out_seqs", [])
    constrain_tree = None
    constrain_tree_path = None
    if out_seqs and len(out_seqs) > 1:
        #constrain_tree = "((%s), (%s));" %(','.join(out_seqs), 
        #                                   ','.join(target_seqs))
        constrain_tree = "(%s, (%s));" %(','.join(out_seqs), 
                                           ','.join(target_seqs))
        
        constrain_tree_path = os.path.join(task.taskdir, "constrain.nw")
                                           
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
        #log.debug("INDEX %s %s %s", index, nseqs, max_seqs)
                
    _min_branch_support = conf["main"]["npr_min_branch_support"][index_slide]
    skip_outgroups = conf["tree_splitter"]["_outgroup_size"] == 0
    
    if seqtype == "nt": 
        _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_nt_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
        _aa_identity_thr = 1.0
    elif seqtype == "aa": 
        _aligner = n2class[conf["main"]["npr_aa_aligner"][index]]
        _alg_cleaner = n2class[conf["main"]["npr_aa_alg_cleaner"][index]]
        _model_tester = n2class[conf["main"]["npr_aa_model_tester"][index]]
        _tree_builder = n2class[conf["main"]["npr_aa_tree_builder"][index]]
        _aa_identity_thr = conf["main"]["npr_max_aa_identity"][index]

    #print node_info, (nseqs, index, _alg_cleaner, _model_tester, _aligner, _tree_builder)
    
    new_tasks = []
    if ttype == "msf":
        alg_task = _aligner(nodeid, task.multiseq_file,
                           seqtype, conf)
        nodeid2info[nodeid]["nseqs"] = task.nseqs
        nodeid2info[nodeid]["target_seqs"] = task.target_seqs
        nodeid2info[nodeid]["out_seqs"] = task.out_seqs
        alg_task.nseqs = task.nseqs
        new_tasks.append(alg_task)

    elif ttype == "alg" or ttype == "acleaner":
        if ttype == "alg":
            nodeid2info[nodeid]["alg_path"] = task.alg_fasta_file
        elif ttype == "acleaner":
            nodeid2info[nodeid]["alg_clean_path"] = task.clean_alg_fasta_file
        
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
        #import time
        #t1 = time.time()
        #mx, mn, mean, std = get_identity(task.alg_fasta_file)
        #print time.time()-t1
        #log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
        #        mx, mn, mean, std)
        #t1 = time.time()
        mx, mn, mean, std = get_statal_identity(task.alg_phylip_file,
                                                conf["app"]["statal"])
        
        #print time.time()-t1
        log.log(26, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
                mx, mn, mean, std)
        task.max_ident = mx
        task.min_ident = mn
        task.mean_ident = mean
        task.std_ident = std
        
        if ttype == "alg" and _alg_cleaner:
            next_task = _alg_cleaner(nodeid, seqtype, alg_fasta_file, 
                                     alg_phylip_file, conf)
        else:
            # Converts aa alignment into nt if necessary
            if seqtype == "aa" and nt_seed_file and \
               task.mean_ident > _aa_identity_thr:
                log.log(26, "switching to codon alignment")
                # Change seqtype config 
                seqtype = "nt"
                _model_tester = n2class[conf["main"]["npr_nt_model_tester"][index]]
                _aligner = n2class[conf["main"]["npr_nt_aligner"][index]]
                _tree_builder = n2class[conf["main"]["npr_nt_tree_builder"][index]]
                alg_fasta_file, alg_phylip_file = switch_to_codon(
                    task.alg_fasta_file, task.alg_phylip_file,
                    nt_seed_file)
            if constrain_tree:
                open(constrain_tree_path, "w").write(constrain_tree)
                                           
            if _model_tester:
                next_task = _model_tester(nodeid,
                                          alg_fasta_file, 
                                          alg_phylip_file,
                                          constrain_tree_path,
                                          conf)
            else:
                next_task = _tree_builder(nodeid, alg_phylip_file, constrain_tree_path,
                                          None,
                                          seqtype, conf)
        next_task.nseqs = task.nseqs
        new_tasks.append(next_task)

    elif ttype == "mchooser":
        alg_fasta_file = task.alg_fasta_file
        alg_phylip_file = task.alg_phylip_file
        model = task.get_best_model()
        if constrain_tree:
            open(constrain_tree_path, "w").write(constrain_tree)
                                          
        tree_task = _tree_builder(nodeid, alg_phylip_file, constrain_tree_path,
                                  model,
                                  seqtype, conf)
        tree_task.nseqs = task.nseqs
        new_tasks.append(tree_task)

    elif ttype == "tree":
        treemerge_task = TreeMerger(nodeid, seqtype, task.tree_file, main_tree, conf)
        #if conf["tree_splitter"]["_outgroup_size"]:
        #    treemerge_task = TreeSplitterWithOutgroups(nodeid, seqtype, task.tree_file, main_tree, conf)
        #else:
        #    treemerge_task = TreeSplitter(nodeid, seqtype, task.tree_file, main_tree, conf)

        treemerge_task.nseqs = task.nseqs
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        if conf["main"]["aa_seed"]:
            source = SeqGroup(conf["main"]["aa_seed"])
            source_seqtype = "aa"
        else:
            source = SeqGroup(conf["main"]["nt_seed"])
            source_seqtype = "nt"

        if not task.task_tree:
            task.finish()
        main_tree = task.main_tree

        def processable_node(_n):
            """ Returns true if node is suitable for NPR """
            
            _isleaf = False
            if _n is not task.task_tree:
                if conf["tree_splitter"]["_max_seq_identity"] < 1.0: 
                    if not hasattr(_n, "seqs_mean_ident"):
                        log.log(20, "Calculating node sequence stats...")
                        mx, mn, avg, std = get_seqs_identity(ALG, [__n.name for __n in n2content[_n]])
                        _n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
                                       seqs_mean_ident=avg, seqs_std_ident=std)
                else:
                    _n.add_features(seqs_max_ident=None, seqs_min_ident=None,
                                    seqs_mean_ident=None, seqs_std_ident=None)

                if _n.seqs_mean_ident >= conf["tree_splitter"]["_max_seq_identity"]:
                    # If sequences are too similar, do not optimize
                    # this node even if it is lowly supported
                    _is_leaf = False
                elif skip_outgroups and _min_branch_support <= 1.0:
                    # If we are optimizing only lowly supported nodes,
                    # and nodes are optimized without outgroup, our
                    # target node is actually the parent of lowly
                    # supported nodes. Therefore, I check if support
                    # is low in children nodes, and return this node
                    # if so.
                    for _ch in _n.children:
                        if _ch.support <= _min_branch_support:
                            _isleaf = True
                            break
                elif _n.support <= _min_branch_support:
                    # If sequences are different enough and node is
                    # not well supported, optimize it. 
                    _isleaf = True
            return _isleaf
        log.log(20, "Loading tree content...")
        n2content = main_tree.get_node2content()

        # Loads information about sequence similarity in each internal
        # node. This info will be used by processable_node()
        alg_path = nodeid2info[nodeid].get("clean_alg_path",
                                           nodeid2info[nodeid]["alg_path"])
        #log.log(20, "Loading by-node sequence similarity...")
        ALG = SeqGroup(alg_path)
        #for n in task.task_tree.traverse(): 
        #    content = n2content[n]
        #    mx, mn, avg, std = get_seqs_identity(ALG, [node.name for node in content])
        #    n.add_features(seqs_max_ident=mx, seqs_min_ident=mn,
        #                   seqs_mean_ident=avg, seqs_std_ident=std)
            
        log.log(20, "Finding next NPR nodes...")        
        for node in task.task_tree.iter_leaves(is_leaf_fn=processable_node):
            #print len(n2content[node])
            log.log(20, "Found processable node. Supports: %0.2f (children=%s)",
                    node.support, ','.join(["%0.2f" % ch.support for ch in node.children]))
            if skip_outgroups:
                seqs = set([_i.name for _i in n2content[node]])
                outs = set()
            else:
                seqs, outs = select_outgroups(node, n2content, conf["tree_splitter"])

            if (conf["_iters"] < int(conf["main"].get("max_iters", conf["_iters"]+1)) and 
                len(seqs) >= int(conf["tree_splitter"]["_min_size"])):
                    msf_task = Msf(seqs, outs, seqtype=source_seqtype, source=source)
                    if msf_task.nodeid not in nodeid2info:
                        nodeid2info[msf_task.nodeid] = {}
                        new_tasks.append(msf_task)
                        conf["_iters"] += 1
                    if DEBUG():
                        NPR_TREE_STYLE.title.clear()
                        NPR_TREE_STYLE.title.add_face( faces.TextFace("MainTree:"
                                                                      "Gold color:Newly generated task nodes ",
                                                                      fgcolor="blue"), 0)
                        node.img_style["fgcolor"] = "Gold"
                        node.img_style["size"] = 30
                        #node.add_face(faces.TextFace("%s" %conf["_iters"], fsize=24), 0, "branch-top")
        if DEBUG():
            task.main_tree.show(tree_style=NPR_TREE_STYLE)
            for _n in task.main_tree.traverse():
                _n.img_style = None
           

    return new_tasks, main_tree

def pipeline(task, main_tree, conf, nodeid2info):
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
        conf["_iters"] = 1
    else:
        new_tasks, main_tree = process_task(task, main_tree, conf, nodeid2info)

    return new_tasks, main_tree

config_specs = """

[main]
max_iters = integer(minv=1)
render_tree_images = boolean()

npr_max_seqs = integer_list(minv=0)
npr_min_branch_support = float_list(minv=0, maxv=1)

npr_max_aa_identity = float_list(minv=0.0)

npr_nt_alg_cleaner = list()
npr_aa_alg_cleaner = list()

npr_aa_aligner = list()
npr_nt_aligner = list()

npr_aa_tree_builder = list()
npr_nt_tree_builder = list()

npr_aa_model_tester = list()
npr_nt_model_tester = list()

[tree_splitter]
_min_size = integer()
_max_seq_identity = float()
_outgroup_size = integer()
_outgroup_min_support = float()
_outgroup_topology_dist = boolean()
"""