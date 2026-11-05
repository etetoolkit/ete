import io
import unittest
from contextlib import redirect_stdout

from ete4.tools.ete import _main


class TestCompareCommand(unittest.TestCase):
    """The compare command must build trees with the current parser argument."""

    def test_documented_compare_prints_distances(self):
        """A matching quartet has RF 0 and a swapped quartet has RF 4."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _main([
                "ete4", "compare",
                "-t", "((A,B),(C,D));", "((A,C),(B,D));",
                "-r", "((A,B),(C,D));",
            ])
        text = buffer.getvalue()
        self.assertIn("((A,B),(C,D));", text)
        self.assertIn("4       | 0.00    | 0.00    | 4.00", text)
        self.assertIn("4       | 1.00    | 4.00    | 4.00", text)

    def test_treeko_compare_prints_a_distance(self):
        """TreeKO uses PhyloTree and still receives the parser argument."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _main([
                "ete4", "compare", "--treeko",
                "-t", "((A,B),(C,D));",
                "-r", "((A,B),(C,D));",
            ])
        self.assertIn("4.00    | 0.00    | 0.00    | 4", buffer.getvalue())
        self.assertIn("1       | 0.00", buffer.getvalue())
