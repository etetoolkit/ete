# #START_LICENSE###########################################################
#
#
# #END_LICENSE#############################################################
import unittest
import sys
#sys.path.insert(0, './')
#sys.path.insert(0, '../')

from .datasets import *
from .test_tree import *
#from .test_seqgroup import *
from .test_phylotree import *
try:
    import numpy
except ImportError: # case numpy is not installed
    pass
else:
    from .test_arraytable import *
    from .test_clustertree import *
#from .test_r_bindings import *
from .test_evol import *

#loader.loadTestsFromTestCase(TestPhylomeDB3Connector)
def test_all():
    loader = unittest.TestLoader()
    #    loader.loadTestsFromTestCase(Test_R_bindings),
    #    loader.loadTestsFromTestCase(Test_Coretype_SeqGroup),
    #    loader.loadTestsFromTestCase(Test_PhyloXML),
    #    loader.loadTestsFromTestCase(Test_NeXML)
    suite = unittest.TestSuite([
        #loader.loadTestsFromTestCase(Test_Coretype_ArrayTable),
        #loader.loadTestsFromTestCase(Test_Coretype_Tree),
        #loader.loadTestsFromTestCase(Test_ClusterTree),
        #loader.loadTestsFromTestCase(TestEvolEvolTree),
        loader.loadTestsFromTestCase(Test_phylo_module)
    ])
    return suite
