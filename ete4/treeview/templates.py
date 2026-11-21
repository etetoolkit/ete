from .. import PhyloTree
from . import layouts

def apply_template(tree_style, template):
    for k, v in template.items():
        setattr(tree_style, k, v)

phylogeny = {
    "layout_fn": layouts.phylogeny,
    "show_leaf_name":False,
    "draw_guiding_lines":False
}

_DEFAULT_STYLE= {
    PhyloTree: phylogeny,
}
