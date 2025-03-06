import unittest

from ete4.core.tree import Tree
from ete4.tools import ete_diff as ediff


example1_nw = '(((ao:1,(ap:1,aq:1)1:1)1:1,(ar:1,(as:1,at:1)1:1)1:1)1:1,((aa:1,ab:1)1:1,((ac:1,(ad:1,(ae:1,(af:1,(ag:1,ah:1)1:1)1:1)1:1)1:1)1:1,((ai:1,(aj:1,(ak:1,al:1)1:1)1:1)1:1,(am:1,an:1)1:1)1:1)1:1)1:1);'

example2_nw = '(((2ao:1,(2ap:1,2aq:1)1:1)1:1,(2ar:1,(2as:1,2at:1)1:1)1:1)1:1,((2aa:1,2ab:1)1:1,((2ac:1,(2ad:1,(2ae:1,(2af:1,(2ag:1,2ah:1)1:1)1:1)1:1)1:1)1:1,((2ai:1,(2aj:1,(2ak:1,2al:1)1:1)1:1)1:1,(2am:1,2an:1)1:1)1:1)1:1)1:1);'

example3_nw = '(((ao:1,(ap:1,2aq:1)1:1)1:1,(ar:1,(as:1,2at:1)1:1)1:1)1:1,((aa:1,ab:1)1:1,((2ac:1,(2ad:1,(2ae:1,(2af:1,(ag:1,2ah:1)1:1)1:1)1:1)1:1)1:1,((2ai:1,(aj:1,(2ak:1,al:1)1:1)1:1)1:1,(2am:1,an:1)1:1)1:1)1:1)1:1);'

example4_nw = '(((2ao:1,(ap:1,aq:1)1:1)1:1,(2ar:1,(2as:1,at:1)1:1)1:1)1:1,((aa:1,2ab:1)1:1,((ac:1,(ad:1,(ae:1,(2af:1,(2ag:1,2ah:1)1:1)1:1)1:1)1:1)1:1,((ai:1,(aj:1,(2ak:1,al:1)1:1)1:1)1:1,(2am:1,an:1)1:1)1:1)1:1)1:1);'


def almost_equal(x, y, precision=1e-6):
    return abs(x - y) / max(abs(x), abs(y)) < precision


class Test_Treediff(unittest.TestCase):
    """Test specific methods for trees linked to treediff."""

    def test_treediff_basic(self):
        """Test tree-diff basic functionality."""
        t1 = Tree(example1_nw)
        t2 = t1

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.EUCL_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertEqual(type(difftable), list)
        self.assertEqual(type(difftable[0]), list)
        self.assertEqual(len(difftable[0]), 7)
        self.assertEqual(len(difftable), 39)

    def test_treediff_EUCL_DIST_1(self):
        """Test tree-diff EUCL_DIST distance."""
        t1 = Tree(example1_nw)
        t2 = Tree(example2_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.EUCL_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]), 39)

    def test_treediff_EUCL_DIST_2(self):
        """ Tests tree-diff EUCL_DIST distance."""
        t1 = Tree(example1_nw)
        t2 = Tree(example3_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.EUCL_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertTrue(almost_equal(sum([i[0] for i in difftable]), 19.621428))

    def test_treediff_EUCL_DIST_3(self):
        """ Tests tree-diff EUCL_DIST diffs"""
        t1 = Tree(example1_nw)
        t2 = Tree(example3_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.EUCL_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertEqual(sorted([i[4] for i in difftable]), DIFFS)

    def test_treediff_RF_DIST_1(self):
        """ Tests tree-diff RF_DIST distance"""
        t1 = Tree(example1_nw)
        t2 = Tree(example2_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.RF_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]), 39.0)

    def test_treediff_RF_DIST_2(self):
        """ Tests tree-diff RF_DIST distance"""
        t1 = Tree(example1_nw)
        t2 = Tree(example3_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.RF_DIST, support=False,
                                   reduce_matrix=False, extended=None,
                                   jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]), 10.0)

    def test_treediff_extendend_cc(self):
        """ Tests tree-diff Extended distance. Cophenetic Compared"""
        t1 = Tree(example1_nw)
        t2 = Tree(example3_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.RF_DIST, support=False,
                                   reduce_matrix=False,
                                   extended=ediff.cc_distance,
                                   jobs=1, parallel=None)

        self.assertEqual(sum([i[1] for i in difftable]), 863.9737020175473)

    def test_treediff_extendend_be(self):
        """ Tests tree-diff  Extended distance. Branch Extended"""
        t1 = Tree(example1_nw)
        t2 = Tree(example3_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.RF_DIST, support=False,
                                   reduce_matrix=False,
                                   extended=ediff.be_distance,
                                   jobs=1, parallel=None)

        self.assertEqual(sum([i[1] for i in difftable]), 616.0)

    def test_treediff_reports(self):
        """ Tests tree-diff Reports"""
        t1 = Tree(example1_nw)
        t2 = Tree(example4_nw)

        difftable = ediff.treediff(t1, t2, prop1='name', prop2='name',
                                   dist_fn=ediff.EUCL_DIST, support=False,
                                   reduce_matrix=False,
                                   extended=ediff.cc_distance,
                                   jobs=1, parallel=None)

        rf , rf_max = t1.robinson_foulds(t2)[:2]

        # NOTE: This is not a test. Calling the functions below just print
        #       stuff on the screen, but there are no checks. Commenting out.
        # ediff.show_difftable_summary(difftable, rf=rf, rf_max=rf_max, extended=ediff.cc_distance))
        # ediff.show_difftable(difftable, extended=ediff.cc_distance)
        # ediff.show_difftable_tab(difftable, extended=ediff.cc_distance)
        # ediff.show_difftable_topo(difftable, 'name', 'name', usecolor=False, extended=ediff.cc_distance)



DIFFS = [
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    set(),
    {'2aq', 'aq'},
    {'2ai', 'at'},
    {'2ah', 'ac'},
    {'2af', 'ad'},
    {'2ae', 'ae'},
    {'2ad', 'af'},
    {'2ac', 'ah'},
    {'2at', 'ai'},
    {'2am', 'ak'},
    {'2ak', 'am'},
    {'2aq', 'aq'},
    {'2at', 'at'},
    {'2ah', 'ah'},
    {'2ak', 'ak'},
    {'2am', 'am'},
    {'2aq', 'aq'},
    {'2at', 'at'},
    {'2af', '2ah', 'af', 'ah'},
    {'2ak', 'ak'},
    {'2ae', '2af', '2ah', 'ae', 'af', 'ah'},
    {'2ai', '2ak', 'ai', 'ak'},
    {'2ad', '2ae', '2af', '2ah', 'ad', 'ae', 'af', 'ah'},
    {'2aq', '2at', 'aq', 'at'},
    {'2ac', '2ad', '2ae', '2af', '2ah', 'ac', 'ad', 'ae', 'af', 'ah'},
    {'2ai', '2ak', '2am', 'ai', 'ak', 'am'},
    {'2ac', '2ad', '2ae', '2af', '2ah', '2ai', '2ak', '2am', 'ac', 'ad',
     'ae', 'af', 'ah', 'ai', 'ak', 'am'},
    {'2ac', '2ad', '2ae', '2af', '2ah', '2ai', '2ak', '2am', 'ac', 'ad',
     'ae', 'af', 'ah', 'ai', 'ak', 'am'},
    {'2ac', '2ad', '2ae', '2af', '2ah', '2ai', '2ak', '2am', '2aq', '2at',
     'ac', 'ad', 'ae', 'af', 'ah', 'ai', 'ak', 'am', 'aq', 'at'}]


if __name__ == '__main__':
    unittest.main()
