#!/usr/bin/env python3

"""
Keep the data of trees and present a REST api to talk
to the world.

REST call examples:
  GET    /users       Get all users
  GET    /users/{id}  Get the user information identified by "id"
  POST   /users       Create a new user
  PUT    /users/{id}  Update the user information identified by "id"
  DELETE /users/{id}  Delete user by "id"
"""

# The structure that we want to follow is:
#
# tree
#   id: int
#   name: str
#   description: str
#   birth: datetime
#   newick: str

import os
os.chdir(os.path.abspath(os.path.dirname(__file__)))

import sys
sys.path.insert(0, '..')

import re
from math import pi
from functools import partial
from time import time
from threading import Timer
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
import gzip
import json
import shutil

from flask import Flask, request, jsonify, g, redirect, url_for
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_compress import Compress
import sqlalchemy
from itsdangerous import TimedJSONWebSignatureSerializer as JSONSigSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from ete4 import Tree
from ete4.smartview import TreeStyle
from ete4.treeview.main import _FaceAreas
from ete4.parser.newick import NewickError
from ete4.smartview.utils import InvalidUsage, get_random_string
from ete4.smartview.ete import nexus, draw, gardening as gdn
from ete4.smartview import get_layout_outline,\
        get_layout_leaf_name, get_layout_branch_length,\
        get_layout_branch_support, get_layout_align_link,\
        get_layout_nleaves

# call initialize() to fill these up
app = None
db = None


# Dataclass containing info specific to each tree
@dataclass
class AppTree:
    tree: Tree = None
    name: str = None
    style: TreeStyle = None
    timer: float = None
    initialized: bool = False
    selected: dict = None
    searches: dict = None

# REST api.

class Drawers(Resource):
    def get(self, name=None, tree_id=None):
        "Return data from the drawer. In aligned mode if aligned faces"
        try:
            tree_id, _ = get_tid(tree_id)
            if name not in ['Rect', 'Circ'] and\
                    any(getattr(ly, 'contains_aligned_face', False)\
                        for ly in app.trees[int(tree_id)].style.layout_fn):
                name = 'Align' + name
            drawer_class = next(d for d in draw.get_drawers()
                if d.__name__[len('Drawer'):] == name)
            return {'type': drawer_class.TYPE,
                    'npanels': drawer_class.NPANELS}
        except StopIteration:
            raise InvalidUsage(f'not a valid drawer: {name}')


class Layouts(Resource):
    def get(self):
        active = [ l.__name__ for l in app.trees['default'].style.layout_fn ]
        app.trees.pop('default')
        return { l.__name__: (l.__name__ in active) for l in app.layouts }


class Trees(Resource):
    def get(self, tree_id=None):
        "Return data from the tree (or info about all trees if no id given)"
        rule = request.url_rule.rule  # shortcut
        
        # Update tree's timer
        if rule.startswith('/trees/<string:tree_id>'):
            tid, subtree = get_tid(tree_id)
            load_tree(tree_id)  # load if it was not loaded in memory
            tree = app.trees[int(tid)]
            tree.timer = time()

        if rule == '/trees':
            if app.memory_only:
                raise InvalidUsage(f'invalid path {rule} in memory_only mode', 404)
            return [get_tree(pid) for pid in dbget0('id', 'trees')]
        elif rule == '/trees/<string:tree_id>':
            if app.memory_only:
                raise InvalidUsage(f'invalid path {rule} in memory_only mode', 404)
            return get_tree(tree_id)
        elif rule == '/trees/<string:tree_id>/nodeinfo':
            node = gdn.get_node(tree.tree, subtree)
            return node.props
        elif rule == '/trees/<string:tree_id>/name':
            return tree.name
        elif rule == '/trees/<string:tree_id>/newick':
            MAX_MB = 2
            return get_newick(tree_id, MAX_MB)
        elif rule == '/trees/<string:tree_id>/selected':
            selected = {  text: { 'nparents': len(parents) }
                for text, (_, parents) in (tree.selected or {}).items() }
            return { 'selected': selected }
        elif rule == '/trees/<string:tree_id>/select':
            nparents = store_selection(tid, subtree)
            return {'message': 'ok', 'nparents': nparents}
        elif rule == '/trees/<string:tree_id>/remove_selection':
            removed = remove_selection(tid, subtree)
            message = 'ok' if removed else 'search not found'
            return {'message': message}
        elif rule == '/trees/<string:tree_id>/searches':
            searches = { 
                text: { 'nresults' : len(results), 'nparents': len(parents) }
                for text, (results, parents) in (tree.searches or {}).items() }
            return { 'searches': searches }
        elif rule == '/trees/<string:tree_id>/search':
            nresults, nparents = store_search(tree_id, request.args.copy())
            return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}
        elif rule == '/trees/<string:tree_id>/remove_search':
            removed = remove_search(tid, request.args.copy())
            message = 'ok' if removed else 'search not found'
            return {'message': message}
        elif rule == '/trees/<string:tree_id>/draw':
            drawer = get_drawer(tree_id, request.args.copy())
            return list(drawer.draw())
        elif rule == '/trees/<string:tree_id>/size':
            width, height = load_tree(tree_id).size
            return {'width': width, 'height': height}
        elif rule == '/trees/<string:tree_id>/properties':
            t = load_tree(tree_id)
            properties = set()
            for node in t.traverse():
                properties |= node.props.keys()
            return list(properties)
        elif rule == '/trees/<string:tree_id>/nodecount':
            t = load_tree(tree_id)
            tnodes = tleaves = 0
            for node in t.traverse():
                tnodes += 1
                if node.is_leaf():
                    tleaves += 1
            return {'tnodes': tnodes, 'tleaves': tleaves}
        elif rule == '/trees/<string:tree_id>/ultrametric':
            return tree.style.ultrametric

    def post(self):
        "Add tree(s)"
        ids = add_trees_from_request()
        return {'message': 'ok', 'ids': ids}, 201

    def put(self, tree_id):
        "Modify tree"
        rule = request.url_rule.rule  # shortcut

        # Update tree's timer
        if rule.startswith('/trees/<string:tree_id>'):
            tid, subtree = get_tid(tree_id)
            app.trees[int(tid)].timer = time()

        if rule == '/trees/<string:tree_id>':
            modify_tree_fields(tree_id)
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/sort':
            node_id, key_text, reverse = request.json
            sort(tree_id, node_id, key_text, reverse)
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/root_at':
            tid, subtree = get_tid(tree_id)
            if subtree:
                raise InvalidUsage('operation not allowed with subtree')
            node_id = request.json
            t = load_tree(tid)
            app.trees[int(tid)].tree = gdn.root_at(gdn.get_node(t, node_id))
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/move':
            try:
                t = load_tree(tree_id)
                node_id, shift = request.json
                gdn.move(gdn.get_node(t, node_id), shift)
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot move ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/remove':
            try:
                t = load_tree(tree_id)
                node_id = request.json
                gdn.remove(gdn.get_node(t, node_id))
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot remove ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/rename':
            try:
                t = load_tree(tree_id)
                node_id, name = request.json
                gdn.get_node(t, node_id).name = name
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot rename ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/reload':
            tid, subtree = get_tid(tree_id)
            if subtree:
                raise InvalidUsage('operation not allowed with subtree')
            reload_tree(tid)
            return {'message': 'ok'}

    def delete(self, tree_id):
        "Delete tree and all references to it"
        tid = int(tree_id)
        if not app.memory_only:
            try:
                assert dbcount('trees WHERE id=?', tid) == 1, 'unknown tree'
            except (ValueError, AssertionError) as e:
                raise InvalidUsage(f'for tree id {tree_id}: {e}')

        del_tree(tid)
        return {'message': 'ok'}


class Id(Resource):
    def get(self, path):
        if not path.startswith('trees/'):
            raise InvalidUsage('invalid path %r' % path, 404)

        name = path.split('/', 1)[-1]
        if path.startswith('trees/'):
            pids = dbget0('id', 'trees WHERE name=?', name)
            if len(pids) != 1:
                raise InvalidUsage('unknown tree name %r' % name)
            return {'id': pids[0]}


# Auxiliary functions.

def init_timer(fn):
    def wrapper(*args, **kwargs):
        if type(args[0]) == int:
            tid = args[0]
            return_val = fn(*args, **kwargs)
        else:
            tid = return_val = fn(*args, **kwargs)
        app.trees[int(tid)].timer = time()
        return return_val
    return wrapper


def load_tree(tree_id):
    "Add tree to app.trees and initialize it if not there, and return it"
    try:
        tid, subtree = get_tid(tree_id)
        tree = app.trees[int(tid)]
        ultrametric = tree.style.ultrametric

        if tree.tree:
            t = gdn.get_node(tree.tree, subtree)
            # Reinitialize if layouts have to be reapplied
            if not tree.initialized:
                tree.initialized = True
                if ultrametric:
                    t.convert_to_ultrametric()
                    gdn.standardize(t)
                for node in t.traverse():
                    node.is_initialized = False
                    node.faces = _FaceAreas()
                    node.collapsed_faces = _FaceAreas()
            return t
        else:
            name, t = retrieve_tree(tid)
            tree = app.trees[int(tid)]
            tree.name, tree.tree = name, t
            return gdn.get_node(t, subtree)

    except (AssertionError, IndexError):
        raise InvalidUsage(f'unknown tree id {tree_id}', 404)


def load_tree_from_newick(tid, newick):
    """Load tree into memory from newick"""
    t = Tree(newick)

    if app.trees[int(tid)].style.ultrametric:
        t.convert_to_ultrametric()

    gdn.standardize(t)
    return t


@init_timer
def retrieve_tree(tid):
    """Retrieve tree from tmp or local db.
    Called when tree has been deleted from memory

    """
    if app.memory_only:
        with open(f'/tmp/{tid}.nwx') as nw:
            name = nw.readline().strip()
            newick = nw.readline().strip()
    else:
        newicks = dbget('name,newick', 'trees WHERE id=?', tid)
        assert len(newicks) == 1, "More than one tree with same id"
        name, newick = newicks[0].values()

    t = load_tree_from_newick(tid, newick)
    return name, t
    

def reload_tree(tid):
    """Delete tree fromm memory and reload it"""
    app.trees.pop(tid, None) # avoid possible key-error
    if app.memory_only:
        name, t = retrieve_tree(tid)
        app.trees[int(tid)].name = name
        app.trees[int(tid)].tree = t
    else:
        load_tree(tid)


def get_drawer(tree_id, args):
    "Return the drawer initialized as specified in the args"
    valid_keys = ['x', 'y', 'w', 'h', 'panel', 'zx', 'zy', 'drawer', 'min_size',
                  'layouts', 'ultrametric', 'collapsed_ids', 
                  'rmin', 'amin', 'amax']

    try:
        assert all(k in valid_keys for k in args.keys()), 'invalid keys'

        get = lambda x, default: float(args.get(x, default))  # shortcut

        viewport = ([get(k, 0) for k in ['x', 'y', 'w', 'h']]
            if all(k in args for k in ['x', 'y', 'w', 'h']) else None)
        assert viewport is None or (viewport[2] > 0 and viewport[3] > 0), \
            'invalid viewport'  # width and height must be > 0

        panel = get('panel', 0)

        zoom = (get('zx', 1), get('zy', 1))
        assert zoom[0] > 0 and zoom[1] > 0, 'zoom must be > 0'

        tid, _ = get_tid(tree_id)
        tree = app.trees[int(tid)]

        active_layouts = args.get('layouts')
        if active_layouts != None:
            update_layouts(active_layouts, tid)

        drawer_name = args.get('drawer', 'RectFaces')
        # Automatically provide aligned drawer when necessary
        if drawer_name not in ['Rect', 'Circ'] and\
                any(getattr(ly, 'contains_aligned_face', False)\
                    for ly in tree.style.layout_fn):
            drawer_name = 'Align' + drawer_name
        drawer_class = next((d for d in draw.get_drawers()
            if d.__name__[len('Drawer'):] == drawer_name), None)

        drawer_class.COLLAPSE_SIZE = get('min_size', 6)
        assert drawer_class.COLLAPSE_SIZE > 0, 'min_size must be > 0'

        limits = (None if not drawer_name.startswith('Circ') else
            (get('rmin', 0), 0,
             get('amin', -180) * pi/180, get('amax', 180) * pi/180))

        collapsed_ids = set(tuple(int(i) for i in node_id.split(','))
            for node_id in json.loads(args.get('collapsed_ids', '[]')))

        update_ultrametric(args.get('ultrametric'), tid)

        selected = tree.selected
        searches = tree.searches
        
        return drawer_class(load_tree(tree_id), viewport, panel, zoom,
                    limits, collapsed_ids, selected, searches, tree.style)
    except StopIteration:
        raise InvalidUsage(f'not a valid drawer: {drawer_name}')
    except (ValueError, AssertionError) as e:
        raise InvalidUsage(str(e))


def get_newick(tree_id, max_mb):
    "Return the newick representation of the given tree"

    newick = load_tree(tree_id).write()

    size_mb = len(newick) / 1e6
    if size_mb > max_mb:
        raise InvalidUsage('newick too big (%.3g MB)' % size_mb)

    return newick


def remove_search(tid, args):
    "Remove search"
    if 'text' not in args:
        raise InvalidUsage('missing search text')

    searches = app.trees[int(tid)].searches
    text = args.pop('text').strip()
    return searches.pop(text, None)


def store_search(tree_id, args):
    "Store the results and parents of a search and return their numbers"
    if 'text' not in args:
        raise InvalidUsage('missing search text')

    text = args.pop('text').strip()
    func = get_search_function(text)

    try:
        results = set(node for node in load_tree(tree_id).traverse() if func(node))

        parents = set()
        for node in results:
            parent = node.up
            while parent and parent not in parents:
                parents.add(parent)
                parent = parent.up

        tid = get_tid(tree_id)[0]
        app.trees[int(tid)].searches[text] = (results, parents)

        return len(results), len(parents)
    except InvalidUsage:
        raise
    except Exception as e:
        raise InvalidUsage(f'evaluating expression: {e}')


def remove_selection(tid, subtree):
    "Remove selection"
    subtree_string = ",".join([ str(i) for i in subtree ])
    return app.trees[int(tid)].selected.pop(subtree_string, None)


def store_selection(tid, subtree):
    "Store the result and parents of a selection and return number of parents"

    app_tree = app.trees[int(tid)]
    node = gdn.get_node(app_tree.tree, subtree)

    parents = set()
    parent = node.up
    while parent and parent not in parents:
        parents.add(parent)
        parent = parent.up

    subtree_string = ",".join([ str(i) for i in subtree ])
    app_tree.selected[subtree_string] = (node, parents)

    return len(parents)


def get_search_function(text):
    "Return a function of a node that returns True for the searched nodes"
    if text.startswith('/'):
        return get_command_search(text)  # command-based search
    elif text == text.lower():
        return lambda node: text in node.name.lower()  # case-insensitive search
    else:
        return lambda node: text in node.name  # case-sensitive search


def get_command_search(text):
    "Return the appropriate node search function according to the command"
    parts = text.split(None, 1)
    if parts[0] not in ['/r', '/e']:
        raise InvalidUsage('invalid command %r' % parts[0])
    if len(parts) != 2:
        raise InvalidUsage('missing argument to command %r' % parts[0])

    command, arg = parts
    if command == '/r':  # regex search
        return lambda node: re.search(arg, node.name)
    elif command == '/e':  # eval expression
        return get_eval_search(arg)
    else:
        raise InvalidUsage('invalid command %r' % command)


def get_eval_search(expression):
    "Return a function of a node that evaluates the given expression"
    try:
        code = compile(expression, '<string>', 'eval')
    except SyntaxError as e:
        raise InvalidUsage(f'compiling expression: {e}')

    return lambda node: safer_eval(code, {
        'name': node.name, 'is_leaf': node.is_leaf(),
        'length': node.dist, 'dist': node.dist, 'd': node.dist,
        'props': node.props, 'p': node.props,
        'get': dict.get,
        'children': node.children, 'ch': node.children,
        'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
        'regex': re.search,
        'len': len, 'sum': sum, 'abs': abs, 'float': float, 'pi': pi})


def safer_eval(code, context):
    "Return a safer version of eval(code, context)"
    for name in code.co_names:
        if name not in context:
            raise InvalidUsage('invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)


def sort(tree_id, node_id, key_text, reverse):
    "Sort the (sub)tree corresponding to tree_id and node_id"
    t = load_tree(tree_id)

    try:
        code = compile(key_text, '<string>', 'eval')
    except SyntaxError as e:
        raise InvalidUsage(f'compiling expression: {e}')

    def key(node):
        return safer_eval(code, {
            'node': node, 'name': node.name, 'is_leaf': node.is_leaf(),
            'length': node.dist, 'dist': node.dist, 'd': node.dist,
            'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
            'children': node.children, 'ch': node.children,
            'len': len, 'sum': sum, 'abs': abs})

    gdn.sort(gdn.get_node(t, node_id), key, reverse)


def add_trees_from_request():
    "Add trees to the database and return a dict of {name: id}"
    if request.form:
        trees = get_trees_from_form()
    else:
        data = get_fields(required=['name', 'newick'],  # id
                          valid_extra=['description'])
        trees = [data]

    return {data['name']: add_tree(data) for data in trees}


def get_trees_from_form():
    "Return list of dicts with tree info read from a form in the request"
    form = request.form
    if 'trees' in request.files:
        text = get_file_contents(request.files['trees'])
        try:
            trees = nexus.get_trees(text)
            return [{'name': name, 'newick': newick}
                        for name,newick in trees.items()]
        except nexus.NexusError:
            return [{'name': form['name'], 'newick': text,
                     'description': form.get('description', '')}]
    else:
        return [{
            'id': form.get('id'),
            'name': form['name'], 
            'newick': form['newick'],
            'description': form.get('description', '')
            }]


def get_file_contents(fp):
    "Return the contents of a file received as formdata"
    try:
        data = fp.stream.read()
        if fp.filename.endswith('.gz'):
            data = gzip.decompress(data)
        return data.decode('utf-8').strip()
    except (gzip.BadGzipFile, UnicodeDecodeError) as e:
        raise InvalidUsage(f'when reading {fp.filename}: {e}')


@init_timer
def add_tree(data, replace=True):
    "Add tree to the database with given data and return its id"
    
    if app.memory_only:
        tid = data['id']
        name = data['name']
        newick = data['newick']
        del_tree(tid)  # delete if there is a tree with same id
        with open(f'/tmp/{tid}.nwx', 'w') as nw:
            nw.writelines([name + '\n', newick])
        return tid
    
    if dbcount('trees WHERE name=?', data['name']) != 0:
        if replace:
            print(f'Found {data["name"]} in local database. Updating tree...')
            with shared_connection([dbget0]) as [get0]:
                tid = get0('id', 'trees WHERE name=?', data['name'])[0]
                del_tree(tid)
        else:
            raise InvalidUsage('existing tree name %r' % data['name'])

    try:
        # load it to validate
        Tree(data['newick']) 
    except NewickError as e:
        raise InvalidUsage(f'malformed tree - {e}')

    data['birth'] = datetime.now()  # add creation time

    tid = None  # will be filled later if it all works
    data.pop('id', None)  # it will raise an error
    with shared_connection([dbget0, dbexe]) as [get0, exe]:
        cols, vals = zip(*data.items())
        try:
            qs = '(%s)' % ','.join('?' * len(vals))
            exe('INSERT INTO trees %r VALUES %s' % (tuple(cols), qs), vals)
        except sqlalchemy.exc.IntegrityError as e:
            raise InvalidUsage(f'database exception adding tree: {e}')

        tid = get0('id', 'trees WHERE name=?', data['name'])[0]
    return tid


def modify_tree_fields(tree_id):
    "Modify in the database the tree fields that appear in a request"
    try:
        tid = int(tree_id)

        assert dbcount('trees WHERE id=?', tid) == 1, 'invalid id'

        data = get_fields(valid_extra=[
            'name', 'description', 'newick'])

        if not data:
            return {'message': 'ok'}

        cols, vals = zip(*data.items())
        qs = ','.join('%s=?' % x for x in cols)
        res = dbexe('UPDATE trees SET %s WHERE id=%d' % (qs, tid), vals)

        assert res.rowcount == 1, f'unknown tree'
    except (ValueError, AssertionError) as e:
        raise InvalidUsage(f'for tree id {tree_id}: {e}')


# Layout related functions
def get_layouts(layouts=[]):
    # Get default layouts from their getters
    default_layouts = [ get_layout_outline(), get_layout_leaf_name(),
            get_layout_branch_length(), get_layout_branch_support(),
            get_layout_nleaves(), get_layout_align_link(), ]

    # Get layouts from TreeStyle
    ts_layouts = app.trees['default'].style.layout_fn
    app.trees.pop('default')

    layouts = list(set(default_layouts + ts_layouts + layouts))

    return [ ly for ly in layouts if ly.__name__ != '<lambda>' ]


def update_layouts(active_layouts, tid):
    """ Update app layouts based on front end status """
    tree_style = app.trees[int(tid)].style  # specific to each tree
    ts_layouts = [ ly.__name__ for ly in tree_style.layout_fn ]
    reinit_trees = False
    for layout in app.layouts:
        name = layout.__name__
        status = name in ts_layouts
        new_status = name in active_layouts
        if status != new_status:
            reinit_trees = True
            # Update tree_style layout functions
            if new_status == True:
                tree_style.layout_fn = layout
            elif new_status == False:
                tree_style.del_layout_fn(name)  # remove layout_fn from ts

    if reinit_trees:
        if app.memory_only:
            app.trees[int(tid)].initialized = False
        else:
            for t in app.trees.values():
                t.initialized = False


def update_ultrametric(ultrametric, tid):
    """ Update trees if ultrametric option toggled """
    tree = app.trees[int(tid)]
    tree_style = tree.style  # specific to each tree
    # Boolean from front-end 0 or 1
    ultrametric = True if (ultrametric and int(ultrametric)) else False
    if tree_style.ultrametric != ultrametric:
        tree_style.ultrametric = ultrametric
        if ultrametric == True:
            tree.initialized = False
        else:
            app.trees.pop(tid, None) # delete from memory


# Database-access functions.

def dbexe(command, *args, conn=None):
    "Execute a sql command (using a given connection if given)"
    conn = conn or db.connect()
    return conn.execute(command, *args)


def dbcount(where, *args, conn=None):
    "Return the number of rows from the given table (and given conditions)"
    res = dbexe('SELECT COUNT(*) FROM %s' % where, *args, conn=conn)
    return res.fetchone()[0]


def dbget(what, where, *args, conn=None):
    "Return result of the query 'select what from where' as a list of dicts"
    res = dbexe('SELECT %s FROM %s' % (what, where), *args, conn=conn)
    return [dict(zip(what.split(','), x)) for x in res.fetchall()]


def dbget0(what, where, *args, conn=None):
    "Return a list of the single column of values from get()"
    assert ',' not in what, 'Use this function to select a single column only'
    return [x[what] for x in dbget(what, where, *args, conn=conn)]


@contextmanager
def shared_connection(functions):
    "Create a connection and yield the given functions but working with it"
    with db.connect() as conn:
        yield [partial(f, conn=conn) for f in functions]


# Manage basic fields (related to the SQL schema, like users, readers, etc.).

def get_tid(tree_id):
    "Return the tree id and the subtree id, with the appropriate types"
    try:
        if type(tree_id) == int:
            return tree_id, []
        else:
            tid, *subtree = tree_id.split(',')
            return int(tid), [int(n) for n in subtree]
    except ValueError:
        raise InvalidUsage(f'invalid tree id {tree_id}', 404)


def get_tree(tree_id):
    "Return all the fields of a given tree"
    tid, subtree = get_tid(tree_id)

    with shared_connection([dbget, dbget0]) as [get, get0]:
        trees = get('id,name,description,birth', 'trees WHERE id=?', tid)
        if len(trees) == 0:
            raise InvalidUsage(f'unknown tree id {tid}', 404)

        tree = trees[0]
        tree['subtree'] = subtree

    return strip(tree)


def del_tree(tid, from_db=True):
    "Delete a tree and everywhere where it appears referenced"
    if app.memory_only:
        shutil.rmtree(f'/tmp/{tid}.nwx', ignore_errors=True)
    elif from_db:
        # Delete from local db
        exe = db.connect().execute
        exe('DELETE FROM trees WHERE id=?', tid)
    app.trees.pop(tid, None)


def purge(interval=None, max_time=30*60, from_db=True):
    """Delete trees that have been inactive for a certain period of time
        :interval: if set, recursively calls purge after given interval.
        :max_time: maximum inactivity time in seconds. Default 30 min.
    """
    trees = list(app.trees.keys())
    for tid in trees:
        inactivity_time = time() - app.trees[tid].timer
        if inactivity_time > max_time: 
            del_tree(tid, from_db)
    # Call self after interval
    if interval: # in seconds
        print(f'Current trees in memory: {len(list(app.trees.keys()))}')
        Timer(interval, purge, [interval, max_time, from_db]).start()


def strip(d):
    "Return dictionary without the keys that have empty values"
    d_stripped = {}
    for k, v in d.items():
        if v:
            d_stripped[k] = d[k]
    return d_stripped


def get_fields(required=None, valid_extra=None):
    "Return fields and raise exception if missing required or invalid present"
    if not request.json:
        raise InvalidUsage('missing json content')

    data = request.json.copy()

    if required and any(x not in data for x in required):
        raise InvalidUsage(f'must have the fields {required}')

    valid = (required or []) + (valid_extra or [])
    if not all(x in valid for x in data):
        raise InvalidUsage(f'can only have the fields {valid}')

    return data


# App initialization.

def create_example_database():
    db_path = app.config['DATABASE']

    os.system(f'sqlite3 {db_path} < create_tables.sql')
    os.system(f'sqlite3 {db_path} < sample_data.sql')

    for tfile in ['HmuY.aln2.tree', 'aves.tree', 'GTDB_bact_r95.tree']:
        os.system(f'./add_tree.py --db {db_path} ../examples/{tfile}')


def initialize(tree=None, tree_style=None, memory_only=False):
    "Initialize the database and the flask app"
    global db

    app = Flask(__name__, instance_relative_config=True)
    configure(app)

    api = Api(app)
    add_resources(api)

    app.memory_only = memory_only
    # Dict containing AppTree dataclasses with tree info
    app.trees = defaultdict(lambda: AppTree(
        name=get_random_string(10),
        style=deepcopy(tree_style) or TreeStyle(),
        timer = time(),
        searches = {},
        selected = {},
    ))

    db = sqlalchemy.create_engine('sqlite:///' + app.config['DATABASE'])

    if tree:
        # If a tree was provided, the entry point is the visualizer
        # :tree: is only a tree_name. The tree will be added to the db later
        @app.route('/')
        def index():
            return redirect(url_for('static', filename='gui.html', tree=tree))
    elif app.memory_only:
        @app.route('/')
        def index():
            return redirect(url_for('static', filename='gui.html'))
    else:
        # Else, provide a user interface for entering a newick to visualize
        @app.route('/')
        def index():
            return redirect(url_for('static', filename='upload_tree.html'))


    @app.route('/help')
    def description():
        return ('<html>\n<head>\n<title>Description</title>\n</head>\n<body>\n'
            '<pre>' + __doc__ + '</pre>\n'
            '<p>For analysis, <a href="/static/gui.html">use our gui</a>!</p>\n'
            '</body>\n</html>')

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify({'message': error.message})
        response.status_code = error.status_code
        return response

    api.handle_error = None
    # so our handling is called even when being served from gunicorn

    return app


def configure(app):
    "Set the configuration for the flask app"
    app.root_path = os.path.abspath('.')  # in case we launched from another dir
    app.instance_path = app.root_path + '/instance'

    CORS(app)  # allow cross-origin resource sharing (requests from other domains)

    Compress(app)  # send results using gzip

    app.config.from_mapping(
        SEND_FILE_MAX_AGE_DEFAULT=0,  # do not cache static files
        DATABASE=f'{app.instance_path}/trees.db',
        SECRET_KEY=' '.join(os.uname()))  # for testing, or else use config.py

    if os.path.exists(f'{app.instance_path}/config.py'):
        app.config.from_pyfile(f'{app.instance_path}/config.py')  # overrides


def add_resources(api):
    "Add all the REST endpoints"
    add = api.add_resource  # shortcut
    add(Drawers, '/drawers/<string:name>/<string:tree_id>')
    add(Layouts, '/layouts')
    add(Trees,
        '/trees',
        '/trees/<string:tree_id>',
        '/trees/<string:tree_id>/nodeinfo',
        '/trees/<string:tree_id>/name',
        '/trees/<string:tree_id>/newick',
        '/trees/<string:tree_id>/draw',
        '/trees/<string:tree_id>/size',
        '/trees/<string:tree_id>/properties',
        '/trees/<string:tree_id>/nodecount',
        '/trees/<string:tree_id>/ultrametric',
        '/trees/<string:tree_id>/select',
        '/trees/<string:tree_id>/selected',
        '/trees/<string:tree_id>/remove_selection',
        '/trees/<string:tree_id>/search',
        '/trees/<string:tree_id>/searches',
        '/trees/<string:tree_id>/remove_search',
        '/trees/<string:tree_id>/sort',
        '/trees/<string:tree_id>/root_at',
        '/trees/<string:tree_id>/move',
        '/trees/<string:tree_id>/remove',
        '/trees/<string:tree_id>/rename',
        '/trees/<string:tree_id>/reload')


def run_smartview(newick=None, tree_name=None, tree_style=None, layouts=[],
        update_old_tree=True, memory_only=False, purge_trees=False, port=5000):
    # Set tree_name to None if no newick was provided
    # Generate tree_name if none was provided
    # update_old_tree: replace tree in local database if identical tree_name
    tree_name = tree_name or get_random_string(10) if newick else None

    global app
    app = initialize(tree_name, tree_style, memory_only=memory_only)
    # purge inactive trees every 15 minutes
    purge(interval=15*60, max_time=30*60, from_db=purge_trees)

    app.layouts = get_layouts(layouts)

    # Create database if not already created
    if not os.path.exists(app.config['DATABASE']):
        create_example_database()

    # Add tree to database if provided
    if newick: 
        print(f'Adding {tree_name} to local database...')
        tree_data = { 
            'id': 0,  # id to be replaced by actual hash
            'name': tree_name,
            'newick': newick,
        }
        with app.app_context():
            tid = add_tree(tree_data, replace=update_old_tree)
            print(f'Added tree {tree_name} with id {tid}.')

    app.run(debug=True, use_reloader=False, port=port)


if __name__ == '__main__':
    run_smartview(memory_only=False)


# But for production it's better if we serve it with something like:
#   gunicorn server:app
