#!/usr/bin/env python3

"""
A simple program to coordinate which tests to run.
"""

import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter as fmt


# Test files to run.
tests = {
    'fast': [
        'test_tree.py', 'test_arraytable.py', 'test_clustertree.py',
        'test_gtdbquery.py', 'test_interop.py', 'test_phylotree.py',
        'test_seqgroup.py', 'test_treediff.py', 'test_ncbiquery.py',
        'test_nexus.py', 'test_treematcher.py',
        'test_orthologs_group_delineation.py'],
    'interactive': [
        'test_treeview/test_all_treeview.py'],
    'slow': [
        'slow/test_ncbiquery_force_download.py']}


def main():
    args = get_args()

    run_pytest(tests['fast'], args.verbose)

    if args.include_interactive:
        run_pytest(tests['interactive'], args.verbose)

    if args.include_slow:
        run_pytest(tests['slow'], args.verbose)


def run_pytest(tfiles, verbose):
    os.system('cd tests; ' +
              'pytest ' + ('-v ' if verbose else '') + ' '.join(tfiles))


def get_args():
    parser = ArgumentParser(description=__doc__, formatter_class=fmt)

    add = parser.add_argument  # shortcut
    add('-i', '--include-interactive', action='store_true',
        help='run tests that require user input')
    add('-s', '--include-slow', action='store_true',
        help='run tests that take a long time')
    add('-v', '--verbose', action='store_true', help='be verbose')

    return parser.parse_args()



if __name__ == '__main__':
    main()
