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
from __future__ import absolute_import
from __future__ import print_function

import re
import itertools
import errno
import six.moves.builtins
import six
from six.moves import map
from six.moves import range
from six import StringIO
from six.moves import input

import sys
import os
import shutil
import signal
from collections import defaultdict
import filecmp
import logging
import tempfile
log = None
from time import ctime, time

# This avoids installing ete_build_lib module. npr script will find it in the
# same directory in which it is
BASEPATH = os.path.split(os.path.realpath(__file__))[0]
APPSPATH = None
args = None

sys.path.insert(0, BASEPATH)

import argparse
from ..citation import Citator

from .ete_build_lib.utils import (SeqGroup, generate_runid, AA, NT, GLOBALS,
                                   encode_seqname, pjoin, pexist, hascontent,
                                   clear_tempdir, colorify, GENCODE,
                                   silent_remove, _max, _min, _std, _mean,
                                   _median, iter_cog_seqs)
from .ete_build_lib.errors import ConfigError, DataError
from .ete_build_lib.master_task import Task
from .ete_build_lib.interface import app_wrapper
from .ete_build_lib.scheduler import schedule
from .ete_build_lib import db
from .ete_build_lib import apps
from .ete_build_lib.logger import logindent

from .ete_build_lib.configcheck import (is_file, is_dir, check_config,
                                         build_genetree_workflow,
                                         build_supermatrix_workflow,
                                         parse_block, list_workflows,
                                         block_detail, list_apps)
from .ete_build_lib import seqio


try:
    from ..version import __version__
except ImportError:
     __version__ = 'unknown'

__DESCRIPTION__ = (
"""
      --------------------------------------------------------------------------------
                  ETE build (%s) - reproducible phylogenetic workflows

      Citation:

       Huerta-Cepas J, Serra F and Bork P. ETE 3: Reconstruction, analysis and
       visualization of phylogenomic data. Mol Biol Evol (2016)
       doi:10.1093/molbev/msw046

      (Note that a list of the external programs used to complete all necessary
      computations will be shown after workflow execution. Those programs should
      also be cited.)

      --------------------------------------------------------------------------------
      """ %(__version__))

__EXAMPLES__ = """
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


    if args.custom_config:
        concat_config = open(args.base_config).readlines()
        concat_config += open(args.custom_config).readlines()
        base_config = check_config(concat_config)
    else:
        base_config = check_config(args.base_config)

    # Check for config file overwriting
    clearname = os.path.basename(args.base_config)
    local_conf_file = pjoin(base_dir, "ete_build.cfg")
    if pexist(base_dir):
        if hascontent(local_conf_file):
            if not args.clearall and not args.resume:
                raise ConfigError("Output directory seems to contain"
                                  " data from a previous run."
                                  " Use --clearall to restart the analysis or --resume to continue.")

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
                fields = [_f.strip() for _f in wkname.split(",")]
                if len(fields) == 1:
                    wkname = fields[0]
                else:
                    wkname = fields[-1]
                    for f in fields[:-1]:
                        if f.startswith("size-range:"): # size filter
                            f = f.replace("size-range:",'')
                            try:
                                min_size, max_size = list(map(int, f.split('-')))
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

            if target_wtype == "genetree" and wkname in base_config.get('genetree_meta_workflow', {}):
                temp_workflows = [x.lstrip('@') for x in base_config['genetree_meta_workflow'][wkname]]
            elif target_wtype == "supermatrix" and wkname in base_config.get('supermatrix_meta_workflow', {}):
                temp_workflows = [x.lstrip('@') for x in base_config['supermatrix_meta_workflow'][wkname]]
            else:
                temp_workflows = [wkname]

            for index, _w in enumerate(list(temp_workflows)):
                if ',' in _w:
                    words = [elem.split(',') for elem in _w.split('-')]
                    for comb in itertools.product(*words):
                        real_wname = '-'.join(comb)
                        temp_workflows.append(real_wname)
                    temp_workflows.pop(index)
            print(temp_workflows)


            # if wkname not in base_config and wkname in base_config.get('meta_workflow', {}):
            #     temp_workflows = [x.lstrip('@') for x in base_config['meta_workflow'][wkname]]
            # else:
            #     temp_workflows = [wkname]

            for _w in temp_workflows:
                if target_wtype == "genetree":
                    base_config.update(build_genetree_workflow(_w))
                elif target_wtype == "supermatrix":
                    base_config.update(build_supermatrix_workflow(_w))
                parse_block(_w, base_config)

                if _w not in base_config:
                    list_workflows(base_config)
                    raise ConfigError('[%s] workflow or meta-workflow name is not found in the config file.' %_w)
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
        for k, (appsrc, cores) in six.iteritems(appset):
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
        if pexist(config["_outpath"]) and args.clearall:
            log.log(20, "Cleaning result directory %s" %config["_outpath"])
            shutil.rmtree(config["_outpath"])
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
                # register root workflow as the main workflow if the contrary not said
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
    with open(local_conf_file, "w") as OUTPUT:
        with open(args.base_config) as INPUT:
            OUTPUT.write(INPUT.read()) # replace by simple copy?

    TARGET_CLADES.discard('')

    if WORKFLOW_TYPE == 'genetree':
        from .ete_build_lib.workflow.genetree import pipeline
    elif WORKFLOW_TYPE == 'supermatrix':
        from .ete_build_lib.workflow.supermatrix import pipeline

    #if args.arch == "auto":
    #    arch = "64 " if sys.maxsize > 2**32 else "32"
    #else:
    #    arch = args.arch

    arch = "64 " if sys.maxsize > 2**32 else "32"

    print(__DESCRIPTION__)

    # check application binary files
    if not args.nochecks:
        log.log(28, "Testing x86-%s portable applications..." % arch)
        apps.test_apps(apps_to_test)

    log.log(28, "Starting ETE-build execution at %s" %(ctime()))
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

    GLOBALS["seqdb_file"]  = pjoin(db_dir, "seq.db") if not args.seqdb else args.seqdb

    # Clear databases if necessary
    if args.clearall:
        log.log(28, "Erasing all existing npr data...")
        shutil.rmtree(GLOBALS["tasks_dir"]) if pexist(GLOBALS["tasks_dir"]) else None
        shutil.rmtree(GLOBALS["tmp"]) if pexist(GLOBALS["tmp"]) else None
        shutil.rmtree(GLOBALS["input_dir"]) if pexist(GLOBALS["input_dir"]) else None

        if not args.seqdb:
            silent_remove(GLOBALS["seqdb_file"])

        silent_remove(GLOBALS["datadb_file"])
        silent_remove(pjoin(base_dir, "etebuild_data.tar"))
        silent_remove(pjoin(base_dir, "etebuild_data.tar.gz"))
        silent_remove(pjoin(base_dir, "etebuild.log"))
        silent_remove(pjoin(base_dir, "etebuild.log.gz"))

    else:
        if args.softclear:
            log.log(28, "Erasing precomputed data (reusing task directory)")
            shutil.rmtree(GLOBALS["tmp"]) if pexist(GLOBALS["tmp"]) else None
            shutil.rmtree(GLOBALS["input_dir"]) if pexist(GLOBALS["input_dir"]) else None
            os.remove(GLOBALS["datadb_file"]) if pexist(GLOBALS["datadb_file"]) else None
        if args.clearseqs and pexist(GLOBALS["seqdb_file"]) and not args.seqdb:
            log.log(28, "Erasing existing sequence database...")
            os.remove(GLOBALS["seqdb_file"])

    if not args.clearall and base_dir != GLOBALS["output_dir"]:
        log.log(24, "Copying previous output files to scratch directory: %s..." %base_dir)
        try:
            shutil.copytree(pjoin(GLOBALS["output_dir"], "db"), db_dir)
        except IOError as e:
            print(e)
            pass

        try:
            shutil.copytree(pjoin(GLOBALS["output_dir"], "tasks/"), pjoin(base_dir, "tasks/"))
        except IOError as e:
            try:
                shutil.copy(pjoin(GLOBALS["output_dir"], "etebuild_data.tar.gz"), base_dir)
            except IOError as e:
                pass

        # try: os.system("cp -a %s/* %s/" %(GLOBALS["output_dir"],  base_dir))
        # except Exception: pass


    # UnCompress packed execution data
    if pexist(os.path.join(base_dir,"etebuild_data.tar.gz")):
        log.warning("Compressed data found. Extracting content to start execution...")
        cmd = "cd %s && gunzip -f etebuild_data.tar.gz && tar -xf etebuild_data.tar && rm etebuild_data.tar" % base_dir
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

    # Species filter
    if args.spfile:
        target_species = set([line.strip() for line in open(args.spfile)])
        target_species.discard("")
        log.log(28, "Enabling %d species", len(target_species))
    else:
        target_species = None

    # Load supermatrix data
    if WORKFLOW_TYPE == "supermatrix":
        observed_species= set()
        target_seqs = set()
        for cog_number, seq_cogs in iter_cog_seqs(args.cogs_file, args.spname_delimiter):
            for seqname, spcode, seqcode in seq_cogs:
                if target_species is None or spcode in target_species:
                    observed_species.add(spcode)
                    target_seqs.add(seqname)

        if target_species is not None:
            if target_species - observed_species:
                raise DataError("The following target_species could not be found in COGs file: %s" %(','.join(target_species-observed_species)))
        else:
            target_species = observed_species
        log.warning("COG file restriction: %d sequences from %s species " %(len(target_seqs), len(target_species)))
    else:
        target_seqs = None

    GLOBALS["target_species"] = target_species

    # Check and load data
    ERROR = ""
    if not pexist(GLOBALS["seqdb_file"]):
        db.init_seqdb(GLOBALS["seqdb_file"])
        seqname2seqid = None
        if args.aa_seed_file:
            seqname2seqid = seqio.load_sequences(args, "aa", target_seqs, target_species, seqname2seqid)
            if not target_seqs:
                target_seqs = list(seqname2seqid.keys())

        if args.nt_seed_file:
            seqname2seqid = seqio.load_sequences(args, "nt", target_seqs, target_species, seqname2seqid)
        # Integrity checks?
        pass

    else:
        db.init_seqdb(GLOBALS["seqdb_file"])
        log.warning("Reusing sequences from existing database!")
        if target_seqs is None:
            seqname2seqid = db.get_seq_name_dict()
        else:
            seqname2seqid = db.get_seq_name_dict()
            if target_seqs - set(seqname2seqid.keys()):
                raise DataError("The following sequence names in COGs file"
                                " are not found in current database: %s" %(
                                    ','.join(target_seqs - db_seqs)))

    log.warning("%d target sequences" %len(seqname2seqid))
    GLOBALS["target_sequences"] = seqname2seqid.values()

    if ERROR:
        with open(pjoin(base_dir, "error.log"), "w") as OUTPUT:
            OUTPUT.write(' '.join(arguments) + "\n\n" + ERROR)
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
                sp2lin[sp] = [x.strip().lower() for x in lineage.split(",")]
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
        log.log(26, "Available levels for NPR optimization:\n%s", '\n'.join(["% 30s (%d spcs)"%x for x in avail_levels]))
        avail_levels = set([lv[0] for lv in avail_levels])
        GLOBALS["lineages"] = (sp2lin, lin2sp)

    # if no lineages file, raise an error
    elif WORKFLOW_TYPE == "supermatrix" and TARGET_CLADES:
        raise ConfigError("The use of target_levels requires a species lineage file provided through the --lineages option")

    # -------------------------------------
    # MISC
    # -------------------------------------

    GLOBALS["_max_cores"] = args.maxcores
    log.debug("Enabling %d CPU cores" %args.maxcores)


    # how task will be executed
    if args.no_execute:
        execution = (None, False)
    # elif args.sge_execute:
    #     execution = ("sge", False)
    else:
        if args.monitor:
            execution =("insitu", True) # True is for run-detached flag
        else:
            execution = ("insitu", False)

    # Scheduling starts here
    log.log(28, "ETE build starts now!")

    # This initialises all pipelines
    pending_tasks = []
    start_time = ctime()
    for wkname, config in six.iteritems(run2config):
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
        if GLOBALS.get('_background_scheduler', None):
            GLOBALS['_background_scheduler'].terminate()

        if args.compress:
            log.log(28, "Compressing intermediate data...")
            cmd = "cd %s && tar --remove-files -cf etebuild_data.tar tasks/ && gzip -f etebuild_data.tar; if [ -e etebuild.log ]; then gzip -f etebuild.log; fi;" %\
              GLOBALS["basedir"]
            os.system(cmd)
        log.log(28, "Deleting temporal data...")
        cmd = "cd %s && rm -rf tmp/" %GLOBALS["basedir"]
        os.system(cmd)
        cmd = "cd %s && rm -rf input/" %GLOBALS["basedir"]
        os.system(cmd)
        GLOBALS["citator"].show()
    else:
        raise DataError("Errors found in some tasks")


def _main(arguments, builtin_apps_path=None):
    global BASEPATH, APPSPATH, args

    # read path of ete_toolchain
    if builtin_apps_path:
        APPSPATH = builtin_apps_path
        
    ETEHOMEDIR = os.path.expanduser("~/.etetoolkit/")

    if len(arguments) == 1:
        if not pexist(APPSPATH):
            print(colorify('\nWARNING: external applications not found', "yellow"), file=sys.stderr)
            print(colorify('Install using conda (recomended):', "lgreen"), file=sys.stderr)
            print(colorify(' conda install -c etetoolkit ete_toolchain', "white"), file=sys.stderr)
            print(colorify('or manually compile from:', "lgreen"), file=sys.stderr)
            print(colorify(' https://github.com/etetoolkit/ete_toolchain', "white"), file=sys.stderr)
            print()


    if len(arguments) > 1:
        _config_path = pjoin(BASEPATH, 'ete_build.cfg')
        if arguments[1] == "check":
            if not pexist(APPSPATH):
                print(colorify('\nWARNING: external applications not found', "yellow"), file=sys.stderr)
                print(colorify('Install using conda (recomended):', "lgreen"), file=sys.stderr)
                print(colorify(' conda install -c etetoolkit ete_toolchain', "white"), file=sys.stderr)
                print(colorify('or manually compile from:', "lgreen"), file=sys.stderr)
                print(colorify(' https://github.com/etetoolkit/ete_toolchain', "white"), file=sys.stderr)
                print()
                sys.exit(0)

            try:
                toolchain_version = open(pjoin(APPSPATH, "__version__")).readline()
            except IOError:
                toolchain_version = "unknown"

            print("Current Toolchain path: %s " %APPSPATH)
            print("Current Toolchain version: %s" %toolchain_version)

            # setup portable apps
            config = {}
            for k in apps.builtin_apps:
                cmd = apps.get_call(k, APPSPATH, "/tmp", "1")
                config[k] = cmd
            apps.test_apps(config)
            sys.exit(0)

        elif arguments[1] in ("workflows", "wl"):
            if arguments[1] == "wl":
                print(colorify("WARNING: 'wl' is obsolete and will be removed in the future, use 'workflows' instead", "orange"), file=sys.stderr)

            base_config = check_config(_config_path)
            try:
                wf_type = arguments[2]
            except IndexError:
                wf_type = None
            list_workflows(base_config, wf_type)
            sys.exit(0)

        elif arguments[1] == "apps":
            base_config = check_config(_config_path)
            list_apps(base_config, set(arguments[2:]))
            sys.exit(0)

        elif arguments[1] == "show":
            base_config = check_config(_config_path)
            try:
                block = arguments[2]
            except IndexError:
                print("Expected a block name, found none")
                sys.exit(1)

            block_detail(block, base_config)
            sys.exit(0)

        elif arguments[1] == "dump":
            if len(arguments) > 2:
                base_config = check_config(_config_path)
                block_detail(arguments[2], base_config, color=False)
            else:
                print(open(_config_path).read())
            sys.exit(0)

        elif arguments[1] == "validate":
            print('Validating configuration file ', arguments[2])
            if pexist(arguments[2]):
                base_config = check_config(arguments[2])
                print('Everything ok')
            else:
                print('File does not exist')
                sys.exit(-1)
            sys.exit(0)

        elif arguments[1] == "version":
            print(__version__)
            sys.exit(0)

    parser = argparse.ArgumentParser(description=__DESCRIPTION__ + __EXAMPLES__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Input data related flags
    input_group = parser.add_argument_group('==== Input Options ====')

    input_group.add_argument('[check | workflows | apps | show | dump | validate]',
                             nargs='?',
                             help=("Utility commands:\n"
                                   "check: check that external applications are executable.\n"
                                   "wl: show a list of available workflows.\n"
                                   "show [name]: show the configuration parameters of a given workflow or application config block.\n"
                                   "dump [name]: dump the configuration parameters of the specified block (allows to modify predefined config).\n"
                                   "validate [configfile]: Validate a custom configuration file.\n"
                                   "version: Show current version.\n"
                                   ))

    input_group.add_argument("-c", "--custom-config", dest="custom_config",
                             type=is_file,
                             help="Custom configuration file.")

    input_group.add_argument("--base-config", dest="base_config",
                             type=is_file, default=BASEPATH+'/ete_build.cfg',
                             help="Base configuration file.")

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

    # input_group.add_argument("--seqformat", dest="seqformat",
    #                          choices=["fasta", "phylip", "iphylip", "phylip_relaxed", "iphylip_relaxed"],
    #                          default="fasta",
    #                          help="")

    input_group.add_argument("--dealign", dest="dealign",
                             action="store_true",
                             help="when used, gaps in the orginal fasta file will"
                             " be removed, thus allowing to use alignment files as input.")

    input_group.add_argument("--seq-name-parser", dest="seq_name_parser",
                             type=str,
                             help=("A Perl regular expression containing a matching group, which is"
                                   " used to parse sequence names from the input files. Use this option to"
                                   " customize the names that should be shown in the output files."
                                   " The matching group (the two parentheses) in the provided regular"
                                   " expression will be assumed as sequence name. By default, all "
                                   " characthers until the first blank space or tab delimiter are "
                                   " used as the sequence names."),
                             default='^([^\s]+)')

    input_group.add_argument("--no-seq-rename", dest="seq_rename",
                             action="store_false",
                             help="If used, sequence names will NOT be"
                             " internally translated to 10-character-"
                             "identifiers.")

    input_group.add_argument("--no-seq-checks", dest="no_seq_checks",
                            action="store_true",
                            help="Skip consistency sequence checks for not allowed symbols, etc.")
    input_group.add_argument("--no-seq-correct", dest="no_seq_correct",
                            action="store_true",
                            help="Skip sequence compatibility changes: i.e. U, J and O symbols are converted into X by default.")

    dup_names_group = input_group.add_mutually_exclusive_group()

    dup_names_group.add_argument("--ignore-dup-seqnames", dest="ignore_dup_seqnames",
                                 action = "store_true",
                                 help=("If duplicated sequence names exist in the input"
                                       " fasta file, a single random instance will be used."))

    dup_names_group.add_argument("--rename-dup-seqnames", dest="rename_dup_seqnames",
                                 action = "store_true",
                                 help=("If duplicated sequence names exist in the input"
                                       " fasta file, duplicates will be renamed."))

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
                             help="EXPERIMENTAL:A file containing the (sorted) lineage "
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
                             help="spname_delimiter is used to split"
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
                           help="EXPERIMENTAL:Enables recursive NPR capabilities (Nested Phylogenetic Reconstruction)"
                           " and specifies custom workflows and filters for each NPR iteration.")
    npr_group.add_argument("--nt-switch-threshold", dest="nt_switch_thr",
                           required=False,
                           type=float,
                           default = 0.95,
                           help="Sequence similarity at which nucleotide based alignments should be used"
                           " instead of amino-acids. ")
    npr_group.add_argument("--max-iters", dest="max_iters",
                           required=False,
                           type=int,
                           default=99999999,
                           help="EXPERIMENTAL:Set a maximum number of NPR iterations allowed.")
    npr_group.add_argument("--first-split-outgroup", dest="first_split",
                           type=str,
                           default='midpoint',
                           help=("EXPERIMENTAL:When used, it overrides first_split option"
                                 " in any tree merger config block in the"
                                 " config file. Default: 'midpoint' "))


    # Output data related flags
    output_group = parser.add_argument_group('==== Output Options ====')
    output_group.add_argument("-o", "--outdir", dest="outdir",
                              type=str, required=True,
                              help="""Output directory for results.""")

    output_group.add_argument("--scratch-dir", dest="scratch_dir",
                              type=is_dir,
                              help="""If provided, ete-build will run on the scratch folder and all files will be transferred to the output dir when finished. """)

    output_group.add_argument("--db-dir", dest="db_dir",
                              type=is_dir,
                              help="""Alternative location of the database directory""")

    output_group.add_argument("--tasks-dir", dest="tasks_dir",
                              type=is_dir,
                              help="""Output directory for the executed processes (intermediate files).""")

    output_group.add_argument("--compress", action="store_true",
                              help="Compress all intermediate files when"
                              " a workflow is finished.")

    output_group.add_argument("--logfile", action="store_true",
                              help="Log messages will be saved into a file named 'etebuild.log' a the root of the output directory.")

    output_group.add_argument("--noimg", action="store_true",
                              help="Tree images will not be generated when a workflow is finished.")

    output_group.add_argument("--email", dest="email",
                              type=str,
                              help="EXPERIMENTAL:Send an email when errors occur or a workflow is done.")

    output_group.add_argument("--email-report-time", dest="email_report_time",
                              type=int, default = 0,
                              help="EXPERIMENTAL:How often (in minutes) an email reporting the status of the execution should be sent. 0=No reports")


    # Task execution related flags
    exec_group = parser.add_argument_group('==== Execution Mode Options ====')

    exec_group.add_argument("-C", "--cpu", dest="maxcores", type=int,
                            default=1, help="Maximum number of CPU cores"
                            " available in the execution host. If higher"
                            " than 1, tasks with multi-threading"
                            " capabilities will enabled. Note that this"
                            " number will work as a hard limit for all applications,"
                            "regardless of their specific configuration.")

    exec_group.add_argument("-t", "--schedule-time", dest="schedule_time",
                            type=float, default=2,
                            help="""How often (in secs) tasks should be checked for available results.""")

    exec_group.add_argument("--launch-time", dest="launch_time",
                            type=float, default=3,
                            help="""How often (in secs) queued jobs should be checked for launching""")

    exec_type_group = exec_group.add_mutually_exclusive_group()

    exec_type_group.add_argument("--noexec", dest="no_execute",
                                 action="store_true",
                                 help=("Prevents launching any external application."
                                       " Tasks will be processed and intermediate steps will"
                                       " run, but no real computation will be performed."))

    exec_group.add_argument("--monitor", dest="monitor",
                            action="store_true",
                            help="Monitor mode: pipeline jobs will be"
                            " detached from the main process. This means that"
                            " when npr execution is interrupted, all currently"
                            " running jobs will keep running. Use this option if you"
                            " want to stop and recover an execution thread or"
                            " if jobs are expected to be executed remotely."
                            )

    exec_group.add_argument("--resume", dest="resume",
                            action="store_true",
                            help="If output directory exists, reuse data from it if possible. ")

    exec_group.add_argument("--clearall", dest="clearall",
                            action="store_true",
                            help="If output directory exists, erase all previous data and start a clean execution.")


    exec_group.add_argument("--softclear", dest="softclear",
                            action="store_true",
                            help="Clear all precomputed data (data.db), but keeps task raw data in the directory, so they can be re-processed.")

    exec_group.add_argument("--clear-seqdb", dest="clearseqs",
                            action="store_true",
                            help="Reload sequences deleting previous database if necessary.")

    exec_group.add_argument("--nochecks", dest="nochecks",
                            action="store_true",
                            help="Skip basic checks (i.e. tools available) everytime the application starts.")
    
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

    args = parser.parse_args(arguments)
    if args.tools_dir:
        APPSPATH = args.tools_dir

    try:
        toolchain_version = open(pjoin(APPSPATH, "__version__")).readline()
    except IOError:
        toolchain_version = "unknown"
    print("Toolchain path: %s " %APPSPATH)
    print("Toolchain version: %s" %toolchain_version)

    if not pexist(APPSPATH):
        print(colorify('\nWARNING: external applications directory are not found at %s' %APPSPATH, "yellow"), file=sys.stderr)
        print(colorify('Use "ete build install_tools" to install or upgrade tools', "orange"), file=sys.stderr)

    args.enable_ui = False
    if not args.noimg:
        try:
            from .. import Tree
            Tree().render('/tmp/etenpr_img_test.png')
        except:
            print('X11 DISPLAY = %s' %colorify(os.environ.get('DISPLAY', 'not detected!'), 'yellow'))
            print('(You can use --noimg to disable graphical capabilities)')
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
        print("Creating temporary scratch dir...", file=sys.stderr)
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
    GLOBALS["cmdline"] = ' '.join(arguments)

    GLOBALS["threadinfo"] = defaultdict(dict)
    GLOBALS["seqtypes"] = set()
    GLOBALS["target_species"] = set()
    GLOBALS["target_sequences"] = set()
    GLOBALS["spname_delimiter"] = args.spname_delimiter
    GLOBALS["color_shell"] = True
    GLOBALS["citator"] = Citator()


    GLOBALS["lineages"] = None
    GLOBALS["cogs_file"] = None

    GLOBALS["citator"].add("ETE")

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
    _main(sys.argv)
