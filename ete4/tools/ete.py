#!/usr/bin/env python3

import sys
import errno

import argparse
from . import (ete_ncbiquery, ete_gtdbquery,
               ete_mod, ete_compare, ete_diff)

from . import common
from .common import log
from .utils import colorify

from subprocess import Popen, PIPE

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
    _main(sys.argv)

def _main(arguments):

    if len(arguments) > 1:
        subcommand = arguments[1]
        if subcommand == "version":
            from .. import __version__

            _version = __version__

            try:
                # If on a git repository and tags are available
                # Use a tag based code (e.g. 3.1.1b2-8-gb2d12f4)
                p = Popen(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # Git not installed
                    pass
                else:
                    raise
            else:
                if p.returncode == 0:
                    _version += " (git-{})".format(bytes.decode(out).rstrip())
                else:
                    # If tags were not available
                    # Use a short hash for the current commit (e.g. b2d12f4)
                    p = Popen(["git", "rev-parse", "--short", "HEAD"], stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()

                    if p.returncode == 0:
                        _version += " (git-{})".format(bytes.decode(out).rstrip())

            print(_version)
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

    # diff
    diff_args_p = argparse.ArgumentParser(add_help=False)
    ete_diff.populate_args(diff_args_p)


    # ADD SUBPROGRAM TO THE MAIN PARSER
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    subparser = parser.add_subparsers(title="AVAILABLE PROGRAMS")

    # - MOD -
    mod_args_pp = subparser.add_parser("mod", parents=[source_args_p, main_args_p, mod_args_p],
                                       description=ete_mod.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    mod_args_pp.set_defaults(func=ete_mod.run)

    # - COMPARE -
    compare_args_p = subparser.add_parser("compare", parents=[source_args_p, ref_args_p, main_args_p],
                                           description=ete_compare.DESC,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    compare_args_p.set_defaults(func=ete_compare.run)
    ete_compare.populate_args(compare_args_p)

    # - NCBIQUERY -
    ncbi_args_p = subparser.add_parser("ncbiquery", parents=[main_args_p],
                                       description=ete_ncbiquery.DESC)
    ncbi_args_p.set_defaults(func=ete_ncbiquery.run)
    ete_ncbiquery.populate_args(ncbi_args_p)

    # - GTDBQUERY -
    gtdb_args_p = subparser.add_parser("gtdbquery", parents=[main_args_p],
                                       description=ete_gtdbquery.DESC)
    gtdb_args_p.set_defaults(func=ete_gtdbquery.run)
    ete_gtdbquery.populate_args(gtdb_args_p)

    # - DIFF -
    diff_args_p = subparser.add_parser("diff", parents=[source_args_p, ref_args_p, main_args_p],
                                           description=ete_diff.DESC,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    diff_args_p.set_defaults(func=ete_diff.run)
    ete_diff.populate_args(diff_args_p)

    # - helpers -

    generate_args_p = subparser.add_parser("version")

    # ===================
    #  EXECUTE PROGRAM
    # ===================
    if len(arguments) == 1:
        parser.print_usage()
        return

    args = parser.parse_args(arguments[1:])
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
