"""
Utilities to evaluate a certain expression or code on a node.

The expression is normally a compiled code with:
  code = compile(expression, '<string>', 'eval')
which allows to reuse the code and not have to process it again for every
node where it is called.

The eval_on_node() function is mainly used when searching for nodes
(returning True for the searched nodes) or sorting (returning a value to
compare like the one used in sorted(key=...)).
"""

from math import pi
import re


def eval_on_node(code, node, context=None, safer=False):
    """Return the given code evaluated on values related to the given node.

    :param code: Expression (normally compiled) to evaluate.
    :param node: Node for which the expression is evaluated.
    :param context: Dictionary used in eval(code, context).
    :param safer: If True, use a safer version of eval restricting keywords.
    """
    context = context or {}

    # Default values that make it easier when checking all nodes, even the root.
    name = node.props.get('name', '')  # node.name could be None
    dist = node.props.get('dist', 0 if node.is_root else 1)  # and node.dist
    support = node.props.get('support', 1)  # and node.support

    context_base = {
        'node': node, 'name': name,
        'dist': dist, 'd': dist, 'length': dist,
        'support': support, 'sup': support,
        'up': node.up, 'parent': node.up,
        'children': node.children, 'ch': node.children,
        'is_leaf': node.is_leaf, 'is_root': node.is_root,
        'props': node.props, 'p': node.props,
        'size': node.size, 'dx': node.size[0], 'dy': node.size[1],
        'regex': re.search,
        'pi': pi,
        'get': dict.get,  # from this point, it's just in case safer=True
        'startswith': str.startswith, 'endswith': str.endswith,
        'upper': str.upper, 'lower': str.lower, 'split': str.split,
        'any': any, 'all': all, 'len': len,
        'sum': sum, 'abs': abs, 'float': float}
    # NOTE: If we wanted to make it convenient for PhyloTrees we could add:
    #    'species': getattr(node, 'species', ''),
    # and so on (get_species, etc.).

    for k in context:
        assert k not in context_base, f'colliding name: {k}'

    eval_context = dict(context_base, **context)  # merge dicts

    evaluate = safer_eval if safer else eval  # risky business

    return evaluate(code, eval_context)


# Calling eval() directly in match() can be a security problem. Specially for
# web services, we are better off using this following function:
def safer_eval(code, context):
    """Return a safer version of eval(code, context)."""
    for name in code.co_names:
        if name not in context:
            raise SyntaxError('invalid use of %r during evaluation' % name)
    return eval(code, {'__builtins__': {}}, context)
