#!/usr/bin/env python3

"""
Example of an ete server with an extended api.
"""

from ete4 import Tree
from ete4.smartview import Layout, TextFace

import ete4.smartview.explorer as ex  # to get all the server functions


# Add NameLayout, a simple example of a layout, that we will use in /load_custom.

def draw_node(node):
    yield TextFace(node.name)

NameLayout = Layout('name', draw_node=draw_node)


# Add the /load_custom endpoint to the api.

@ex.post('/load_custom')
def callback():
    """Load a tree in whatever way we want, like using databases."""
    try:
        # We can get all the information we need, and create our tree.
        info = ex.req_json()  # get the POST json as a dict

        #t = load_tree(info['cluname'])  # <-- or whatever
        t = Tree(info['newick'])  # example key, with the newick

        name = info['name']  # example key, with the name for the gui

        ex.add_tree(t, name, layouts=[NameLayout],
                    extra_style={'show_popup_props': None})

        ex.response.status = 201  # http code for new resource created
        return {'message': 'ok'}  # arbitrary, just what ete endpoints use
    except KeyError as e:
        ex.abort(400, f'missing data in request: {e}')
    except (newick.NewickError, ValueError) as e:
        ex.abort(400, f'malformed tree - {e}')


# Run the server and show where it is.

_, server = ex.start_server(verbose=True)  # just to show what is going on

host, port = server.bind_addr
print(f'Explorer available at http://{host}:{port}')

print('Press enter to stop the server and finish.')
input()
