#!/usr/bin/env python3

"""
A simple program to coordinate which tests to run.
"""

import sys
import os
import subprocess
from argparse import ArgumentParser


# Test files to run.
tests = {
    'fast': [
        'test_tree.py',
        'test_ncbiquery.py', 'test_gtdbquery.py',
        'test_interop.py', 'test_phylotree.py', 'test_evoltree.py',
        'test_nexus.py', 'test_indent.py',
        'test_treematcher.py',
        'test_seqgroup.py', 'test_treediff.py',
        'test_orthologs_group_delineation.py'],
    'interactive': [
        'test_treeview/test_all_treeview.py'],
    'slow': [
        'slow/test_ncbiquery_force_download.py']}


def main():
    args = get_args()

    if args.list:
        print('Tests included in each category:')
        for category, ctests in tests.items():
            print(f'\n{category}')
            print(' ', '\n  '.join(ctests))
        sys.exit()

    run_pytest(tests['fast'], args.verbose)

    if args.include_interactive:
        run_pytest(tests['interactive'], args.verbose)

    if args.include_slow:
        run_pytest(tests['slow'], args.verbose)


def run_pytest(tfiles, verbose):
    # The previous shell line was `cd tests; pytest ...`. Windows cmd
    # treats ";" as part of the path, so the documented command never
    # started pytest there. Call pytest in the tests directory instead.
    command = [sys.executable, "-m", "pytest"]
    if verbose:
        command.append("-v")
    command.extend(tfiles)
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    subprocess.run(command, cwd=tests_dir)


def get_args():
    parser = ArgumentParser(description=__doc__)

    add = parser.add_argument  # shortcut
    add('-l', '--list', action='store_true', help='list the tests in each category and exit')
    add('-i', '--include-interactive', action='store_true', help='run tests that require user input')
    add('-s', '--include-slow', action='store_true', help='run tests that take a long time')
    add('-v', '--verbose', action='store_true', help='be verbose')

    return parser.parse_args()



if __name__ == '__main__':
    main()
