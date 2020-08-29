from __future__ import absolute_import
from __future__ import print_function
import unittest

from .. import Tree

class Test_Interoperability(unittest.TestCase):
    def test_parent_child_table(self):
        tree = Tree.from_parent_child_table([("A", "B", 0.1), ("A", "C", 0.2), ("C", "D", 1), ("C", "E", 1.5)])
        newick = tree.write(format_root_node=True, format=1)
        self.assertEqual(newick, "(B:0.1,(D:1,E:1.5)C:0.2)A:1;")


  # Disabled temporarily. following error is reported:
  #
  # File "/home/travis/build/etetoolkit/ete/test_tmp/miniconda3/envs/test_3.5/lib/python3.5/site-packages/parso/__init__.py", line 41, in <module>
  #    from parso.parser import ParserSyntaxError
  #  File "/home/travis/build/etetoolkit/ete/test_tmp/miniconda3/envs/test_3.5/lib/python3.5/site-packages/parso/parser.py", line 113
  #     node_map: Dict[str, type] = {}
  # SyntaxError: invalid syntax
    def disabled_test_skbio(self): 
        from skbio import TreeNode
        skb_tree = TreeNode.read([u"(B:0.1,(D:1,E:1.5)C:0.2)A:1;"])
        for node in skb_tree.traverse():
            node.test = node.name
        tree = Tree.from_skbio(skb_tree, map_attributes=["test"])
        newick = tree.write(format_root_node=True, format=1, features=["test"])
        expected = "(B:0.1[&&NHX:test=B],(D:1[&&NHX:test=D],E:1.5[&&NHX:test=E])C:0.2[&&NHX:test=C])A:1[&&NHX:test=A];"
        self.assertEqual(newick, expected)

        

if __name__ == '__main__':
    unittest.main()
