#!/usr/bin/env python3

"""
Keep the data of trees and present a REST api to talk
to the world.

REST call examples:
  GET    /trees       Get all trees
  GET    /trees/{id}  Get the tree information identified by "id"
  POST   /trees       Create a new tree
  PUT    /trees/{id}  Update the tree information identified by "id"
  DELETE /trees/{id}  Delete tree by "id"
"""

import os
import re
import platform
from subprocess import Popen, DEVNULL
from threading import Thread
from importlib import reload as module_reload
from math import pi, inf
from time import time, sleep
from datetime import datetime
from collections import defaultdict, namedtuple
from copy import copy, deepcopy
from dataclasses import dataclass
import gzip, bz2, zipfile, tarfile
import json
import _pickle as pickle
import shutil
import logging

import brotli

from bottle import (
    get, post, put, redirect, static_file,
    BaseRequest, request, response, error, abort, HTTPError, run)

BaseRequest.MEMFILE_MAX = 50 * 1024 * 1024  # maximum upload size (in bytes)

from ete4 import Tree
from ete4.parser import newick
from ete4.smartview import TreeStyle, layout_modules
from ete4.parser import ete_format, nexus
from ete4.smartview.renderer import gardening as gdn
from ete4.smartview.renderer import drawer as drawer_module
from ete4 import treematcher as tm


class GlobalStuff:
    pass  # class to store data


# Make sure we send the errors as json too.
@error(400)
@error(404)
def json_error(error):
    response.content_type = 'application/json'
    return json.dumps({'message': error.body})


def req_json():
    """Return what request.json would return, but gracefully aborting."""
    try:
        return json.loads(request.body.read())
    except json.JSONDecodeError as e:
        abort(400, f'bad json content: {e}')


def nice_html(content, title='Tree Explorer'):
    return f"""
<!DOCTYPE html>
<html><head><title>{title}</title>
<link rel="icon" type="image/png" href="/static/icon.png">
<link rel="stylesheet" href="/static/upload.css"></head>
<body><div class="centered">{content}</div></body></html>"""


# call initialize() to fill it up
app = None
g_threads = {}


# Dataclass containing info specific to each tree
@dataclass
class AppTree:
    tree: Tree = None
    name: str = None
    style: TreeStyle = None
    nodestyles: dict = None
    include_props: list = None
    exclude_props: list = None
    layouts: list = None
    timer: float = None
    initialized: bool = False
    selected: dict = None
    active: namedtuple = None  # active nodes
    searches: dict = None


# Routes.

@get('/')
def callback():
    if app.trees:
        if len(app.trees) == 1:
            name = list(t.name for t in app.trees.values())[0]
            redirect(f'/static/gui.html?tree={name}')
        else:
            trees = '\n'.join('<li><a href="/static/gui.html?tree='
                              f'{t.name}">{t.name}</li>' for t in app.trees.values())
            return nice_html(f'<h1>Loaded Trees</h1><ul>\n{trees}\n</ul>')
    else:
        return nice_html("""<h1>ETE</h1>
<p>No trees loaded.</p>
<p>See the <a href="/help">help page</a> for more information.</p>""")

@get('/help')
def callback():
    return nice_html("""<h1>Help</h1>
You can go to the <a href="/static/upload.html">upload page</a>, see
a <a href="/">list of loaded trees</a>, or
<a href="http://etetoolkit.org/">consult the documentation</a>.""")

@get('/static/<path:path>')
def callback(path):
    DIR = os.path.dirname(os.path.abspath(__file__))
    return static_file(path, f'{DIR}/static')

@get('/drawers/<name>/<tree_id>')
def callback(name, tree_id):
    """Return type (rect/circ) and number of panels of the drawer."""
    try:
        tree_id, _ = get_tid(tree_id)

        # NOTE: Apparently we need to know the tree_id we are
        # referring to because it checks if there are aligned faces in
        # it to see if we are using a DrawerAlignX drawer (instead of
        # DrawerX).
        tree_layouts = sum(app.trees[int(tree_id)].layouts.values(), [])
        if (name not in ['Rect', 'Circ'] and
            any(getattr(ly, 'aligned_faces', False) and ly.active
                for ly in tree_layouts)):
            name = 'Align' + name
        # TODO: We probably want to get rid of all this.

        drawer_class = next(d for d in drawer_module.get_drawers()
                            if d.__name__[len('Drawer'):] == name)
        return {'type': drawer_class.TYPE,
                'npanels': drawer_class.NPANELS}
    except StopIteration:
        abort(400, f'not a valid drawer: {name}')

@get('/layouts')
def callback():
    # Return dict that, for every layout module, has a dict with the
    # names of its layouts and whether they are active or not.
    app.trees.pop('default', None)  # FIXME: Why do we do this??

    return {'default': {layout.name: layout.active
                        for layout in app.default_layouts if layout.name}}
    # The response will look like:
    # {
    #     "default": {
    #         "Branch length": true,
    #         "Branch support": true,
    #         "Leaf name": true,
    #         "Number of leaves": false
    #     }
    # }

@get('/layouts/list')
def callback():
    return {module: [[ly.name, ly.description] for ly in layouts if ly.name]
            for module, layouts in app.avail_layouts.items()}
    # The response will look like:
    # {"context_layouts": [["Genomic context", ""]],
    #  "domain_layouts":  [["Pfam domains", ""], ["Smart domains",""]],
    #  ...
    #  "staple_layouts": [["Barplot_None_None", ""]]}

@get('/layouts/<tree_id>')
def callback(tree_id):
    # Return dict that, for every layout module in the tree, has a dict
    # with the names of its layouts and whether they are active or not.
    tid = get_tid(tree_id)[0]
    tree_layouts = app.trees[int(tid)].layouts

    layouts = {}
    for module, lys in tree_layouts.items():
        layouts[module] = {l.name: l.active for l in lys if l.name}

    return layouts
    # The response will look like:
    # {
    #     "default": {
    #         "Branch length": true,
    #         "Branch support": true,
    #         "Leaf name": true,
    #         "Number of leaves": false
    #     }
    # }

@put('/layouts/update')
def callback():
    update_app_available_layouts()


@get('/trees')
def callback():
    if app.safe_mode:
        abort(404, 'invalid path /trees in safe_mode mode')

    response.content_type = 'application/json'
    return json.dumps([{'id': i, 'name': v.name} for i, v in app.trees.items()])

def touch_and_get(tree_id):
    """Load tree, update its timer, and return the tree object and subtree."""
    tid, subtree = get_tid(tree_id)
    load_tree(tree_id)  # load if it was not loaded in memory
    tree = app.trees[tid]
    tree.timer = time()  # update the tree's timer
    return tree, subtree

@get('/trees/<tree_id>')
def callback(tree_id):
    if app.safe_mode:
        abort(404, f'invalid path /trees/{tree_id} in safe_mode mode')

    tree, subtree = touch_and_get(tree_id)

    props = set()
    for node in tree.tree[subtree].traverse():
        props |= {k for k in node.props if not k.startswith('_')}

    return {'name': tree.name, 'props': list(props)}

@get('/trees/<tree_id>/nodeinfo')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    return tree.tree[subtree].props

@get('/trees/<tree_id>/nodestyle')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    response.content_type = 'application/json'
    return json.dumps(tree.tree[subtree].sm_style)

@get('/trees/<tree_id>/editable_props')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    return {k: v for k, v in tree.tree[subtree].props.items()
            if k not in ['tooltip', 'hyperlink'] and type(v) in [int, float, str]}
    # TODO: Document what the hell is going on here.

@get('/trees/<tree_id>/name')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    response.content_type = 'application/json'
    return json.dumps(tree.name)

@get('/trees/<tree_id>/newick')
def callback(tree_id):
    MAX_MB = 200
    response.content_type = 'application/json'
    return json.dumps(get_newick(tree_id, MAX_MB))

@get('/trees/<tree_id>/seq')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    def fasta(node):
        name = node.name if node.name else ','.join(map(str, node.id))
        return '>' + name + '\n' + node.props['seq']

    response.content_type = 'application/json'
    return json.dumps('\n'.join(fasta(leaf) for leaf in tree.tree[subtree].leaves()
                      if leaf.props.get('seq')))

@get('/trees/<tree_id>/nseq')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    response.content_type = 'application/json'
    return json.dumps(sum(1 for leaf in tree.tree[subtree].leaves() if leaf.props.get('seq')))

@get('/trees/<tree_id>/all_selections')
def callback(tree_id):
    tree, _ = touch_and_get(tree_id)
    return {'selected': {name: {'nresults': len(results), 'nparents': len(parents)}
                         for name, (results, parents) in (tree.selected or {}).items()}}

@get('/trees/<tree_id>/selections')
def callback(tree_id):
    return {'selections': get_selections(tree_id)}

@get('/trees/<tree_id>/select')
def callback(tree_id):
    nresults, nparents = store_selection(tree_id, request.query)
    return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}

@get('/trees/<tree_id>/unselect')
def callback(tree_id):
    removed = unselect_node(tree_id, request.query)
    return {'message': 'ok' if removed else 'selection not found'}

@get('/trees/<tree_id>/remove_selection')
def callback(tree_id):
    removed = remove_selection(tree_id, request.query)
    return {'message': 'ok' if removed else 'selection not found'}

@get('/trees/<tree_id>/change_selection_name')
def callback(tree_id):
    change_selection_name(tree_id, request.query)
    return {'message': 'ok'}

@get('/trees/<tree_id>/selection/info')
def callback(tree_id):
    tree, _ = touch_and_get(tree_id)
    return get_selection_info(tree, request.query)

@get('/trees/<tree_id>/search_to_selection')
def callback(tree_id):
    search_to_selection(tree_id, request.query)
    return {'message': 'ok'}

@get('/trees/<tree_id>/prune_by_selection')
def callback(tree_id):
    prune_by_selection(tree_id, request.query)
    return {'message': 'ok'}

@get('/trees/<tree_id>/active')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    node = tree.tree[subtree]

    response.content_type = 'application/json'
    if get_active_clade(node, tree.active.clades.results):
        return json.dumps('active_clade')
    elif node in tree.active.nodes.results:
        return json.dumps('active_node')
    else:
        return json.dumps('')

@get('/trees/<tree_id>/activate_node')
def callback(tree_id):
    activate_node(tree_id)
    return {'message': 'ok'}

@get('/trees/<tree_id>/deactivate_node')
def callback(tree_id):
    deactivate_node(tree_id)
    return {'message': 'ok'}

@get('/trees/<tree_id>/activate_clade')
def callback(tree_id):
    activate_clade(tree_id)
    return {'message': 'ok'}

@get('/trees/<tree_id>/deactivate_clade')
def callback(tree_id):
    deactivate_clade(tree_id)
    return {'message': 'ok'}

@get('/trees/<tree_id>/store_active_nodes')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    nresults, nparents = store_active(tree, 0, request.query)
    return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}

@get('/trees/<tree_id>/store_active_clades')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    nresults, nparents = store_active(tree, 1, request.query)
    return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}

@get('/trees/<tree_id>/remove_active_nodes')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    remove_active(tree, 0)
    return {'message': 'ok'}

@get('/trees/<tree_id>/remove_active_clades')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    remove_active(tree, 1)
    return {'message': 'ok'}

@get('/trees/<tree_id>/all_active')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    return {
        'nodes': get_nodes_info(tree.tree, tree.active.nodes.results, ['*']),
        'clades': get_nodes_info(tree.tree, tree.active.clades.results, ['*']),
    }

@get('/trees/<tree_id>/all_active_leaves')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    active_leaves = set(n for n in tree.active.nodes.results if n.is_leaf)
    for n in tree.active.clades.results:
        active_leaves.update(set(n.leaves()))

    return get_nodes_info(tree.tree, active_leaves, ['*'])

# Searches
@get('/trees/<tree_id>/searches')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    return {'searches': {text: {'nresults': len(results), 'nparents': len(parents)}
                         for text, (results, parents) in (tree.searches or {}).items()}}

@get('/trees/<tree_id>/search')
def callback(tree_id):
    nresults, nparents = store_search(tree_id, request.query)
    return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}

@get('/trees/<tree_id>/remove_search')
def callback(tree_id):
    removed = remove_search(tree_id, request.query)
    return {'message': 'ok' if removed else 'search not found'}

# Find
@get('/trees/<tree_id>/find')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    node = find_node(tree.tree, request.query)
    node_id = ','.join(map(str, node.id))
    return {'id': node_id}

@get('/trees/<tree_id>/draw')
def callback(tree_id):
    try:
        drawer = get_drawer(tree_id, request.query)

        graphics = json.dumps(list(drawer.draw())).encode('utf8')

        response.content_type = 'application/json'
        if app.compress:
            response.add_header('Content-Encoding', 'br')
            return brotli.compress(graphics)
        else:
            return graphics
    except (AssertionError, SyntaxError) as e:
        abort(400, f'when drawing: {e}')

@get('/trees/<tree_id>/size')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    width, height = tree.tree[subtree].size
    return {'width': width, 'height': height}

@get('/trees/<tree_id>/collapse_size')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    response.content_type = 'application/json'
    return json.dumps(tree.style.collapse_size)

@get('/trees/<tree_id>/properties')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    props = set()
    for node in tree.tree[subtree].traverse():
        props |= node.props.keys()

    response.content_type = 'application/json'
    return json.dumps(list(props))

@get('/trees/<tree_id>/properties/<pname>')
def callback(tree_id, pname):
    return get_stats(tree_id, pname)

@get('/trees/<tree_id>/nodecount')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    tnodes = tleaves = 0
    for node in tree.tree[subtree].traverse():
        tnodes += 1
        if node.is_leaf:
            tleaves += 1

    return {'tnodes': tnodes, 'tleaves': tleaves}

@get('/trees/<tree_id>/ultrametric')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)
    response.content_type = 'application/json'
    return json.dumps(tree.style.ultrametric)

@post('/trees')
def callback():
    ids = add_trees_from_request()
    response.status = 201
    return {'message': 'ok', 'ids': ids}

@put('/trees/<tree_id>')
def callback(tree_id):
    modify_tree_fields(tree_id)
    return {'message': 'ok'}

@put('/trees/<tree_id>/sort')
def callback(tree_id):
    node_id, key_text, reverse = req_json()
    sort(tree_id, node_id, key_text, reverse)
    return {'message': 'ok'}

@put('/trees/<tree_id>/root_at')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    if subtree:
        abort(400, 'operation not allowed with subtree')

    node_id = req_json()
    tree.tree.set_outgroup(tree.tree[node_id])
    return {'message': 'ok'}

@put('/trees/<tree_id>/move')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    try:
        node_id, shift = req_json()
        gdn.move(tree.tree[subtree][node_id], shift)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot move {node_id}: {e}')

@put('/trees/<tree_id>/remove')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    try:
        node_id = req_json()
        gdn.remove(tree.tree[subtree][node_id])
        gdn.update_sizes_all(tree.tree)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot remove {node_id}: {e}')

@put('/trees/<tree_id>/update_props')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    try:
        node = tree.tree[subtree]
        update_node_props(node, req_json())
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot update props of {node_id}: {e}')

@put('/trees/<tree_id>/update_nodestyle')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    try:
        node = tree.tree[subtree]
        update_node_style(node, req_json().copy())
        tree.nodestyles[node] = req_json().copy()
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot update style of {node_id}: {e}')

@put('/trees/<tree_id>/reinitialize')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    gdn.standardize(tree.tree)
    tree.initialized = False
    return {'message': 'ok'}

@put('/trees/<tree_id>/reload')
def callback(tree_id):
    tree, subtree = touch_and_get(tree_id)

    if subtree:
        abort(400, 'operation not allowed with subtree')

    app.trees.pop(tree_id, None)  # avoid possible key-error
    return {'message': 'ok'}


# Auxiliary functions.

def initialize_tree_style(tree, ultrametric=False):
    aligned_grid_dxs = deepcopy(tree.style.aligned_grid_dxs)
    tree.style = TreeStyle()
    tree.style.aligned_grid_dxs = aligned_grid_dxs
    tree.style.ultrametric = ultrametric

    # Layout pre-render
    for layouts in tree.layouts.values():
        for layout in layouts:
            if layout.active:
                layout.set_tree_style(tree.tree, tree.style)

    tree.initialized = True

def load_tree(tree_id):
    "Add tree to app.trees and initialize it if not there, and return it"
    try:
        tid, subtree = get_tid(tree_id)
        tree = app.trees[tid]

        if tree.tree:
            # Reinitialize if layouts have to be reapplied
            if not tree.initialized:
                initialize_tree_style(tree)

                for node in tree.tree[subtree].traverse():
                    node.is_initialized = False
                    node._smfaces = None
                    node._collapsed_faces = None
                    node._sm_style = None

                for node, args in tree.nodestyles.items():
                    update_node_style(node, args.copy())

            return tree.tree[subtree]
        else:
            tree.name, tree.tree, tree.layouts = retrieve_tree(tid)

            if tree.style.ultrametric:
                tree.tree.to_ultrametric()
                gdn.standardize(tree.tree)

            initialize_tree_style(tree)

            return tree.tree[subtree]

    except (AssertionError, IndexError):
        abort(404, f'unknown tree id {tree_id}')

def load_tree_from_newick(tid, nw):
    """Load tree into memory from newick"""
    t = Tree(nw)

    if app.trees[int(tid)].style.ultrametric:
        t.to_ultrametric()

    gdn.standardize(t)
    return t

def retrieve_layouts(layouts):
    layouts = layouts or []
    tree_layouts = defaultdict(list)

    for ly in layouts:
        name_split = ly.split(':')

        if len(name_split) not in (2, 3):
            continue

        if len(name_split) == 2:
            key, ly_name = name_split
            active = None

        elif len(name_split) == 3:
            key, ly_name, active = name_split
            active = True if active == "on" else False

        avail = deepcopy(app.avail_layouts.get(key, []))
        if ly_name == '*':
            if active is not None:
                for ly in avail:
                    ly.active = active

            tree_layouts[key] = avail
        else:
            match = next((ly for ly in avail if ly.name == ly_name ), None)
            if match:
                if active is not None:
                    match.active = active
                tree_layouts[key].append(match)

    # Add default layouts
    tree_layouts["default"] = deepcopy(app.default_layouts)

    return dict(tree_layouts)


def retrieve_tree(tid):
    """Retrieve tree from tmp pickle file."""
    # Called when tree has been deleted from memory.
    start = time()
    with open(f'/tmp/{tid}.pickle', 'rb') as handle:
        data = pickle.load(handle)

    print(f'Unpickle: {time() - start}')

    name = data["name"]
    tree = data["tree"]
    layouts = retrieve_layouts(data["layouts"])

    app.trees[tid].timer = time()

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

        return drawer_class(
            load_tree(tree_id), viewport, panel, zoom,
            limits, collapsed_ids, active, selected, searches,
            layouts, tree.style, tree.include_props, tree.exclude_props)
    # bypass errors for now...
    except StopIteration as error:
        abort(400, f'not a valid drawer: {drawer_name}')
    except (ValueError, AssertionError) as e:
        abort(400, str(e))
    except:
        pass


def get_newick(tree_id, max_mb):
    "Return the newick representation of the given tree"

    nw = load_tree(tree_id).write()

    size_mb = len(nw) / 1e6
    if size_mb > max_mb:
        abort(400, 'newick too big (%.3g MB)' % size_mb)

    return nw


def remove_search(tid, args):
    "Remove search"
    if 'text' not in args:
        abort(400, 'missing search text')

    searches = app.trees[int(tid)].searches
    text = args.pop('text').strip()
    return searches.pop(text, None)


def store_search(tree_id, args):
    "Store the results and parents of a search and return their numbers"
    if 'text' not in args:
        abort(400, 'missing search text')

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
    except Exception as e:
        abort(400, f'evaluating expression: {e}')


def find_node(tree, args):
    if 'text' not in args:
        abort(400, 'missing search text')

    text = args.pop('text').strip()
    func = get_search_function(text)

    try:
        return next((node for node in tree.traverse() if func(node)), None)

    except Exception as e:
        abort(400, f'evaluating expression: {e}')


def get_selections(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    return [ name for name, (results, _) in tree.selected.items() if node in results ]


def update_node_props(node, args):
    for prop, value in node.props.items():
        newvalue = args.pop(prop, "").strip()
        if newvalue:
            try:  # convert to proper type
                newvalue = type(value)(newvalue)
            except:
                abort(400, f'property {prop} should be of type {type(value)}')
            node.add_prop(prop, newvalue)


def update_node_style(node, args):
    newstyle = {}
    for prop, value in dict(node.sm_style).items():
        newvalue = args.pop(prop, "").strip()
        if newvalue:
            try:  # convert to proper type
                newvalue = type(value)(newvalue)
            except:
                abort(400, f'property {prop} should be of type {type(value)}')
            else:
                newstyle[prop] = newvalue

    extend_to_descendants = args.pop("extend_to_descendants", None)
    if extend_to_descendants:
        nodes = node.traverse()
    else:
        nodes = [ node ]

    for node in nodes:
        for key, value in newstyle.items():
            node.sm_style[key] = value


def get_nodes_info(tree, nodes, props):
    no_props = len(props) == 1 and props[0] == ''

    if 'id' in props or no_props or '*' in props:
        node_ids = [ ",".join(map(str, node.id))
                for node in nodes ]
    if no_props:
        return node_ids

    nodes_info = []
    for idx, node in enumerate(nodes):
        if props[0] == "*":
            node_id = node_ids[idx]
            nodes_info.append({'id': node_id })
        else:
            node_p = { p: node.props.get(p) for p in props }
            if 'id' in props:
                node_p['id'] = node_ids[idx]
            nodes_info.append(node_p)

    return nodes_info


def get_selection_info(tree, args):
    "Get selection info from their nodes"
    if 'text' not in args:
        abort(400, 'missing selection text')
    name = args.pop('text').strip()
    nodes = tree.selected.get(name, [[]])[0]

    props = args.pop('props', '').strip().split(',')
    return get_nodes_info(tree.tree, nodes, props)


def remove_selection(tid, args):
    "Remove selection"
    if 'text' not in args:
        abort(400, 'missing selection text')
    name = args.pop('text').strip()
    return app.trees[int(tid)].selected.pop(name, None)


def change_selection_name(tid, args):
    if 'name' not in args or 'newname' not in args:
        abort(400, 'missing renaming parameters')

    name = args.pop('name').strip()
    selected = app.trees[int(tid)].selected

    if name not in selected.keys():
        abort(400, f'selection {name} does not exist')

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
        abort(400, 'missing selection text')

    text = args.copy().pop('text').strip()
    selected = app.trees[int(tid)].selected

    if text in selected.keys():
        abort(400, 'selection already exists')

    search = remove_search(tid, args)
    selected[text] = search


def prune_by_selection(tid, args):
    "Prune tree by keeping selections identified by their names"

    if 'names' not in args:
        abort(400, 'missing selection names')

    names = set(args.pop('names').strip().split(','))
    tree = app.trees[int(tid)]

    selected = set()
    for name,(results,_) in tree.selected.items():
        if name in names:
            selected.update(results)

    if len(selected) == 0:
        abort(400, 'selection does not exist')

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


def get_parents(results, count_leaves=False):
    "Return a set of parents given a set of results"
    parents = defaultdict(lambda: 0)
    for node in results:
        if count_leaves:
            nleaves = len(node)
        else:
            nleaves = 1
        parent = node.up
        while parent:
            parents[parent] += nleaves
            parent = parent.up
    return parents


def store_selection(tree_id, args):
    "Store the results and parents of a selection and return their numbers"
    if 'text' not in args:
        abort(400, 'missing selection text')

    tid, subtree = get_tid(tree_id)
    tree = app.trees[tid]
    node = tree.tree[subtree]

    parents = get_parents([node])

    name = args.pop('text').strip()
    return update_selection(tree, name, set([node]), parents)


def activate_node(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    tree.active.nodes.results.add(node)
    tree.active.nodes.parents.clear()
    tree.active.nodes.parents.update(get_parents(tree.active.nodes.results))


def deactivate_node(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[tid]
    node = tree.tree[subtree]
    tree.active.nodes.results.discard(node)
    tree.active.nodes.parents.clear()
    tree.active.nodes.parents.update(get_parents(tree.active.nodes.results))


def get_active_clade(node, active):
    if node in active:
        return node
    parent = node.up
    while parent:
        if parent in active:
            return parent
        else:
            parent = parent.up
    return None


def get_active_clades(results, parents):
    active = set()
    for node in results:
        parent = node.up
        current_active = node
        while parent:
            if parents.get(parent, 0) == len(parent):
                current_active = parent
                parent = parent.up
            else:
                active.add(current_active)
                break
    # Case where active clade is root
    if len(active) == 0 and len(parents.keys()) == 1:
        root = list(parents.keys())[0]
        if root.dist > 0:
            active.add(root)
        else:
            active.update(root.children)
    return active


def activate_clade(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    tree.active.clades.results.add(node)
    for n in node.descendants():
        tree.active.clades.results.discard(n)
    results = tree.active.clades.results
    parents = get_parents(results, count_leaves=True)
    active_parents = get_active_clades(results, parents)
    tree.active.clades.results.clear()
    tree.active.clades.parents.clear()
    tree.active.clades.results.update(active_parents)
    tree.active.clades.parents.update(get_parents(active_parents, count_leaves=True))


def remove_active_clade(node, active):
    active_parent = get_active_clade(node, active)
    active.discard(active_parent)

    if node == active_parent:
        return

    while node.up:
        parent = node.up
        active.update(parent.children)
        active.discard(node)
        node = parent
        if node == active_parent:
            return


def deactivate_clade(tree_id):
    tid, subtree = get_tid(tree_id)
    tree = app.trees[int(tid)]
    node = gdn.get_node(tree.tree, subtree)
    remove_active_clade(node, tree.active.clades.results)
    tree.active.clades.parents.clear()
    tree.active.clades.parents.update(get_parents(tree.active.clades.results))


def store_active(tree, idx, args):
    if 'text' not in args:
        abort(400, 'missing selection text')

    name = args.pop('text').strip()
    results = copy(tree.active[idx].results)
    if idx == 0:  # active.nodes
        parents = copy(tree.active[idx].parents)
    else:         # active.clades
        parents = get_parents(results)

    remove_active(tree, idx)

    return update_selection(tree, name, results, parents)


def remove_active(tree, idx):
    tree.active[idx].parents.clear()
    tree.active[idx].results.clear()


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
    if parts[0] not in ['/r', '/e', '/t']:
        abort(400, 'invalid command %r' % parts[0])
    if len(parts) != 2:
        abort(400, 'missing argument to command %r' % parts[0])

    command, arg = parts
    if command == '/r':  # regex search
        return lambda node: re.search(arg, node.name)
    elif command == '/e':  # eval expression
        return get_eval_search(arg)
    elif command == '/t':  # topological search
        return get_topological_search(arg)
    else:
        abort(400, 'invalid command %r' % command)


def get_eval_search(expression):
    "Return a function of a node that evaluates the given expression"
    try:
        code = compile(expression, '<string>', 'eval')
    except SyntaxError as e:
        abort(400, f'compiling expression: {e}')

    return lambda node: safer_eval(code, {
        'node': node, 'parent': node.up, 'up': node.up,
        'name': node.name, 'is_leaf': node.is_leaf,
        'length': node.dist, 'dist': node.dist, 'd': node.dist,
        'props': node.props, 'p': node.props,
        'get': dict.get,
        'children': node.children, 'ch': node.children,
        'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
        'regex': re.search,
        'startswith': str.startswith, 'endswith': str.endswith,
        'upper': str.upper, 'lower': str.lower, 'split': str.split,
        'any': any, 'all': all, 'len': len,
        'sum': sum, 'abs': abs, 'float': float, 'pi': pi})


def safer_eval(code, context):
    "Return a safer version of eval(code, context)"
    for name in code.co_names:
        if name not in context:
            abort(400, 'invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)


def get_topological_search(pattern):
    "Return a function of a node that sees if it matches the given pattern"
    try:
        tree_pattern = tm.TreePattern(pattern)
    except newick.NewickError as e:
        abort(400, 'invalid pattern %r: %s' % (pattern, e))

    return lambda node: tm.match(tree_pattern, node)


def get_stats(tree_id, pname):
    "Return some statistics about the given property pname"
    pmin, pmax = inf, -inf
    n, pmean, pmean2 = 0, 0, 0
    try:
        for node in load_tree(tree_id):
            if pname in node.props:
                value = float(node.props[pname])
                pmin, pmax = min(pmin, value), max(pmax, value)
                pmean = (n * pmean + value) / (n + 1)
                pmean2 = (n * pmean2 + value*value) / (n + 1)
                n += 1
        assert n > 0, 'no node has the given property'
        return {'n': n, 'min': pmin, 'max': pmax, 'mean': pmean,
                'var': pmean2 - pmean*pmean}
    except (ValueError, AssertionError) as e:
        abort(400, f'when reading property {pname}: {e}')


def sort(tree_id, node_id, key_text, reverse):
    "Sort the (sub)tree corresponding to tree_id and node_id"
    t = load_tree(tree_id)

    try:
        code = compile(key_text, '<string>', 'eval')
    except SyntaxError as e:
        abort(400, f'compiling expression: {e}')

    def key(node):
        return safer_eval(code, {
            'node': node, 'name': node.name, 'is_leaf': node.is_leaf,
            'length': node.dist, 'dist': node.dist, 'd': node.dist,
            'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
            'children': node.children, 'ch': node.children,
            'len': len, 'sum': sum, 'abs': abs})

    gdn.sort(gdn.get_node(t, node_id), key, reverse)


def add_trees_from_request():
    """Add trees to app.trees and return a dict of {name: id}."""
    try:
        if request.content_type.startswith('application/json'):
            trees = [req_json()]  # we have only one tree
            parser = newick.PARSER_DEFAULT
        else:
            trees = get_trees_from_form()
            parser = get_parser(request.forms.get('internal', 'name'))

        for tree in trees:
            add_tree(tree)

        return {tree['name']: tree['id'] for tree in trees}
        # TODO: tree ids are already equal to their names, so in the future
        # we could remove the need to send back their "ids".
    except (newick.NewickError, ValueError) as e:
        abort(400, f'malformed tree - {e}')


def get_parser(internal):
    """Return parser given the internal nodes main property interpretation."""
    p = {'name': newick.NAME, 'support': newick.SUPPORT}[internal]  # (()p:d);
    return dict(newick.PARSER_DEFAULT, internal=[p, newick.DIST])


def get_trees_from_form():
    """Return list of dicts with tree info read from a form in the request."""
    if 'trees' in request.files:
        try:
            fu = request.files['trees']  # bottle FileUpload object
            return get_trees_from_file(fu.filename, fu.file)
        except (gzip.BadGzipFile, UnicodeDecodeError) as e:
            abort(400, f'when reading {fupload.filename}: {e}')
    else:
        return [{
            'name': request.forms['name'],
            'newick': request.forms['newick'],
            'id': request.forms.get('id'),
            'b64pickle': request.forms.get('b64pickle'),
            'description': request.forms.get('description', ''),
            'layouts': request.forms.get('layouts', []),
            'include_props': request.forms.get('include_props', None),
            'exclude_props': request.forms.get('exclude_props', None),
        }]


def get_trees_from_file(filename, fileobject=None):
    """Return list of {'name': ..., 'newick': ...} extracted from file."""
    fileobject = fileobject or open(filename, 'rb')

    trees = []
    def extend(btext, fname):
        name = os.path.splitext(os.path.basename(fname))[0]  # /d/n.e -> n
        trees.extend(get_trees_from_nexus_or_newick(btext, name))

    if filename.endswith('.zip'):
        zf = zipfile.ZipFile(fileobject)
        for fname in zf.namelist():
            extend(zf.read(fname), fname)
    elif filename.endswith('.tar'):
        tf = tarfile.TarFile(fileobj=fileobject)
        for fname in tf.getnames():
            extend(tf.extractfile(fname).read(), fname)
    elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
        tf = tarfile.TarFile(fileobj=gzip.GzipFile(fileobj=fileobject))
        for fname in tf.getnames():
            extend(tf.extractfile(fname).read(), fname)
    elif filename.endswith('.gz'):
        extend(gzip.GzipFile(fileobj=fileobject).read(), filename)
    elif filename.endswith('.bz2'):
        extend(bz2.BZ2File(fileobject).read(), filename)
    else:
        extend(fileobject.read(), filename)

    return trees


def get_trees_from_nexus_or_newick(btext, name_newick):
    """Return list of {'name': ..., 'newick': ...} extracted from btext."""
    text = btext.decode('utf8').strip()

    try:  # we first try to read it as a nexus file
        trees = nexus.get_trees(text)
        return [{'name': name, 'newick': nw} for name, nw in trees.items()]
    except nexus.NexusError:  # if it isn't, we assume the text is a newick
        return [{'name': name_newick, 'newick': text}]  # only one tree!



def add_tree(data):
    "Add tree with given data and return its id"
    tid = int(data['id'])
    name = data['name']
    nw = data.get('newick')
    bpickle = data.get('b64pickle')
    layouts = data.get('layouts', [])
    if type(layouts) == str:
        layouts = layouts.split(',')
    include_props = data.get('include_props')
    if type(include_props) == str:
        include_props = include_props.split(',')
    exclude_props = data.get('exclude_props')
    if type(exclude_props) == str:
        exclude_props = exclude_props.split(',')

    del_tree(tid)  # delete if there is a tree with same id

    if nw is not None:
        tree = load_tree_from_newick(tid, nw)
    elif bpickle is not None:
        tree = ete_format.loads(bpickle, unpack=True)
        gdn.standardize(tree)
    else:
        tree = data.get('tree')
        if not tree:
            abort(400, 'Either Newick or Tree object has to be provided.')

    # TODO: Do we need to do this? (Maybe for the trees uploaded with a POST)
    # gdn.update_sizes_all(t)

    app_tree = app.trees[tid]
    app_tree.name = name
    app_tree.tree = tree
    app_tree.layouts = retrieve_layouts(layouts)
    app_tree.include_props = include_props
    app_tree.exclude_props = exclude_props

    def write_tree():
        """Write tree data as a temporary pickle file."""
        obj = { 'name': name, 'layouts': layouts, 'tree': tree }
        with open(f'/tmp/{tid}.pickle', 'wb') as handle:
            pickle.dump(obj, handle)
    thr_write = Thread(daemon=True, target=write_tree)  # so we are not delayed
    thr_write.start()                                   # by big trees

    app.trees[tid].timer = time()

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
        app.avail_layouts = get_layouts_from_getters()
        app.avail_layouts.pop('default_layouts', None)
    except Exception as e:
        abort(400, f'Error while updating app layouts: {e}')


def get_layouts_from_getters():
    """Return a dict {name: [layout1, ...]} for all layout submodules."""
    # The list contains, for every submodule of layout_modules, an
    # instance of all the LayoutX classes that the submodule contains.
    submodules = [getattr(layout_modules, module) for module in dir(layout_modules)
                  if not module.startswith('__')]

    all_layouts = {}
    for module in submodules:
        name = module.__name__.split('.')[-1]

        layouts = [getattr(module, getter)() for getter in dir(module)
                   if getter.startswith('Layout')]

        for layout in layouts:  # TODO: is this necessary? remove if not
            layout.module = name  # set for future reference

        all_layouts[name] = layouts

    return all_layouts


# Layout related functions
def get_layouts(layouts=None):
    # Get layouts from their getters in layouts module:
    # smartview/redender/layouts
    layouts_from_module = get_layouts_from_getters()

    # Get default layouts
    default_layouts = layouts_from_module.pop("default_layouts")

    all_layouts = {}
    for idx, layout in enumerate(default_layouts + (layouts or [])):
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
            tree.tree.to_ultrametric()
            gdn.standardize(tree.tree)
            initialize_tree_style(tree, ultrametric=True)
        else:
            app.trees.pop(tid, None) # delete from memory


def get_tid(tree_id):
    "Return the tree id and the subtree id, with the appropriate types"
    # Example: '3342,1,0,1,1' -> (3342, [1, 0, 1, 1])
    try:
        if type(tree_id) == int:
            return tree_id, []
        else:
            tid, *subtree = tree_id.split(',')
            return int(tid), [int(n) for n in subtree]
    except ValueError:
        abort(404, f'invalid tree id {tree_id}')


def del_tree(tid):
    "Delete a tree and everywhere where it appears referenced"
    shutil.rmtree(f'/tmp/{tid}.pickle', ignore_errors=True)
    return app.trees.pop(tid, None)


def get_fields(required=None, valid_extra=None):
    "Return fields and raise exception if missing required or invalid present"
    data = req_json()

    if required and any(x not in data for x in required):
        abort(400, f'must have the fields {required}')

    valid = (required or []) + (valid_extra or [])
    if not all(x in valid for x in data):
        abort(400, f'can only have the fields {valid}')

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

def initialize(tree=None, layouts=None,
               include_props=None, exclude_props=None,
               safe_mode=False, compress=False):
    """Initialize the global object app."""
    app = GlobalStuff()

    app.safe_mode = safe_mode

    app.compress = compress

    # App associated layouts
    # Layouts will be accessible for each tree independently
    app.default_layouts, app.avail_layouts = get_layouts(layouts)

    # Dict containing AppTree dataclasses with tree info
    app.trees = defaultdict(lambda: AppTree(
        name='tree',
        style=copy_style(TreeStyle()),
        nodestyles={},
        include_props=deepcopy(include_props),
        exclude_props=deepcopy(exclude_props),
        layouts=deepcopy(app.default_layouts),
        timer=time(),
        searches={},
        selected={},
        active=drawer_module.get_empty_active(),
    ))

    thread_maintenance = Thread(daemon=True, target=maintenance, args=(app,))
    thread_maintenance.start()
    g_threads['maintenance'] = thread_maintenance

    return app


def run_smartview(tree=None, name=None, layouts=[],
                  include_props=None, exclude_props=None,
                  safe_mode=False, host='localhost', port=5000, quiet=True,
                  compress=False, daemon=True):
    # Set tree_name to None if no tree was provided
    # Generate tree_name if none was provided
    name = name or (make_name() if tree else None)

    global app
    app = initialize(name, layouts,
                     include_props=include_props, exclude_props=exclude_props,
                     safe_mode=safe_mode, compress=compress)

    # TODO: Create app.recent_trees with paths to recently viewed trees

    if tree:
        gdn.standardize(tree)
        tree_data = {
            'id': 0,  # id to be replaced by actual hash
            'name': name,
            'tree': tree,
            'layouts': [],
            'include_props': include_props,
            'exclude_props': exclude_props,
        }
        tid = add_tree(tree_data)
        print(f'Added tree {name} with id {tid}.')

    launch_browser(host, port)

    if 'webserver' not in g_threads:
        thread_webserver = Thread(
            daemon=daemon,
            target=run,
            kwargs={'quiet': quiet, 'host': host, 'port': port})
        thread_webserver.start()
        g_threads['webserver'] = thread_webserver


def maintenance(app, check_interval=60, max_time=30*60):
    """Perform maintenance tasks every check_interval seconds."""
    while True:
        # Remove trees that haven't been accessed in max_time.
        tids = list(app.trees.keys())
        for tid in tids:
            inactivity_time = time() - app.trees[tid].timer
            if inactivity_time > max_time:
                del_tree(tid)

        sleep(check_interval)


def make_name():
    """Return a unique tree name like 'tree-<number>'."""
    if app:
        tnames = [t.name for t in app.trees.values()
                  if t.name.startswith('tree-')
                  and t.name[len('tree-'):].isdecimal()]
    else:
        tnames = []
    n = max((int(name[len('tree-'):]) for name in tnames), default=0) + 1
    return f'tree-{n}'


def launch_browser(host, port):
    """Try to open a browser window in a different process."""
    try:
        command = {'Linux': 'xdg-open', 'Darwin': 'open'}[platform.system()]
        Popen([command, f'http://{host}:{port}'],
              stdout=DEVNULL, stderr=DEVNULL)
    except (KeyError, FileNotFoundError) as e:
        print(f'Explorer available at http://{host}:{port}')



if __name__ == '__main__':
    run_smartview(safe_mode=True)
