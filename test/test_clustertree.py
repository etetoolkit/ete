import unittest

from ete2 import *
from datasets import *

class Test_ClusterTree(unittest.TestCase):
    """ Tests specific methods for trees linked to ArrayTables"""
    def test_clustertree(self):
        """ Tests tree-ArrayTable association """

        t = ClusterTree("(((A,B),(C,(D,E))),(F,(G,H)));", text_array=expression)
        # Now we can ask the expression profile of a single gene
        node = t.get_common_ancestor("C", "D", "E")
        self.assertEqual((t&"A").profile.tolist(), \
                             [-1.23, -0.81, 1.79, 0.78,-0.42,-0.69, 0.58])
        print node.profile
        print node.deviation
        print node.silhouette
        print node.intracluster_dist
        print node.intercluster_dist

        from ete2.clustering import clustvalidation
        c1 = t.get_common_ancestor("A", "B")
        c2 = t.get_common_ancestor("C", "D", "E")
        c3 = t.get_common_ancestor("F", "G", "H")
        print t.get_dunn([c1, c2, c3])

