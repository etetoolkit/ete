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
