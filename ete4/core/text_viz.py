"""
Tree text visualization.

Functions to show a string drawing of a tree suitable for printing on
a console.
"""

# These functions would not normally be used direclty. Instead, they
# are used when doing things like:
#   print(t)
# or like:
#   t.to_str(...)


def to_str(tree, show_internal=True, compact=False, props=None,
           px=None, py=None, px0=0, cascade=False):
    """Return a string containing an ascii drawing of the tree.

    :param show_internal: If True, show the internal nodes too.
    :param compact: If True, use exactly one line per tip.
    :param props: List of node properties to show. If None, show all.
    :param px, py, px0: Paddings (x, y, x for leaves). Overrides `compact`.
    :param cascade: Use a cascade representation. Overrides
        `show_internal`, `compact`, `px`, `py`, `px0`.
    """
    if not cascade:
        px = px if px is not None else (0 if show_internal else 1)
        py = py if py is not None else (0 if compact else 1)

        lines, _ = ascii_art(tree, show_internal, props, px, py, px0)
        return '\n'.join(lines)
    else:
        px = px if px is not None else 1
        return to_cascade(tree, props, px)


# For representations like:
#    ╭╴a
# ╴h╶┤   ╭╴b
#    ╰╴g╶┼╴e╶┬╴c
#        │   ╰╴d
#        ╰╴f

def ascii_art(tree, show_internal=True, props=None, px=0, py=0, px0=0):
    """Return list of strings representing the tree, and their middle point.

    :param tree: Tree to represent as ascii art.
    :param show_internal: If True, show the internal node names too.
    :param props: List of properties to show for each node. If None, show all.
    :param px, py: Padding in x and y.
    :param px0: Padding in x for leaves.
    """
    # Node description (including all the requested properties).
    descr = ','.join(
        (f'{k}={v}' for k, v in tree.props.items()) if props is None else
        (str(tree.get_prop(p, '')) or '⊗' for p in props))

    if tree.is_leaf:
        return (['─' * px0 + '╴' + descr], 0)

    lines = []
    padding = ((px0 + 1 + len(descr) + 1) if show_internal else 0) + px
    for child in tree.children:
        lines_child, mid = ascii_art(child, show_internal, props, px, py, px0)

        if len(tree.children) == 1:       # only one child
            lines += add_prefix(lines_child, padding, mid, ' ',
                                                           '─',
                                                           ' ')
            pos_first = mid
            pos_last = len(lines) - mid
        elif child == tree.children[0]:   # first child
            lines += add_prefix(lines_child, padding, mid, ' ',
                                                           '╭',
                                                           '│')
            lines.extend([' ' * padding + '│'] * py)  # y padding
            pos_first = mid
        elif child != tree.children[-1]:  # a child in the middle
            lines += add_prefix(lines_child, padding, mid, '│',
                                                           '├',
                                                           '│')
            lines.extend([' ' * padding + '│'] * py)  # y padding
        else:                             # last child
            lines += add_prefix(lines_child, padding, mid, '│',
                                                           '╰',
                                                           ' ')
            pos_last = len(lines_child) - mid

    mid = (pos_first + len(lines) - pos_last) // 2  # middle point

    lines[mid] = add_base(lines[mid], px, px0, descr, show_internal)

    return lines, mid


def add_prefix(lines, px, mid, c1, c2, c3):
    """Return the given lines adding a prefix.

    :param lines: List of strings, to return with prefixes.
    :param int px: Padding in x.
    :param int mid: Middle point (index of the row where the node would hang).
    :param c1, c2, c3: Character to use as prefix before, at, and after mid.
    """
    prefix = lambda i: ' ' * px + (c1 if i < mid else (c2 if i == mid else c3))

    return [prefix(i) + line for i, line in enumerate(lines)]


def add_base(line, px, px0, txt, show_internal):
    """Return the same line but adding a base line."""
    # Example of change at the beginning of line: ' │' -> '─┤'
    replacements = {
        '│': '┤',
        '─': '╌',
        '├': '┼',
        '╭': '┬'}

    padding = ((px0 + 1 + len(txt) + 1) if show_internal else 0) + px

    prefix_txt = '─' * px0 + (f'╴{txt}╶' if txt else '──')

    return ((prefix_txt if show_internal else '') +
            '─' * px + replacements[line[padding]] + line[padding+1:])


# For representations like:
# h
# ├─╴a
# └─┐g
#   ├─╴b
#   ├─┐e
#   │ ├─╴c
#   │ └─╴d
#   └─╴f

def to_cascade(tree, props=None, px=1, are_last=None):
    """Return string with a visual representation of the tree as a cascade."""
    are_last = are_last or []

    # Node description (including all the requested properties).
    descr = ','.join(
        (f'{k}={v}' for k, v in tree.props.items()) if props is None else
        (str(tree.get_prop(p, '')) or '⊗' for p in props))

    branches = get_branches_repr(are_last, tree.is_leaf, px)

    wf = lambda n, lasts: to_cascade(n, props, px, lasts)  # shortcut

    return '\n'.join([branches + descr] +
                     [wf(n, are_last + [False]) for n in tree.children[:-1]] +
                     [wf(n, are_last + [True] ) for n in tree.children[-1:]])


def get_branches_repr(are_last, is_leaf, px):
    """Return a text line representing the open branches according to are_last.

    :param are_last: List of bools that say per level if we are the last node.
    :param is_leaf: says if the node to represent in this line has no children.
    :param px: Padding in x.

    Example (for is_leaf=True, px=6)::

      [True , False, True , True , True ] ->
      '│             │      │      ├──────╴'
    """
    if len(are_last) == 0:
        return ''

    prefix = ''.join((' ' if is_last else '│') + ' ' * px
                     for is_last in are_last[:-1])

    return (prefix   + ('└' if are_last[-1] else '├') +
            '─' * px + ('╴' if is_leaf      else '┐'))


def to_repr(tree, depth=4, nchildren=3):
    """Return a text representation that exactly recreates the tree.

    If depth and nchildren are None, return the full representation.
    """
    children = tree.children[:nchildren]
    depth_1 = depth if depth is None else depth - 1
    children_repr = '...' if depth == 0 else (
        ', '.join(to_repr(node, depth_1, nchildren) for node in children) +
        ('' if nchildren is None or len(tree.children) <= nchildren
         else ', ...'))

    return 'Tree(%r, [%s])' % (tree.props, children_repr)
