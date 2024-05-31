# TODO: This file needs reviewing. No need to do all this just to get
# classes LayoutPfamDomains and LayoutSmartDomains.
import os
import json

from ..treelayout import TreeLayout, cased_name
from ..faces import SeqMotifFace
from ..draw_helpers import Padding

from ete4.config import ETE_DATA_HOME, update_ete_data


class _LayoutDomains(TreeLayout):
    def __init__(self, prop, name, column=10, min_fsize=4, max_fsize=15,
                 padding_x=5, padding_y=0):
        super().__init__(name or "Domains layout")
        self.prop = prop
        self.column = column
        self.aligned_faces = True
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)

        # Load colormap from file if necessary.
        color_file = ETE_DATA_HOME + f'/{prop}2color.json'

        # Make sure the color file is up-to-date.
        update_ete_data(color_file, url=f'layouts/{prop}2color.json')

        with open(color_file) as handle:
            self.colormap = json.load(handle)

    def get_doms(self, node):
        leaf = next(node.leaves())  # 1st leaf
        return leaf.props.get(self.prop, [])

    def parse_doms(self, dom_list):
        def translate(dom):
            name, start, end = dom
            color = self.colormap.get(name, 'lightgray')
            return [int(start), int(end), '()', None, None, color, color,
                    f'arial|20|black|{name}']

        return [translate(dom) for dom in dom_list]

    def set_node_style(self, node):
        doms = self.parse_doms(self.get_doms(node))
        fake_seq = '-' * int(node.props.get('len_alg', 0))
        if doms or fake_seq:
            seqFace = SeqMotifFace(seq=fake_seq, motifs=doms, width=250, height=10)
            node.add_face(seqFace, column=self.column, position='aligned',
                          collapsed_only=(not node.is_leaf))


def create_domain_layout(prop, name, active, column):
    """Add a layout named Layout<name> to the globals, and return it."""
    # Because this is the wild west, apparently.
    class Layout(_LayoutDomains):
        def __init__(self, prop=prop, name=name, column=column, *args, **kwargs):
            super().__init__(prop=prop, name=name, column=column, *args, **kwargs)
            self.active = active

        def __name__(self):
            return layout_name

    # Let's play with the environment like there's no tomorrow!
    layout_name = "Layout" + cased_name(name)
    Layout.__name__ = layout_name
    globals()[layout_name] = Layout
    return Layout


domain_layout_args = [
    ["pfam", "Pfam domains", True],
    ["smart", "Smart domains", False],
]

col0 = 20
domain_layouts = [create_domain_layout(*args, i+col0)
                  for i, args in enumerate(domain_layout_args)]

__all__ = [ *[layout.__name__ for layout in domain_layouts] ]
