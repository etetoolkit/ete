from ..treelayout import TreeLayout, _LayoutNodeProperty, _TitleCase
from ..faces import TextFace

from ..draw_helpers import summary, Padding
from .evol_events_layouts import LayoutEvolEvents
from .ncbi_taxonomy_layouts import LayoutLastCommonAncestor
from .domain_layouts import LayoutPfamDomains, LayoutSmartDomains


def create_property_layout(prop, name, color, pos, active, column):
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
            self.active = active

        def __name__(self):
            return layout_name
    layout_name = "Layout" + _TitleCase(name)
    Layout.__name__ = layout_name
    globals()[layout_name] = Layout
    return Layout


prop_layout_args = [
        [ "sci_name",     "Scientific name", "black", "branch_right", True  ],
        [ "best_name",    "Best name",       "black", "aligned",      True  ],
        [ "prot_name",    "Protein name",    "gray",  "aligned",      True  ],
        [ "cazy",         "Cazy",            "gray",  "aligned",      False ],
        [ "card",         "CARD",            "gray",  "aligned",      False ],
        [ "pdb",          "PDB",             "gray",  "aligned",      False ],
        [ "bigg",         "BIGG",            "gray",  "aligned",      False ],
        [ "kegg_number",  "KEGG number",     "gray",  "aligned",      False ],
        [ "kegg_pathway", "KEGG number",     "gray",  "aligned",      False ],
        [ "kegg_module",  "KEGG module",     "gray",  "aligned",      False ],
        [ "kegg_enzyme",  "KEGG enzyme",     "gray",  "aligned",      False ],
        # [ "GOslim",       "GOslim",          "gray",  "aligned",      False ],
    ]

col0 = 2
prop_layouts = [ create_property_layout(*args, i+col0)\
                 for i, args in enumerate(prop_layout_args) ]


__all__ = [ *[layout.__name__ for layout in prop_layouts],
            "LayoutEvolEvents", "LayoutLastCommonAncestor",
            "LayoutPfamDomains", "LayoutSmartDomains" ]
