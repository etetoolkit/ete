"""Regression checks for common-leaf RF polytomy correction (issue745)."""
import unittest
from ete4 import Tree
from ete4.core.tree import TreeError

class TestRFPolytomyCorrection(unittest.TestCase):
    def test_unrooted_root_representations(self):
        forms = ['((A,B),(C,D));', '(A,B,(C,D));', '((A,B),C,D);']
        for left in forms:
            for right in forms:
                with self.subTest(left=left, right=right):
                    result = Tree(left).robinson_foulds(
                        Tree(right), unrooted_trees=True,
                        correct_by_polytomy_size=True)
                    self.assertEqual(result[:2], [0, 2])

    def test_common_leaf_projection(self):
        cases = [
            ('((A,B,X),(C,D));', '((A,B),(C,D));', False),
            ('((A,B,X),C,D);', '(A,B,(C,D));', True),
            ('((A,B,X),C,D);', '((A,B),(C,D));', True),
            ('((A,B,X),(C,D));', '((A,B,Y),(C,D));', False),
            ('((A,B,X),C,D);', '((A,B,Y),C,D);', True),
        ]
        for left, right, unrooted in cases:
            with self.subTest(left=left, right=right, unrooted=unrooted):
                result = Tree(left).robinson_foulds(
                    Tree(right), unrooted_trees=unrooted,
                    correct_by_polytomy_size=True)
                self.assertEqual(result[0], 0)

    def test_true_polytomy_still_counts(self):
        for left, right, unrooted in [
            ('(A,B,C,D);', '(A,B,(C,D));', True),
            ('((A,B,C),D);', '(((A,B),C),D);', False),
        ]:
            with self.subTest(unrooted=unrooted):
                self.assertEqual(Tree(left).robinson_foulds(
                    Tree(right), unrooted_trees=unrooted,
                    correct_by_polytomy_size=True)[0], 0)
                with self.assertRaisesRegex(TreeError, 'Both trees contain polytomies'):
                    Tree(left).robinson_foulds(
                        Tree(left), unrooted_trees=unrooted,
                        correct_by_polytomy_size=True)

    def test_small_common_leaf_sets(self):
        for right in ['A;', '(A,B);', '(X,Y);']:
            with self.subTest(right=right):
                self.assertEqual(Tree('(A,B,C,D);').robinson_foulds(
                    Tree(right), unrooted_trees=True,
                    correct_by_polytomy_size=True)[0], 0)

    def test_unary_paths_and_custom_labels(self):
        left=Tree('((((A),B)),((C,D)));')
        right=Tree('(A,B,(C,D));')
        for index, tree in enumerate([left,right]):
            for tip in tree:
                tip.add_prop('taxon', tip.name)
                tip.name += '_gene' + str(index)
        old_left, old_right=left.write(props=['taxon']), right.write(props=['taxon'])
        self.assertEqual(left.robinson_foulds(
            right, prop_t1='taxon', prop_t2='taxon', unrooted_trees=True,
            correct_by_polytomy_size=True)[:2], [0,2])
        self.assertEqual(left.write(props=['taxon']), old_left)
        self.assertEqual(right.write(props=['taxon']), old_right)

if __name__ == '__main__':
    unittest.main()
