from ete_dev import PhyloTree, PhyloNode, ClusterTree, ClusterNode
import layouts 

def apply_template(tree_style, template):
    for k, v in template.iteritems(): 
        setattr(tree_style, k, v)

phylogeny = {
    "layout_fn": layouts.phylogeny, 
     "show_leaf_name":False, 
     "draw_guiding_lines":False
    }


clustering = {
    "layout_fn": layouts.large, 
    "show_leaf_name":False
    }

_DEFAULT_STYLE={
    PhyloTree: phylogeny,
    PhyloNode: phylogeny,
    ClusterTree: clustering,
    ClusterNode: clustering, 
    }
