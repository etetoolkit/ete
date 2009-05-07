import re
import os 

__all__ = ["read_newick", "write_newick"]

# Regular expressions used for reading newick format
_NHX_RE = "\[&&NHX:[^\]]*\]"
_FLOAT_RE = "[+-]?\d+(\.\d+)?" 
_NAME_RE = "[^():,;\[\]]+"
_DIST_RE = ":("+_FLOAT_RE+")"
_SUPPORT_RE = _FLOAT_RE
_LEAF_NODE_RE = '(%s)(%s)?(%s)?' % (_NAME_RE, _DIST_RE, _NHX_RE)
_INTERNAL_NODE_RE = '(%s)?(%s)?(%s)?' % (_SUPPORT_RE, _DIST_RE, _NHX_RE)

_LEAF_NODE_MATCH     = re.compile(_LEAF_NODE_RE)
_INTERNAL_NODE_MATCH = re.compile(_INTERNAL_NODE_RE)

_ILEGAL_NEWICK_CHARS = ":;(),\[\]\t\n\r="

class NewickError(Exception): 
  """Exception class designed for NewickIO errors."""
  def __init__(self, value=''):
    self.value = value
  def __str__(self):
    return repr(self.value)

def read_newick(newick, root_node=None):
  """ Reads a newick tree either from a string or file, and returns an
  ETE tree structure. 

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
    return _read_newick_from_string(nw, root_node)
  else:
    raise NewickError, \
        "'newick' argument must be either a filename or a newick string."

def _read_newick_from_string(nw, root_node):
  """ Reads a newick string in the New Hampshire format. """
  if nw.count('(') != nw.count(')'):
      raise NewickError, 'Parentheses do not match. Broken tree structure'

  nw = re.sub("\s", "", nw)
  current_parent = None
  counter = 0
  # Skips the first element because is always '' and never represents
  # a node
  for subpart in nw.split("(")[1:]:
    # If this is the root of tree, use the root_node instead of
    # creating it, otherwise make a new one.
    if current_parent is None:
      current_parent = root_node
    else:
      current_parent = current_parent.add_child()
    if subpart != '':
      for subsubpart in subpart.split(","):
        read_internal_node_info = False
        for subsubsubpart in subsubpart.split(")"):
          if subsubsubpart != '':
            if read_internal_node_info: 
              _read_internal(subsubsubpart, current_parent)
            else:
              _read_leaf(subsubsubpart, current_parent)
          if read_internal_node_info: 
              current_parent = current_parent.up
          read_internal_node_info = True
  return root_node

def _read_newick_from_string_OLD_PROBLEM_WITH_ONE_CHILD_NODES(nw, root_node):
  """ Reads a newick string in the New Hampshire format. """

  if nw.count('(') != nw.count(')'):
      raise NewickError, 'Parentheses do not match. Broken tree structure'

  nw = re.sub("\s", "", nw)
  current_parent = None

  for subpart in nw.split(","):
      nclose = subpart.count(")")
      nopen  = subpart.count("(")

      if nopen>0:
          # descendants
          for i in xrange(nopen):
            if current_parent is None:
              current_parent = root_node
            else:
              current_parent = current_parent.add_child()

          # reads leaf
          try:
              _read_leaf(subpart, current_parent)
          except:
              raise NewickError, 'Bad newick structure'

      elif nclose>0:
          # reads leaf before close nodes
          _read_leaf(subpart, current_parent)

          # Goes up
          for i in xrange(nclose):
              start_data = subpart.find(")")+1
              try:
                  _read_internal(subpart[start_data:], current_parent)
              except:
                  raise NewickError, 'Bad newick structure'

              if current_parent.up:
                  current_parent = current_parent.up
              subpart = subpart[start_data:]
      else:
          try:
              _read_leaf(subpart, current_parent)
          except:
              raise NewickError, 'Bad newick structure'
  return current_parent

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

def _read_leaf(subnw, parent):
    """ Reads a leaf node from a subpart of the original newick
    tree """
    leaf_data = re.search(_LEAF_NODE_MATCH, subnw)
    if leaf_data:
      info = leaf_data.groups()
      child = parent.add_child()
      child.name = info[0].strip()
      if info[2] is not None:
        child.dist = float(info[2])
      if info[4] is not None:
        _parse_extra_features(child, info[4])
    else:
	raise NewickError, "Leaf node without name "+ subnw

def _read_internal(subnw, node):
    """ Reads an internal node from a subpart of the original newick
    tree """
    internal_data = re.match(_INTERNAL_NODE_MATCH, subnw)
    if internal_data:
      info = internal_data.groups()
      if info[3] is not None:
        node.dist = float(info[3])
      if info[0] is not None:
        node.support = float(info[0])
      if info[5] is not None:
        _parse_extra_features(node, info[5])

def write_newick(node, features=[], support=True, dist=True, \
                   _is_root=True):
  """ Recursively reads a tree structure and returns its NHX
  representation. """
  newick = ""
  if not node.children:
    if dist:
        newick += "%s:%0.6f" % (node.name, node.dist)
    else:
        newick += "%s" % (node.name)
    newick += _get_features_string(node, features)
    return newick
  else:
    if node.children:
      newick+= "("
    for cnode in node.children:
      newick += write_newick(cnode, features, support, dist, \
                               _is_root = False)
      # After last child is processed, add closing string
      if cnode == node.children[-1]:
          newick += ")"
          if node.up is not None:
            if support:
                newick +=  '%0.6f' % node.support
            if dist:
                newick +=  ':%0.6f' % node.dist
          newick += _get_features_string(node, features)
      else:
        newick += ','
  if _is_root:
    newick += ";"
  return newick

def _get_features_string(self,features=[]):
    """ Generates the extended newick string NHX with extra data about
    a node. """
    string = ""
    if len(features)>0:
	for pr in features:
	    if hasattr(self, pr):
              value = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
                               getattr(self,pr))
              if string != "": 
                string +=":"
              string +="%s=%s"  %(pr, value)
	if string != "":
	    string = "[&&NHX:"+string+"]"
    return string
