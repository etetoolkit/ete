"""
Parser where the structure is given by the indentation.

For example::

  node0
    node1
    node2
      node3
        node4
    node5
      node6

Or like the output of ``t.to_str(cascade=True)``, as in::

  t = Tree()
  t.populate(6)
  print(t.to_str(cascade=True, props=['name']))

  ⊗
  ├─┐⊗
  │ ├─┐⊗
  │ │ ├─╴c
  │ │ └─┐⊗
  │ │   ├─╴a
  │ │   └─╴b
  │ └─┐⊗
  │   ├─╴e
  │   └─╴f
  └─╴d
"""

from ..core.tree import Tree


# Any of these chars are considered part of the (left) indentation.
DEFAULT_INDENT_CHARS = ' \t\n\r-|_/\\`─│┐├┤┬┼╌╭╰╴└\xa0'


def load(fp, parse_content=None, indent_chars=DEFAULT_INDENT_CHARS):
    """Return tree read from a file with its indented representation."""
    assert hasattr(fp, 'read'), f'fp is not a file object: {fp}'
    return read(fp, parse_content, indent_chars)


def loads(text, parse_content=None, indent_chars=DEFAULT_INDENT_CHARS):
    """Return tree read from a text with its indented representation."""
    return read(text.splitlines(), parse_content, indent_chars)


def read(lines, parse_content=None, indent_chars=DEFAULT_INDENT_CHARS):
    """Return tree read from lines with its indented representation.

    :param lines: A generator of lines (a file object or a list of
        strings) with the textual representation of the tree.
    :param parse_content: Function returning a node from the content of a line.
    :param indent_chars: Characters that may appear as part of the indentation.
    """
    parse_content = parse_content or (lambda name: Tree({'name': name}))

    indentations = [0]  # levels of indentation
    node_last = Tree()  # last node we processed

    for line in lines:
        line = line.rstrip()  # helps disambiguating indentation of empty lines

        assert line, 'found an unexpected empty line'

        content = line.lstrip(indent_chars)
        indent = len(line) - len(content)
        node = parse_content(content)

        # Find the right parent for the current node.
        if indent > indentations[-1]:  # we incresed indentation
            indentations.append(indent)
            parent = node_last  # so the last node we saw will be our parent
        else:
            parent = node_last.up  # we share parent, or...
            while indentations[-1] != indent:  # we find it at its indentation
                indentations.pop()
                node_last = parent
                parent = node_last.up

        if parent is not None:
            parent.add_child(node)

        node_last = node

    return node.root


def dumps(tree, props=None, px=1):
    """Return indented representation of the given tree."""
    return tree.to_str(props=props, px=px, cascade=True)


def dump(tree, fp, props=None, px=1):
    fp.write(tree.to_str(props=props, px=px, cascade=True))
