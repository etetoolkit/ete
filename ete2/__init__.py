# #START_LICENSE###########################################################
#
#
#
# #END_LICENSE#############################################################

# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.

from warnings import warn
from ncbi_taxonomy import *

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
    pass
    #warn("Clustering module could not be loaded. Is numpy installed?")
    #warn(e)
else:
    from clustering.clustertree import *

try:
    from phylomedb.phylomeDB3 import *
except ImportError, e:
    pass
    #warn("MySQLdb module could not be loaded")
    #warn(e)

try:
    from treeview.main import *
    from treeview.faces import *
    from treeview import faces
    from treeview import layouts
    from treeview.svg_colors import *
except ImportError, e:
    pass
    #warn("Treeview module could not be loaded")
    #warn(e)

__version__ = '2.3.0beta'
    
# Do not modify the following line. It will be checked during
# installation
__ETEID__="d4dda7ba3ff89460c6f5d0cbe15fc3d2"
