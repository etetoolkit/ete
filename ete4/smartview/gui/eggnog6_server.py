from server import run_smartview
from ete4.smartview.renderer.layouts.default_layouts import LayoutLeafName
from ete4.smartview.renderer.layouts.eggnog6_layouts import *


leafname = LayoutLeafName()
leafname.active = False

layouts = [
        leafname,
        LayoutEvolEvents(),
        LayoutLastCommonAncestor(),
        LayoutPfamDomains(),
        LayoutSmartDomains(),
        LayoutScientificName(),
        LayoutBestName(),
        LayoutProteinName(),
        LayoutCazy(),
        LayoutCard(),
        LayoutPdb(),
        LayoutBigg(),
        LayoutKeggNumber(),
        LayoutKeggPathway(),
        LayoutKeggModule(),
        LayoutKeggEnzyme(),
    ]


run_smartview(layouts=layouts, port=8997, host="0.0.0.0", run=True,
        safe_mode=True)
