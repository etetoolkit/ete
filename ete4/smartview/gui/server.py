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

import os
os.chdir(os.path.abspath(os.path.dirname(__file__)))

# import sys
# sys.path.insert(0, '..')

import re
from importlib import reload as module_reload
from math import pi
from functools import partial
from time import time
from threading import Timer
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict, namedtuple
from copy import copy, deepcopy
from dataclasses import dataclass
import gzip
import json
import _pickle as pickle
from types import FunctionType
import shutil

from flask import Flask, request, jsonify, g, redirect, url_for
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_compress import Compress
from itsdangerous import TimedJSONWebSignatureSerializer as JSONSigSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from ... import Tree
from .. import TreeStyle, layout_modules
from ..utils import InvalidUsage, get_random_string
from ..renderer import nexus, gardening as gdn
from ..renderer import drawer as drawer_module

# call initialize() to fill it up
app = None


# Dataclass containing info specific to each tree
@dataclass
class AppTree:
    tree: Tree = None
    name: str = None
    style: TreeStyle = None
    layouts: list = None
    timer: float = None
    initialized: bool = False
    selected: dict = None
    active: namedtuple = None  # active nodes
    searches: dict = None

# REST api.

class Drawers(Resource):
    def get(self, name=None, tree_id=None):
        "Return data from the drawer. In aligned mode if aligned faces"
        try:
            tree_id, _ = get_tid(tree_id)
            if name not in ['Rect', 'Circ'] and\
                    any(getattr(ly, 'aligned_faces', False) and ly.active\
                        for ly in sum(app.trees[int(tree_id)].layouts.values(),[])):
                name = 'Align' + name
            drawer_class = next(d for d in drawer_module.get_drawers()
                if d.__name__[len('Drawer'):] == name)
            return {'type': drawer_class.TYPE,
                    'npanels': drawer_class.NPANELS}
        except StopIteration:
            raise InvalidUsage(f'not a valid drawer: {name}')


class Layouts(Resource):
    def get(self, tree_id=None):
        rule = request.url_rule.rule  # shortcut

        if rule == '/layouts':
            tree_style = app.trees['default'].style
            app.trees.pop('default')
            avail_layouts = { 'default': app.default_layouts }
        elif rule == '/layouts/<string:tree_id>':
            tid = get_tid(tree_id)[0]
            tree = app.trees[int(tid)]
            tree_style = tree.style
            avail_layouts = tree.layouts
        elif rule == '/layouts/list':
            return { module: [ [ ly.name, ly.description ] for ly in layouts if ly.name ]
                    for module, layouts in app.avail_layouts.items() }

        layouts = {}
        for module, lys in avail_layouts.items():
            layouts[module] = { l.name: l.active for l in lys if l.name}

        return layouts

    def put(self):
        rule = request.url_rule.rule  # shortcut

        if rule == '/layouts/update':
            update_app_available_layouts()


class Trees(Resource):
    def get(self, tree_id=None):
        "Return data from the tree (or info about all trees if no id given)"
        rule = request.url_rule.rule  # shortcut
        
        # Update tree's timer
        if rule.startswith('/trees/<string:tree_id>'):
            tid, subtree = get_tid(tree_id)
            t = load_tree(tree_id)  # load if it was not loaded in memory
            tree = app.trees[int(tid)]
            tree.timer = time()

        if rule == '/trees':
            if app.safe_mode:
                raise InvalidUsage(f'invalid path {rule} in safe_mode mode', 404)
            return [{ 'id': i, 'name': v.name } for i, v in app.trees.items()]
        elif rule == '/trees/<string:tree_id>':
            if app.safe_mode:
                raise invalidusage(f'invalid path {rule} in safe_mode mode', 404)
            properties = set()
            for node in tree.tree.traverse():
                properties |= node.props.keys()
            properties = [ p for p in properties if not p.startswith("_") ]
            return { 'name': tree.name, 'props': properties }
        elif rule == '/trees/<string:tree_id>/nodeinfo':
            node = gdn.get_node(tree.tree, subtree)
            return node.props
        elif rule == '/trees/<string:tree_id>/name':
            return tree.name
        elif rule == '/trees/<string:tree_id>/newick':
            MAX_MB = 2
            return get_newick(tree_id, MAX_MB)
        # Selections
        elif rule == '/trees/<string:tree_id>/all_selections':
            selected = {
                name: { 'nresults': len(results), 'nparents': len(parents) }
                for name, (results, parents) in (tree.selected or {}).items() }
            return { 'selected': selected }
        elif rule == '/trees/<string:tree_id>/selections':
            return { 'selections': get_selections(tree_id) }
        elif rule == '/trees/<string:tree_id>/select':
            nresults, nparents = store_selection(tree_id, request.args.copy())
            return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}
        elif rule == '/trees/<string:tree_id>/unselect':
            removed = unselect_node(tree_id, request.args.copy())
            message = 'ok' if removed else 'selection not found'
            return {'message': message}
        elif rule == '/trees/<string:tree_id>/remove_selection':
            removed = remove_selection(tid, request.args.copy())
            message = 'ok' if removed else 'selection not found'
            return {'message': message}
        elif rule == '/trees/<string:tree_id>/change_selection_name':
            change_selection_name(tid, request.args.copy())
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/selection/info':
            return get_selection_info(tid, request.args.copy())
        elif rule == '/trees/<string:tree_id>/search_to_selection':
            search_to_selection(tid, request.args.copy())
            return { 'message': 'ok' }
        elif rule == '/trees/<string:tree_id>/prune_by_selection':
            prune_by_selection(tid, request.args.copy())
            return { 'message': 'ok' }
        # Active nodes
        elif rule == '/trees/<string:tree_id>/activate':
            activate_node(tree_id)
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/deactivate':
            deactivate_node(tree_id)
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/store_active':
            nresults, nparents = store_active(tree, request.args.copy())
            return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}
        elif rule == '/trees/<string:tree_id>/remove_active':
            remove_active(tree)
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/all_active':
            nodes = []
            for node in tree.active.results:
                node_id = ",".join(map(str, get_node_id(tree.tree, node, [])))
                props = { k:v for k,v in node.props.items() if not k.startswith('_') }
                nodes.append({ 'id': node_id, **props })
            return nodes
        # Searches
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
        # Find
        elif rule == '/trees/<string:tree_id>/find':
            node = find_node(tree.tree, request.args.copy())
            node_id = ",".join(map(str, get_node_id(tree.tree, node, [])))
            props = { k:v for k,v in node.props.items() if not k.startswith('_') }
            return { 'id': node_id, **props }
        elif rule == '/trees/<string:tree_id>/draw':
            drawer = get_drawer(tree_id, request.args.copy())
            return list(drawer.draw())
        elif rule == '/trees/<string:tree_id>/size':
            width, height = t.size
            return {'width': width, 'height': height}
        elif rule == '/trees/<string:tree_id>/collapse_size':
            return tree.style.collapse_size
        elif rule == '/trees/<string:tree_id>/properties':
            properties = set()
            for node in t.traverse():
                properties |= node.props.keys()
            return list(properties)
        elif rule == '/trees/<string:tree_id>/nodecount':
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
            t = load_tree(tid)
            tree = app.trees[int(tid)]
            tree.timer = time()

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
            tree.tree.set_outgroup(gdn.get_node(t, node_id))
            # app.trees[int(tid)].tree = gdn.root_at(gdn.get_node(t, node_id))
            return {'message': 'ok'}
        elif rule == '/trees/<string:tree_id>/move':
            try:
                node_id, shift = request.json
                gdn.move(gdn.get_node(t, node_id), shift)
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot move ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/remove':
            try:
                node_id = request.json
                gdn.remove(gdn.get_node(t, node_id))
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot remove ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/rename':
            try:
                node_id, name = request.json
                gdn.get_node(t, node_id).name = name
                return {'message': 'ok'}
            except AssertionError as e:
                raise InvalidUsage(f'cannot rename ${node_id}: {e}')
        elif rule == '/trees/<string:tree_id>/reload':
            tid, subtree = get_tid(tree_id)
            if subtree:
                raise InvalidUsage('operation not allowed with subtree')

            app.trees.pop(tid, None) # avoid possible key-error
            load_tree(tid)

            return {'message': 'ok'}

    def delete(self, tree_id):
        "Delete tree and all references to it"
        tid = int(tree_id)
        tree = del_tree(tid)
        return {'message': 'ok' if tree else f'tree with id {tid} not found.'}


class Id(Resource):
    def get(self, path):
        if not path.startswith('trees/'):
            raise InvalidUsage('invalid path %r' % path, 404)

        name = path.split('/', 1)[-1]
        # if path.startswith('trees/'):
            # pids = dbget0('id', 'trees WHERE name=?', name)
            # if len(pids) != 1:
                # raise InvalidUsage('unknown tree name %r' % name)
            # return {'id': pids[0]}


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

        if tree.tree:
            t = gdn.get_node(tree.tree, subtree)
            # Reinitialize if layouts have to be reapplied
            if not tree.initialized:
                tree.style = TreeStyle()

                # Layout pre-render
                for layouts in tree.layouts.values():
                    for layout in layouts:
                        if layout.active:
                            layout.set_tree_style(tree.style)

                tree.initialized = True

                for node in t.traverse():
                    node.is_initialized = False
                    node._smfaces = None
                    node._collapsed_faces = None

            return t
        else:
            tree.name, tree.tree, tree.layouts = retrieve_tree(tid)
            if tree.style.ultrametric:
                tree.tree.convert_to_ultrametric()
                gdn.standardize(tree.tree)
            return gdn.get_node(tree.tree, subtree)

    except (AssertionError, IndexError):
        raise InvalidUsage(f'unknown tree id {tree_id}', 404)


def load_tree_from_newick(tid, newick):
    """Load tree into memory from newick"""
    t = Tree(newick, format=1)

    if app.trees[int(tid)].style.ultrametric:
        t.convert_to_ultrametric()
        gdn.standardize(t)

    gdn.standardize(t)
    return t


def retrieve_layouts(layouts):
    layouts = layouts or []
    tree_layouts = defaultdict(list)

    for ly in layouts:
        name_split = ly.split(':')

        if len(name_split) != 2:
            continue

        key, ly_name = name_split
        avail = app.avail_layouts.get(key, [])
        if ly_name == '*':
            tree_layouts[key] = avail
        else:
            match = next((ly for ly in avail if ly.name == ly_name ), None)
            if match:
                tree_layouts[key].append(match)

    # Add default layouts
    tree_layouts["default"] = app.default_layouts

    return dict(tree_layouts)

@init_timer
def retrieve_tree(tid):
    """Retrieve tree from tmp pickle file.
    Called when tree has been deleted from memory
    """
    start = time()
    with open(f'/tmp/{tid}.pickle', 'rb') as handle:
        data = pickle.load(handle)

    print(f'Unpickle: {time() - start}')

    name = data["name"]
    tree = data["tree"]
    layouts = retrieve_layouts(data["layouts"])
    return name, tree, layouts
   

def get_drawer(tree_id, args):
    "Return the drawer initialized as specified in the args"
    valid_keys = ['x', 'y', 'w', 'h', 'panel', 'zx', 'zy', 'za',
                  'drawer', 'min_size',
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

        zoom = (get('zx', 1), get('zy', 1), get('za', 1))
        assert zoom[0] > 0 and zoom[1] > 0 and zoom[2] > 0, 'zoom must be > 0'

        tid, _ = get_tid(tree_id)
        tree = app.trees[int(tid)]

        active_layouts = args.get('layouts')
        if active_layouts != None:
            update_layouts(active_layouts, tid)

        layouts = set(ly for ly in sum(tree.layouts.values(), []) if ly.active)

        drawer_name = args.get('drawer', 'RectFaces')
        # Automatically provide aligned drawer when necessary
        if drawer_name not in ['Rect', 'Circ'] and\
                any(getattr(ly, 'aligned_faces', False) for ly in layouts):
            drawer_name = 'Align' + drawer_name
        drawer_class = next((d for d in drawer_module.get_drawers()
            if d.__name__[len('Drawer'):] == drawer_name), None)

        drawer_class.COLLAPSE_SIZE = get('min_size', 6)
        assert drawer_class.COLLAPSE_SIZE > 0, 'min_size must be > 0'

        limits = (None if not drawer_name.startswith('Circ') else
            (get('rmin', 0), 0,
             get('amin', -180) * pi/180, get('amax', 180) * pi/180))

        collapsed_ids = set(tuple(int(i) for i in node_id.split(','))
            for node_id in json.loads(args.get('collapsed_ids', '[]')))

        update_ultrametric(args.get('ultrametric'), tid)

        active = tree.active
        selected = tree.selected
        searches = tree.searches
        
        return drawer_class(load_tree(tree_id), viewport, panel, zoom,
                    limits, collapsed_ids, active, selected, searches,
                    layouts, tree.style)
    except StopIteration:
        raise InvalidUsage(f'not a valid drawer: {drawer_name}')
    except (ValueError, AssertionError) as e:
        raise InvalidUsage(str(e))


def get_newick(tree_id, max_mb):
    "Return the newick representation of the given tree"

    newick = load_tree(tree_id).write(properties=[])

    size_mb = len(newick) / 1e6
    if size_mb > max_mb:
        raise InvalidUsage('newick too big (%.3g MB)' % size_mb)

    return newick


def get_parents(results):
    "Return a set of parents given a set of results"
    parents = defaultdict(lambda: 0)
    for node in results:
        parent = node.up
        while parent:
            parents[parent] += 1
            parent = parent.up
    return parents


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

        if len(results) == 0:
            return 0, 0

        parents = get_parents(results)

        tid = get_tid(tree_id)[0]
        app.trees[int(tid)].searches[text] = (results, parents)

        return len(results), len(parents)
    except InvalidUsage:
        raise
    except Exception as e:
        raise InvalidUsage(f'evaluating expression: {e}')


def find_node(tree, args):
    if 'text' not in args:
        raise InvalidUsage('missing search text')

    text = args.pop('text').strip()
    func = get_search_function(text)

    try:
        return next((node for node in tree.traverse() if func(node)), None)

    except InvalidUsage:
        raise
    except Exception as e:
        raise InvalidUsage(f'evaluating expression: {e}')


def get_selections(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    return [ name for name, (results, _) in tree.selected.items() if node in results ]


def get_node_id(tree, node, node_id):
    parent = node.up
    if not parent:
        node_id.reverse()
        return node_id
    node_id.append(parent.children.index(node))
    return get_node_id(tree, parent, node_id)


def get_selection_info(tid, args):
    "Get selection info from their nodes"
    if 'text' not in args:
        raise InvalidUsage('missing selection text')
    tree = app.trees[int(tid)]
    name = args.pop('text').strip()
    nodes = tree.selected.get(name, [[]])[0]

    props = args.pop('props', '').strip().split(',')
    no_props = len(props) == 1 and props[0] == ''

    if 'node_id' in props or no_props or '*' in props:
        node_ids = [ ",".join(map(str, get_node_id(tree.tree, node, []))) 
                for node in nodes ]
    if no_props:
        return node_ids

    node_props = []
    for idx, node in enumerate(nodes):
        if props[0] == "*":
            node_id = node_ids[idx]
            node_props.append({ **node.props, 'node_id': node_id })
        else:
            node_p = { p: node.props.get(p) for p in props }
            if 'node_id' in props:
                node_p['node_id'] = node_ids[idx]
            node_props.append(node_p)


    return node_props


def remove_selection(tid, args):
    "Remove selection"
    if 'text' not in args:
        raise InvalidUsage('missing selection text')
    name = args.pop('text').strip()
    return app.trees[int(tid)].selected.pop(name, None)


def change_selection_name(tid, args):
    if 'name' not in args or 'newname' not in args:
        raise InvalidUsage('missing renaming parameters')

    name = args.pop('name').strip()
    selected = app.trees[int(tid)].selected

    if name not in selected.keys():
        raise InvalidUsage(f'selection {name} does not exist')

    new_name = args.pop('newname').strip()
    selected[new_name] = selected[name]
    selected.pop(name)


def unselect_node(tree_id, args):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    name = args.pop('text', '').strip()

    if name in tree.selected.keys():
        selections = { name: tree.selected[name] }
    else:
        selections = dict(tree.selected)

    removed = False
    for name, (results, parents) in selections.items():
        nresults = len(results)
        results.discard(node)
        if len(results) == 0:
            removed = True
            tree.selected.pop(name)
        elif nresults > len(results):
            removed = True
            parents = get_parents(results)
            tree.selected[name] = (results, parents)

    return removed


def search_to_selection(tid, args):
    "Store search as selection"
    if 'text' not in args:
        raise InvalidUsage('missing selection text')

    text = args.copy().pop('text').strip()
    selected = app.trees[int(tid)].selected

    if text in selected.keys():
        raise InvalidUsage('selection already exists')

    search = remove_search(tid, args)
    selected[text] = search


def prune_by_selection(tid, args):
    "Prune tree by keeping selections identified by their names"

    if 'names' not in args:
        raise InvalidUsage('missing selection names')

    names = set(args.pop('names').strip().split(','))
    tree = app.trees[int(tid)]

    selected = set()
    for name,(results,_) in tree.selected.items():
        if name in names:
            selected.update(results)

    if len(selected) == 0:
        raise InvalidUsage('selection does not exist')

    tree.tree.prune(selected)

    gdn.standardize(tree.tree)

    tree.initialized = False


def update_selection(tree, name, results, parents):
    if name in tree.selected.keys():
        all_results, all_parents = tree.selected[name]
        all_results.update(results)
        for p, v in parents.items():  # update parents defaultdict
            all_parents[p] += v
        tree.selected[name] = (all_results, all_parents)
    else:
        tree.selected[name] = (results, parents)

    results, parents = tree.selected[name]
    return len(results), len(parents)


def store_selection(tree_id, args):
    "Store the results and parents of a selection and return their numbers"
    if 'text' not in args:
        raise InvalidUsage('missing selection text')

    tid, subtree = get_tid(tree_id)
    app_tree = app.trees[int(tid)]
    node = gdn.get_node(app_tree.tree, subtree)

    parents = get_parents([node])

    name = args.pop('text').strip()
    return update_selection(tree, name, set([node]), parents)


def activate_node(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    tree.active.results.add(node)
    tree.active.parents.clear()
    tree.active.parents.update(get_parents(tree.active.results))


def deactivate_node(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    tree.active.results.discard(node)
    tree.active.parents.clear()
    tree.active.parents.update(get_parents(tree.active.results))


def store_active(tree, args):
    if 'text' not in args:
        raise InvalidUsage('missing selection text')

    name = args.pop('text').strip()
    results = copy(tree.active.results)
    parents = copy(tree.active.parents)

    remove_active(tree)

    return update_selection(tree, name, results, parents)


def remove_active(tree):
    tree.active.parents.clear()
    tree.active.results.clear()



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
    "Add trees to the app dict return a dict of {name: id}"
    if request.form:
        trees = get_trees_from_form()
    else:
        data = get_fields(required=['name', 'newick'],  # id
                          valid_extra=['layouts', 'description'])
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
            'description': form.get('description', ''),
            'layouts': form.get('layouts', [])
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
def add_tree(data):
    "Add tree with given data and return its id"
    tid = int(data['id'])
    name = data['name']
    newick = data.get('newick', None)
    layouts = data.get('layouts', [])
    if type(layouts) == str:
        layouts = layouts.split(",")

    del_tree(tid)  # delete if there is a tree with same id

    if newick:
        tree = load_tree_from_newick(tid, newick)
    else:
        tree = data.get('tree', None)
        if not tree:
            raise InvalidUsage('Either Newick or Tree object has to be provided.')
    
    app_tree = app.trees[int(tid)]
    app_tree.name = name
    app_tree.tree = tree
    app_tree.layouts = retrieve_layouts(layouts)

    print("Tree added to app.trees")

    start = time()
    print('Dumping tree...')
    # Write tree data as a temporary pickle file
    obj = { 'name': name, 'layouts': layouts, 'tree': tree }
    with open(f'/tmp/{tid}.pickle', 'wb') as handle:
        pickle.dump(obj, handle)

    print(f'Dump: {time() - start}')

    return tid


def modify_tree_fields(tree_id):
    "Modify in the database the tree fields that appear in a request"
    tid = int(tree_id)

    data = get_fields(valid_extra=[
        'name', 'description', 'newick'])

    if not data:
        return {'message': 'ok'}


def update_app_available_layouts():
    try:
        module_reload(layout_modules)
        avail_layouts = get_layouts_from_getters(layout_modules)
    except Exception as e:
        raise "Error while updating app layouts.\n{e}"
    else:
        avail_layouts.pop("default_layouts", None)
        app.avail_layouts = avail_layouts


def get_layouts_from_getters(layout_modules):
    def get_modules(ly_modules):
        return ( getattr(ly_modules, module) for module in dir(ly_modules)\
                if not module.startswith("__")) # and module != "default_layouts")
    def get_layouts(module):
        return ( getattr(module, getter)() for getter in dir(module)\
                if not getter.startswith("_")\
                and getter.startswith("Layout") )

    all_layouts = {}
    all_modules = get_modules(layout_modules)
    for module in all_modules:
        layouts = get_layouts(module)
        name = module.__name__.split(".")[-1]
        all_layouts[name] = list(layouts)
        # Set _module attr for future reference (update_layouts)
        for ly in all_layouts[name]:
            ly.module = name

        # if type(next(layouts, None)) == FunctionType:
            # Simple file with layout function getters
            # all_layouts[name] = list(layouts)
        # else:
            # # Module of layout function getters
            # all_layouts[module.__name__] = []
            # for inner_mod in get_modules(module):
                # all_layouts[module.__name__].extend(get_layouts(inner_mod))

    return all_layouts

# Layout related functions
def get_layouts(layouts=[]):
    # Get layouts from their getters in layouts module:
    # smartview/redender/layouts
    layouts_from_module = get_layouts_from_getters(layout_modules)

    # Get default layouts
    default_layouts = layouts_from_module.pop("default_layouts")

    all_layouts = {}
    for idx, layout in enumerate(default_layouts + layouts):
        layout.module = "default"
        all_layouts[layout.name or idx] = layout

        
    return list(all_layouts.values()), layouts_from_module


def update_layouts(active_layouts, tid):
    """ Update app layouts based on front end status """
    tree = app.trees[int(tid)]
    reinit_trees = False
    for module, layouts in tree.layouts.items():
        for layout in layouts:
            if not layout.always_render:
                name = f'{module}:{layout.name}'
                new_status = name in active_layouts
                if layout.active != new_status:
                    reinit_trees = True
                    layout.active = new_status

    if reinit_trees:
        if app.safe_mode:
            tree.initialized = False
        else:
            for t in app.trees.values():
                t.initialized = False


def update_ultrametric(ultrametric, tid):
    """ Update trees if ultrametric option toggled """
    tree = app.trees[int(tid)]
    # Boolean from front-end 0 or 1
    ultrametric = True if (ultrametric and int(ultrametric)) else False
    if tree.style.ultrametric != ultrametric:
        tree.style.ultrametric = ultrametric
        if ultrametric == True:
            tree.tree.convert_to_ultrametric()
            gdn.standardize(tree.tree)
        else:
            app.trees.pop(tid, None) # delete from memory


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


def del_tree(tid):
    "Delete a tree and everywhere where it appears referenced"
    shutil.rmtree(f'/tmp/{tid}.pickle', ignore_errors=True)
    return app.trees.pop(tid, None)


def purge(interval=None, max_time=30*60):
    """Delete trees that have been inactive for a certain period of time
        :interval: if set, recursively calls purge after given interval.
        :max_time: maximum inactivity time in seconds. Default 30 min.
    """
    trees = list(app.trees.keys())
    for tid in trees:
        inactivity_time = time() - app.trees[tid].timer
        if inactivity_time > max_time: 
            del_tree(tid)
    # Call self after interval
    if interval: # in seconds
        print(f'Current trees in memory: {len(list(app.trees.keys()))}')
        Timer(interval, purge, [interval, max_time]).start()


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


def copy_style(tree_style):
    def add_faces_to_header(header, facecontainer):
        for column, face_list in facecontainer.items():
            for face in face_list:
                header.add_face(face, column=column)

    header = deepcopy(dict(tree_style.aligned_panel_header))
    footer = deepcopy(dict(tree_style.aligned_panel_footer))

    ts = deepcopy(tree_style)
    add_faces_to_header(ts.aligned_panel_header, header)
    add_faces_to_header(ts.aligned_panel_footer, footer)

    return ts


# App initialization.

def initialize(tree=None, layouts=[], safe_mode=False):
    "Initialize the database and the flask app"
    app = Flask(__name__, instance_relative_config=True)
    configure(app)

    api = Api(app)
    add_resources(api)

    app.safe_mode = safe_mode

    # tree_style = copy_style(tree_style) if tree_style else TreeStyle()

    # App associated layouts
    # Layouts will be accessible for each tree independently
    app.default_layouts, app.avail_layouts = get_layouts(layouts)
    # Dict containing AppTree dataclasses with tree info
    app.trees = defaultdict(lambda: AppTree(
        name=get_random_string(10),
        style=copy_style(TreeStyle()),
        layouts = app.default_layouts,
        timer = time(),
        searches = {},
        selected = {},
        active = drawer_module.Active(set(), defaultdict(lambda: 0)),
    ))

    if tree:
        # If a tree was provided, the entry point is the visualizer
        # :tree: is only a tree_name. The tree will be added to the db later
        @app.route('/')
        def index():
            return redirect(url_for('static', filename='gui.html', tree=tree))
    elif app.safe_mode:
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
        SECRET_KEY=' '.join(os.uname()))  # for testing, or else use config.py

    if os.path.exists(f'{app.instance_path}/config.py'):
        app.config.from_pyfile(f'{app.instance_path}/config.py')  # overrides


def add_resources(api):
    "Add all the REST endpoints"
    add = api.add_resource  # shortcut
    add(Drawers, '/drawers/<string:name>/<string:tree_id>')
    add(Layouts, '/layouts', '/layouts/<string:tree_id>','/layouts/list', '/layouts/update')
    add(Trees,
        '/trees',
        '/trees/<string:tree_id>',
        '/trees/<string:tree_id>/nodeinfo',
        '/trees/<string:tree_id>/name',
        '/trees/<string:tree_id>/newick',
        '/trees/<string:tree_id>/draw',
        '/trees/<string:tree_id>/size',
        '/trees/<string:tree_id>/collapse_size',
        '/trees/<string:tree_id>/properties',
        '/trees/<string:tree_id>/nodecount',
        '/trees/<string:tree_id>/ultrametric',
        '/trees/<string:tree_id>/select',  # select node
        '/trees/<string:tree_id>/unselect',  # unselect node
        '/trees/<string:tree_id>/selections', # selections perfomed on a node
        '/trees/<string:tree_id>/all_selections',  # name and nresults, nparents for each selection
        '/trees/<string:tree_id>/selection/info',  # get selection info: list of node_ids or dict with their desired properties
        '/trees/<string:tree_id>/remove_selection',
        '/trees/<string:tree_id>/change_selection_name',
        '/trees/<string:tree_id>/search_to_selection',  # convert search to selection
        '/trees/<string:tree_id>/prune_by_selection',  # prune based on selection
        '/trees/<string:tree_id>/activate',
        '/trees/<string:tree_id>/deactivate',
        '/trees/<string:tree_id>/store_active',
        '/trees/<string:tree_id>/remove_active',
        '/trees/<string:tree_id>/all_active',
        '/trees/<string:tree_id>/search',
        '/trees/<string:tree_id>/searches',
        '/trees/<string:tree_id>/remove_search',
        '/trees/<string:tree_id>/find',
        '/trees/<string:tree_id>/sort',
        '/trees/<string:tree_id>/root_at',
        '/trees/<string:tree_id>/move',
        '/trees/<string:tree_id>/remove',
        '/trees/<string:tree_id>/rename',
        '/trees/<string:tree_id>/reload')


def run_smartview(tree=None, tree_name=None, layouts=[],
        safe_mode=False, port=5000, run=True):
    # Set tree_name to None if no tree was provided
    # Generate tree_name if none was provided
    tree_name = tree_name or get_random_string(10) if tree else None

    global app
    app = initialize(tree_name, layouts, safe_mode=safe_mode)
    # purge inactive trees every 15 minutes
    purge(interval=15*60, max_time=30*60)

    # TODO: Create app.recent_trees with paths to recently viewed trees

    if tree: 
        gdn.standardize(tree)
        tree_data = { 
            'id': 0,  # id to be replaced by actual hash
            'name': tree_name,
            'tree': tree,
            'layouts': []
        }
        with app.app_context():
            tid = add_tree(tree_data)
            print(f'Added tree {tree_name} with id {tid}.')

    if run:
        app.run(debug=True, use_reloader=False, port=port)
    else:
        return app


if __name__ == '__main__':
    run_smartview(safe_mode=False)



# But for production it's better if we serve it with something like:
#   gunicorn server:app

# To do so, uncomment the following line
# app = run_smartview(safe_mode=True, run=False)
