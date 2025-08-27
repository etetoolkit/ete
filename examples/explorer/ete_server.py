#!/usr/bin/env python3

"""
Example of an ete server with an extended api.
"""

from ete4 import Tree, newick, nexus
from ete4.smartview import Layout, TextFace, BASIC_LAYOUT

import ete4.smartview.explorer as exp  # to get all the server functions


# Add the /load endpoint to the api.

@exp.post('/load')
def callback():
    """Load a tree from a given path."""
    try:
        # We can get all the information we need, and create our tree.
        info = exp.req_json()  # get the POST json (a dict in our case)

        name = info['name']
        path = info['path']
        parser = info.get('parser', 'support')
        extra_style = info.get('show_popup_props', None)
        layout_names = [x.strip() for x in info.get('layouts', '').split(',')]

        layouts = [x for x in exp.get_layouts() if x.name in layout_names]

        t = Tree(open(path).read().strip(), parser=parser)
        exp.add_tree(t, name, layouts, extra_style)

        exp.response.status = 201  # http code for new resource created
        return {'message': 'ok'}  # arbitrary, just what ete endpoints use
    except FileNotFoundError as e:
        exp.abort(404, f'path {path} not found: {e}')
    except (newick.NewickError, nexus.NexusError, AssertionError) as e:
        exp.abort(400, f'parsing error: {e}')
    except KeyError as e:
        exp.abort(400, f'missing data in request: {e}')


# Create and add an example new layout, so we can use it when we /load a tree.

def draw_node(node):
    if node.name:
        yield TextFace(node.name)

NameLayout = Layout('name', draw_node=draw_node)

exp.add_layouts([BASIC_LAYOUT, NameLayout])


# Run the server and show where it is.

exp.start_server(verbose=True)  # just to show what is going on

host, port = exp.get_server_address()
print(f'Explorer available at http://{host}:{port}')

print('Press enter to stop the server and finish.')
input()
