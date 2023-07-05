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

    def test_str(self):

        # See if the representation of a pattern as a text is the expected one.
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

        # See if we can use quotes in a different way, and format more widely.
        pattern2 = tm.TreePattern("""
        (
        '  len(ch) > 2  '  ,
        '  name in ["hello", "bye"]'
        )
        '(len(name) < 3 or name == "accept") and d >= 0.5  '
        """)
        self.assertEqual(str(pattern), str(pattern2).replace('"', "'"))

    def test_search(self):
        pattern = tm.TreePattern("""
        (
          "len(ch) > 2",
          "name in ['hello', 'bye']"
        )
        "(len(name) < 3 or name == 'accept') and d >= 0.5"
        """)

        for (newick, expected_result) in [
                ('((hello:1,(1:1,2:1,3:1)xx:1)accept:1, NODE):0;', True),
                ('((hello:1,(1:1,2:1,3:1)xx:1)accept:0.4, NODE):0;', False),
                ('(hello:1,(1:1,2:1,3:1)xx:1)accept:1;', True),
                ('((bye:1,(1:1,2:1,3:1)xx:1)none:1, NODE):0;', False),
                ('((bye:1,(1:1,2:1,3:1)xx:1)y:1, NODE):0;', True)]:
            tree = Tree(newick)

            self.assertEqual(bool(tm.search(pattern, tree)), expected_result)
