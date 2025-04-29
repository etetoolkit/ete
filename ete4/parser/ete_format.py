"""
Prototype of the "future ete format", an alternative to the newick format,
that encodes types too (and is probably faster).
"""

import io
import json
import pickle
import base64
import gzip
import ete4


def pickle_pack(data):
    return base64.b64encode(pickle.dumps(data)).decode()

def pickle_unpack(data):
    return pickle.loads(base64.b64decode(data))

def b64gzip_pack(data):
    return base64.b64encode(gzip.compress(bytes(data, 'utf-8'))).decode()

def b64gzip_unpack(data):
    return gzip.decompress(base64.b64decode(data))


def dumps(t, encoder='pickle', pack=False):
    OUT = io.StringIO()

    assert encoder in ['pickle', 'json'], f'Invalid encoder: {encoder}'

    for i, n in enumerate(t.traverse()):
        n.props['__id'] = i
    next_nodes = [t]

    while next_nodes:
        n = next_nodes.pop()
        next_nodes.extend(n.children)

        if encoder == 'json':
            packed_content = json.dumps(n.props)
        elif encoder == 'pickle':
            packed_content = pickle_pack(n.props)
        else:
            raise ValueError(f'unknown encoder: {encoder}')

        print('p', n.props['__id'], packed_content, sep='\t', file=OUT)

        if n.up:
            print('t', n.props['__id'], n.up.props['__id'], sep='\t', file=OUT)
        else:
            print('t', n.props['__id'], '', sep='\t', file=OUT)

    if pack:
        return b64gzip_pack(OUT.getvalue())
    else:
        return OUT.getvalue()


def loads(INPUT, encoder='pickle', unpack=False):
    if unpack:
        INPUT = b64gzip_unpack(INPUT).decode()

    assert encoder in ['pickle', 'json'], f'Invalid encoder: {encoder}'

    id2node = {}
    root = None
    for line in io.StringIO(INPUT).readlines():
        etype, nid, b = map(str.strip, line.split('\t'))
        if nid not in id2node:
            node = id2node[nid] = ete4.Tree()

        if etype == 'p':
            if encoder == 'pickle':
                node.props = pickle_unpack(b)
            if encoder == 'json':
                node.props = json.loads(b)
        elif etype == 't':
            if b:
                id2node[b].add_child(node)
                node.up = id2node[b]
            else:
                root = node
    return root
