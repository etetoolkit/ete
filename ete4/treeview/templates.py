from .. import PhyloTree, EvolTree, EvolNode
from . import layouts

def apply_template(tree_style, template):
    for k, v in template.items():
        setattr(tree_style, k, v)

phylogeny = {
    "layout_fn": layouts.phylogeny,
    "show_leaf_name":False,
    "draw_guiding_lines":False
}

evol = {
    "layout_fn": layouts.evol_layout,
    "show_leaf_name":True,
    "draw_guiding_lines":False
}

_DEFAULT_STYLE= {
    PhyloTree: phylogeny,
    EvolTree: evol,
    EvolNode: evol,
}
