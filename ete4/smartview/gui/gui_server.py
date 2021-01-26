#!/usr/bin/env python3

import os
import sys
from functools import partial
from contextlib import contextmanager
from flask import Flask, request, jsonify, g, redirect, url_for
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_restful import Resource, Api
from flask_cors import CORS
import sqlalchemy

from ete4 import Tree
from ete4.smartview import draw
from ete4.smartview.treeimage import TreeImage 

app = None

import os

class InvalidUsage(Exception):
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = 'Error: ' + message
        self.status_code = status_code

class Trees(Resource):
    def get(self, tree_id=None):
        "Return info about the tree (or all trees if no id given)"
        rule = request.url_rule.rule  # shortcut
        
        if rule == '/trees':
            return [{"id":tindex, "name":"test", "desc":"test"} for tindex, t in enumerate(app.trees)]
        elif rule == '/trees/drawers':
            return [d.__name__[len('Drawer'):] for d in draw.get_drawers()]
        elif rule == '/trees/<int:tree_id>':
            return get_tree(app.trees[tree_id].tree)
        elif rule == '/trees/<int:tree_id>/newick':
            return get_tree(app.trees[tree_id].tree.write())
        elif rule == '/trees/<int:tree_id>/draw':
            try:
                viewport = get_viewport(request.args)
                zoom = [float(request.args.get(z, 1)) for z in ['zx', 'zy']]
                assert zoom[0] > 0 and zoom[1] > 0, 'zoom must be > 0'
                drawer = get_drawer(request.args)
                drawer.MIN_HEIGHT = float(request.args.get('min_height', 6))
                assert drawer.MIN_HEIGHT > 0, 'min_height must be > 0'
                return list(drawer(viewport, zoom).draw(load_tree(tree_id)))
            except (ValueError, AssertionError) as e:
                raise InvalidUsage(str(e))
        elif rule == '/trees/<int:tree_id>/size':
            
            width, height = load_tree(tree_id).tree.size
            return {'width': width, 'height': height}
        else:
            raise InvalidUsage('unknown tree GET request')


def load_tree(tree_id):
    """ Add tree to app.trees and initialize it if not there, and return it """
    tree_id=0
    global app
    if tree_id not in app.trees:       
        t = Tree(app.newicks[int(tree_id)])
        t_img = TreeImage(t)
        app.trees[tree_id] = t_img
    return app.trees[tree_id]
    
def get_viewport(args):
    "Return the viewport (x, y, w, h) specified in the args"
    try:
        x, y, w, h = [float(args[v]) for v in ['x', 'y', 'w', 'h']]
        assert w > 0 and h > 0, 'width and height should be > 0'
        return (x, y, w, h)
    except KeyError as e:
        return None  # None is interpreted as an infinite rectangle
    except (ValueError, AssertionError) as e:
        raise InvalidUsage(f'not a valid viewport: {e}')

def get_drawer(args):
    "Return the drawer specified in the args"
    try:
        drawer_name = request.args.get('drawer', 'Full')
        return next(d for d in draw.get_drawers()
            if d.__name__[len('Drawer'):] == drawer_name)
    except StopIteration:
        raise InvalidUsage(f'not a valid drawer: {drawer_name}')


# App initialization.
def initialize(newicks):
    "Initialize the database and the flask app"
    global app 
       
    app = Flask(__name__, instance_relative_config=True)
    configure(app)
        
    api = Api(app)
    add_resources(api)
    
    app.newicks = newicks # a list of paths from where to load trees
    app.trees = {}  # to keep in memory loaded trees
    load_tree(0) # preloads the first tree
       
    @app.route('/')
    def index():
        return redirect(url_for('static', filename='gui.html'))

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

    CORS(app)  # allows cross-origin resource sharing (requests from other domains)

    app.config.from_mapping(
        SEND_FILE_MAX_AGE_DEFAULT=0,  # do not cache static files
        DATABASE=f'{app.instance_path}/trees.db',
        SECRET_KEY=' '.join(os.uname()))  # for testing, or else use config.py

    if os.path.exists(f'{app.instance_path}/config.py'):
        app.config.from_pyfile(f'{app.instance_path}/config.py')  # overrides

def add_resources(api):
    "Add all the REST endpoints"
    add = api.add_resource  # shortcut
    add(Trees, '/trees', '/trees/drawers',
        '/trees/<int:tree_id>',
        '/trees/<int:tree_id>/newick',
        '/trees/<int:tree_id>/draw',
        '/trees/<int:tree_id>/size')

from argparse import ArgumentParser
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-t", dest="trees", nargs='+', type=str, help="Trees to browse")
    args = parser.parse_args()
    newicks = [os.path.abspath(t) for t in args.trees]
    # probably a dirty approach, but we need to serve contect with root anchored
    # to the same dir. Alternatives?
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    app = initialize(newicks)
    app.run(debug=True, use_reloader=False)     
   