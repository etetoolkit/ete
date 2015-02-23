#!/usr/bin/env python
import sys
import os
TOOLSPATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.insert(0, TOOLSPATH)

import argparse
import ete_split, ete_expand, ete_annotate, ete_ncbiquery, ete_view, ete_generate, ete_mod, ete_extract, ete_compare
import common
from common import log


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
    if not args.src_trees:
        log.debug("Reading trees from standard input...")
        args.src_trees = sys.stdin
    
    for stree in args.src_trees:
        # CHECK WHAT is needed before process the main command, allows mods before analyses        
        yield stree
      
        
def main():
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

    # - ANNOTATE -
    mod_args_pp = subparser.add_parser("mod", parents=[source_args_p, main_args_p, mod_args_p],
                                       description=ete_mod.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    mod_args_pp.set_defaults(func=ete_mod.run)
    
    # - ANNOTATE -
    annotate_args_p = subparser.add_parser("annotate", parents=[source_args_p, main_args_p],
                                       description=ete_annotate.DESC,
                                       formatter_class=argparse.RawDescriptionHelpFormatter)
    annotate_args_p.set_defaults(func=ete_annotate.run)
    ete_annotate.populate_args(annotate_args_p)
    

    # - COMPARE -
    compare_args_p = subparser.add_parser("compare", parents=[source_args_p, mod_args_p, ref_args_p, main_args_p],
                                           description=ete_compare.DESC,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    compare_args_p.set_defaults(func=ete_compare.run)
    ete_compare.populate_args(compare_args_p)

    # - VIEW -
    view_args_p = subparser.add_parser("view", parents=[source_args_p, mod_args_p, main_args_p],
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

    # - build -
    generate_args_p = subparser.add_parser("build")
    

    # ===================
    #  EXECUTE PROGRAM
    # ===================
    
    args = parser.parse_args()
    
    LOG_LEVEL = args.verbosity 
    
    if hasattr(args, "src_trees"):
        args.src_tree_iterator = tree_iterator(args)
        
    elif hasattr(args, "search"):
        if not args.search:
            log.debug("Reading taxa from standard input...")
            args.search = sys.stdin 
        
    # Call main program
    args.func(args)

if __name__=="__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        import phylobuild
        del sys.argv[1]
        phylobuild._main()
        
    else:
        main()
