"""Tests for "ete4 mod"."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from ete4 import Tree
from ete4.tools.ete import _main


class TestMod(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, 't.nw')
        open(self.path, 'w').write('((A:1,B:2):1,(C:1,(D:1,E:3):1):2);')

    def tearDown(self):
        self.tmpdir.cleanup()

    def mod(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            _main(['ete4', 'mod', '-t', self.path] + list(args))
        return Tree(out.getvalue().strip())

    def test_no_options(self):  # the tree must come out unchanged
        self.assertEqual(self.mod().write(),
                         '((A:1,B:2):1,(C:1,(D:1,E:3):1):2);')

    def test_outgroup(self):
        t = self.mod('--outgroup', 'A')
        self.assertEqual(t.children[0].name, 'A')
        t = self.mod('--outgroup', 'D', 'E')
        self.assertEqual(sorted(t.children[0].leaf_names()), ['D', 'E'])

    def test_unroot(self):
        self.assertEqual(len(self.mod('--unroot').children), 3)

    def test_ultrametric(self):
        for args, height in [((), 6), (('10',), 10)]:
            t = self.mod('--ultrametric', *args)
            for leaf in t.leaves():
                self.assertAlmostEqual(t.get_distance(t, leaf), height)


if __name__ == '__main__':
    unittest.main()
