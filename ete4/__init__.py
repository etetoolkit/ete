# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.
from warnings import warn

from .ncbi_taxonomy import *
from .gtdb_taxonomy import *
from .coretype.tree import *
from .coretype.seqgroup import *
from .phylo.phylotree import *
from .evol.evoltree import *
from .phyloxml import Phyloxml, PhyloxmlTree
from .nexml import Nexml, NexmlTree
from .evol import EvolTree
from .coretype.arraytable import *
from .clustering.clustertree import *

try:
    from .treeview.svg_colors import *
    from .treeview.main import *
    from .treeview.faces import *
    from .treeview import faces
    from .treeview import layouts
except ImportError as e:
    pass

try:
    from .version import __version__
except ImportError:
     __version__ = 'unknown'
