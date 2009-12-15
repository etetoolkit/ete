# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
import re
import os

__all__ = ["read_newick", "write_newick", "print_supported_formats"]

# Regular expressions used for reading newick format
_ILEGAL_NEWICK_CHARS = ":;(),\[\]\t\n\r="
_NHX_RE = "\[&&NHX:[^\]]*\]"
_FLOAT_RE = "[+-]?\d+\.?\d*"
_NAME_RE = "[^():,;\[\]]+"

DEFAULT_DIST = 1.0
DEFAULT_NAME = ''
DEFAULT_SUPPORT = 1.0


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


def format_node(node, node_type, format):
    if node_type == "leaf":
        container1 = NW_FORMAT[format][0][0]
        container2 = NW_FORMAT[format][1][0]
        converterFn1 = NW_FORMAT[format][0][1]
        converterFn2 = NW_FORMAT[format][1][1]
    else:
        container1 = NW_FORMAT[format][2][0]
        container2 = NW_FORMAT[format][3][0]
        converterFn1 = NW_FORMAT[format][2][1]
        converterFn2 = NW_FORMAT[format][3][1]

    if converterFn1 == str:
        try:
            FIRST_PART = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                                  str(getattr(node, container1)))
        except (AttributeError, TypeError):
            FIRST_PART = "?"

    elif converterFn1 is None:
        FIRST_PART = ""
    else:
        try:
            FIRST_PART =  "%0.6f" %(converterFn2(getattr(node, container1)))
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
            SECOND_PART = ":%0.6f" %(converterFn2(getattr(node, container2)))
        except (ValueError, TypeError):
            SECOND_PART = ":?"

    return "%s%s" %(FIRST_PART, SECOND_PART)

# Used to write into specific formats
def node2leafformat(node, format):
    safe_name = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                             str(getattr(node, "name")))

    if format == 0 or format == 1 or format == 2 or format ==3:
        return "%s:%0.6f" %(safe_name, node.dist)
    elif format == 4 or format == 7:
        return ":%0.6f" %(node.dist)
    elif format == 5 or format == 6:
        return "%s" %(safe_name)

def node2internalformat(node, format):
    safe_name = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                             str(getattr(node, "name")))
    if format == 0 or format == 1:
        return "%0.6f:%0.6f" %(node.support, node.dist)
    elif format == 2:
        return "%s:%0.6f" %(safe_name, node.dist)
    elif format == 3 or format == 4:
        return ":%0.6f" %(node.dist)
    elif format == 5:
        return "%s" %(safe_name)
    elif format == 6 or format == 7:
        return ""

def print_supported_formats():
    from ete_dev.coretype.tree import TreeNode
    t = TreeNode()
    t.populate(4, "ABCDEFGHI")
    print t
    for f in NW_FORMAT:
        print "Format", f,"=", write_newick(t, features=None, format=f)

class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    pass

def read_newick(newick, root_node=None, format=0):
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
        from ete_dev.coretype.tree import TreeNode
        root_node = TreeNode()

    if type(newick) == str:

        if os.path.exists(newick):
            nw = open(newick, 'rU').read()
        else:
            nw = newick
        nw = nw.strip()
        if not nw.startswith('(') or not nw.endswith(';'):
            raise NewickError, 'Unexisting tree file or Malformed newick tree structure.'
        return _read_newick_from_string(nw, root_node, format)
    else:
        raise NewickError, \
            "'newick' argument must be either a filename or a newick string."

def _read_newick_from_string(nw, root_node, format):
    """ Reads a newick string in the New Hampshire format. """

    if nw.count('(') != nw.count(')'):
        raise NewickError, 'Parentheses do not match. Broken tree structure'

    # white spaces and separators are removed
    nw = re.sub("\n", "", nw)
    nw = re.sub("\r", "", nw)
    nw = re.sub("\t", "", nw)

    current_parent = None


    # Ok, this is my own way of reading newick structures. I find it
    # more flexible and elegant than other docummented methods. Don't
    # know if I'm loosing much efficiency. It Starts by splitting the
    # structure using open parentheses. Each of the resulting chunks
    # represent an internal node. So for each chunk I create a new node
    # that hungs from the current parent node.  Each internal node chunk
    # may contain information about terminal nodes hanging from the
    # internal and clossing parenthessis (closing previously opened
    # internal nodes).
    #
    # Enjoy.
    # by JHC ;)

    # Skip the first chunk. It is always == ''
    for internal_node in nw.split("(")[1:]:
        # If this is the root of tree, use the root_node instead of
        # creating it, otherwise make a new one.
        if current_parent is None:
            current_parent = root_node
        else:
            current_parent = current_parent.add_child()
        # We can only find leaf nodes within this chunk, since rest of
        # internal nodes will be in the next newick chunks
        possible_leaves = internal_node.split(",")
        for i, leaf in enumerate(possible_leaves):
            # Any resulting sub-chunk resulting from splitting by commas can
            # be considered (tpologically) as a child to the current parent
            # node. We only discard chunks if they are empty and in the last
            # possition, meaining that the next brother is not terminal bu
            # internal node (will be visited in the next newick chunk)
            if leaf.strip() == '' and i == len(possible_leaves)-1:
                continue
            # Leaf text strings may end with a variable number of clossing
            # parenthesis. For each ')' we read the information of the
            # current node, close it and go up one more node.
            clossing_nodes = leaf.split(")")
            # first par contain leaf info
            _read_node_data(clossing_nodes[0], current_parent, "leaf", format)
            # The next parts containg clossing nodes and info about the
            # internal nodes.
            if len(clossing_nodes)>1:
                for closing_internal in clossing_nodes[1:]:
                    if closing_internal.strip() ==";": continue
                    _read_node_data(closing_internal, current_parent, "internal", format)
                    current_parent = current_parent.up
    return root_node

def _parse_extra_features(node, NHX_string):
    """ Reads node's extra data form its NHX string. NHX uses this
    format:  [&&NHX:prop1=value1:prop2=value2] """
    NHX_string = NHX_string.replace("[&&NHX:", "")
    NHX_string = NHX_string.replace("]", "")
    for field in NHX_string.split(":"):
        try:
            pname, pvalue = field.split("=")
        except ValueError, e:
            print NHX_string, field.split("=")
            raise ValueError, e
        node.add_feature(pname, pvalue)

def _read_node_data(subnw, current_node, node_type,format):
    """ Reads a leaf node from a subpart of the original newick
    tree """

    if node_type == "leaf":
        node = current_node.add_child()
        container1 = NW_FORMAT[format][0][0]
        container2 = NW_FORMAT[format][1][0]
        converterFn1 = NW_FORMAT[format][0][1]
        converterFn2 = NW_FORMAT[format][1][1]
        flexible1 = NW_FORMAT[format][0][2]
        flexible2 = NW_FORMAT[format][1][2]
    else:
        node = current_node
        container1 = NW_FORMAT[format][2][0]
        container2 = NW_FORMAT[format][3][0]
        converterFn1 = NW_FORMAT[format][2][1]
        converterFn2 = NW_FORMAT[format][3][1]
        flexible1 = NW_FORMAT[format][2][2]
        flexible2 = NW_FORMAT[format][3][2]

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

    if flexible1:
        FIRST_MATCH += "?"
    if flexible2:
        SECOND_MATCH += "?"

    MATCH = '%s\s*%s\s*(%s)?' % (FIRST_MATCH, SECOND_MATCH, _NHX_RE)
    data = re.match(MATCH, subnw)
    if data:
        data = data.groups()
        if data[0] is not None and data[0] != '':
            node.add_feature(container1, converterFn1(data[0].strip()))

        if data[1] is not None and data[1] != '':
            node.add_feature(container2, converterFn2(data[1][1:].strip()))

        if data[2] is not None \
                and data[2].startswith("[&&NHX"):
            _parse_extra_features(node, data[2])
    else:
        raise NewickError, "Unexpected leaf node format:\n\t"+ subnw[0:50]
    return

def write_newick(node, features=[], format=1, _is_root=True):
    """ Recursively reads a tree structure and returns its NHX
    representation. """
    newick = ""
    if not node.children:
        safe_name = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                               str(getattr(node, "name")))

        newick += format_node(node, "leaf", format)
        newick += _get_features_string(node, features)
        return newick
    else:
        if node.children:
            newick+= "("
        for cnode in node.children:
            newick += write_newick(cnode, features, format=format,\
                                     _is_root = False)
            # After last child is processed, add closing string
            if cnode == node.children[-1]:
                newick += ")"
                if node.up is not None:
                    newick += format_node(node, "internal", format)
                newick += _get_features_string(node, features)
            else:
                newick += ','
    if _is_root:
        newick += ";"
    return newick


def _get_features_string(self, features=[]):
    """ Generates the extended newick string NHX with extra data about
    a node. """
    string = ""
    if features is None:
        features = []
    elif features == []:
        features = self.features

    for pr in features:
        if hasattr(self, pr):
            value = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                             str(getattr(self, pr)))
            if string != "":
                string +=":"
            string +="%s=%s"  %(pr, str(value))
    if string != "":
        string = "[&&NHX:"+string+"]"

    return string
