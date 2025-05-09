"""
Module to do pattern matching with trees.

It does with patterns and trees something similar to what the re module does
with expressions and strings.
"""

from itertools import permutations
import re

from ete4 import Tree
from ete4.core.eval import eval_on_node


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

    if not eval_on_node(pattern.props['code'], node, context, pattern.safer):
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
