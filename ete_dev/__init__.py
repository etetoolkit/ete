# #START_LICENSE###########################################################
#
#
#
# #END_LICENSE#############################################################

from sys import stderr
from coretype.tree import *
from coretype.seqgroup import *
from phylo.phylotree import *
from webplugin.webapp import *
from phyloxml import Phyloxml
from nexml import Nexml

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
    from treeview.svg_colors import SVG_COLORS


except ImportError, e:
    print >>stderr, "Treeview module could not be loaded"
    print e
