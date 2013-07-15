# #START_LICENSE###########################################################
#
#
#
# #END_LICENSE#############################################################

# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.

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
    from coretype.arraytable import *
except ImportError, e:
    print >>stderr, "Clustering module could not be loaded"
    print e
else:
    from clustering.clustertree import *

try:
    from phylomedb.phylomeDB3 import *
except ImportError, e:
    print >>stderr, " MySQLdb module could not be loaded"
    print e

try:
    from treeview.main import *
    from treeview.faces import *
    from treeview import faces
    from treeview import layouts
    from treeview.svg_colors import *
except ImportError, e:
    print >>stderr, "Treeview module could not be loaded"
    print e

# Do not modify the following line. It will be checked during
# installation
__ETEID__="4acedec9a868dd4e14bd5264ad394607"
