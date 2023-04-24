"""
Heuristics to guess if a string is an existing filename, and extract
text from it, compressed or not.
"""

import os
import gzip


def file_extract(obj):
    """Return text from the given object."""
    if hasattr(obj, 'read'):
        return obj.read()  # we have a file object or similar, so read from it

    assert type(obj) == str, 'Cannot extract text from unknown type: %r' % obj

    if not os.path.exists(obj):
        return obj  # the text doesn't correspond to a file

    if obj.endswith('.gz'):
        with gzip.open(obj) as fin:
            return fin.read()
    else:
        with open(obj) as fin:
            return fin.read()
