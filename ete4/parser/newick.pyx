""" Jordi's newick parser """
from ete4 import Tree


class NewickError(Exception):
    pass


LENGTH_FORMAT = '%g'  # format used to represent the length as a string


# Functions that depend on the tree being represented in Newick format.
def load(fp):
    return read_newick(fp.read().strip())


def read_newick(tree_text):
    "Return tree from its newick representation"
    if tree_text == '':
        return Tree()
    if tree_text[0] != '(':
        name, length, properties = get_content_fields(tree_text.rstrip(';'))
        t = Tree()
        t.name = name
        t.dist = length
        t.properties = properties
        return t

    if not tree_text.endswith(';'):
        raise NewickError('text ends with no ";"')

    if tree_text[0] == '(':
        nodes, pos = read_nodes(tree_text, 0)
    else:
        nodes, pos = [], 0

    content, pos = read_content(tree_text, pos)
    if pos != len(tree_text) - 1:
        raise NewickError(f'root node ends at position {pos}, before tree ends')

    t = Tree(content)
    t.children = nodes
    return  t


def read_nodes(nodes_text, int pos=0):
    "Return a list of nodes and the position in the text where they end"
    # nodes_text looks like '(a,b,c)', where any element can be a list of nodes
    if nodes_text[pos] != '(':
        raise NewickError('nodes text starts with no "("')

    nodes = []
    while nodes_text[pos] != ')':
        pos += 1
        if pos >= len(nodes_text):
            raise NewickError('nodes text ends missing a matching ")"')

        while nodes_text[pos] in ' \t\r\n':
            pos += 1  # skip whitespace

        if nodes_text[pos] == '(':
            children, pos = read_nodes(nodes_text, pos)
        else:
            children = []

        content, pos = read_content(nodes_text, pos)

        t = Tree(content)
        t.children = children
        nodes.append(t)

    return nodes, pos+1


def read_content(str text, int pos, endings=',);'):
    "Return content starting at position pos in the text, and where it ends"
    start = pos
    if pos < len(text) and text[pos] == "'":
        _, pos = read_quoted_name(text, pos)
    while pos < len(text) and text[pos] not in endings:
        pos += 1
    return text[start:pos], pos


def read_quoted_name(str text, int pos):
    "Return quoted name and the position where it ends"
    if pos >= len(text) or text[pos] != "'":
        raise NewickError(f'text at position {pos} does not start with "\'"')

    pos += 1
    start = pos
    while pos < len(text):
        if text[pos] == "'":
            # Newick format escapes ' as ''
            if pos+1 >= len(text) or text[pos+1] != "'":
                return text[start:pos].replace("''", "'"), pos+1
            pos += 2
        else:
            pos += 1

    raise NewickError(f'unfinished quoted name: {text[start:]}')


def get_content_fields(content):
    """Return name, length, properties from the content (as a newick) of a node

    Example:
      'abc:123[&&NHX:x=foo:y=bar]' -> ('abc', 123, {'x': 'foo', 'y': 'bar'})
    """
    cdef double length
    if content.startswith("'"):
        name, pos = read_quoted_name(content, 0)
    else:
        name, pos = read_content(content, 0, endings=':[')

    if pos < len(content) and content[pos] == ':':
        length_txt, pos = read_content(content, pos+1, endings='[')
        try:
            length = float(length_txt)
        except ValueError:
            raise NewickError('invalid number %r in %r' % (length_txt, content))
    else:
        length = -1

    if pos < len(content) and content[pos] == '[':
        properties = get_properties(content[pos:])
    elif pos >= len(content):
        properties = {}
    else:
        raise NewickError('malformed content: %r' % content)

    return name, length, properties


def get_properties(text):
    """Return a dict with the properties extracted from the text in NHX format

    Example: '[&&NHX:x=foo:y=bar]' -> {'x': 'foo', 'y': 'bar'}
    """
    try:
        assert text.startswith('[&&NHX:') and text.endswith(']'), \
            'properties not contained between "[&&NHX:" and "]"'
        pairs = text[len('[&&NHX:'):-1].split(':')
        return dict(pair.split('=') for pair in pairs)
    except (AssertionError, ValueError) as e:
        raise NewickError('invalid NHX format (%s) in text %r' % (e, text))


def content_repr(node):
    "Return content of a node as represented in newick format"
    length_str = f':{LENGTH_FORMAT}' % node.dist if node.dist >= 0 else ''
    pairs_str = ':'.join('%s=%s' % kv for kv in node.properties.items())
    props_str = f'[&&NHX:{pairs_str}]' if pairs_str else ''
    return quote(node.name) + length_str + props_str


def quote(name, escaped_chars=" \t\r\n()[]':;,"):
    "Return the name quoted if it has any characters that need escaping"
    if any(c in name for c in escaped_chars):
        return "'%s'" % name.replace("'", "''")  # ' escapes to '' in newicks
    else:
        return name


def write_newick(tree):
    "Return newick representation from tree"
    children_text = ','.join(write_newick(node).rstrip(';') for node in tree.children)
    return (f'({children_text})' if children_text else '') + tree.content + ';'


def dump(tree, fp):
    fp.write(write_newick(tree))
