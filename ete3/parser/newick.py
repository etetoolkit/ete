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
from __future__ import absolute_import
from __future__ import print_function
import re
import os
import six
from six.moves import map

__all__ = ["read_newick", "write_newick", "print_supported_formats"]

ITERABLE_TYPES = set([list, set, tuple, frozenset])

# Regular expressions used for reading newick format
_ILEGAL_NEWICK_CHARS = ":;(),\[\]\t\n\r="
_NON_PRINTABLE_CHARS_RE = "[\x00-\x1f]+"

_NHX_RE = "\[&&NHX:[^\]]*\]"
_FLOAT_RE = "\s*[+-]?\d+\.?\d*(?:[eE][-+]?\d+)?\s*"
#_FLOAT_RE = "[+-]?\d+\.?\d*"
#_NAME_RE = "[^():,;\[\]]+"
_NAME_RE = "[^():,;]+?"

# thanks to: http://stackoverflow.com/a/29452781/1006828
_QUOTED_TEXT_RE = r"""((?=["'])(?:"[^"\\]*(?:\\[\s\S][^"\\]*)*"|'[^'\\]*(?:\\[\s\S][^'\\]*)*'))"""
#_QUOTED_TEXT_RE = r"""["'](?:(?<=")[^"\\]*(?s:\\.[^"\\]*)*"|(?<=')[^'\\]*(?s:\\.[^'\\]*)*')""]"]"""
#_QUOTED_TEXT_RE = r"""(?=["'])(?:"[^"\\]*(?:\\[\s\S][^"\\]*)*"|'[^'\\]*(?:\\[\s\S][^'\\]*)*')]"]")"]"""

_QUOTED_TEXT_PREFIX='ete3_quotref_'

DEFAULT_DIST = 1.0
DEFAULT_NAME = ''
DEFAULT_SUPPORT = 1.0
FLOAT_FORMATTER = "%0.6g"
#DIST_FORMATTER = ":"+FLOAT_FORMATTER
NAME_FORMATTER = "%s"

def set_float_format(formatter):
    ''' Set the conversion format used to represent float distances and support
    values in the newick representation of trees.

    For example, use set_float_format('%0.32f') to specify 32 decimal numbers
    when exporting node distances and bootstrap values.

    Scientific notation (%e) or any other custom format is allowed. The
    formatter string should not contain any character that may break newick
    structure (i.e.: ":;,()")

    '''
    global FLOAT_FORMATTER
    FLOAT_FORMATTER = formatter
    #DIST_FORMATTER = ":"+FLOAT_FORMATTER

# Allowed formats. This table is used to read and write newick using
# different convenctions. You can also add your own formats in an easy way.
#
#
# FORMAT: [[LeafAttr1, LeafAttr1Type, Strict?], [LeafAttr2, LeafAttr2Type, Strict?],\
#    [InternalAttr1, InternalAttr1Type, Strict?], [InternalAttr2, InternalAttr2Type, Strict?]]
#
# Attributes are placed in the newick as follows:
#
# .... ,LeafAttr1:LeafAttr2)InternalAttr1:InternalAttr2 ...
#
#
#           /-A
# -NoName--|
#          |          /-B
#           \C-------|
#                    |          /-D
#                     \E-------|
#                               \-G
#
# Format 0 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)1.000000:0.642905)1.000000:0.567737);
# Format 1 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)E:0.642905)C:0.567737);
# Format 2 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)1.000000:0.642905)1.000000:0.567737);
# Format 3 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)E:0.642905)C:0.567737);
# Format 4 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)));
# Format 5 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729):0.642905):0.567737);
# Format 6 = (A:0.350596,(B:0.728431,(D:0.609498,G:0.125729)E)C);
# Format 7 = (A,(B,(D,G)E)C);
# Format 8 = (A,(B,(D,G)));
# Format 9 = (,(,(,)));

NW_FORMAT = {
  0: [['name', str, True],  ["dist", float, True],    ['support', float, True],   ["dist", float, True]], # Flexible with support
  1: [['name', str, True],  ["dist", float, True],    ['name', str, True],      ["dist", float, True]], # Flexible with internal node names
  2: [['name', str, False], ["dist", float, False],   ['support', float, False],  ["dist", float, False]],# Strict with support values
  3: [['name', str, False], ["dist", float, False],   ['name', str, False],     ["dist", float, False]], # Strict with internal node names
  4: [['name', str, False], ["dist", float, False],   [None, None, False],        [None, None, False]],
  5: [['name', str, False], ["dist", float, False],   [None, None, False],        ["dist", float, False]],
  6: [['name', str, False], [None, None, False],      [None, None, False],        ["dist", float, False]],
  7: [['name', str, False], ["dist", float, False],   ["name", str, False],       [None, None, False]],
  8: [['name', str, False], [None, None, False],      ["name", str, False],       [None, None, False]],
  9: [['name', str, False], [None, None, False],      [None, None, False],        [None, None, False]], # Only topology with node names
  100: [[None, None, False],  [None, None, False],      [None, None, False],        [None, None, False]] # Only Topology
}


def format_node(node, node_type, format, dist_formatter=None,
                support_formatter=None, name_formatter=None,
                quoted_names=False):
    if dist_formatter is None: dist_formatter = FLOAT_FORMATTER
    if support_formatter is None: support_formatter = FLOAT_FORMATTER
    if name_formatter is None: name_formatter = NAME_FORMATTER

    if node_type == "leaf":
        container1 = NW_FORMAT[format][0][0] # name
        container2 = NW_FORMAT[format][1][0] # dists
        converterFn1 = NW_FORMAT[format][0][1]
        converterFn2 = NW_FORMAT[format][1][1]
        flexible1 = NW_FORMAT[format][0][2]
    else:
        container1 = NW_FORMAT[format][2][0] #support/name
        container2 = NW_FORMAT[format][3][0] #dist
        converterFn1 = NW_FORMAT[format][2][1]
        converterFn2 = NW_FORMAT[format][3][1]
        flexible1 = NW_FORMAT[format][2][2]

    if converterFn1 == str:
        try:
            if not quoted_names:
                FIRST_PART = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                                    str(getattr(node, container1)))
            else:
                FIRST_PART = str(getattr(node, container1))
            if not FIRST_PART and container1 == 'name' and not flexible1:
                FIRST_PART = "NoName"

        except (AttributeError, TypeError):
            FIRST_PART = "?"

        FIRST_PART = name_formatter %FIRST_PART
        if quoted_names:
            #FIRST_PART = '"%s"' %FIRST_PART.decode('string_escape').replace('"', '\\"')
            FIRST_PART = '"%s"' %FIRST_PART

    elif converterFn1 is None:
        FIRST_PART = ""
    else:
        try:
            FIRST_PART = support_formatter %(converterFn2(getattr(node, container1)))
        except (ValueError, TypeError):
            FIRST_PART = "?"

    if converterFn2 == str:
        try:
            SECOND_PART = ":"+re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                                  str(getattr(node, container2)))
        except (ValueError, TypeError):
            SECOND_PART = ":?"
    elif converterFn2 is None:
        SECOND_PART = ""
    else:
        try:
            #SECOND_PART = ":%0.6f" %(converterFn2(getattr(node, container2)))
            SECOND_PART = ":%s" %(dist_formatter %(converterFn2(getattr(node, container2))))
        except (ValueError, TypeError):
            SECOND_PART = ":?"

    return "%s%s" %(FIRST_PART, SECOND_PART)


def print_supported_formats():
    from ..coretype.tree import TreeNode
    t = TreeNode()
    t.populate(4, "ABCDEFGHI")
    print(t)
    for f in NW_FORMAT:
        print("Format", f,"=", write_newick(t, features=None, format=f))

class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        if value is None:
            value = ''
        value += "\nYou may want to check other newick loading flags like 'format' or 'quoted_node_names'."
        Exception.__init__(self, value)

def read_newick(newick, root_node=None, format=0, quoted_names=False):
    """ Reads a newick tree from either a string or a file, and returns
    an ETE tree structure.

    A previously existent node object can be passed as the root of the
    tree, which means that all its new children will belong to the same
    class as the root(This allows to work with custom TreeNode
    objects).

    You can also take advantage from this behaviour to concatenate
    several tree structures.
    """

    if root_node is None:
        from ..coretype.tree import TreeNode
        root_node = TreeNode()

    if isinstance(newick, six.string_types):

        # try to determine whether the file exists.
        # For very large trees, if newick contains the content of the tree, rather than a file name,
        # this may fail, at least on Windows, because the os fails to stat the file content, deeming it
        # too long for testing with os.path.exists.  This raises a ValueError with description
        # "stat: path too long for Windows".  This is described in issue #258
        try:
            file_exists = os.path.exists(newick)
        except ValueError:      # failed to stat
            file_exists = False

        # if newick refers to a file, read it from file; otherwise, regard it as a Newick content string.
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


        matcher = compile_matchers(formatcode=format)
        nw = nw.strip()
        if not nw.startswith('(') and nw.endswith(';'):
            #return _read_node_data(nw[:-1], root_node, "single", matcher, format)
            return _read_newick_from_string(nw, root_node, matcher, format, quoted_names)
        elif not nw.startswith('(') or not nw.endswith(';'):
            raise NewickError('Unexisting tree file or Malformed newick tree structure.')
        else:
            return _read_newick_from_string(nw, root_node, matcher, format, quoted_names)

    else:
        raise NewickError("'newick' argument must be either a filename or a newick string.")

def _read_newick_from_string(nw, root_node, matcher, formatcode, quoted_names):
    """ Reads a newick string in the New Hampshire format. """

    if quoted_names:
        # Quoted text is mapped to references
        quoted_map = {}
        unquoted_nw = ''
        counter = 0
        for token in re.split(_QUOTED_TEXT_RE, nw):
            counter += 1
            if counter % 2 == 1 : # normal newick tree structure data
                unquoted_nw += token
            else: # quoted text, add to dictionary and replace with reference
                quoted_ref_id= _QUOTED_TEXT_PREFIX + str(int(counter/2))
                unquoted_nw += quoted_ref_id
                quoted_map[quoted_ref_id]=token[1:-1]  # without the quotes
        nw = unquoted_nw

    if not nw.startswith('(') and nw.endswith(';'):
        _read_node_data(nw[:-1], root_node, "single", matcher, format)
        if quoted_names:
            if root_node.name.startswith(_QUOTED_TEXT_PREFIX):
                root_node.name = quoted_map[root_node.name]
        return root_node

    if nw.count('(') != nw.count(')'):
        raise NewickError('Parentheses do not match. Broken tree structure?')

    # white spaces and separators are removed
    nw = re.sub("[\n\r\t]+", "", nw)

    current_parent = None
    # Each chunk represents the content of a parent node, and it could contain
    # leaves and closing parentheses.
    # We may find:
    # leaf, ..., leaf,
    # leaf, ..., leaf))),
    # leaf)), leaf, leaf))
    # leaf))
    # ) only if formatcode == 100

    for chunk in nw.split("(")[1:]:
        # If no node has been created so far, this is the root, so use the node.
        current_parent = root_node if current_parent is None else current_parent.add_child()

        subchunks = [ch.strip() for ch in chunk.split(",")]
        # We should expect that the chunk finished with a comma (if next chunk
        # is an internal sister node) or a subchunk containing closing parenthesis until the end of the tree.
        #[leaf, leaf, '']
        #[leaf, leaf, ')))', leaf, leaf, '']
        #[leaf, leaf, ')))', leaf, leaf, '']
        #[leaf, leaf, ')))', leaf), leaf, 'leaf);']
        if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
            raise NewickError('Broken newick structure at: %s' %chunk)

        # lets process the subchunks. Every closing parenthesis will close a
        # node and go up one level.
        for i, leaf in enumerate(subchunks):
            if leaf.strip() == '' and i == len(subchunks) - 1:
                continue # "blah blah ,( blah blah"
            closing_nodes = leaf.split(")")

            # first part after splitting by ) always contain leaf info
            _read_node_data(closing_nodes[0], current_parent, "leaf", matcher, formatcode)

            # next contain closing nodes and data about the internal nodes.
            if len(closing_nodes)>1:
                for closing_internal in closing_nodes[1:]:
                    closing_internal =  closing_internal.rstrip(";")
                    # read internal node data and go up one level
                    _read_node_data(closing_internal, current_parent, "internal", matcher, formatcode)
                    current_parent = current_parent.up

    # references in node names are replaced with quoted text before returning
    if quoted_names:
        for node in root_node.traverse():
            if node.name.startswith(_QUOTED_TEXT_PREFIX):
                node.name = quoted_map[node.name]

    return root_node

def _parse_extra_features(node, NHX_string):
    """ Reads node's extra data form its NHX string. NHX uses this
    format:  [&&NHX:prop1=value1:prop2=value2] """
    NHX_string = NHX_string.replace("[&&NHX:", "")
    NHX_string = NHX_string.replace("]", "")
    for field in NHX_string.split(":"):
        try:
            pname, pvalue = field.split("=")
        except ValueError as e:
            raise NewickError('Invalid NHX format %s' %field)
        node.add_feature(pname, pvalue)

def compile_matchers(formatcode):
    matchers = {}
    for node_type in ["leaf", "single", "internal"]:
        if node_type == "leaf" or node_type == "single":
            container1 = NW_FORMAT[formatcode][0][0]
            container2 = NW_FORMAT[formatcode][1][0]
            converterFn1 = NW_FORMAT[formatcode][0][1]
            converterFn2 = NW_FORMAT[formatcode][1][1]
            flexible1 = NW_FORMAT[formatcode][0][2]
            flexible2 = NW_FORMAT[formatcode][1][2]
        else:
            container1 = NW_FORMAT[formatcode][2][0]
            container2 = NW_FORMAT[formatcode][3][0]
            converterFn1 = NW_FORMAT[formatcode][2][1]
            converterFn2 = NW_FORMAT[formatcode][3][1]
            flexible1 = NW_FORMAT[formatcode][2][2]
            flexible2 = NW_FORMAT[formatcode][3][2]

        if converterFn1 == str:
            FIRST_MATCH = "("+_NAME_RE+")"
        elif converterFn1 == float:
            FIRST_MATCH = "("+_FLOAT_RE+")"
        elif converterFn1 is None:
            FIRST_MATCH = '()'

        if converterFn2 == str:
            SECOND_MATCH = "(:"+_NAME_RE+")"
        elif converterFn2 == float:
            SECOND_MATCH = "(:"+_FLOAT_RE+")"
        elif converterFn2 is None:
            SECOND_MATCH = '()'

        if flexible1 and node_type != 'leaf':
            FIRST_MATCH += "?"
        if flexible2:
            SECOND_MATCH += "?"


        matcher_str= '^\s*%s\s*%s\s*(%s)?\s*$' % (FIRST_MATCH, SECOND_MATCH, _NHX_RE)
        compiled_matcher = re.compile(matcher_str)
        matchers[node_type] = [container1, container2, converterFn1, converterFn2, compiled_matcher]

    return matchers

def _read_node_data(subnw, current_node, node_type, matcher, formatcode):
    """ Reads a leaf node from a subpart of the original newick
    tree """

    if node_type == "leaf" or node_type == "single":
        if node_type == "leaf":
            node = current_node.add_child()
        else:
            node = current_node
    else:
        node = current_node

    subnw = subnw.strip()

    if not subnw and node_type == 'leaf' and formatcode != 100:
        raise NewickError('Empty leaf node found')
    elif not subnw:
        return

    container1, container2, converterFn1, converterFn2, compiled_matcher = matcher[node_type]
    data = re.match(compiled_matcher, subnw)
    if data:
        data = data.groups()
        # This prevents ignoring errors even in flexible nodes:
        if subnw and data[0] is None and data[1] is None and data[2] is None:
            raise NewickError("Unexpected newick format '%s'" %subnw)

        if data[0] is not None and data[0] != '':
            node.add_feature(container1, converterFn1(data[0].strip()))

        if data[1] is not None and data[1] != '':
            node.add_feature(container2, converterFn2(data[1][1:].strip()))

        if data[2] is not None \
                and data[2].startswith("[&&NHX"):
            _parse_extra_features(node, data[2])
    else:
        raise NewickError("Unexpected newick format '%s' " %subnw[0:50])
    return

def write_newick(rootnode, features=None, format=1, format_root_node=True,
                 is_leaf_fn=None, dist_formatter=None, support_formatter=None,
                 name_formatter=None, quoted_names=False):
    """ Iteratively export a tree structure and returns its NHX
    representation. """
    newick = []
    leaf = is_leaf_fn if is_leaf_fn else lambda n: not bool(n.children)
    for postorder, node in rootnode.iter_prepostorder(is_leaf_fn=is_leaf_fn):
        if postorder:
            newick.append(")")
            if node.up is not None or format_root_node:
                newick.append(format_node(node, "internal", format,
                                          dist_formatter=dist_formatter,
                                          support_formatter=support_formatter,
                                          name_formatter=name_formatter,
                                          quoted_names=quoted_names))
                newick.append(_get_features_string(node, features))
        else:
            if node is not rootnode and node != node.up.children[0]:
                newick.append(",")

            if leaf(node):
                newick.append(format_node(node, "leaf", format,
                                          dist_formatter=dist_formatter,
                                          support_formatter=support_formatter,
                                          name_formatter=name_formatter,
                                          quoted_names=quoted_names))
                newick.append(_get_features_string(node, features))
            else:
                newick.append("(")

    newick.append(";")
    return ''.join(newick)

def _get_features_string(self, features=None):
    """ Generates the extended newick string NHX with extra data about
    a node. """
    string = ""
    if features is None:
        features = []
    elif features == []:
        features = sorted(self.features)

    for pr in features:
        if hasattr(self, pr):
            raw = getattr(self, pr)
            if type(raw) in ITERABLE_TYPES:
                raw = '|'.join(map(str, raw))
            elif type(raw) == dict:
                raw = '|'.join(map(lambda x,y: "%s-%s" %(x, y), six.iteritems(raw)))
            elif type(raw) == str:
                pass
            else:
                raw = str(raw)

            value = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                             raw)
            if string != "":
                string +=":"
            string +="%s=%s"  %(pr, str(value))
    if string != "":
        string = "[&&NHX:"+string+"]"

    return string
