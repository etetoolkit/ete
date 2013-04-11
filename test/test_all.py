# #START_LICENSE###########################################################
#
#
# #END_LICENSE#############################################################

import unittest
import sys
sys.path.insert(0, './')
sys.path.insert(0, '../')

from datasets import *
from test_tree import *
from test_seqgroup import *
from test_phylotree import *
try:
    import numpy
except ImportError: # case numpy is not installed
    pass
else:
    from test_arraytable import *
    from test_clustertree import *
from test_r_bindings import *
from test_evol import *

if __name__ == '__main__':
    unittest.main()
