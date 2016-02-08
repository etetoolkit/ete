from __future__ import absolute_import

import unittest
from .datasets import *
from .test_tree import *
from .test_interop import *
from .test_seqgroup import *
from .test_phylotree import *
from .test_ncbiquery import *

from .test_arraytable import *
from .test_clustertree import *

from .test_evol import *
#from .test_xml_parsers import *

from .test_treeview.test_all_treeview import *

def run():
    unittest.main()

if __name__ == '__main__':
    run()
