#!/usr/bin/env python3

"""
Example program to quickly identify nodes and move them around in the tree.
"""

import sys

from ete4 import Tree, TreeError, newick, operations as ops


def main():
    try:
        # Load the tree or an example.
        if len(sys.argv) > 1:
            print('Loading tree from:', sys.argv[1])
            t = Tree(open(sys.argv[1]))
        else:
            print('No tree given. Loading an example tree with 10 leaves.')
            t = Tree()
            t.populate(10)

        add_node_id_prop(t)  # so we can show it (printed or in the explorer)

        ask_and_process(t)

    except (FileNotFoundError, newick.NewickError) as e:
        sys.exit(e)
    except (KeyboardInterrupt, EOFError) as e:
        print()  # and we exit


def ask_and_process(t):
    options = """Select:
  p - Print tree (simple)
  i - Print tree (with node ids)
  e - Launch explorer
  m - Move node
  s - Write newick (to screen)
  f - Write newick (to file)
  q - Exit"""

    print(options)

    while True:
        option = input('> ').strip().lower()

        if option == 'p':
            print(t)
        elif option == 'i':
            print(t.to_str(props=['node_id'], compact=True))
        elif option == 'e':
            t.explore(show_popup_props=['node_id'])
        elif option == 'm':
            try:
                id0 = str2id(input('Id of node to move: '))
                id1 = str2id(input('Id of new hanging node: '))
                rehang(t[id0], t[id1])
                ops.update_sizes_all(t)  # so it shows well in the explorer
                add_node_id_prop(t)  # update the annotated ids
            except (ValueError, AssertionError, TreeError) as e:
                print('Error:', e)
        elif option == 's':
            print(t.write())
        elif option == 'f':
            fname = input('Output file: ').strip()
            if fname:
                t.write(outfile=fname)
                print('Newick written to', fname)
        elif option == 'q':
            return
        elif option == '?':
            print(options)
        else:
            print('Unrecognized option (enter "?" to see options).')


def add_node_id_prop(t):
    """Add (or update) the node id as a property 'node_id'."""
    for node in t.traverse():
        node.props['node_id'] = ','.join(str(i) for i in node.id)
        # So it looks like '1,0,1,1' instead of (1, 0, 1, 1)


def str2id(id_str):
    """Return a node id (as a tuple of ints) from its text representation."""
    return tuple(int(x) for x in id_str.split(','))  # '1,0,1,1' -> (1, 0, 1, 1)


def rehang(node1, node2):
    """Hang node1 where node2 is."""
    assert not node1.is_root and not node2.is_root, 'Node cannot be the root.'
    assert node1 not in node2.ancestors(), 'Cannot hang to a descendant.'

    # Detach and remember the original parent.
    up1 = node1.up
    node1.detach()

    # Put in new position by adding an intermediate new node.
    up2 = node2.up
    i = up2.children.index(node2)
    new = Tree(children=[node2, node1])
    up2.children[i] = new
    new.up = up2

    # Join branch if it has only one child.
    if len(up1.children) == 1:
        ops.join_branch(up1)



if __name__ == '__main__':
    main()
