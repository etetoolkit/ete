# Note that the use of "from x import *" is safe here. Modules include
# the __all__ variable.
from warnings import warn

from .core.tree import Tree, TreeError
from .core import operations, text_viz
from .parser import newick, ete_format, nexus
from .config import (ETE_DATA_HOME, ETE_CONFIG_HOME, ETE_CACHE_HOME,
                     update_ete_data)
from .ncbi_taxonomy import *
from .gtdb_taxonomy import *
from .core.seqgroup import *
from .phylo.phylotree import *
from .evol.evoltree import *
from .phyloxml import Phyloxml, PhyloxmlTree
from .nexml import Nexml, NexmlTree
from .evol import EvolTree
from .core.arraytable import *
from .clustering.clustertree import *
from .utils import SVG_COLORS, COLOR_SCHEMES, random_color

from .version import __version__
