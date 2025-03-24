"""
Parser for trees represented in newick format.

The main functions are ``loads()`` and ``dumps()``, which read/write a tree
from/to its newick text representation.

When reading a newick file, the argument ``parser=...`` specifies
which kind of parser to use.

The classical ones in ete are the following:

.. table::

  ====== ======================================== =================================
  Format Description                              Example
  ====== ======================================== =================================
  0 (*)  internal nodes with support (flexible)   ((D:2,E:5)1.0:9,(F:6,G):7);
  1      internal nodes with names (flexible)     ((D:2,E:5)B:9,(F:6,G):7);
  2      internal w/ support, all values present  ((D:2,E:5)1.0:9,(F:6,G:3)1.0:7);
  3      internal w/ names, all values present    ((D:2,E:5)B:9,(F:6,G:3)C:7);
  4      names and lengths for leaves only        ((D:2,E:5),(F:6,G:3));
  5      leaf names and all lengths               ((D:2,E:5):9,(F:6,G:3):7);
  6      leaf names and internal lengths          ((D,F):6,(B,H):8);
  7      all names and leaf lengths               ((D:2,E:5)B,(F:6,G:3)C);
  8      all names (leaves and internal nodes)    ((D,E)B,(F,G)C);
  9      leaf names only                          ((D,E),(F,G));
  100    topology only                            ((,),(,));
  ====== ======================================== =================================

where the example tree would look (more or less) like::

         ╭╴D:2
   ╭╴B:9╶┤
   │     ╰╴E:5
  ╶┤
   │     ╭╴F:6
   ╰╴C:7╶┤
         ╰╴G:3

There are other valid values for ``parser``:

- ``'name'``, same as 1
- ``'support'``, same as 0
- ``'multisupport'``, internal nodes look like ``((X:5)80/100:7)...``, that is,
  have multiple values of support separated by ``/``

More generally, ``parser`` can be a dictionary that specifies in
detail how to read/write each field. It must say, for leaf and internal
nodes, what ``p0:p1`` means (which properties they are, including how
to read and write them). For example, the default parser looks like::

  PARSER_DEFAULT = {
      'leaf':     [NAME,    DIST],  # ((name:dist)x:y);
      'internal': [SUPPORT, DIST],  # ((x:y)support:dist);
  }

where ``NAME`` and ``DIST`` are "property dicts", that have all the
information for a property (``pname``) to know which function to apply
to read/write from/to a string. For example, ``DIST`` is::

  DIST = {'pname': 'dist', 'read': float, 'write': lambda x: '%g' % float(x)}
"""

# See https://en.wikipedia.org/wiki/Newick_format

from ..core.tree import Tree


class NewickError(Exception):
    pass

def error(text):  # to be able to raise error as a function call
    raise NewickError(text)


def quote(name, escaped_chars=" \t\r\n()[]':;,"):
    """Return the name quoted if it has any characters that need escaping."""
    if any(c in name for c in escaped_chars):
        return "'%s'" % name.replace("'", "''")  # ' escapes to '' in newicks
    else:
        return name

def unquote(name):
    """Return the name unquoted if it was quoted."""
    name = str(name).strip()

    if name.startswith("'") and name.endswith("'"):  # standard quoting with '
        return name[1:-1].replace("''", "'")  # ' escapes to '' in newicks
    elif name.startswith('"') and name.endswith('"'):  # non-standard quoting "
        return name[1:-1].replace('""', '"')
    else:
        return name

# A "property dict" has all the information for a property ('pname') to know
# which function to apply to read/write from/to a string.
#
# For example: {'pname': 'my-prop', 'read': str, 'write': str}

NAME    = {'pname': 'name',    'read': unquote, 'write': quote}
DIST    = {'pname': 'dist',    'read': float,   'write': lambda x: '%g' % float(x)}
SUPPORT = {'pname': 'support', 'read': float,   'write': lambda x: '%g' % float(x)}

MULTISUPPORT = {  # to parse multiple values of support written as v1/v2[/...]
    'pname': 'multisupport',
    'read': lambda field: [float(x) for x in field.split('/')],
    'write': lambda xs: '/'.join('%g' % float(x) for x in xs),
}

# A "parser dict" says, for leaf and internal nodes, what 'p0:p1' means
# (which properties they are, including how to read and write them).

PARSER_DEFAULT = {
    'leaf':     [NAME,    DIST],  # ((name:dist)x:y);
    'internal': [SUPPORT, DIST],  # ((x:y)support:dist);
}

# This part is used for parsers referred by name (or old-fashioned integers).

NAME_REQ = dict(NAME, req=True)  # value required
DIST_REQ = dict(DIST, req=True)
SUPPORT_REQ = dict(SUPPORT, req=True)

EMPTY = {'pname': '',
         'read': lambda x: error(f'parser expected empty field but got: {x}'),
         'write': lambda x: ''}

PARSERS = {  # predefined parsers
    None: PARSER_DEFAULT,
    0:   {'leaf': [NAME,     DIST],     'internal': [SUPPORT,     DIST]},
    1:   {'leaf': [NAME,     DIST],     'internal': [NAME,        DIST]},
    2:   {'leaf': [NAME_REQ, DIST_REQ], 'internal': [SUPPORT_REQ, DIST_REQ]},
    3:   {'leaf': [NAME_REQ, DIST_REQ], 'internal': [NAME_REQ,    DIST_REQ]},
    4:   {'leaf': [NAME_REQ, DIST_REQ], 'internal': [EMPTY,       EMPTY]},
    5:   {'leaf': [NAME_REQ, DIST_REQ], 'internal': [EMPTY,       DIST_REQ]},
    6:   {'leaf': [NAME_REQ, EMPTY],    'internal': [EMPTY,       DIST_REQ]},
    7:   {'leaf': [NAME_REQ, DIST_REQ], 'internal': [NAME_REQ,    EMPTY]},
    8:   {'leaf': [NAME_REQ, EMPTY],    'internal': [NAME_REQ,    EMPTY]},
    9:   {'leaf': [NAME_REQ, EMPTY],    'internal': [EMPTY,       EMPTY]},
    100: {'leaf': [EMPTY,    EMPTY],    'internal': [EMPTY,       EMPTY]},
    'name':         {'leaf': [NAME, DIST], 'internal': [NAME,         DIST]},
    'support':      {'leaf': [NAME, DIST], 'internal': [SUPPORT,      DIST]},
    'multisupport': {'leaf': [NAME, DIST], 'internal': [MULTISUPPORT, DIST]},
}

def make_parser(parser=None, name='%s', dist='%g', support='%g'):
    """Return parser changing the format of properties name, dist or support."""
    # Auxiliary function to return modified property dicts.
    def copy(props):
        p0, p1 = props[0].copy(), props[1].copy()  # so the changes are local
        for p in [p0, p1]:  # change the writer functions
            if p['pname'] == 'name':
                p['write'] = lambda x: quote(name % x)  # "name" looks like '%s'
            elif p['pname'] == 'dist':
                p['write'] = lambda x: dist % float(x)  # "dist" looks like '%g'
            elif p['pname'] == 'support':
                p['write'] = lambda x: support % float(x)  # etc
        return [p0, p1]

    parser = parser if type(parser) is dict else PARSERS[parser]
    return {'leaf': copy(parser['leaf']), 'internal': copy(parser['internal'])}


# Interpret and represent the content of a node in newick format.

def prop_repr(prop):
    """Return a newick-acceptable representation of the given property."""
    ptype = type(prop)

    if ptype in [list, tuple, set, frozenset]:
        text = '|'.join(str(x) for x in prop)
    elif issubclass(ptype, dict):
        text = '|'.join(f'{x}-{y}' for x, y in prop.items())
    else:
        text = str(prop)

    for c in ':;(),[]=':
        text = text.replace(c, '_')

    return text


def content_repr(node, props=None, parser=None):
    """Return content of a node as represented in newick format."""
    parser = parser if type(parser) is dict else PARSERS[parser]
    prop0, prop1 = parser['leaf' if node.is_leaf else 'internal']

    # Shortcuts.
    p0_name, p0_write, p0_req = prop0['pname'], prop0['write'], prop0.get('req')
    p1_name, p1_write, p1_req = prop1['pname'], prop1['write'], prop1.get('req')

    p0_str = p0_write(node.props[p0_name]) if p0_name in node.props else ''
    p1_str = p1_write(node.props[p1_name]) if p1_name in node.props else ''

    assert p0_str or not p0_req, f'missing {p0_name} in node with: {node.props}'
    assert p1_str or not p1_req, f'missing {p1_name} in node with: {node.props}'

    props = props if props is not None else sorted(node.props)  # overwrite
    pairs_str = ':'.join('%s=%s' % (k, prop_repr(node.props[k])) for k in props
                         if k in node.props and k not in [p0_name, p1_name])

    return (p0_str + (f':{p1_str}' if p1_str else '') +     # p0:p1
            (f'[&&NHX:{pairs_str}]' if pairs_str else ''))  # [&&NHX:p2=x:p3=y]


def read_props(str text, long pos, is_leaf, dict parser, check_req):
    """Return the properties from the content of a node, and where it ends.

    Example (for the default format of a leaf node):
      'abc:123[&&NHX:x=foo]'  ->  {'name': 'abc', 'dist': 123, 'x': 'foo'}
    """
    prop0, prop1 = parser['leaf' if is_leaf else 'internal']

    # Shortcuts.
    p0_name, p0_read, p0_req = prop0['pname'], prop0['read'], prop0.get('req')
    p1_name, p1_read, p1_req = prop1['pname'], prop1['read'], prop1.get('req')

    props = {}  # will contain the properties extracted from the content string

    p0_str, pos = read_content(text, pos, endings=':[,);')

    try:
        assert not check_req or not p0_req or p0_str, 'missing required value'
        if p0_str:
            props[p0_name] = p0_read(p0_str)
    except (AssertionError, ValueError) as e:
        raise NewickError('parsing %r: %s' % (p0_str, e))

    try:
        if pos < len(text) and text[pos] == ':':
            pos = skip_spaces_and_comments(text, pos+1)
            p1_str, pos = read_content(text, pos, endings='[ ,);')
            props[p1_name] = p1_read(p1_str)
        elif check_req and p1_req:
            raise AssertionError('missing required value')
    except (AssertionError, ValueError) as e:
        raise NewickError('parsing %r: %s' % (p1_str, e))

    pos = skip_spaces_and_comments(text, pos)

    if text[pos] == '[':  # this can't be a comment since we just skipped those
        start = pos + 1
        pos = text.find(']', start)
        assert pos >= 0, 'unfinished extended props'
        props.update(get_extended_props(text[start:pos]))
        pos = skip_spaces_and_comments(text, pos + 1)  # after the "]"

    return props, pos


def get_extended_props(str text):
    """Return a dict with the properties extracted from the text in NHX format.

    Example: '&&NHX:x=foo:y=bar'  ->  {'x': 'foo', 'y': 'bar'}
    """
    try:
        assert text.startswith('&&NHX:'), 'unknown annotation -- not "&&NHX"'
        return dict(pair.split('=') for pair in text[len('&&NHX:'):].split(':'))
    except (AssertionError, ValueError) as e:
        raise NewickError('invalid NHX format (%s) in text %s' %
                          (e, repr_short(text)))


def repr_short(obj, max_len=50):
    """Return a representation of the given object, limited in length."""
    # To use for messages in exceptions.
    txt = repr(obj)
    return txt if len(txt) < max_len else txt[:max_len-10] + ' ... ' + txt[-5:]


# Parsing.

def load(fp, parser=None):
    return loads(fp.read().strip(), parser)


def loads(str text, parser=None, tree_class=Tree):
    """Return tree from its newick representation."""
    try:
        assert text.endswith(';'), 'text ends with no ";"'

        parser = parser if type(parser) is dict else PARSERS[parser]

        tree, pos = read_node(text, 0, parser, tree_class, check_req=False)
        # We set check_req=False because the formats requiring certain
        # fields mean it for all nodes but the root.

        assert pos == len(text) - 1, f'root node ends prematurely at {pos}'

        return tree

    except AssertionError as e:
        raise NewickError(str(e))


def read_node(str text, long pos, dict parser, tree_class=Tree, check_req=True):
    """Return a node and the position in the text where it ends."""
    pos = skip_spaces_and_comments(text, pos)

    if text[pos] == '(':  # node has children
        children, pos = read_nodes(text, pos, parser, tree_class)
    else:  # node is a leaf
        children = []

    props, pos = read_props(text, pos, not children, parser, check_req)

    return tree_class(props, children), pos


def read_nodes(str text, long pos, dict parser, tree_class=Tree):
    """Return a list of nodes and the position in the text where they end."""
    # text looks like '(a,b,c)', where any element can be a list of nodes
    nodes = []
    while pos < len(text) and text[pos] != ')':
        pos += 1  # advance from the separator: "(" or ","

        node, pos = read_node(text, pos, parser, tree_class)

        nodes.append(node)

    assert pos < len(text), 'nodes text ends missing a matching ")"'

    return nodes, pos+1  # it is +1 to advance from the closing ")"


def skip_spaces_and_comments(str text, long pos):
    """Return position in text after pos and all whitespaces and comments."""
    # text = '...  [this is a comment] node1...'
    #            ^-- pos               ^-- pos (returned)
    while pos < len(text) and text[pos] in ' \t\r\n[':
        if text[pos] == '[':
            start = pos
            if text[pos+1] == '&':  # special annotation
                return pos
            else:
                pos = text.find(']', pos+1)  # skip comment
                assert pos >= 0, f'unfinished comment at position {start}'
        pos += 1  # skip whitespace and comment endings

    return pos


def skip_content(str text, long pos, endings=',);'):
    """Return the position where the content ends."""
    pos = skip_spaces_and_comments(text, pos)

    if pos < len(text) and text[pos] in ["'", '"']:
        pos = skip_quoted_name(text, pos)

    while pos < len(text) and text[pos] not in endings:
        pos += 1

    return pos


def read_content(str text, long pos, endings=',);'):
    """Return content starting at position pos in text, and where it ends."""
    # text = '...(node_1:0.5[&&NHX:p=a],...'  ->  'node_1:0.5[&&NHX:p=a]'
    #             ^-- pos              ^-- pos (returned)
    start = pos
    pos = skip_content(text, pos, endings)
    return text[start:pos], pos


def skip_quoted_name(str text, long pos):
    """Return the position where a quoted name ends."""
    # text = "... 'node ''2'' in tree' ..."
    #             ^-- pos             ^-- pos (returned)
    start = pos
    q = text[start]  # quoting character (can be ' or ")

    while pos+1 < len(text):
        pos += 1

        if text[pos] == q:
            # Newick format escapes ' as '' (and we generalize to q -> qq)
            if pos+1 >= len(text) or text[pos+1] != q:
                return pos+1  # that was the closing quote
            else:
                pos += 1  # that was an escaped quote - skip

    raise NewickError('unfinished quoted name: %s' % repr_short(text[start:]))


def dumps(tree, props=None, parser=None, format_root_node=True, is_leaf_fn=None):
    """Return newick representation of the given tree."""
    node_str = ('' if tree.is_root and not format_root_node else
                content_repr(tree, props, parser))

    if tree.children and (not is_leaf_fn or not is_leaf_fn(tree)):
        children_str = ','.join(dumps(node, props, parser,
                                      format_root_node, is_leaf_fn).rstrip(';')
                                for node in tree.children)
        return f'({children_str}){node_str};'
    else:
        return f'{node_str};'


def dump(tree, fp, props=None, parser=None, format_root_node=True, is_leaf_fn=None):
    fp.write(dumps(tree, props, parser, format_root_node, is_leaf_fn))
    fp.write('\n')
