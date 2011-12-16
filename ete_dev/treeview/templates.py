from ete_dev import PhyloTree, ClusterTree


def apply_template(tree_style, template):
    for k, v in template.iteritems(): 
        setattr(tree_style, k, v)

phylogeny = {
    "layout_fn":"phylogeny", 
     "show_leaf_name":False, 
     "draw_guiding_lines":False
    }


clustering = {
    "layout_fn":"large", 
    "show_leaf_name":False
    }

_DEFAULT_STYLE={
    PhyloTree: phylogeny,
    ClusterTree: clustering, 
    }
