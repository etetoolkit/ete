# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.
from warnings import warn

from .config import ETE_DATA_HOME, ETE_CONFIG_HOME, ETE_CACHE_HOME, update_ete_data
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
from .utils import SVG_COLORS, COLOR_SCHEMES, random_color

try:
    from .treeview.main import *
    from .treeview.faces import *
    from .treeview import faces
    from .treeview import layouts
except ImportError as e:
    pass

from .version import __version__
