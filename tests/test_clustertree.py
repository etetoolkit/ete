import unittest

from ete4 import ClusterTree
from . import datasets as ds


class Test_ClusterTree(unittest.TestCase):
    """Tests specific methods for trees linked to ArrayTables."""

    def test_clustertree(self):
        """Test tree-ArrayTable association."""
        t = ClusterTree("(((A,B),(C,(D,E))),(F,(G,H)));",
                        text_array=ds.expression)

        # Now we can ask the expression profile of a single gene
        node = t.common_ancestor(["C", "D", "E"])
        self.assertEqual(t["A"].profile.tolist(),
                         [-1.23, -0.81, 1.79, 0.78,-0.42,-0.69, 0.58])
        print(node.profile)
        print(node.deviation)
        print(node.silhouette)
        print(node.intracluster_dist)
        print(node.intercluster_dist)

        c1 = t.common_ancestor(["A", "B"])
        c2 = t.common_ancestor(["C", "D", "E"])
        c3 = t.common_ancestor(["F", "G", "H"])
        print(t.get_dunn([c1, c2, c3]))


if __name__ == '__main__':
    unittest.main()
