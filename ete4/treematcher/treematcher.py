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

    def __init__(self, *args, **kargs):
        Tree.__init__(self, *args, quoted_node_names=True, format=1, **kargs)

        for node in self.traverse():
            if node.name:
                node.props['code'] = compile(node.name, '<string>', 'eval')

    def __str__(self):
        return self.get_ascii(show_internal=True)


def match(pattern, tree):
    """Return True if the pattern matches the given tree."""
    context = {
        'tree': tree, 'node': tree,
        'name': tree.name, 'up': tree.up, 'is_leaf': tree.is_leaf,
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

    if not safer_eval(pattern.props.get('code', 'True'), context):
        return False

    if not pattern.children:
        return True

    if len(tree.children) != len(pattern.children):
        return False

    # Check all possible comparisons between pattern children and tree children.
    for ch_perm in permutations(pattern.children):
        if all(match(sub_pattern, tree.children[i])
               for i, sub_pattern in enumerate(ch_perm)):
            return True
    return False


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
