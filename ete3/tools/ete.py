#!/usr/bin/env python

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
import sys
import os
from os.path import join as pjoin
from os.path import split as psplit
from os.path import exists as pexist

from six.moves import input

TOOLSPATH = os.path.realpath(os.path.split(os.path.realpath(__file__))[0])
#sys.path.insert(0, TOOLSPATH)
#sys.path.insert(1, TOOLSPATH.replace("ete3/tools", ''))
#print sys.path

import argparse
from . import ete_split, ete_expand, ete_annotate, ete_ncbiquery, ete_view, ete_generate, ete_mod, ete_extract, ete_compare, ete_codeml
from . import common
from .common import log
from .utils import colorify

"""
def ete_split(args):
    # bydups, bydist, name, find clsuters
def ete_expand(args):
    # polytomies
def ete_extract(args):
    #dups, orthologs, partitions, edges, dist_matrix, ancestor,
def ete_convert(args):
    # between newick formats, orthoxml, phyloxml
def ete_maptrees(args):
def ete_reconcile(args):
def ete_consense(args):
    # all observed splits
def ete_fetch(args):
def ete_codeml(args):

"""

def tree_iterator(args):
    if not args.src_trees and not sys.stdin.isatty():
        log.debug("Reading trees from standard input...")
        args.src_trees = sys.stdin
    elif not args.src_trees:
        log.error("At least one tree is required as input (i.e --src_trees ) ")
        sys.exit(-1)

    for stree in args.src_trees:
        # CHECK WHAT is needed before process the main command, allows mods before analyses
        yield stree.strip()


def main():

    if len(sys.argv) > 1:
        subcommand = sys.argv[1]
        if  subcommand == "version":
            from .. import __version__
            print(__version__)
            return
        elif subcommand == "upgrade-external-tools":
            import tarfile
            try:
                from urllib import urlretrieve
            except ImportError:
                # python 3
                from urllib.request import urlretrieve

            
            APPSPATH = os.path.expanduser("~/.etetoolkit/ext_apps-latest/")
            ETEHOMEDIR = os.path.expanduser("~/.etetoolkit/")
            
            if os.path.exists(pjoin('/etc/etetoolkit/', 'ext_apps-latest')):
                # if a copy of apps is part of the ete distro, use if by default
                APPSPATH = pjoin('/etc/etetoolkit/', 'ext_apps-latest')
                ETEHOMEDIR = '/etc/etetoolkit/'
            else:
                # if not, try a user local copy
                APPSPATH = pjoin(ETEHOMEDIR, 'ext_apps-latest')

            print (colorify('Downloading latest version of tools...', "green"), file=sys.stderr)

            if len(sys.argv) > 2:
                TARGET_DIR = sys.argv[2]
            else:
                TARGET_DIR = ''
                
            while not pexist(TARGET_DIR):
                TARGET_DIR = input('target directory? [%s]:' %ETEHOMEDIR).strip()
                if TARGET_DIR == '':
                    TARGET_DIR = ETEHOMEDIR
                    break
                
            if TARGET_DIR == ETEHOMEDIR:
                try:
                    os.mkdir(ETEHOMEDIR)
                except OSError:
                    pass

            version_file = "latest.tar.gz"
            urlretrieve("https://github.com/jhcepas/ext_apps/archive/%s" %version_file, pjoin(TARGET_DIR, version_file))
            print(colorify('Decompressing...', "green"), file=sys.stderr)
            tfile = tarfile.open(pjoin(TARGET_DIR, version_file), 'r:gz')
            tfile.extractall(TARGET_DIR)
            print(colorify('Compiling tools...', "green"), file=sys.stderr)
            sys.path.insert(0, pjoin(TARGET_DIR, 'ext_apps-latest'))
            import compile_all
            s = compile_all.compile_all()
            sys.exit(s)
            
        elif subcommand == "build":
            from . import phylobuild
            del sys.argv[1]
            phylobuild._main()
            return

    # CREATE REUSABLE PARSER OPTIONS

    # main args
    main_args_p = argparse.ArgumentParser(add_help=False)
    common.populate_main_args(main_args_p)
    # source tree args
    source_args_p = argparse.ArgumentParser(add_help=False)
    common.populate_source_args(source_args_p)
    # ref tree args
    ref_args_p = argparse.ArgumentParser(add_help=False)
    common.populate_ref_args(ref_args_p)
    # mod
    mod_args_p = argparse.ArgumentParser(add_help=False)
    ete_mod.populate_args(mod_args_p)
    # expand
    expand_args_p = argparse.ArgumentParser(add_help=False)
    ete_expand.populate_args(expand_args_p)
    # extract
    extract_args_p = argparse.ArgumentParser(add_help=False)
    ete_extract.populate_args(extract_args_p)
    # split
    split_args_p = argparse.ArgumentParser(add_help=False)
    ete_split.populate_args(split_args_p)


    # ADD SUBPROGRAM TO THE MAIN PARSER
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    subparser = parser.add_subparsers(title="AVAILABLE PROGRAMS")

    # - MOD -
    mod_args_pp = subparser.add_parser("mod", parents=[source_args_p, main_args_p, mod_args_p],
                                       description=ete_mod.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    mod_args_pp.set_defaults(func=ete_mod.run)

    # - EXTRACT -
    extract_args_pp = subparser.add_parser("extract", parents=[source_args_p, main_args_p, extract_args_p],
                                       description=ete_extract.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    extract_args_pp.set_defaults(func=ete_extract.run)


    # - ANNOTATE -
    annotate_args_p = subparser.add_parser("annotate", parents=[source_args_p, main_args_p],
                                       description=ete_annotate.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    annotate_args_p.set_defaults(func=ete_annotate.run)
    ete_annotate.populate_args(annotate_args_p)


    # - COMPARE -
    compare_args_p = subparser.add_parser("compare", parents=[source_args_p, ref_args_p, main_args_p],
                                           description=ete_compare.DESC,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    compare_args_p.set_defaults(func=ete_compare.run)
    ete_compare.populate_args(compare_args_p)

    # - VIEW -
    view_args_p = subparser.add_parser("view", parents=[source_args_p, main_args_p],
                                        description=ete_view.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    view_args_p.set_defaults(func=ete_view.run)
    ete_view.populate_args(view_args_p)


    # - NCBIQUERY -
    ncbi_args_p = subparser.add_parser("ncbiquery", parents=[main_args_p],
                                       description=ete_ncbiquery.DESC)
    ncbi_args_p.set_defaults(func=ete_ncbiquery.run)
    ete_ncbiquery.populate_args(ncbi_args_p)

    # - GENERATE -
    generate_args_p = subparser.add_parser("generate", parents=[source_args_p, main_args_p],
                                           description=ete_generate.DESC,
                                           formatter_class=argparse.RawDescriptionHelpFormatter)

    generate_args_p.set_defaults(func=ete_generate.run)
    ete_generate.populate_args(generate_args_p)

    # - CODEML -
    codeml_args_p = subparser.add_parser("codeml", parents=[main_args_p],
                                       description=ete_codeml.DESC)
    codeml_args_p.set_defaults(func=ete_codeml.run)
    ete_codeml.populate_args(codeml_args_p)
    
    # - build -
    generate_args_p = subparser.add_parser("build")

    # - helpers -
    
    generate_args_p = subparser.add_parser("version")
    generate_args_p = subparser.add_parser("upgrade-external-tools")
    
    # ===================
    #  EXECUTE PROGRAM
    # ===================

    args = parser.parse_args()

    LOG_LEVEL = args.verbosity
    if hasattr(args, "src_trees"):
        args.src_tree_iterator = tree_iterator(args)

    elif args.func==ete_ncbiquery.run and not getattr(args, "search", None):
        if not args.search and not sys.stdin.isatty():
            log.debug("Reading taxa from standard input...")
            args.search = sys.stdin

    # Call main program
    args.func(args)

if __name__=="__main__":
    main()
