# #START_LICENSE###########################################################
#
#
#
# #END_LICENSE#############################################################

# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.
from __future__ import print_function
from sys import stderr
from coretype.tree import *
from coretype.seqgroup import *
from phylo.phylotree import *
from evol.evoltree import *
from webplugin.webapp import *
from phyloxml import Phyloxml, PhyloxmlTree
from nexml import Nexml, NexmlTree
from evol import EvolTree

try:
    from ncbi_taxonomy import ncbiquery
except ImportError, e:
    print >>stderr, "NCBI taxonomy module could not be loaded"
    print e

try:
    from coretype.arraytable import *
except ImportError as e:
    print("Clustering module could not be loaded", file=stderr)
    print(e)
else:
    from clustering.clustertree import *

try:
    from phylomedb.phylomeDB3 import *
except ImportError as e:
    print(" MySQLdb module could not be loaded", file=stderr)
    print(e)

try:
    from treeview.main import *
    from treeview.faces import *
    from treeview import faces
    from treeview import layouts
    from treeview.svg_colors import *
except ImportError as e:
    print("Treeview module could not be loaded", file=stderr)
    print(e)

# Do not modify the following line. It will be checked during
# installation
__ETEID__="f44535d4f4996f0f2af92a57c9f983e6"
