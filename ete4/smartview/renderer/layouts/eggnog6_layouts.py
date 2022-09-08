from ..treelayout import TreeLayout, _LayoutNodeProperty
from ..faces import TextFace

from ..draw_helpers import summary, Padding
from .evol_events_layouts import LayoutEvolEvents
from .ncbi_taxonomy_layouts import LayoutLastCommonAncestor
from .pfam_layouts import LayoutPfamDomains


def TitleCase(string):
    return "".join(x.title() for x in string.replace("_", " ").split())

def create_property_layout(prop, name, color, pos, column):
    # branch_right; column 2; color black
    class Layout(_LayoutNodeProperty):
        def __init__(self, 
                prop=prop, 
                name=name,
                pos=pos, 
                column=column,
                color=color,
                *args, **kwargs):
            super().__init__(
                    prop=prop, 
                    name=name,
                    pos=pos,
                    column=column,
                    color=color, 
                    *args, **kwargs)
        def __name__(self):
            return layout_name
    layout_name = "Layout" + TitleCase(name)
    Layout.__name__ = layout_name
    globals()[layout_name] = Layout
    return Layout


prop_layout_args = [
        [ "sci_name",     "Scientific name", "black", "branch_right" ],
        [ "prot_name",    "Protein name",    "gray",  "aligned"      ],
        [ "alias",        "Best name",       "black", "aligned"      ],
        [ "cazy",         "Cazy",            "gray",  "aligned"      ],
        [ "card",         "CARD",            "gray",  "aligned"      ],
        [ "pdb",          "PDB",             "gray",  "aligned"      ],
        [ "bigg",         "BIGG",            "gray",  "aligned"      ],
        [ "goslim",       "GOslim",          "gray",  "aligned"      ],
        [ "kegg_number",  "KEGG number",     "gray",  "aligned"      ],
        [ "kegg_pathway", "KEGG number",     "gray",  "aligned"      ],
        [ "kegg_module",  "KEGG module",     "gray",  "aligned"      ],
        [ "kegg_enzyme",  "KEGG enzyme",     "gray",  "aligned"      ],
    ]

col0 = 2
prop_layouts = [ create_property_layout(*args, i+col0)\
                 for i, args in enumerate(prop_layout_args) ]


__all__ = [ *[layout.__name__ for layout in prop_layouts],
            "LayoutEvolEvents", "LayoutLastCommonAncestor",
            "LayoutPfamDomains", ]
