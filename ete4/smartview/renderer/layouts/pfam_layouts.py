import json
from pathlib import Path

from ..treelayout import TreeLayout
from ..faces import SeqMotifFace
from ..draw_helpers import Padding


with open(Path(__file__).parent / "pfam2color.json") as handle:
    _pfam2color = json.load(handle)


class LayoutPfamDomains(TreeLayout):
    def __init__(self, prop="pfam",
            column=10, color='black',
            ftype='sans-serif',
            min_fsize=4, max_fsize=15,
            padding_x=5, padding_y=0):
        super().__init__("Pfam domains")
        self.prop = prop
        self.column = column
        self.aligned_faces = True
        self.color = color
        self.ftype = ftype
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self.padding = Padding(padding_x, padding_y)


    def get_pfam_doms(self, node):
        if node.is_leaf():
            dom_arq = node.props.get(self.prop)
            return dom_arq
        else:
            first_node = next(node.iter_leaves())
            return first_node.props.get(self.prop)

    def parse_pfam_doms(self, dom_string):
        doms = []
        for d in dom_string.split('|'):
            name, start, end = d.split('@')
            color = _pfam2color.get(name, "lightgray")
            dom = [int(start), int(end), "()", 
                   None, None, color, color,
                   "arial|20|black|%s" %(name)]
            doms.append(dom)
        return doms

    def set_node_style(self, node):
        dom_string = self.get_pfam_doms(node)
        if dom_string:
            print(dom_string)
            doms = self.parse_pfam_doms(dom_string)
            fake_seq = '-' * int(node.props.get('len_alg'))
            seqFace = SeqMotifFace(seq=fake_seq, motifs=doms, width=500)
            node.add_face(seqFace, column=self.column, 
                    position="aligned",
                    collapsed_only=(not node.is_leaf()))
