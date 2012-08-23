import numpy 
import re
import commands
import logging

from nprlib.utils import (del_gaps, GENCODE, PhyloTree, SeqGroup,
                          TreeStyle, generate_node_ids, DEBUG,
                          NPR_TREE_STYLE, faces)
from nprlib.task import TreeMerger, Msf

from nprlib.errors import DataError
from nprlib.utils import GLOBALS, rpath, pjoin, generate_runid
from nprlib import db
from nprlib.master_task import register_task_recursively
from nprlib.template.common import (IterConfig, get_next_npr_node,
                                    process_new_tasks, get_iternumber)
from nprlib.logger import logindent
log = logging.getLogger("main")

def annotate_node(t, final_task):
    cladeid2node = {}
    # Annotate cladeid in the whole tree
    for n in t.traverse():
        if n.is_leaf():
            n.add_feature("realname", db.get_seq_name(n.name))
            #n.name = n.realname
        if hasattr(n, "cladeid"):
            cladeid2node[n.cladeid] = n

    alltasks = GLOBALS["nodeinfo"][final_task.nodeid]["tasks"]
    npr_iter = get_iternumber(final_task.threadid)
    n = cladeid2node[t.cladeid]
    n.add_features(size=final_task.size)
    for task in alltasks:
        params = ["%s %s" %(k,v) for k,v in  task.args.iteritems() 
                  if not k.startswith("_")]
        params = " ".join(params)

        if task.ttype == "msf":
            n.add_features(msf_outseqs=task.out_seqs,
                           msf_file=task.multiseq_file)

        elif task.ttype == "acleaner":
            n.add_features(clean_alg_mean_ident=task.mean_ident, 
                           clean_alg_std_ident=task.std_ident, 
                           clean_alg_max_ident=task.max_ident, 
                           clean_alg_min_ident=task.min_ident, 
                           clean_alg_type=task.tname, 
                           clean_alg_cmd=params,
                           clean_alg_path=rpath(task.clean_alg_fasta_file))
        elif task.ttype == "alg":
            n.add_features(alg_mean_ident=task.mean_ident, 
                           alg_std_ident=task.std_ident, 
                           alg_max_ident=task.max_ident, 
                           alg_min_ident=task.min_ident, 
                           alg_type=task.tname, 
                           alg_cmd=params,
                           alg_path=rpath(task.alg_fasta_file))

        elif task.ttype == "tree":
            n.add_features(tree_model=task.model, 
                           tree_seqtype=task.seqtype, 
                           tree_type=task.tname, 
                           tree_cmd=params,
                           tree_file=rpath(task.tree_file),
                           tree_constrain=task.constrain_tree,
                           npr_iter=npr_iter)
        elif task.ttype == "mchooser":
            n.add_features(modeltester_models=task.models, 
                           modeltester_type=task.tname, 
                           modeltester_params=params, 
                           modeltester_bestmodel=task.get_best_model(), 
                           )
        elif task.ttype == "treemerger":
            n.add_features(treemerger_type=task.tname, 
                           treemerger_rf="RF=%s [%s]" %(task.rf[0], task.rf[1]),
                           treemerger_out_match_dist = task.outgroup_match_dist,
                           treemerger_out_match = task.outgroup_match,
            )

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

    #all_nt_alg = SeqGroup(nt_seed_file)
    aa_alg = SeqGroup(alg_fasta_file)
    nt_alg = SeqGroup()

    for seqname, aaseq, comments in aa_alg.iter_entries():
        #ntseq = all_nt_alg.get_seq(seqname).upper()
        ntseq = db.get_seq(seqname, "nt").upper()
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

def process_task(task, npr_conf, nodeid2info):
    conf = GLOBALS["config"]
    seqtype = task.seqtype
    nodeid = task.nodeid
    ttype = task.ttype
    threadid = task.threadid
    node_info = nodeid2info[nodeid]
    size = task.size#node_info.get("size", 0)
    target_seqs = node_info.get("target_seqs", [])
    out_seqs = node_info.get("out_seqs", [])
    constrain_tree = None
    constrain_tree_path = None
    if out_seqs and len(out_seqs) > 1:
        #constrain_tree = "((%s), (%s));" %(','.join(out_seqs), 
        #                                   ','.join(target_seqs))
        constrain_tree = "(%s, (%s));" %(','.join(out_seqs), 
                                           ','.join(target_seqs))
        
        constrain_tree_path = pjoin(task.taskdir, "constrain.nw")
                                           
    
    new_tasks = []
    if ttype == "msf":
        db.add_node(task.threadid,
                    task.nodeid, task.cladeid,
                    task.target_seqs,
                    task.out_seqs)
        
        alg_task = npr_conf.aligner(nodeid, task.multiseq_file,
                                    seqtype, conf)
        nodeid2info[nodeid]["size"] = task.size
        nodeid2info[nodeid]["target_seqs"] = task.target_seqs
        nodeid2info[nodeid]["out_seqs"] = task.out_seqs
        alg_task.size = task.size
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
        #log.log(24, "Identity: max=%0.2f min=%0.2f mean=%0.2f +- %0.2f",
        #        mx, mn, mean, std)
        task.max_ident = mx
        task.min_ident = mn
        task.mean_ident = mean
        task.std_ident = std
        next_task = None
        if ttype == "alg" and npr_conf.alg_cleaner:
            next_task = npr_conf.alg_cleaner(nodeid, seqtype,
                                             alg_fasta_file,
                                             alg_phylip_file, conf)
        else:
            # Converts aa alignment into nt if necessary
            if seqtype == "aa" and "nt" in GLOBALS["seqtypes"] and \
               task.mean_ident > npr_conf.switch_aa_similarity:
                log.log(26, "switching to codon alignment")
                # Change seqtype config
                npr_conf = IterConfig("genetree", task.size, "nt")
                seqtype = "nt"
                alg_fasta_file, alg_phylip_file = switch_to_codon(
                    task.alg_fasta_file, task.alg_phylip_file,
                    nt_seed_file)
                
            if constrain_tree:
                open(constrain_tree_path, "w").write(constrain_tree)
                                           
            if npr_conf.model_tester:
                next_task = npr_conf.model_tester(nodeid,
                                                  alg_fasta_file,
                                                  alg_phylip_file,
                                                  constrain_tree_path, conf)
            elif npr_conf.tree_builder:
                next_task = npr_conf.tree_builder(nodeid,
                                                  alg_phylip_file,
                                                  constrain_tree_path, None,
                                                  seqtype, conf)
        if next_task:
            next_task.size = task.size
            new_tasks.append(next_task)

    elif ttype == "mchooser":
        if npr_conf.tree_builder:
            alg_fasta_file = task.alg_fasta_file
            alg_phylip_file = task.alg_phylip_file
            model = task.get_best_model()
            if constrain_tree:
                open(constrain_tree_path, "w").write(constrain_tree)

            tree_task = npr_conf.tree_builder(nodeid, alg_phylip_file,
                                              constrain_tree_path, model, seqtype,
                                              conf)
            tree_task.size = task.size
            new_tasks.append(tree_task)

    elif ttype == "tree":
        treemerge_task = TreeMerger(nodeid, seqtype, task.tree_file, conf)
        #if conf["tree_splitter"]["_outgroup_size"]:
        #    treemerge_task = TreeSplitterWithOutgroups(nodeid, seqtype, task.tree_file, main_tree, conf)
        #else:
        #    treemerge_task = TreeSplitter(nodeid, seqtype, task.tree_file, main_tree, conf)

        treemerge_task.size = task.size
        new_tasks.append(treemerge_task)

    elif ttype == "treemerger":
        if not task.task_tree:
            task.finish()

        log.log(28, "Saving task tree...")
        annotate_node(task.task_tree, task) 
        db.update_node(nid=task.nodeid, 
                       runid=task.threadid,
                       newick=db.encode(task.task_tree))
        db.commit()

        # Add new nodes
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        ttree, mtree = task.task_tree, task.main_tree
        log.log(28, "Processing tree: %s seqs, %s outgroups",
                len(target_seqs), len(out_seqs))
        alg_path = node_info.get("clean_alg_path", node_info["alg_path"])
        for node, seqs, outs in get_next_npr_node(threadid, ttree,
                                                  mtree, alg_path, npr_conf):
            log.log(28, "Registering new node: %s seqs, %s outgroups",
                    len(seqs), len(outs))
            new_task_node = Msf(seqs, outs, seqtype=source_seqtype)
            new_tasks.append(new_task_node)

    return new_tasks

def pipeline(task):
    logindent(2)
    nodeid2info = GLOBALS["nodeinfo"]
    if not task:
        source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
        all_seqs = GLOBALS["target_sequences"]
        initial_task = Msf(set(all_seqs), set(),
                           seqtype=source_seqtype)
        
        initial_task.main_tree = None
        initial_task.threadid = generate_runid()

        # Register node 
        db.add_node(initial_task.threadid, initial_task.nodeid,
                    initial_task.cladeid, initial_task.target_seqs,
                    initial_task.out_seqs)
        
        new_tasks = [initial_task]
    else:
        npr_conf = IterConfig("genetree", task.size, task.seqtype)
        new_tasks  = process_task(task, npr_conf, nodeid2info)

    process_new_tasks(task, new_tasks)
    logindent(-2)
    return new_tasks


def OLD_STUFF():
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

            if (conf["_iters"] < int(conf["genetree"].get("max_iters", conf["_iters"]+1)) and 
                len(seqs) >= int(conf["tree_splitter"]["_min_size"])):
                    msf_task = Msf(seqs, outs, seqtype=source_seqtype)
                    if msf_task.nodeid not in nodeid2info:
                        msf_task.main_tree = main_tree
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
                
