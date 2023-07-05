"""
Module to do pattern matching with trees.

It does with patterns and trees something similar to what the re module does
with expressions and strings.
"""

from itertools import permutations
import re

from ete4 import Tree


class TreePattern(Tree):
    """A pattern of conditions to be satisfied by a subtree in a tree.

    It stores in the node names the constraints for that node.
    """

    def __init__(self, pattern='', children=None, parser=None):
        if type(pattern) == str:
            # We expect a newick tree whose names will be the conditions
            # to check for in each node. No need to end with ";".
            newick = pattern.strip().rstrip(';') + ';'
            Tree.__init__(self, newick)
        else:  # we are being recursively called, and were passed a dict
            data = {'name': pattern.get('name', '').strip()}
            Tree.__init__(self, data, children)

        # Add the "code" property with its compiled condition.
        self.props['code'] = compile(self.name or 'True', '<string>', 'eval')

    def __str__(self):
        return self.to_str(show_internal=True, props=['name'])

    def match(tree):
        return match(self, tree)

    def search(tree):
        return search(self, tree)


def match(pattern, tree):
    """Return True if the pattern matches the given tree."""
    if pattern.children and len(tree.children) != len(pattern.children):
        return False  # no match if there's not the same number of children

    context = {
        'tree': tree, 'node': tree,
        'name': tree.props.get('name', ''),
        'up': tree.up, 'is_leaf': tree.is_leaf, 'is_root': tree.is_root,
        'dist': tree.dist, 'd': tree.dist,
        'props': tree.props, 'p': tree.props,
        'get': dict.get,
        'children': tree.children, 'ch': tree.children,
        'size': tree.size, 'dx': tree.size[0], 'dy': tree.size[1],
        'regex': re.search,
        'startswith': str.startswith, 'endswith': str.endswith,
        'upper': str.upper, 'lower': str.lower, 'split': str.split,
        'any': any, 'all': all, 'len': len,
        'sum': sum, 'abs': abs, 'float': float}

    if not safer_eval(pattern.props['code'], context):
        return False  # no match if the condition for this node if false

    if not pattern.children:
        return True  # if the condition was true and pattern ends here, we match

    # Check all possible comparisons between pattern children and tree children.
    for ch_perm in permutations(pattern.children):
        if all(match(sub_pattern, tree.children[i])
               for i, sub_pattern in enumerate(ch_perm)):
            return True

    return False  # no match if no permutation of children satisfied sub-matches


def search(pattern, tree):
    """Return the first node that matches the given pattern, or None."""
    return next((node for node in tree.traverse("preorder")
                 if match(pattern, node)), None)


def safer_eval(code, context):
    """Return a safer version of eval(code, context)."""
    for name in code.co_names:
        if name not in context:
            raise ValueError('invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)
