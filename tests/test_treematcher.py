"""
Tests related to the treematcher module.
"""

from ete4 import Tree, PhyloTree
import ete4.treematcher as tm

import pytest


def strip(text):
    """Return the given text stripping the empty lines and indentation."""
    # Helps compare tree visualizations.
    indent = min(len(line) - len(line.lstrip())
                 for line in text.splitlines() if line.strip())
    return '\n'.join(line[indent:].rstrip()
        for line in text.splitlines() if line.strip())


def test_str():
    # See if the representation of a pattern as a text is the expected one.
    pattern = tm.TreePattern("""
    (
      "len(ch) > 2",
      "name in ['hello', 'bye']"
    )
    "(len(name) < 3 or name == 'accept') and d >= 0.5"
    """)
    assert str(pattern) == strip("""
                                                  ╭╴len(ch) > 2
╴(len(name) < 3 or name == 'accept') and d >= 0.5╶┤
                                                  ╰╴name in ['hello', 'bye']
    """)

    # See if we can use quotes in a different way, and format more widely.
    pattern2 = tm.TreePattern("""
    (
    '  len(ch) > 2  '  ,
    '  name in ["hello", "bye"]'
    )
    '(len(name) < 3 or name == "accept") and d >= 0.5  '
    """)
    assert str(pattern) == str(pattern2).replace('"', "'")


def test_search():
    pattern = tm.TreePattern("""
    (
      "len(ch) > 2",
      "name in ['hello', 'bye']"
    )
    "(len(name) < 3 or name == 'accept') and d >= 0.5"
    """)

    for newick, expected_result in [
            ('((hello:1,(1:1,2:1,3:1)xx:1)accept:1, NODE):0;', ['accept']),
            ('((hello:1,(1:1,2:1,3:1)xx:1)accept:0.4, NODE):0;', []),
            ('(hello:1,(1:1,2:1,3:1)xx:1)accept:1;', ['accept']),
            ('((bye:1,(1:1,2:1,3:1)xx:1)none:1, NODE):0;', []),
            ('((bye:1,(1:1,2:1,3:1)xx:1)y:1, NODE):0;', ['y']),
            ('((bye,(,,))x:1,((,,),bye)y:1):0;', ['x', 'y'])]:
        tree = Tree(newick, parser=1)

        assert ([n.name for n in tm.search(pattern, tree)] ==
                [n.name for n in pattern.search(tree)] ==
                expected_result)


def test_safer():
    t = PhyloTree('(a,(b,c));', sp_naming_function=lambda name: name)

    tp_unsafe = tm.TreePattern('("node.get_species()=={\'c\'}",'
                               '  node.species=="b")')
    assert list(tp_unsafe.search(t)) == [t.common_ancestor(['b', 'c'])]

    tp_safer = tm.TreePattern('("node.get_species()=={\'c\'}",'
                              '  node.species=="b")', safer=True)
    with pytest.raises(SyntaxError):
        list(tp_safer.search(t))  # asked for unknown function get_species()
