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


def test_upload_does_not_read_files(tmp_path):
    # The newick text in a request must never be taken as the path of a
    # file in the server, and the client cannot choose parsers like "ete".
    import io, json, bottle
    from urllib.parse import urlencode
    from ete4.smartview import explorer

    def post(body, content_type):
        body = body.encode()
        bottle.request.bind({'REQUEST_METHOD': 'POST',
                             'CONTENT_TYPE': content_type,
                             'CONTENT_LENGTH': str(len(body)),
                             'wsgi.input': io.BytesIO(body)})
        return explorer.add_trees_from_request()

    path = str(tmp_path / 'tree.nw')  # a newick file in the server
    with open(path, 'w') as f:
        f.write('(a,b);')

    with pytest.raises(bottle.HTTPError):
        post(json.dumps({'name': 'x', 'newick': path}), 'application/json')

    for parser in ['ete', 'nexus', 'auto', 'file-name']:
        with pytest.raises(bottle.HTTPError):
            post(urlencode({'name': 'x', 'parser': parser, 'newick': path}),
                 'application/x-www-form-urlencoded')

    assert post(urlencode({'name': 'test_upload', 'parser': 'support',
                           'newick': '((a,b)90,c);'}),
                'application/x-www-form-urlencoded') == ['test_upload']
    explorer.g_trees.pop('test_upload')


def test_upload_bad_or_big_files():
    import io, gzip, bottle
    from ete4.smartview import explorer

    # Stop reading (uncompressed) files that are too big.
    data = gzip.compress(b'((a,b),c);' + b' ' * 1000)
    assert (explorer.get_trees_from_file('t.nw.gz', io.BytesIO(data), 2000) ==
            [{'name': 't.nw', 'newick': '((a,b),c);'}])
    with pytest.raises(ValueError):
        explorer.get_trees_from_file('t.nw.gz', io.BytesIO(data), 100)

    # A bad file gives an error 400 (and not 500).
    body = ('--XX\r\n'
            'Content-Disposition: form-data; name="trees"; filename="t.nw.gz"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n'
            'not a gzip file\r\n'
            '--XX--\r\n').encode()
    bottle.request.bind({'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': 'multipart/form-data; boundary=XX',
                         'CONTENT_LENGTH': str(len(body)),
                         'wsgi.input': io.BytesIO(body)})
    with pytest.raises(bottle.HTTPError) as e:
        explorer.get_trees_from_form()
    assert e.value.status_code == 400
