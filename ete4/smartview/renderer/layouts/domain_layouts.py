import json
from pathlib import Path

from ..treelayout import TreeLayout, _TitleCase
from ..faces import SeqMotifFace
from ..draw_helpers import Padding


with open(Path(__file__).parent / "pfam2color.json") as handle:
    _pfam2color = json.load(handle)

with open(Path(__file__).parent / "smart2color.json") as handle:
    _smart2color = json.load(handle)


class _LayoutDomains(TreeLayout):
    def __init__(self, prop, name,
            column=10, colormap={},
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__(name or "Domains layout")
        self.prop = prop
        self.column = column
        self.aligned_faces = True
        self.colormap = colormap
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

    def get_doms(self, node):
        if node.is_leaf():
            return node.props.get(self.prop, [])
        else:
            first_node = next(node.iter_leaves())
            return first_node.props.get(self.prop, [])

    def parse_doms(self, dom_list):
        doms = []
        for name, start, end in dom_list:
            color = self.colormap.get(name, "lightgray")
            dom = [int(start), int(end), "()", 
                   None, None, color, color,
                   "arial|20|black|%s" %(name)]
            doms.append(dom)
        return doms

    def set_node_style(self, node):
        dom_list = self.get_doms(node)
        doms = self.parse_doms(dom_list)
        fake_seq = '-' * int(node.props.get('len_alg'))
        seqFace = SeqMotifFace(seq=fake_seq, motifs=doms, width=250,
                height=10)
        node.add_face(seqFace, column=self.column, 
                position="aligned",
                collapsed_only=(not node.is_leaf()))


def create_domain_layout(prop, name, colormap, active, column):
    # branch_right; column 2; color black
    class Layout(_LayoutDomains):
        def __init__(self, 
                prop=prop, 
                name=name,
                colormap=colormap,
                column=column,
                *args, **kwargs):
            super().__init__(
                    prop=prop, 
                    name=name,
                    colormap=colormap,
                    column=column,
                    *args, **kwargs)
            self.active = active

        def __name__(self):
            return layout_name
    layout_name = "Layout" + _TitleCase(name)
    Layout.__name__ = layout_name
    globals()[layout_name] = Layout
    return Layout


domain_layout_args = [ 
        [ "pfam",  "Pfam domains",  _pfam2color,  False  ],
        [ "smart", "Smart domains", _smart2color, False  ],
    ]

col0 = 20
domain_layouts = [ create_domain_layout(*args, i+col0)\
                 for i, args in enumerate(domain_layout_args) ]

__all__ = [ *[layout.__name__ for layout in domain_layouts] ]
