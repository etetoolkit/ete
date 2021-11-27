#!/usr/bin/env python3

"""
Add a tree to the database using the newick representation that exists in
a given file.
"""

import sys
from os.path import abspath, dirname, basename
sys.path.insert(0, f'{abspath(dirname(__file__))}/..')

from datetime import datetime
from collections import namedtuple
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter as fmt

import sqlite3

from ...parser.newick import read_newick, NewickError

TData = namedtuple('TData', 'name description newick')


def main():
    try:
        args = get_args()
        print(f'Adding from {args.treefile} to database {args.db} ...')
        newick = get_newick(args.treefile, verify=not args.no_verify)
        tname = args.name or basename(args.treefile).rsplit('.', 1)[0]
        tdata = TData(tname, args.description, newick)
        with sqlite3.connect(args.db) as connection:
            tree_id, name = update_database(connection, tdata)
        print(f'Added tree {name} with id {tree_id}.')
    except (FileNotFoundError, NewickError,
            sqlite3.OperationalError, sqlite3.IntegrityError) as e:
        sys.exit(e)


def get_args():
    "Return the command-line arguments"
    parser = ArgumentParser(description=__doc__, formatter_class=fmt)

    add = parser.add_argument  # shortcut
    add('treefile', help='file with the tree in newick format (- for stdin)')
    add('--db', default='trees.db', help='sqlite database file')
    add('-n', '--name', default='', help='name of the tree')
    add('-d', '--description', default='', help='description of the tree')
    add('--no-verify', action='store_true', help='do not verify newick')

    return parser.parse_args()


def get_newick(treefile, verify=True):
    "Return newick read from treefile"
    fin = open(treefile) if treefile != '-' else sys.stdin
    newick = fin.read().strip()

    if verify:
        print('Verifying newick...')
        read_newick(newick)  # discarded, but will raise exception if invalid

    return newick


def update_database(connection, tdata):
    "Update database with the tree data supplied and return its id and name"
    c = connection.cursor()

    c.execute('SELECT MAX(id) FROM trees')
    tree_id = int(c.fetchone()[0] or 0) + 1

    name = tdata.name if tdata.name != '-' else 'Tree %d' % tree_id

    c.execute('INSERT INTO trees VALUES (?, ?, ?, ?, ?)',
        [tree_id, name, tdata.description, datetime.now(), tdata.newick])

    return tree_id, name



if __name__ == '__main__':
    main()
