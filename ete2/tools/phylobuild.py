#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import errno
import __builtin__
def wrap(method, retries):
    def fn(*args, **kwargs):
        for i in xrange(retries):
            try:
                return method(*args, **kwargs)
            except IOError, e:            
                if e.errno == errno.EINTR:
                    print >>sys.stderr, "A system call interruption was captured"
                    print >>sys.stderr, "Retrying", i, "of", retries, "until exception is raised"
                    continue
                else:
                    raise
    fn.retries = retries
    return fn

class safefile(file):
    __retries = 2
    def read(self, *args, **kargs):
        for i in xrange(self.__retries):
            try:
                return file.read(self, *args, **kargs)
            except IOError, e:            
                if e.errno == errno.EINTR:
                    print >>sys.stderr, "A system call interruption was captured"
                    print >>sys.stderr, "Retrying", i, "of", self.__retries, "until exception is raised"
                    continue
                else:
                    raise
    def write(self, *args, **kargs):
        for i in xrange(self.__retries):
            try:
                return file.read(self, *args, **kargs)
            except IOError, e:            
                if e.errno == errno.EINTR:
                    print >>sys.stderr, "A system call interruption was captured"
                    print >>sys.stderr, "Retrying", i, "of", self.__retries, "until exception is raised"
                    continue
                else:
                    raise
                
__builtin__.file = safefile
__builtin__.raw_input = wrap(raw_input, 100)
 
import sys
import os
import shutil
import signal
from StringIO import StringIO
from collections import defaultdict
import filecmp
import logging
import tempfile
log = None
from time import ctime, time

# This avoids installing phylobuild_lib module. npr script will find it in the
# same directory in which it is
NPRPATH = os.path.split(os.path.realpath(__file__))[0]
APPSPATH = None
args = None

sys.path.insert(0, NPRPATH)

try:
    import argparse
except ImportError:
    from ete2 import _argparse as argparse

from ete2.tools.phylobuild_lib.utils import (strip, SeqGroup, generate_runid,  AA, NT,
                                  GLOBALS, encode_seqname, pjoin, pexist,
                                  hascontent, clear_tempdir, ETE_CITE, colorify,
                                  GENCODE, silent_remove, _max, _min, _std, _mean, _median)
from ete2.tools.phylobuild_lib.errors import ConfigError, DataError
from ete2.tools.phylobuild_lib.master_task import Task
from ete2.tools.phylobuild_lib.interface import app_wrapper
from ete2.tools.phylobuild_lib.scheduler import schedule
from ete2.tools.phylobuild_lib import db
from ete2.tools.phylobuild_lib import apps
from ete2.tools.phylobuild_lib.logger import logindent
from ete2.tools.phylobuild_lib.citation import Citator
from ete2.tools.phylobuild_lib.configcheck import is_file, is_dir, check_config, list_workflows, block_detail, list_apps

#APPSPATH =  pjoin(NPRPATH, "ext_apps/")

try:
    __VERSION__ = open(os.path.join(NPRPATH, "VERSION")).read().strip()
except:
    __VERSION__ = "unknown"

try:
    __DATE__ = open(os.path.join(NPRPATH, "DATE")).read().strip()
except:
    __DATE__ = "unknown"

__DESCRIPTION__ = (
"""
      --------------------------------------------------------------------------------
                  Nested Phylogenetic Reconstruction (NPR) program.
                         ETE-NPR %s (beta), %s.
    
      ETE-NPR is a bioinformatics program providing a complete environment for
      the execution of phylogenomic workflows, including super-matrix
      and family-tree reconstruction approaches. ETE-NPR covers all
      necessary steps for high quality phylogenetic reconstruction, from
      alignment reconstruction and model testing to the generation of
      publication ready images of the produced trees and alignments. ETE-NPR is
      built on top of a bunch of specialized software and comes with a number
      of predefined workflows. 

      If you use ETE-NPR in a published work, please cite:

       Jaime Huerta-Cepas, Peer Bork and Toni Gabaldon. In preparation. 

      (Note that a list of the external programs used to complete the necessary
      computations will be also shown together with your results. They should
      also be cited.)
      --------------------------------------------------------------------------------

    """ %(__VERSION__, __DATE__))

__EXAMPLES__ = """
===============================
++++ COMMAND LINE EXAMPLES ++++
===============================

Runs a genetree workflow:

  $ npr -a fasta.aa.fa  -w linsi_fasttree -o results/
      
Runs a genetree workflow in recursive mode (the same workflow is applied for all
iterations):

  $ npr -a fasta.aa.fa  -w linsi_fasttree -o results/ --recursive

Runs a genetree workflow in recursive mode using dynamic workflow adjustment
depending on subtree size:

  $ npr -a fasta.aa.fa -w linsi_fasttree -o results/  \\
        --recursive  “size-range:500-1000,linsi_fasttree” \\
                     “size-range:0-499,linsi_phyml”

Runs a genetree workflow in recursive mode using dynamic workflow adjustment
depending on subtree size and combining amino-acids and nucleotide alignments:

  $ npr -a fasta.aa.fa -w linsi_fasttree -o results/ \\
        --recursive  “size-range:500-1000,linsi_fasttree” \\
                     “size-range:0-499,linsi_phyml” \\
        -nt_switch_thr 0.95
"""

def main(args):
    """ Read and parse all configuration and command line options,
    setup global variables and data, and initialize the master task of
    all workflows. """
    
    global log 
    log = logging.getLogger("main")
    
    base_dir = GLOBALS["basedir"]
        
    # -------------------------------------
    # READ CONFIG FILE AND PARSE WORKFLOWS
    # -------------------------------------
        
    # Load and check config file
    base_config = check_config(args.configfile)
    
    # Check for config file overwriting
    clearname = os.path.basename(args.configfile)        
    local_conf_file = pjoin(base_dir, "phylobuild.cfg")
    if pexist(base_dir):
        if hascontent(local_conf_file):
            if not filecmp.cmp(args.configfile, local_conf_file):
                if not args.override:
                    raise ConfigError("Output directory seem to contain"
                                      " a NPR execution using a different"
                                      " config file [workflow.cfg]. Use"
                                      " --override option or change the"
                                      " output path.")

    # Creates a tree splitter config block on the fly. In the future this
    # options should be more accessible by users.
    base_config['default_tree_splitter'] = {
        '_app' : 'treesplitter',
        '_max_outgroup_size' : '10%', # dynamic or fixed selection of out seqs.
        '_min_outgroup_support' : 0.9, # avoids fixing labile nodes as monophyletic
        '_outgroup_topology_dist' : False}

                    
    # prepare workflow config dictionaries
    workflow_types = defaultdict(list)
    TARGET_CLADES = set()
    VALID_WORKFLOW_TYPES = set(['genetree', 'supermatrix'])
    # extract workflow filters


    def parse_workflows(names, target_wtype, parse_filters=False):
        parsed_workflows = []
        if not names:
            return parsed_workflows

        for wkname in names:
            if parse_filters:
                wfilters = {}    
                fields = map(strip, wkname.split(","))
                if len(fields) == 1:
                    wkname = fields[0]
                else:
                    wkname = fields[-1]
                    for f in fields[:-1]:
                        if f.startswith("size-range:"): # size filter
                            f = f.replace("size-range:",'')
                            try:
                                min_size, max_size = map(int, f.split('-'))
                                if min_size < 0 or min_size > max_size:
                                    raise ValueError
        
                            except ValueError:
                                raise ConfigError('size filter should consist of two integer numbers (i.e. 50-100). Found [%s] instead' %f)
                            wfilters["max_size"] = max_size
                            wfilters["min_size"] = min_size
                        elif f.startswith("seq-sim-range:"): 
                            f = f.replace("seq-sim-range:",'')
                            try:
                                min_seq_sim, max_seq_sim  = map(float, f.split('-'))
                                if min_seq_sim > 1 or min_seq_sim < 0:
                                    raise ValueError
                                if max_seq_sim > 1 or max_seq_sim < 0:
                                    raise ValueError
                                if min_seq_sim > max_seq_sim:
                                    raise ValueError
                            except ValueError:
                                raise ConfigError('sequence similarity filter should consist of two float numbers between 0 and 1 (i.e. 0-0.95). Found [%s] instead' %f)
                            wfilters["min_seq_sim"] = min_seq_sim
                            wfilters["max_seq_sim"] = max_seq_sim
                        else:
                            raise ConfigError('Unknown workflow filter [%s]' %f)
            
            if wkname not in base_config and wkname in base_config.get('meta_workflow', {}):
                temp_workflows = [x.lstrip('@') for x in base_config['meta_workflow'][wkname]]
            else:
                temp_workflows = [wkname]
                
            for _w in temp_workflows:
                if _w not in base_config:
                    list_workflows(base_config)
                    raise ConfigError('[%s] workflow or meta_workflow name is not found in the config file.' %_w)
                wtype = base_config[_w]['_app']
                if wtype not in VALID_WORKFLOW_TYPES:
                    raise ConfigError('[%s] is not a valid workflow: %s?' %(_w, wtype))
                if wtype != target_wtype:
                    raise ConfigError('[%s] is not a valid %s workflow' %(wkname, target_wtype))
                    
            if parse_filters:
                if len(temp_workflows) == 1:
                    parsed_workflows.extend([(temp_workflows[0], wfilters)])
                else:
                    raise ConfigError('Meta-workflows with multiple threads are not allowed as recursive workflows [%s]' %wkname)
            else:
                parsed_workflows.extend(temp_workflows)
        return parsed_workflows
    
    genetree_workflows = parse_workflows(args.workflow, "genetree")
    supermatrix_workflows = parse_workflows(args.supermatrix_workflow, "supermatrix")
                
    # Stop if mixing types of meta-workflows 
    if supermatrix_workflows and len(genetree_workflows) > 1:
        raise ConfigError("A single genetree workflow must be specified when used in combination with super-matrix workflows.")                    

    # Sets master workflow type
    if supermatrix_workflows:
        WORKFLOW_TYPE = "supermatrix"
        master_workflows = supermatrix_workflows
    else:
        WORKFLOW_TYPE = "genetree"
        master_workflows = genetree_workflows
        
    # Parse npr workflows and filters
    npr_workflows = []
    use_npr = False
    if args.npr_workflows is not None:        
        use_npr = True
        npr_workflows = parse_workflows(args.npr_workflows, WORKFLOW_TYPE, parse_filters=True)

    # setup workflows and create a separate config dictionary for each of them
    run2config = {}
    for wkname in master_workflows:
        config = dict(base_config)
        run2config[wkname] = config
        
        appset = config[config[wkname]['_appset'][1:]]
        
        # Initialized application command line commands for this workflow
        config['app'] = {}
        config['threading'] = {}
        
        apps_to_test = {}
        for k, (appsrc, cores) in appset.iteritems():
            cores = int(cores)
            if appsrc == "built-in":
                #cores = int(config["threading"].get(k, args.maxcores))
                cores = min(args.maxcores, cores)
                config["threading"][k] = cores
                cmd = apps.get_call(k, APPSPATH, base_dir, str(cores))
                config["app"][k] = cmd
                apps_to_test[k] = cmd
                
        # Copy config file                
        config["_outpath"] = pjoin(base_dir, wkname)
        config["_nodeinfo"] = defaultdict(dict)
        try:
            os.makedirs(config["_outpath"])
        except OSError:
            pass
            
        # setup genetree workflow as the processor of concat alignment jobs
        if WORKFLOW_TYPE == "supermatrix":
            concatenator = config[wkname]["_alg_concatenator"][1:]
            config[concatenator]["_workflow"] = '@%s' % genetree_workflows[0]
            
        # setup npr options for master workflows        
        if use_npr:
            config['_npr'] = {
                # register root workflow as the main NPR workflow if the contrary not said
                "wf_type": WORKFLOW_TYPE,
                "workflows": npr_workflows if npr_workflows else [(wkname, {})],
                'nt_switch_thr': args.nt_switch_thr,
                'max_iters': args.max_iters,
                }
            
            #config[wkname]['_npr'] = '@'+npr_config
            #target_levels = config[npr_config].get('_target_levels', [])
            #target_dict = config['_optimized_levels'] = {}            
            #for tg in target_levels:
                # If target level name starts with ~, we allow para and
                # poly-phyletic grouping of the species in such level
                #strict_monophyly = True
                #if tg.startswith("~"):
                    #tg = target_level.lstrip("~")
                    #strict_monophyly = False
                #tg = tg.lower()
                # We add the level as non-optimized
                #target_dict[target_level] = [False, strict_monophyly]
            #TARGET_CLADES.update(target_levels)
        else:
            config['_npr'] = {
                'nt_switch_thr': args.nt_switch_thr,
            }
            
        
    # dump log config file 
    open(local_conf_file, "w").write(open(args.configfile).read())

    TARGET_CLADES.discard('')

    if WORKFLOW_TYPE == 'genetree':
        from ete2.tools.phylobuild_lib.workflow.genetree import pipeline
    elif WORKFLOW_TYPE == 'supermatrix':
        from ete2.tools.phylobuild_lib.workflow.supermatrix import pipeline

    #if args.arch == "auto":
    #    arch = "64 " if sys.maxsize > 2**32 else "32"
    #else:
    #    arch = args.arch

    arch = "64 " if sys.maxsize > 2**32 else "32"
        
    print __DESCRIPTION__
    
    # check application binary files
    if not args.nochecks:
        log.log(28, "Testing x86-%s portable applications..." % arch)
        apps.test_apps(apps_to_test)

    log.log(28, "Starting NPR execution at %s" %(ctime()))
    log.log(28, "Output directory %s" %(GLOBALS["output_dir"]))
    
        
    # -------------------------------------
    # PATH CONFIGs
    # -------------------------------------
    
    # Set up paths    
    gallery_dir = os.path.join(base_dir, "gallery")
    sge_dir = pjoin(base_dir, "sge_jobs")
    tmp_dir = pjoin(base_dir, "tmp")
    tasks_dir = os.path.realpath(args.tasks_dir) if args.tasks_dir else  pjoin(base_dir, "tasks")
    input_dir = pjoin(base_dir, "input")
    db_dir = os.path.realpath(args.db_dir) if args.db_dir else  pjoin(base_dir, "db")

    GLOBALS["db_dir"] = db_dir
    GLOBALS["sge_dir"] = sge_dir
    GLOBALS["tmp"] = tmp_dir
    GLOBALS["gallery_dir"] = gallery_dir
    GLOBALS["tasks_dir"] = tasks_dir
    GLOBALS["input_dir"] = input_dir
    
    GLOBALS["nprdb_file"]  = pjoin(db_dir, "npr.db")
    GLOBALS["datadb_file"]  = pjoin(db_dir, "data.db")
    GLOBALS["orthodb_file"]  = pjoin(db_dir, "ortho.db") if not args.orthodb else args.orthodb
    GLOBALS["seqdb_file"]  = pjoin(db_dir, "seq.db") if not args.seqdb else args.seqdb
    
    # Clear databases if necessary
    if args.clearall:
        log.log(28, "Erasing all existing npr data...")
        shutil.rmtree(GLOBALS["tasks_dir"]) if pexist(GLOBALS["tasks_dir"]) else None
        shutil.rmtree(GLOBALS["tmp"]) if pexist(GLOBALS["tmp"]) else None
        shutil.rmtree(GLOBALS["input_dir"]) if pexist(GLOBALS["input_dir"]) else None
        
        if not args.seqdb:
            silent_remove(GLOBALS["seqdb_file"])
        if not args.orthodb:
            silent_remove(GLOBALS["orthodb_file"])

        silent_remove(GLOBALS["datadb_file"])
        silent_remove(pjoin(base_dir, "nprdata.tar"))
        silent_remove(pjoin(base_dir, "nprdata.tar.gz"))
        #silent_remove(pjoin(base_dir, "npr.log"))
        silent_remove(pjoin(base_dir, "npr.log.gz"))                    
    else:
        if args.softclear:
            log.log(28, "Erasing precomputed data (reusing task directory)")
            shutil.rmtree(GLOBALS["tmp"]) if pexist(GLOBALS["tmp"]) else None
            shutil.rmtree(GLOBALS["input_dir"]) if pexist(GLOBALS["input_dir"]) else None
            os.remove(GLOBALS["datadb_file"]) if pexist(GLOBALS["datadb_file"]) else None
        if args.clearseqs and pexist(GLOBALS["seqdb_file"]) and not args.seqdb:
            log.log(28, "Erasing existing sequence database...")
            os.remove(GLOBALS["seqdb_file"])
        if args.clearorthology and pexist(GLOBALS["orthodb_file"]) and not args.orthodb:
            log.log(28, "Erasing existing orthologs database...")
            os.remove(GLOBALS["orthodb_file"])

    if not args.clearall and base_dir != GLOBALS["output_dir"]:
        log.log(24, "Copying previous output files to scratch directory: %s..." %base_dir)
        try:
            shutil.copytree(pjoin(GLOBALS["output_dir"], "db"), db_dir)
        except IOError, e:
            print e
            pass

        try:
            shutil.copytree(pjoin(GLOBALS["output_dir"], "tasks/"), pjoin(base_dir, "tasks/"))
        except IOError, e:
            try:
                shutil.copy(pjoin(GLOBALS["output_dir"], "nprdata.tar.gz"), base_dir)
            except IOError, e:
                pass
            
        # try: os.system("cp -a %s/* %s/" %(GLOBALS["output_dir"],  base_dir))
        # except Exception: pass

        
    # UnCompress packed execution data
    if pexist(os.path.join(base_dir,"nprdata.tar.gz")):
        log.warning("Compressed data found. Extracting content to start execution...")
        cmd = "cd %s && gunzip -f nprdata.tar.gz && tar -xf nprdata.tar && rm nprdata.tar" % base_dir
        os.system(cmd)
            
    # Create dir structure
    for dirname in [tmp_dir, tasks_dir, input_dir, db_dir]:
        try:
            os.makedirs(dirname)
        except OSError:
            log.warning("Using existing dir: %s", dirname)

       
    # -------------------------------------
    # DATA READING AND CHECKING
    # -------------------------------------
        
    # Set number of CPUs available
    
    if WORKFLOW_TYPE == "supermatrix" and not args.cogs_file:
        raise ConfigError("Species tree workflow requires a list of COGS"
                          " to be supplied through the --cogs"
                          " argument.")
    elif WORKFLOW_TYPE == "supermatrix":
        GLOBALS["cogs_file"] = os.path.abspath(args.cogs_file)
        
    GLOBALS["seqtypes"] = set()
    if args.nt_seed_file:
        GLOBALS["seqtypes"].add("nt")
        GLOBALS["inputname"] = os.path.split(args.nt_seed_file)[-1]
        
    if args.aa_seed_file:
        GLOBALS["seqtypes"].add("aa")
        GLOBALS["inputname"] = os.path.split(args.aa_seed_file)[-1]

        
    # Initialize db if necessary, otherwise extract basic info
    db.init_nprdb(GLOBALS["nprdb_file"])
    db.init_datadb(GLOBALS["datadb_file"])
    
    # Check and load data
    ERROR = ""
    if not pexist(GLOBALS["seqdb_file"]):
        target_seqs = None
        target_seqs, seqnames, name2len, name2unk, name2seq = scan_sequences(args, target_seqs)
        ERROR = check_seq_integrity(args, target_seqs, seqnames, name2len, name2unk, name2seq)
        sp2counter = defaultdict(int)
        if WORKFLOW_TYPE == "supermatrix":
            for name in target_seqs:
                spname = name.split(GLOBALS["spname_delimiter"], 1)[0]
                sp2counter[spname] += 1
                #seq_species = set([name.split(GLOBALS["spname_delimiter"])[0] 
                #               for name in target_seqs])
            seq_species = set(sp2counter.keys())
        if not ERROR:
            db.init_seqdb(GLOBALS["seqdb_file"])
            if WORKFLOW_TYPE == "supermatrix":
                db.add_seq_species(sp2counter)
            load_sequences(target_seqs, name2seq, WORKFLOW_TYPE)
        seqnames, name2len, name2unk, name2seq = [None] * 4 # Release mem?
    else:
        db.init_seqdb(GLOBALS["seqdb_file"])
        log.warning("Skipping check and load sequences (loading from database...)")
        target_seqs = db.get_all_seq_names()
        
    log.warning("%d sequences in database" %len(target_seqs))

    if ERROR:
        open(pjoin(base_dir, "error.log"), "w").write(' '.join(sys.argv) + "\n\n" + ERROR)
        raise DataError("Errors were found while loading data. Please"
                        " check error file for details")
    
    if WORKFLOW_TYPE == "supermatrix":
        if not pexist(GLOBALS["orthodb_file"]):
             db.init_orthodb(GLOBALS["orthodb_file"])            
             all_species = set()
             for line in open(args.cogs_file):
                 all_species.update(map(lambda n: n.split(args.spname_delimiter, 1)[0].strip(), line.split("\t")))
             db.update_cog_species(all_species)
             db.orthoconn.commit()
        else:
            db.init_orthodb(GLOBALS["orthodb_file"])
            log.warning("Skipping check and load ortholog pairs (loading from database...)")
        
        # species in ortho pairs
        ortho_species = db.get_ortho_species()
        log.log(28, "Found %d unqiue species codes in ortholog-pairs" %(len(ortho_species)))
        # species in fasta file
        seq_species = db.get_seq_species()
        log.log(28, "Found %d unqiue species codes in sequence names" %(len(seq_species))) 
        
        # Species filter
        if args.spfile:
            target_species = set([line.strip() for line in open(args.spfile)])
            target_species.discard("")
            log.log(28, "Enabling NPR for %d species", len(target_species))
        else: 
            target_species = seq_species

        # Check that orthologs are available for all species
        if target_species - seq_species: 
            ERROR += "The following species have no sequence information: %s" %(target_species - seq_species)
        if target_species - ortho_species: 
            ERROR += "The following species have no orthology information: %s" %(target_species - ortho_species)
            
        GLOBALS["target_species"] = target_species
        
    if ERROR:
        open(pjoin(base_dir, "error.log"), "w").write(' '.join(sys.argv) + "\n\n" + ERROR)
        raise DataError("Errors were found while loading data. Please"
                        " check error file for details")
    
    # Prepare target taxa levels, if any
    if WORKFLOW_TYPE == "supermatrix" and args.lineages_file and TARGET_CLADES:
        sp2lin = {}
        lin2sp = defaultdict(set)
        all_sorted_levels = []
        for line in open(args.lineages_file):
            sp, lineage = line.split("\t")
            sp = sp.strip()
            if sp in target_species:
                sp2lin[sp] = map(lambda x: x.strip().lower(), lineage.split(","))
                for lin in sp2lin[sp]:
                    if lin not in lin2sp:
                        all_sorted_levels.append(lin)
                    lin2sp[lin].add(sp)
        # any target species without lineage information?
        if target_species - set(sp2lin):
            missing = target_species - set(sp2lin)
            log.warning("%d species not found in lineages file" %len(missing))
            
        # So, the following levels (with at least 2 species) could be optimized     
        avail_levels = [(lin, len(lin2sp[lin])) for lin in all_sorted_levels if len(lin2sp[lin])>=2]
        log.log(26, "Available levels for NPR optimization:\n%s", '\n'.join(map(lambda x: "% 30s (%d spcs)"%x, avail_levels)))
        avail_levels = set([lv[0] for lv in avail_levels])
        GLOBALS["lineages"] = (sp2lin, lin2sp)
    # if we miss lineages file, raise an error
    elif WORKFLOW_TYPE == "supermatrix" and TARGET_CLADES:
        raise ConfigError("The use of target_levels requires a species lineage file provided through the --lineages option")
        
    target_seqs = None # release mem

    if WORKFLOW_TYPE == "genetree":
        if "aa" in GLOBALS["seqtypes"]:
            GLOBALS["target_sequences"] = db.get_all_seqids("aa")
        else:
            GLOBALS["target_sequences"] = db.get_all_seqids("nt")
        log.log(28, "Working on %d ids whose sequences are available", len(GLOBALS["target_sequences"]))


    # -------------------------------------
    # MISC 
    # -------------------------------------

    GLOBALS["_max_cores"] = args.maxcores
    log.debug("Enabling %d CPU cores" %args.maxcores)

       
    # how task will be executed
    if args.no_execute:
        execution = (None, False)
    elif args.sge_execute:
        execution = ("sge", False)
    else:
        if args.monitor:
            execution =("insitu", True) # True is for run-detached flag
        else:
            execution = ("insitu", False)
       
    # Scheduling starts here
    log.log(28, "NPR starts now!")
    
    # This initialises all pipelines
    pending_tasks = []
    start_time = ctime()
    for wkname, config in run2config.iteritems():
        # Feeds pending task with the first task of the workflow
        config["_name"] = wkname
        new_tasks = pipeline(None, wkname, config)
        if not new_tasks:
            continue # skips pipelines not fitting workflow filters
        thread_id = new_tasks[0].threadid
        config["_configid"] = thread_id
        GLOBALS[thread_id] = config
        pending_tasks.extend(new_tasks)

        # Clear info from previous runs
        open(os.path.join(config["_outpath"], "runid"), "a").write('\t'.join([thread_id, GLOBALS["nprdb_file"]+"\n"]))
        # Write command line info
        cmd_info = '\t'.join([start_time, thread_id, str(args.monitor), GLOBALS["cmdline"]])
        open(pjoin(config["_outpath"], "command_lines"), "a").write(cmd_info+"\n")

    thread_errors = schedule(pipeline, pending_tasks, args.schedule_time,
                             execution, args.debug, args.noimg)
    db.close()
    
    if not thread_errors:
        if args.compress:
            log.log(28, "Compressing intermediate data...")
            cmd = "cd %s && tar --remove-files -cf nprdata.tar tasks/ && gzip -f nprdata.tar; if [ -e npr.log ]; then gzip -f npr.log; fi;" %\
              GLOBALS["basedir"]
            os.system(cmd)
        log.log(28, "Deleting temporal data...")
        cmd = "cd %s && rm tmp/ -rf" %GLOBALS["basedir"]
        os.system(cmd)
        cmd = "cd %s && rm input/ -rf" %GLOBALS["basedir"]
        os.system(cmd)
        
        GLOBALS["citator"].show()
    else:
        raise DataError("Errors found in some tasks")
        
def check_and_load_orthologs(fname):
    log.log(28, "importing orthologous pairs into database (this may take a while)...")
    template_import = tempfile.NamedTemporaryFile()
    template_import.write('''
PRAGMA cache_size = 1000000;
PRAGMA synchronous = OFF;
PRAGMA journal_mode = OFF;
PRAGMA locking_mode = EXCLUSIVE;
PRAGMA temp_store = MEMORY;
PRAGMA auto_vacuum = NONE;
.separator "\\t"
.import %s ortho_pair
PRAGMA locking_mode = EXCLUSIVE;

CREATE INDEX IF NOT EXISTS i7 ON ortho_pair (taxid2, seqid2, taxid1);
CREATE INDEX IF NOT EXISTS i10 ON ortho_pair (taxid1, taxid2);

PRAGMA synchronous = NORMAL;
PRAGMA journal_mode = DELETE;
PRAGMA locking_mode = NORMAL;

''' %  fname)

    template_import.flush()
    cmd = "sqlite3 %s < %s" %(GLOBALS["orthodb_file"], template_import.name)
    print cmd
    os.system(cmd)
    template_import.close()
    

def load_sequences(target_seqs, name2seq, workflow_type):
    if args.seq_rename:
        name2hash, hash2name = hash_names(target_seqs)
        log.log(28, "Loading %d sequence name translations..." %len(hash2name))
        db.add_seq_name_table(hash2name.items())
        if workflow_type == "genetree":
            GLOBALS["target_sequences"] = hash2name.keys()
    else:
        name2hash, hash2name = {}, {}

    for seqtype in GLOBALS["seqtypes"]:
        log.log(28, "Loading %d %s sequences..." %(len(name2seq[seqtype]), seqtype))
        db.add_seq_table([(name2hash.get(k, k), seq) for k,seq in
                          name2seq[seqtype].iteritems()], seqtype)
    db.seqconn.commit()

def scan_sequences(args, target_seqs):
    source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
    visited_seqs = {"aa":[], "nt":[]}
    seq2length = {"aa":{}, "nt":{}}
    seq2unknown = {"aa":{}, "nt":{}}
    seq2seq = {"aa":{}, "nt":{}}
    skipped_seqs = 0
    for seqtype in ["aa", "nt"]:
        seqfile = getattr(args, "%s_seed_file" %seqtype)
        if not seqfile:
            continue
        GLOBALS["seqtypes"].add(seqtype)
        log.log(28, "Scanning %s sequence file...", seqtype)
        fix_dups = True if args.rename_dup_seqnames else False
        SEQS = SeqGroup(seqfile, fix_duplicates=fix_dups, format=args.seqformat)
        for c1, (seqid, seq) in enumerate(SEQS.id2seq.iteritems()):
            if c1%10000 == 0:
                print >>sys.stderr, c1, "\r",
                sys.stderr.flush()

            seqname = SEQS.id2name[seqid]
            if target_seqs and seqname not in target_seqs:
                skipped_seqs += 1
                continue
            visited_seqs[seqtype].append(seqname)

            # Clear problematic symbols
            if not args.no_seq_checks:
                seq = seq.replace(".", "-")
                seq = seq.replace("*", "X")
                if seqtype == "aa":
                    seq = seq.upper()
                    seq = seq.replace("J", "X") # phyml fails with J
                    seq = seq.replace("O", "X") # mafft fails with O
                    seq = seq.replace("U", "X") # selenocysteines
            if args.dealign:
                seq = seq.replace("-", "").replace(".", "")
            seq2seq[seqtype][seqname] = seq
            seq2length[seqtype][seqname] = len(seq)
            if not args.no_seq_checks:
                # Load unknown symbol inconsistencies
                if seqtype == "nt" and set(seq) - NT:
                    seq2unknown[seqtype][seqname] = set(seq) - NT
                elif seqtype == "aa" and set(seq) - AA:
                    seq2unknown[seqtype][seqname] = set(seq) - AA

        # Initialize target sets using aa as source
        if not target_seqs: # and seqtype == "aa":
            target_seqs = set(visited_seqs[source_seqtype])

    if skipped_seqs:
        log.warning("%d sequences will not be used since they are"
                    "  not present in the aa seed file." %skipped_seqs)
                             
    return target_seqs, visited_seqs, seq2length, seq2unknown, seq2seq

def check_seq_integrity(args, target_seqs, visited_seqs, seq2length, seq2unknown, seq2seq):
    log.log(28, "Checking data consistency ...")
    source_seqtype = "aa" if "aa" in GLOBALS["seqtypes"] else "nt"
    error = ""

    # Check for duplicate ids
    if not args.ignore_dup_seqnames:
        seq_number = len(set(visited_seqs[source_seqtype]))
        if len(visited_seqs[source_seqtype]) != seq_number:
            counter = defaultdict(int)
            for seqname in visited_seqs[source_seqtype]:
                counter[seqname] += 1
            duplicates = ["%s\thas %d copies" %(key, value) for key, value in counter.iteritems() if value > 1]
            error += "\nDuplicate sequence names.\n"
            error += '\n'.join(duplicates)

    # check that the seq of all targets is available
    if target_seqs: 
        for seqtype in GLOBALS["seqtypes"]:
            missing_seq = target_seqs - set(seq2seq[seqtype].keys())
            if missing_seq:
                error += "\nThe following %s sequences are missing:\n" %seqtype
                error += '\n'.join(missing_seq)

    # check for unknown characters
    for seqtype in GLOBALS["seqtypes"]:
        if seq2unknown[seqtype]:
            error += "\nThe following %s sequences contain unknown symbols:\n" %seqtype
            error += '\n'.join(["%s\tcontains:\t%s" %(k,' '.join(v)) for k,v in seq2unknown[seqtype].iteritems()] )

    # check for aa/cds consistency
    REAL_NT = set('ACTG')
    if GLOBALS["seqtypes"] == set(["aa", "nt"]):
        inconsistent_cds = set()
        for seqname, ntlen in seq2length["nt"].iteritems():
            if seqname in seq2length["aa"]:
                aa_len = seq2length["aa"][seqname]
                if ntlen / 3.0 != aa_len:
                    inconsistent_cds.add("%s\tExpected:%d\tFound:%d" %\
                                         (seqname,
                                         aa_len*3,
                                         ntlen))
                else:
                    if not args.no_seq_checks:
                        for i, aa in enumerate(seq2seq["aa"][seqname]):
                            codon = seq2seq["nt"][seqname][i*3:(i*3)+3]
                            if not (set(codon) - REAL_NT): 
                                if GENCODE[codon] != aa:
                                    log.warning('@@2:Unmatching codon in seq:%s, aa pos:%s (%s != %s)@@1: Use --no-seq-checks to skip' %(seqname, i, codon, aa))
                                    inconsistent_cds.add('Unmatching codon in seq:%s, aa pos:%s (%s != %s)' %(seqname, i, codon, aa))

        if inconsistent_cds:
            error += "\nUnexpected coding sequence length for the following ids:\n"
            error += '\n'.join(inconsistent_cds)

    # Show some stats
    all_len = seq2length[source_seqtype].values()
    max_len = _max(all_len)
    min_len = _min(all_len)
    mean_len = _mean(all_len)
    std_len = _std(all_len)
    outliers = []
    for v in all_len:
        if abs(mean_len - v) >  (3 * std_len):
            outliers.append(v)
    log.log(28, "Total sequences:  %d" %len(all_len))
    log.log(28, "Average sequence length: %d +- %0.1f " %(mean_len, std_len))
    log.log(28, "Max sequence length:  %d" %max_len)
    log.log(28, "Min sequence length:  %d" %min_len)

    if outliers:
        log.warning("%d sequence lengths look like outliers" %len(outliers))

    return error

def hash_names(target_names):
    """Given a set of strings of variable lengths, it returns their
    conversion to fixed and safe hash-strings.
    """
    # An example of hash name collision
    #test= ['4558_15418', '9600_21104', '7222_13002', '3847_37647', '412133_16266']
    #hash_names(test)

    log.log(28, "Generating safe sequence names...")
    hash2name = defaultdict(list)
    for c1, name in enumerate(target_names):
        print >>sys.stderr, c1, "\r",
        sys.stderr.flush()
        hash_name = encode_seqname(name)
        hash2name[hash_name].append(name)

    collisions = [(k,v) for k,v in hash2name.iteritems() if len(v)>1]
    #GLOBALS["name_collisions"] = {}
    if collisions:
        visited = set(hash2name.keys())
        for old_hash, coliding_names in collisions:
            logindent(2)
            log.log(20, "Collision found when hash-encoding the following gene names: %s", coliding_names)
            niter = 1
            valid = False
            while not valid or len(new_hashes) < len(coliding_names):
                niter += 1
                new_hashes = defaultdict(list)
                for name in coliding_names:
                    hash_name = encode_seqname(name*niter)
                    new_hashes[hash_name].append(name)
                valid = set(new_hashes.keys()).isdisjoint(visited)
                
            log.log(20, "Fixed with %d concatenations! %s", niter, ', '.join(['%s=%s' %(e[1][0], e[0]) for e in  new_hashes.iteritems()]))
            del hash2name[old_hash]
            hash2name.update(new_hashes)
            #GLOBALS["name_collisions"].update([(_name, _code) for _code, _name in new_hashes.iteritems()])
            logindent(-2)
    #collisions = [(k,v) for k,v in hash2name.iteritems() if len(v)>1]
    #log.log(28, "Final collisions %s", collisions )
    hash2name = dict([(k, v[0]) for  k,v in hash2name.iteritems()])
    name2hash = dict([(v, k) for  k,v in hash2name.iteritems()])
    return name2hash, hash2name

   
def _main():
    global NPRPATH, APPSPATH, args
    ETEHOMEDIR = os.path.expanduser("~/.etetoolkit/")
    
    if os.path.exists(pjoin('/etc/etetoolkit/', 'ext_apps-latest')):
        # if a copy of apps is part of the ete distro, use if by default
        APPSPATH = pjoin('/etc/etetoolkit/', 'ext_apps-latest')
        ETEHOMEDIR = '/etc/etetoolkit/'
    else:
        # if not, try a user local copy
        APPSPATH = pjoin(ETEHOMEDIR, 'ext_apps-latest')

    if len(sys.argv) == 1:
        if not pexist(APPSPATH):
            print >>sys.stderr, colorify('\nWARNING: external applications directory are not found at %s' %APPSPATH, "yellow")
            print >>sys.stderr, colorify('Use "ete build install_tools" to install or upgrade tools', "orange")
    
    elif len(sys.argv) > 1:
        _config_path = pjoin(NPRPATH, 'phylobuild.cfg')

        if sys.argv[1] == "install_tools":
            import urllib
            import tarfile
            print >>sys.stderr, colorify('Downloading latest version of tools...', "green")
            if len(sys.argv) > 2:
                TARGET_DIR = sys.argv[2]
            else:
                TARGET_DIR = ''
            while not pexist(TARGET_DIR):
                TARGET_DIR = raw_input('target directory? [%s]:' %ETEHOMEDIR).strip()
                if TARGET_DIR == '':
                    TARGET_DIR = ETEHOMEDIR
                    break
            if TARGET_DIR == ETEHOMEDIR:
                try:
                    os.mkdir(ETEHOMEDIR)
                except OSError: 
                    pass
                
            version_file = "latest.tar.gz"
            urllib.urlretrieve("https://github.com/jhcepas/ext_apps/archive/%s" %version_file, pjoin(TARGET_DIR, version_file))
            print >>sys.stderr, colorify('Decompressing...', "green")
            tfile = tarfile.open(pjoin(TARGET_DIR, version_file), 'r:gz')
            tfile.extractall(TARGET_DIR)
            print >>sys.stderr, colorify('Compiling tools...', "green")
            sys.path.insert(0, pjoin(TARGET_DIR, 'ext_apps-latest'))
            import compile_all
            s = compile_all.compile_all()
            sys.exit(s)                    
        
        elif sys.argv[1] == "check":
            if not pexist(APPSPATH):
                print >>sys.stderr, colorify('\nWARNING: external applications directory are not found at %s' %APPSPATH, "yellow")
                print >>sys.stderr, colorify('Use "ete build install_tools" to install or upgrade', "orange")
            # setup portable apps
            config = {}
            for k in apps.builtin_apps:
                cmd = apps.get_call(k, APPSPATH, "/tmp", "1")
                config[k] = cmd
            apps.test_apps(config)
            sys.exit(0)                    

        elif sys.argv[1] == "wl":
            base_config = check_config(_config_path)
            list_workflows(base_config)
            sys.exit(0)
            
        elif sys.argv[1] == "show":
            base_config = check_config(_config_path)
            block_detail(sys.argv[2], base_config)
            sys.exit(0)

        elif sys.argv[1] == "dump":
            if len(sys.argv) > 2:
                base_config = check_config(_config_path)
                block_detail(sys.argv[2], base_config, color=False)
            else:
                print open(_config_path).read()
            sys.exit(0)

        elif sys.argv[1] == "validate":
            print 'Validating configuration file ', sys.argv[2]
            if pexist(sys.argv[2]):
                base_config = check_config(sys.argv[2])
                print 'Everything ok'
            else:
                print 'File does not exist'
                sys.exit(-1)
            sys.exit(0)

        elif sys.argv[1] == "apps":
            base_config = check_config(_config_path)
            list_apps(base_config, sys.argv[2:])
            sys.exit(0)
            
        elif sys.argv[1] == "version":
            print __VERSION__, '(%s)' %__DATE__
            sys.exit(0)
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__ + __EXAMPLES__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Input data related flags
    input_group = parser.add_argument_group('==== Input Options ====')

    input_group.add_argument('[check | wl | show | dump | validate | version | install_tools]',
                             nargs='?',
                             help=("Utility commands:\n"
                                   "check: check that external applications are executable.\n"
                                   "wl: show a list of available workflows.\n"
                                   "show [name]: show the configuration parameters of a given workflow or application config block.\n"
                                   "dump [name]: dump the configuration parameters of the specified block (allows to modify predefined config).\n"
                                   "validate [configfile]: Validate a custom configuration file.\n"
                                   "version: Show current version.\n"
                                   ))

    input_group.add_argument("-c", "--config", dest="configfile",
                             type=is_file, default=NPRPATH+'/phylobuild.cfg',
                             help="Custom configuration file.")
    
    input_group.add_argument("--tools-dir", dest="tools_dir",
                             type=str,
                             help="Custom path where external software is avaiable.")
    
    input_group.add_argument("-w", dest="workflow",
                             required=True,
                             nargs='+', 
                             help="One or more gene-tree workflow names. All the specified workflows will be executed using the same input data.")

    input_group.add_argument("-m", dest="supermatrix_workflow",
                             required=False,
                             nargs='+', 
                             help="One or more super-matrix workflow names. All the specified workflows will be executed using the same input data.")
    
    input_group.add_argument("-a", dest="aa_seed_file",
                             type=is_file,
                             help="Initial multi sequence file with"
                             " protein sequences.")

    
    input_group.add_argument("-n", dest="nt_seed_file",
                             type=is_file,
                             help="Initial multi sequence file with"
                             " nucleotide sequences")

    
    input_group.add_argument("--seqformat", dest="seqformat",
                             choices=["fasta", "phylip", "iphylip", "phylip_relaxed", "iphylip_relaxed"],
                             default="fasta",
                             help="")

    input_group.add_argument("--dealign", dest="dealign",
                             action="store_true",
                             help="when used, gaps in the orginal fasta file will"
                             " be removed, thus allowing to use alignment files as input.")
    
    input_group.add_argument("--no-seq-rename", dest="seq_rename",
                             action="store_false",
                             help="If used, sequence names will NOT be"
                             " internally translated to 10-character-"
                             "identifiers.")

    input_group.add_argument("--no-seq-checks", dest="no_seq_checks",
                            action="store_true",
                            help="Skip consistency sequence checks for not allowed symbols, etc.")
    
    dup_names_group = input_group.add_mutually_exclusive_group()
    
    dup_names_group.add_argument("--ignore-dup-seqnames", dest="ignore_dup_seqnames",
                                 action = "store_true",
                                 help=("If duplicated sequence names exist in the input"
                                       " fasta file, a single random instance will be used."))
    
    dup_names_group.add_argument("--rename-dup-seqnames", dest="rename_dup_seqnames",
                                 action = "store_true",
                                 help=("If duplicated sequence names exist in the input"
                                       " fasta file, duplicates will be renamed."))
    
    
    input_group.add_argument("--orthodb", dest="orthodb",
                             type=str,
                             help="Uses a custom orthology-pair database file")
    
    input_group.add_argument("--seqdb", dest="seqdb",
                             type=str,
                             help="Uses a custom sequence database file")

    
    # supermatrix workflow
    
    input_group.add_argument("--cogs", dest="cogs_file",
                             type=is_file,
                             help="A file defining clusters of orthologous groups."
                             " One per line. Tab delimited sequence ids. ")

    input_group.add_argument("--lineages", dest="lineages_file",
                             type=is_file,
                             help="A file containing the (sorted) lineage "
                                  "track of each species. It enables "
                                  "NPR algorithm to fix what taxonomic "
                                  "levels should be optimized."
                                  "Note that linage tracks must consist in "
                                  "a comma separated list of taxonomic levels "
                                  "sorted from deeper to swallower clades "
                                  "(i.e. 9606 [TAB] Eukaryotes,Mammals,Primates)"
                             )
    
    input_group.add_argument("--spname-delimiter", dest="spname_delimiter",
                             type=str, default="_",
                             help="In supermatrix mode, spname_delimiter is used to split"
                             " the name of sequences into species code and"
                             " sequence identifier (i.e. HUMAN_p53 = HUMAN, p53)."
                             " Note that species name must always precede seq.identifier.")

    input_group.add_argument("--spfile", dest="spfile",
                             type=is_file,
                             help="If specified, only the sequences and ortholog"
                             " pairs matching the group of species in this file"
                             " (one species code per line) will be used. ")
    
    npr_group = parser.add_argument_group('==== NPR options ====')
    npr_group.add_argument("-r", "--recursive", dest="npr_workflows",
                           required=False,
                           nargs="*",
                           help="Enables recursive NPR capabilities (Nested Phylogenetic Reconstruction)"
                           " and specifies custom workflows and filters for each NPR iteration.")
    npr_group.add_argument("--nt_switch_thr", dest="nt_switch_thr",
                           required=False,
                           type=float,
                           default = 0.95,
                           help="Sequence similarity at which nucleotide based alignments should be used"
                           " instead of amino-acids. ")
    npr_group.add_argument("--max_iters", dest="max_iters",
                           required=False,
                           type=int,
                           default=99999999,
                           help="Set a maximum number of NPR iterations allowed.")
    npr_group.add_argument("--first-split-outgroup", dest="first_split",
                           type=str,
                           default='midpoint',
                           help=("When used, it overrides first_split option"
                                 " in any tree merger config block in the"
                                 " config file. Default: 'midpoint' "))
    
    
    # Output data related flags
    output_group = parser.add_argument_group('==== Output Options ====')
    output_group.add_argument("-o", "--outdir", dest="outdir",
                              type=str, required=True,
                              help="""Output directory for results.""")

    output_group.add_argument("--scratch_dir", dest="scratch_dir",
                              type=is_dir, 
                              help="""If provided, ete-build will run on the scratch folder and all files will be transferred to the output dir when finished. """)

    output_group.add_argument("--db_dir", dest="db_dir",
                              type=is_dir, 
                              help="""Alternative location of the database directory""")
    
    output_group.add_argument("--tasks_dir", dest="tasks_dir",
                              type=is_dir,
                              help="""Output directory for the executed processes (intermediate files).""")
    
    output_group.add_argument("--compress", action="store_true",
                              help="Compress all intermediate files when"
                              " a workflow is finished.")
    
    output_group.add_argument("--logfile", action="store_true",
                              help="Log messages will be saved into a file named npr.log within the output directory.")

    output_group.add_argument("--noimg", action="store_true",
                              help="Tree images will not be generated when a workflow is finished.")
        
    output_group.add_argument("--email", dest="email",
                              type=str, 
                              help="Send an email when errors occur or a workflow is done.")
    
    output_group.add_argument("--email_report_time", dest="email_report_time",
                              type=int, default = 0, 
                              help="How often (in minutes) an email reporting the status of the execution should be sent. 0=No reports")
    
    
    # Task execution related flags
    exec_group = parser.add_argument_group('==== Execution Mode Options ====')

    exec_group.add_argument("-C", "--cpu", dest="maxcores", type=int,
                            default=1, help="Maximum number of CPU cores"
                            " available in the execution host. If higher"
                            " than 1, tasks with multi-threading"
                            " capabilities will enabled. Note that this"
                            " number will work as a hard limit for all applications,"
                            "regardless of their specific configuration.")

    exec_group.add_argument("-t", "--schedule_time", dest="schedule_time",
                            type=float, default=2,
                            help="""How often (in secs) tasks should be checked for available results.""")
    
    exec_group.add_argument("--launch_time", dest="launch_time",
                            type=float, default=5,
                            help="""How often (in secs) queued jobs should be checked for launching""")
    
    exec_type_group = exec_group.add_mutually_exclusive_group()
    
    exec_type_group.add_argument("--noexec", dest="no_execute",
                                 action="store_true",
                                 help=("Prevents launching any external application."
                                       " Tasks will be processed and intermediate steps will"
                                       " run, but no real computation will be performed."))
    
    exec_type_group.add_argument("--sge", dest="sge_execute",
                                 action="store_true", help="EXPERIMENTAL!: Jobs will be"
                                 " launched using the Sun Grid Engine"
                                 " queue system.")

    exec_group.add_argument("--monitor", dest="monitor",
                            action="store_true",
                            help="Monitor mode: pipeline jobs will be"
                            " detached from the main NPR process. This means that"
                            " when npr execution is interrupted, all currently"
                            " running jobs will keep running. Use this option if you"
                            " want to stop and recover an NPR execution thread or"
                            " if jobs are expected to be executed remotely."
                            )

    exec_group.add_argument("--override", dest="override",
                            action="store_true",
                            help="Override workflow configuration file if a previous version exists." )

    exec_group.add_argument("--clearall", dest="clearall",
                            action="store_true",
                            help="Erase all previous data in the output directory and start a clean execution.")
    
    exec_group.add_argument("--softclear", dest="softclear",
                            action="store_true",
                            help="Clear all precomputed data (data.db), but keeps task raw data in the directory, so they can be re-processed.")
    
    exec_group.add_argument("--clear_orthodb", dest="clearorthology",
                            action="store_true",
                            help="Reload orthologous group information.")

    exec_group.add_argument("--clear_seqdb", dest="clearseqs",
                            action="store_true",
                            help="Reload sequences deleting previous database if necessary.")

    # exec_group.add_argument("--arch", dest="arch",
    #                         choices=["auto", "32", "64"],
    #                         default="auto", help="Set the architecture of"
    #                         " execution hosts (needed only when using"
    #                         " built-in applications.)")
    
    exec_group.add_argument("--nochecks", dest="nochecks",
                            action="store_true",
                            help="Skip application check when npr starts.")
    
    # Interface related flags
    ui_group = parser.add_argument_group("==== Program Interface Options ====")
    # ui_group.add_argument("-u", dest="enable_ui",
    #                     action="store_true", help="When used, a color"
    #                     " based interface is launched to monitor NPR"
    #                     " processes. This feature is EXPERIMENTAL and"
    #                     " requires NCURSES libraries installed in your"
    #                     " system.")

    ui_group.add_argument("-v", dest="verbosity",
                          default=0,
                          type=int, choices=[0,1,2,3,4],
                          help="Verbosity level: 0=very quiet, 4=very "
                          " verbose.")

    ui_group.add_argument("--debug", nargs="?",
                          const="all",
                          help="Start debugging"
                          " A taskid can be provided, so"
                          " debugging will start from such task on.")
    
    args = parser.parse_args()
    if args.tools_dir: 
        APPSPATH = args.tools_dir

    if not pexist(APPSPATH):
        print >>sys.stderr, colorify('\nWARNING: external applications directory are not found at %s' %APPSPATH, "yellow")
        print >>sys.stderr, colorify('Use "ete build install_tools" to install or upgrade tools', "orange")
        
    args.enable_ui = False
    if not args.noimg:
        print 'Testing ETE-NPR graphics support...'
        print 'X11 DISPLAY = %s' %colorify(os.environ.get('DISPLAY', 'not detected!'), 'yellow')
        print '(You can use --noimg to disable graphical capabilities)'
        try:
            from ete2 import Tree
            Tree().render('/tmp/etenpr_img_test.png')
        except:
            raise ConfigError('img generation not supported')
    
    if not args.aa_seed_file and not args.nt_seed_file:
        parser.error('At least one input file argument (-a, -n) is required')
        
    outdir = os.path.abspath(args.outdir)
    final_dir, runpath = os.path.split(outdir)
    if not runpath:
        raise ValueError("Invalid outdir")

    GLOBALS["output_dir"] = os.path.abspath(args.outdir)
    
    if args.scratch_dir:
        # set paths for scratch folder for sqlite files 
        print >>sys.stderr, "Creating temporary scratch dir..."
        base_scratch_dir = os.path.abspath(args.scratch_dir)        
        scratch_dir = tempfile.mkdtemp(prefix='npr_tmp', dir=base_scratch_dir)
        GLOBALS["scratch_dir"] = scratch_dir
        GLOBALS["basedir"] = scratch_dir
    else:
        GLOBALS["basedir"] = GLOBALS["output_dir"]
        
        
    GLOBALS["first_split_outgroup"] = args.first_split

    GLOBALS["email"] = args.email
    GLOBALS["verbosity"] = args.verbosity
    GLOBALS["email_report_time"] = args.email_report_time * 60
    GLOBALS["launch_time"] = args.launch_time
    GLOBALS["cmdline"] = ' '.join(sys.argv)

    GLOBALS["threadinfo"] = defaultdict(dict)
    GLOBALS["seqtypes"] = set()
    GLOBALS["target_species"] = set()
    GLOBALS["target_sequences"] = set()
    GLOBALS["spname_delimiter"] = args.spname_delimiter
    GLOBALS["color_shell"] = True
    GLOBALS["citator"] = Citator()

    
    GLOBALS["lineages"] = None
    GLOBALS["cogs_file"] = None 
   
    GLOBALS["citator"].add(ETE_CITE)
    
    if not pexist(GLOBALS["basedir"]):
        os.makedirs(GLOBALS["basedir"])

    # when killed, translate signal into exception so program can exit cleanly
    def raise_control_c(_signal, _frame):
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, raise_control_c)
    
    # Start the application
    app_wrapper(main, args)

if __name__ == "__main__":
    _main()
