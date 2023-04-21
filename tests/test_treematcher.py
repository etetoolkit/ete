"""
Tests related to the treematcher module.
"""

import unittest

from ete4 import Tree
import ete4.treematcher as tm



def strip(text):
    """Return the given text stripping the empty lines and indentation."""
    # Helps compare tree visualizations.
    indent = min(len(line) - len(line.lstrip())
                 for line in text.splitlines() if line.strip())
    return '\n'.join(line[indent:].rstrip()
        for line in text.splitlines() if line.strip())


class TestTreematcher(unittest.TestCase):

    def test_search(self):
        pattern = tm.TreePattern("""
        (
          "len(ch) > 2",
          "name in ['hello', 'bye']"
        )
        "(len(name) < 3 or name == 'accept') and d >= 0.5"
        """)

        self.assertEqual(str(pattern), strip("""
                                                  ╭╴len(ch) > 2
╴(len(name) < 3 or name == 'accept') and d >= 0.5╶┤
                                                  ╰╴name in ['hello', 'bye']
        """))

        for (newick, expected_result) in [
                ('((hello,(1,2,3)xx)accept:1, NODE);', True),
                ('((hello,(1,2,3)xx)accept:0.4, NODE);', False),
                ('(hello,(1,2,3)xx)accept:1;', True),
                ('((bye,(1,2,3)xx)none:1, NODE);', False),
                ('((bye,(1,2,3)xx)y:1, NODE);', True)]:
            tree = Tree(newick, format=1)

            self.assertEqual(bool(tm.search(pattern, tree)), expected_result)
