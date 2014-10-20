# #START_LICENSE###########################################################
#
#
# #END_LICENSE#############################################################
import unittest
import sys

from .datasets import *
from .test_tree import *
from .test_seqgroup import *
from .test_phylotree import *
try:
    import numpy
except ImportError: # case numpy is not installed
    pass
else:
    from .test_arraytable import *
    from .test_clustertree import *
from .test_r_bindings import *
from .test_evol import *

def test_all():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([
        loader.loadTestsFromTestCase(Test_Coretype_ArrayTable),
        loader.loadTestsFromTestCase(Test_ClusterTree),
        loader.loadTestsFromTestCase(TestEvolEvolTree),
        loader.loadTestsFromTestCase(Test_phylo_module),
        loader.loadTestsFromTestCase(Test_R_bindings),
        loader.loadTestsFromTestCase(Test_Coretype_SeqGroup),
        loader.loadTestsFromTestCase(Test_Coretype_Tree)
    ])
    return suite

def test_optional():
    from .test_xml_parsers import Test_PhyloXML,Test_NeXML
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([
        #loader.loadTestsFromTestCase(TestPhylomeDB3Connector),
        loader.loadTestsFromTestCase(Test_PhyloXML),
        loader.loadTestsFromTestCase(Test_NeXML)
    ])
    return suite
