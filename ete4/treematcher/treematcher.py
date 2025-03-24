"""
Module to do pattern matching with trees.

It does with patterns and trees something similar to what the re module does
with expressions and strings.
"""

from itertools import permutations
import re

from ete4 import Tree


class TreePattern(Tree):
    """
    A pattern of conditions to be satisfied by a subtree in a tree.

    It stores in the node names the constraints for that node.
    """

    def __init__(self, pattern='', children=None, parser=1, safer=False):
        """
        :param pattern: Tree pattern to match, as a newick string. Optionally
            with conditions on the nodes too (in place of node names).
        :param safer: If True, calls to eval() will be safer by strongly
            restricting the Python keywords that can be used.

        The other parameters (children and parser) are needed to call
        Tree's constructor appropriately, but should not be used when
        creating a TreePattern.
        """
        if type(pattern) == str:
            # We expect a newick tree whose names will be the conditions
            # to check for in each node. No need to end with ";".
            newick = pattern.strip().rstrip(';') + ';'
            super().__init__(newick, parser=1)
        else:  # we are being recursively called, and were passed a dict
            data = {'name': pattern.get('name', '').strip()}
            super().__init__(data, children)

        # Add the "code" property with its compiled condition.
        self.props['code'] = compile(self.name or 'True', '<string>', 'eval')

        for node in self.traverse():  # after init, needs to go to every node
            node.safer = safer  # will use to know if to use eval or safer_eval

    def __str__(self):
        return self.to_str(show_internal=True, props=['name'])

    def match(self, tree, context=None):
        return match(self, tree, context)

    def search(self, tree, context=None, strategy='levelorder'):
        return search(self, tree, context, strategy)


def match(pattern, node, context=None):
    """Return True if the pattern matches the given node."""
    if pattern.children and len(node.children) != len(pattern.children):
        return False  # no match if there's not the same number of children

    context = context or {}
    context_base = {
        'node': node,
        'name': node.props.get('name', ''),  # node.name could be None
        'dist': node.dist, 'd': node.dist,
        'support': node.support, 'sup': node.support,
        'up': node.up, 'parent': node.up,
        'children': node.children, 'ch': node.children,
        'is_leaf': node.is_leaf, 'is_root': node.is_root,
        'props': node.props, 'p': node.props,
        'species': getattr(node, 'species', ''),  # for PhyloTree
        'get': dict.get,
        'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
        'regex': re.search,
        'startswith': str.startswith, 'endswith': str.endswith,
        'upper': str.upper, 'lower': str.lower, 'split': str.split,
        'any': any, 'all': all, 'len': len,
        'sum': sum, 'abs': abs, 'float': float}

    for k in context:
        assert k not in context_base, f'colliding name: {k}'

    eval_context = dict(context_base, **context)  # merge dicts

    evaluate = safer_eval if pattern.safer else eval  # risky business
    if not evaluate(pattern.props['code'], eval_context):
        return False  # no match if the condition for this node if false

    if not pattern.children:
        return True  # if the condition was true and pattern ends here, we match

    # Check all possible comparisons between pattern children and node children.
    for ch_perm in permutations(pattern.children):
        if all(match(sub_pattern, node.children[i], context)
               for i, sub_pattern in enumerate(ch_perm)):
            return True

    return False  # no match if no permutation of children satisfied sub-matches


def search(pattern, tree, context=None, strategy='levelorder'):
    """Yield nodes that match the given pattern."""
    for node in tree.traverse(strategy):
        if match(pattern, node, context):
            yield node


# Calling eval() directly in match() can be a security problem. Specially for
# web services, we are better off using this following function:
def safer_eval(code, context):
    """Return a safer version of eval(code, context)."""
    for name in code.co_names:
        if name not in context:
            raise ValueError('invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)
