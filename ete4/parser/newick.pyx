"""
Parser for trees represented in newick format.
"""

# See https://en.wikipedia.org/wiki/Newick_format

from ete4.coretype.tree import Tree


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

# Common IO parts in property dicts.
STRING_IO = {'read': unquote, 'write': quote}
NUMBER_IO = {'read': float,   'write': lambda x: '%g' % float(x)}

# Common property dicts.
NAME    = dict(STRING_IO, pname='name')
DIST    = dict(NUMBER_IO, pname='dist')
SUPPORT = dict(NUMBER_IO, pname='support')

# A "parser dict" says, for leaf and internal nodes, what 'p0:p1' means
# (which properties they are, including how to read and write them).

PARSER_DEFAULT = {
    'leaf':     [NAME, DIST],  # ((name:dist)x:y);
    'internal': [NAME, DIST],  # ((x:y)name:dist);
}

# This part is only used to read the old-fashioned int formats.
NAME_REQ = dict(NAME, req=True)  # value required
DIST_REQ = dict(DIST, req=True)
SUPPORT_REQ = dict(SUPPORT, req=True)
EMPTY = {'pname': '',
         'read': lambda x: error(f'parser expected empty field but got: {x}'),
         'write': lambda x: ''}
INT_PARSERS = {  # parsers corresponding to old-style integers
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
}

def make_parser(number=1, name='%s', dist='%g', support='%g'):
    """Return "int" parser changing the format of name, dist or support."""
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

    parser = INT_PARSERS[number]
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
    parser = parser or PARSER_DEFAULT
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


def get_props(content, is_leaf, parser=None):
    """Return the properties from the content (as a newick) of a node.

    Example (for the default format of a leaf node):
      'abc:123[&&NHX:x=foo]'  ->  {'name': 'abc', 'dist': 123, 'x': 'foo'}
    """
    parser = parser or PARSER_DEFAULT
    prop0, prop1 = parser['leaf' if is_leaf else 'internal']

    # Shortcuts.
    p0_name, p0_read, p0_req = prop0['pname'], prop0['read'], prop0.get('req')
    p1_name, p1_read, p1_req = prop1['pname'], prop1['read'], prop1.get('req')

    props = {}  # will contain the properties extracted from the content string

    p0_str, pos = read_content(content, 0, endings=':[')

    try:
        assert p0_str or not p0_req, 'missing required value'
        if p0_str:
            props[p0_name] = p0_read(p0_str)
    except (AssertionError, ValueError) as e:
        raise NewickError('parsing 1st position of %r: %s' % (content, e))

    try:
        if pos < len(content) and content[pos] == ':':
            pos = skip_spaces_and_comments(content, pos+1)
            p1_str, pos = read_content(content, pos, endings='[ ')
            props[p1_name] = p1_read(p1_str)
        elif p1_req:
            raise AssertionError('missing required value')
    except (AssertionError, ValueError) as e:
        raise NewickError('parsing 2nd position of %r: %s' % (content, e))

    pos = skip_spaces_and_comments(content, pos)

    if pos < len(content) and content[pos] == '[':
        pos_end = content.find(']', pos+1)
        props.update(get_extended_props(content[pos+1:pos_end]))
    elif pos < len(content):
        raise NewickError('malformed content: %s' % repr_short(content))

    return props


def get_extended_props(text):
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


def loads(tree_text, parser=None, tree_class=Tree):
    """Return tree from its newick representation."""
    assert type(tree_text) == str, 'newick is not a string'

    if not tree_text.endswith(';'):
        raise NewickError('text ends with no ";"')

    if tree_text[0] == '(':
        nodes, pos = read_nodes(tree_text, parser, 0, tree_class)
    else:
        nodes, pos = [], 0

    content, pos = read_content(tree_text, pos)
    if pos != len(tree_text) - 1:
        raise NewickError(f'root node ends at position {pos}, before tree ends')

    props = get_props(content, not nodes, parser) if content else {}

    return tree_class(props, nodes)


def read_nodes(nodes_text, parser, pos=0, tree_class=Tree):
    """Return a list of nodes and the position in the text where they end."""
    # nodes_text looks like '(a,b,c)', where any element can be a list of nodes
    if nodes_text[pos] != '(':
        raise NewickError('nodes text starts with no "("')

    nodes = []
    while nodes_text[pos] != ')':
        pos += 1
        if pos >= len(nodes_text):
            raise NewickError('nodes text ends missing a matching ")"')

        pos = skip_spaces_and_comments(nodes_text, pos)

        if nodes_text[pos] == '(':  # this element is a list of nodes
            children, pos = read_nodes(nodes_text, parser, pos, tree_class)
        else:  # this element is a leaf
            children = []

        content, pos = read_content(nodes_text, pos)

        nodes.append(tree_class(get_props(content, not children, parser),
                                children))

    return nodes, pos+1


def skip_spaces_and_comments(text, pos):
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
                if pos < 0:
                    raise NewickError(f'unfinished comment at position {start}')
        pos += 1  # skip whitespace and comment endings

    return pos


def read_content(text, pos, endings=',);'):
    """Return content starting at position pos in text, and where it ends."""
    # text = '...(node_1:0.5[&&NHX:p=a],...'  ->  'node_1:0.5[&&NHX:p=a]'
    #             ^-- pos              ^-- pos (returned)
    start = pos

    pos = skip_spaces_and_comments(text, pos)

    if pos < len(text) and text[pos] in ["'", '"']:
        pos = skip_quoted_name(text, pos)

    while pos < len(text) and text[pos] not in endings:
        pos += 1

    return text[start:pos], pos


def skip_quoted_name(text, pos):
    """Return the position where a quoted name ends."""
    # text = "... 'node ''2'' in tree' ..."
    #             ^-- pos             ^-- pos (returned)
    if pos >= len(text) or text[pos] not in ["'", '"']:
        raise NewickError(f'text at position {pos} does not start with quote')

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
