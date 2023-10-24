import random

from ete4 import Tree
from ete4.treeview import TreeStyle, NodeStyle, faces, AttrFace, CircleFace


def layout(node):
    if node.is_leaf:
        # Add node name to leaf nodes.
        N = AttrFace('name', fsize=14, fgcolor='black')
        faces.add_face_to_node(N, node, 0)

    if 'weight' in node.props:
        # Create a sphere face whose size is proportional to the node's  'weight'.
        C = CircleFace(radius=node.props['weight'], color='RoyalBlue', style='sphere')
        # Let's make the sphere transparent.
        C.opacity = 0.3
        # And place it as a float face over the tree.
        faces.add_face_to_node(C, node, 0, position='float')


def get_example_tree():
    # Make a random tree.
    t = Tree()
    t.populate(20, random_branches=True)

    # Add some random weight to all nodes.
    for n in t.traverse():
        n.add_props(weight=random.randint(0, 50))

    # Create an empty TreeStyle.
    ts = TreeStyle()

    # Set our custom layout function.
    ts.layout_fn = layout

    # Draw a circular tree.
    ts.mode = 'c'

    # We will add node names manually.
    ts.show_leaf_name = False
    # Show branch data.
    ts.show_branch_length = True
    ts.show_branch_support = True

    return t, ts


if __name__ == '__main__':
    t, ts = get_example_tree()
    t.show(tree_style=ts)
    # If we want to save it, we can do:
    #   t.render('bubble_map.png', w=600, dpi=300, tree_style=ts)
