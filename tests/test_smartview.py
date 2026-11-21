"""
Tests related to the smartview module.
"""

from ete4 import Tree
from ete4.smartview import draw, faces

import pytest


def test_labels_are_safer():
    # Labels come from the gui (in the request to /trees/<id>/draw), so
    # their expressions must not be able to run arbitrary code.
    t = Tree('(a:1,b:1);')
    node = t['a']

    label = draw.read_label(['name', 'any', 'top', 0, [None, None], 16])
    face = draw.make_face(label)
    assert faces.eval_as_str(face.code, node, face.safer) == 'a'
    assert face.draw([node], draw.Size(10, 10), collapsed=False)[0]

    label = draw.read_label(["__import__('os').getpid()",
                             'any', 'top', 0, [None, None], 16])
    face = draw.make_face(label)
    with pytest.raises(SyntaxError):
        face.draw([node], draw.Size(10, 10), collapsed=False)


def test_labels_with_builtins():
    # Safer labels can still use harmless builtins, and comprehensions
    # can use the names of the context (like len or startswith).
    t = Tree('((ab:1.2345,b:2):3,c:1);')
    node = t.common_ancestor(['ab', 'b'])

    for expression, result in [
            ('round(dist, 2)', '3.0'),
            ('str(int(dist))', '3'),
            ('max(1, dist)', '3.0'),
            ('sorted(c.name for c in ch)', "['ab', 'b']"),
            ('any(len(n.name) == 1 for n in ch)', 'True'),
            ("[n.name for n in ch if startswith(n.name, 'a')]", "['ab']")]:
        label = draw.read_label([expression, 'any', 'top', 0, [None, None], 16])
        face = draw.make_face(label)
        assert faces.eval_as_str(face.code, node, face.safer) == result

    label = draw.read_label(["[x for x in ch for x in str.__subclasses__()]",
                             'any', 'top', 0, [None, None], 16])
    face = draw.make_face(label)
    with pytest.raises(SyntaxError):
        faces.eval_as_str(face.code, node, face.safer)
