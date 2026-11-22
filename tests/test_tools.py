"""Tests for the ete4 command line tools."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from ete4.tools.ete import _main


def run_ete4(*args):
    """Return the standard output of running "ete4 <args>"."""
    out = io.StringIO()
    with redirect_stdout(out):
        _main(['ete4'] + list(args))
    return out.getvalue()


class TestCompare(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.t1 = os.path.join(self.tmpdir.name, 't1.nw')
        self.t2 = os.path.join(self.tmpdir.name, 't2.nw')
        open(self.t1, 'w').write('((A,B),(C,(D,E)));')
        open(self.t2, 'w').write('((A,C),(B,(D,E)));')

    def tearDown(self):
        self.tmpdir.cleanup()

    def table(self, *args):
        lines = run_ete4('compare', '--taboutput', *args).splitlines()
        return [line.split('\t') for line in lines[1:]]  # skip header

    def test_rooted(self):
        rows = self.table('-t', self.t1, '-r', self.t2)
        self.assertEqual(rows[0][2:6], ['5', '0.6666666666666666', '4.0', '6.0'])

    def test_unrooted(self):
        rows = self.table('-t', self.t1, self.t2, '-r', self.t2, '--unrooted')
        self.assertEqual(rows[0][2:6], ['5', '0.5', '2.0', '4.0'])  # t1 vs t2
        self.assertEqual(rows[1][3:5], ['0.0', '0.0'])  # t2 vs itself

    def test_attr_parser(self):
        open(self.t2, 'w').write('((A_1,C_1),(B_1,(D_1,E_1)));')
        rows = self.table('-t', self.t1, '-r', self.t2,
                          '--ref_attr_parser', '^(.)_')
        self.assertEqual(rows[0][2:6], ['5', '0.6666666666666666', '4.0', '6.0'])


if __name__ == '__main__':
    unittest.main()
