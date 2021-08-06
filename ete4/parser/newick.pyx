# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
#
#                     ABOUT THE ETE PACKAGE
#                     =====================
#
# ETE is distributed under the GPL copyleft license (2008-2015).
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in
# the toolkit may be available in the documentation.
#
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
#
# #END_LICENSE#############################################################
""" Jordi's newick parser """
import os
from re import sub

from ete4 import Tree


class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        if value is None:
            value = ''
        value += "\nYou may want to check the input Newick format."
        Exception.__init__(self, value)

DEFAULT_FLOAT_FORMATTER = "%0.6g"
DEFAULT_NAME_FORMATTER = "%s"

FLOAT_FORMATTER = DEFAULT_FLOAT_FORMATTER
DIST_FORMATTER = FLOAT_FORMATTER
SUPPORT_FORMATTER = FLOAT_FORMATTER
NAME_FORMATTER = DEFAULT_NAME_FORMATTER

_ILLEGAL_NEWICK_CHARS = ":;(),\[\]\t\n\r="
NW_FORMAT = {
  #       leaf name                 leaf dist             internal support/name          internal dist
  0: [['name', str, True],    ["dist", float, True],     ['support', float, True],   ["dist", float, True]],  # Flexible with support
  1: [['name', str, True],    ["dist", float, True],     ['name', str, True],        ["dist", float, True]],  # Flexible with internal node names
  2: [['name', str, False],   ["dist", float, False],    ['support', float, False],  ["dist", float, False]], # Strict with support values
  3: [['name', str, False],   ["dist", float, False],    ['name', str, False],       ["dist", float, False]], # Strict with internal node names
  4: [['name', str, False],   ["dist", float, False],    [None, None, False],        [None, None, False]],
  5: [['name', str, False],   ["dist", float, False],    [None, None, False],        ["dist", float, False]],
  6: [['name', str, False],   [None, None, False],       [None, None, False],        ["dist", float, False]],
  7: [['name', str, False],   ["dist", float, False],    ["name", str, False],       [None, None, False]],    # all names
  8: [['name', str, False],   [None, None, False],       ["name", str, False],       [None, None, False]],    # leaf names
  9: [['name', str, False],   [None, None, False],       [None, None, False],        [None, None, False]],    # Only topology with node names
  100: [[None, None, False],  [None, None, False],       [None, None, False],        [None, None, False]]     # Only Topology
}


def set_formatters(float_formatter=None, dist_formatter=None,
                   support_formatter=None, name_formatter=None):
    ''' Set the conversion format used to represent float distances and support
    values in the newick representation of trees.
    For example, use set_float_format('%0.32f') to specify 32 decimal numbers
    when exporting node distances and bootstrap values.
    Scientific notation (%e) or any other custom format is allowed. The
    formatter string should not contain any character that may break newick
    structure (i.e.: ":;,()")
    '''
    if float_formatter:
        global FLOAT_FORMATTER
        FLOAT_FORMATTER = float_formatter

    global DIST_FORMATTER, SUPPORT_FORMATTER, NAME_FORMATTER
    DIST_FORMATTER = dist_formatter or FLOAT_FORMATTER
    SUPPORT_FORMATTER = support_formatter or FLOAT_FORMATTER
    NAME_FORMATTER = name_formatter or DEFAULT_NAME_FORMATTER


def get_newick_txt(newick):
    # try to determine whether the file exists.
    # For very large trees, if newick contains the content of the tree,
    # rather than a file name, this may fail, at least on Windows, 
    # because the os fails to stat the file content, deeming it
    # too long for testing with os.path.exists.  
    # This raises a ValueError with description
    # "stat: path too long for Windows".  
    # This is described in issue #258
    try:
        file_exists = os.path.exists(newick)
    except ValueError:      # failed to stat
        file_exists = False

    # if newick refers to a file, read it from file
    # otherwise, regard it as a Newick content string.
    if file_exists:
        if newick.endswith('.gz'):
            import gzip
            with gzip.open(newick) as INPUT:
                nw = INPUT.read()
        else:
            with open(newick) as INPUT:
                nw = INPUT.read()
    else:
        nw = newick
    return str(nw).strip()


def read_newick(nw, root_node=None):
    """ Reads a newick tree from either a string or a file, and returns
    an ETE tree structure.
    A previously existent node object can be passed as the root of the
    tree, which means that all its new children will belong to the same
    class as the root. This allows to work with custom TreeNode
    objects.
    You can also take advantage from this behaviour to concatenate
    several tree structures.
    """
    # Retrieve file content nw is an existant file name
    newick = get_newick_txt(nw)
    t = root_node or Tree()
    if newick == '' or newick[0] != '(':
        # Get content from incomplete newick string
        fill_node_content(t, newick)
    else:
        # Parse complete newick
        read_newick_from_string(newick, t)
    return t


def read_newick_from_string(tree_text, root_node):
    "Return tree from its newick representation"
    if not tree_text.endswith(';'):
        raise NewickError('text ends with no ";"')

    if tree_text[0] == '(':
        nodes, pos = read_nodes(tree_text, root_node.__class__, 0)
    else:
        nodes, pos = [], 0

    content, pos = read_content(tree_text, pos)
    if pos != len(tree_text) - 1:
        raise NewickError(f'root node ends at position {pos}, before tree ends')

    t = root_node
    fill_node_content(t, content)
    t.add_children(nodes)

    return t


def read_nodes(nodes_text, NewNode, int pos=0):
    "Return a list of nodes and the position in the text where they end"
    # nodes_text looks like '(a,b,c)', where any element can be a list of nodes
    if nodes_text[pos] != '(':
        raise NewickError('nodes text starts with no "("')

    nodes = []
    while nodes_text[pos] != ')':
        pos += 1
        if pos >= len(nodes_text):
            raise NewickError('nodes text ends missing a matching ")"')

        pos = skip_spaces_and_comments(nodes_text, pos)

        if nodes_text[pos] == '(':
            children, pos = read_nodes(nodes_text, NewNode, pos)
        else:
            children = []

        content, pos = read_content(nodes_text, pos)

        t = NewNode(content)
        t.add_children(children)
        nodes.append(t)

    return nodes, pos+1


def fill_node_content(node, newick, children=None):
    """Fill TreeNode with 'content' information: a tuple
    consisting of name, dist and properties. 
    Such information is extracted from an incomplete newick text field
    In addition, already computed children may be added to the TreeNode object
    """
    content = get_content_fields(newick.rstrip(';'))
    name, dist, properties = content
    node.name = name
    node.dist = dist
    # Avoid removing preexisting properties
    # while overriding default values
    node.props = { **node.props, **properties }
    
    if children:
        node.add_children(children)

    return node


def skip_spaces_and_comments(text, int pos):
    "Return position in text after pos and after all whitespaces and comments"
    while pos < len(text) and text[pos] in ' \t\r\n[':
        if text[pos] == '[':
            if text[pos+1] == '&':  # special annotation
                return pos
            else:
                pos = text.find(']', pos+1)  # skip comment
        pos += 1  # skip whitespace and comment endings
    return pos


def read_content(str text, int pos, endings=',);'):
    "Return content starting at position pos in the text, and where it ends"
    start = pos
    if pos < len(text) and text[pos] == "'":
        _, pos = read_quoted_name(text, pos)
    stop = True
    while pos < len(text) and (not stop or text[pos] not in endings):
        if text[pos] == '[':
            stop = False
        elif text[pos] == ']':
            stop = True
        pos += 1
    return text[start:pos], pos


def read_quoted_name(str text, int pos):
    "Return quoted name and the position where it ends"
    if pos >= len(text) or text[pos] not in ("'", '"'):
        raise NewickError(f'text at position {pos} does not start with "\'"\
                            nor "\"')

    pos += 1
    start = pos
    while pos < len(text):
        if text[pos] in ("'", '"'):
            # Newick format escapes ' as ''
            if pos+1 >= len(text) or text[pos+1] != "'":
                return text[start:pos].replace("''", "'"), pos
            pos += 2
        else:
            pos += 1

    raise NewickError(f'unfinished quoted name: {text[start:]}')


def get_content_fields(content):
    """Return name, dist, properties from the content (as a newick) of a node

    Example:
      'abc:123[&&NHX:x=foo:y=bar]' -> ('abc', 123, {'x': 'foo', 'y': 'bar'})
    """
    cdef double dist
    if content.startswith(("'", '"')):
        name, pos = read_quoted_name(content, 0)
        pos = skip_spaces_and_comments(content, pos+1)
    else:
        name, pos = read_content(content, 0, endings=':[')

    if pos < len(content) and content[pos] == ':':
        pos = skip_spaces_and_comments(content, pos+1)
        dist_txt, pos = read_content(content, pos, endings='[ ')
        try:
            dist = float(dist_txt)
        except ValueError:
            raise NewickError('invalid number %r in %r' % (dist_txt, content))
    else:
        dist = -1

    if pos < len(content) and content[pos] == '[':
        pos_end = content.find(']', pos+1)
        properties = get_properties(content[pos+1:pos_end])
    elif pos >= len(content):
        properties = {}
    else:
        raise NewickError('malformed content: %r' % content)

    return name, dist, properties


def get_properties(text):
    """Return a dict with the properties extracted from the text in NHX format

    Example: '&&NHX:x=foo:y=bar' -> {'x': 'foo', 'y': 'bar'}
    """
    try:
        assert text.startswith('&&NHX:'), 'unknown annotation (not "&&NHX")'
        return dict(pair.split('=') for pair in text[len('&&NHX:'):].split(':'))
    except (AssertionError, ValueError) as e:
        raise NewickError('invalid NHX format (%s) in text %r' % (e, text))


def content_repr(node, format=0, properties=[], quoted_names=False):
    "Return content of a node as represented in specified newick format"
    # Empty list includes all properties
    properties = list(node.props.keys())\
            if properties == [] else (properties or [])

    if node.is_leaf():
        name = NW_FORMAT[format][0][0]
        dist = NW_FORMAT[format][1][0]
        name_type = NW_FORMAT[format][0][1]
        dist_type = NW_FORMAT[format][1][1]
        flexible = NW_FORMAT[format][0][2]
    else:
        name = NW_FORMAT[format][2][0]
        dist = NW_FORMAT[format][3][0]
        name_type = NW_FORMAT[format][2][1]
        dist_type = NW_FORMAT[format][3][1]
        flexible = NW_FORMAT[format][2][2]

    # NAME/SUPPORT FORMATTING
    name_str = ''
    support_str = ''
    if name_type == str:
        if node.name:
            name_str = f'{NAME_FORMATTER}' % str(node.name)
        elif not flexible:
            name_str = f'{NAME_FORMATTER}' % 'NoName'

        # Quote name or remove newick-illegal characters
        if quoted_names:
            # TO CONSIDER: use quote() instead of quoted_names argument
            name_str = "'" + name_str + "'"
        else:
            name_str = sub(f'[{_ILLEGAL_NEWICK_CHARS}]', '_', name_str)

    elif name_type == float:  # support value
        support_str = f'{SUPPORT_FORMATTER}' % float(node.support)
        # Do not write redundant information
        if 'support' in properties:
            properties.remove('support')
    else:  # name_type == None
        name_str = ''

    # DIST FORMATTING
    dist_str = f':{DIST_FORMATTER}' % float(node.dist) \
            if (node.dist >= 0 and dist_type != None) else ''

    # PROPERTIES FORMATTING
    pairs_str = ':'.join('%s=%s' % (k, node.props.get(k)) 
                                    for k in properties
                                    if node.props.get(k))
    props_str = f'[&&NHX:{pairs_str}]' if pairs_str else ''

    return (name_str or support_str) + dist_str + props_str


def quote(name, escaped_chars=" \t\r\n()[]':;,"):
    "Return the name quoted if it has any characters that need escaping"
    if any(c in name for c in escaped_chars):
        return "'%s'" % name.replace("'", "''")  # ' escapes to '' in newicks
    else:
        return name


def write_newick(tree, format=0, properties=[], quoted_names=False):
    "Return newick representation from tree"
    children_text = ','.join(write_newick(node, format, properties=properties,
                                          quoted_names=quoted_names)\
                       .rstrip(';') for node in tree.children)
    content_text = content_repr(tree, format=format, properties=properties,
                                quoted_names=quoted_names)
    return (f'({children_text})' if tree.children else '') + content_text + ';'


def print_supported_formats():
    from ete4.smartview.ete.gardening import standardize
    t = Tree()
    t.populate(4, "ABCDEFGHI")
    print(t)
    for f in NW_FORMAT:
        print(' '.join(["Format", str(f),"=", 
            write_newick(t, format=f, properties=None, quoted_names=False)]))
