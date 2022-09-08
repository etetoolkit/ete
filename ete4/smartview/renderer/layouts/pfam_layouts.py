from ..treelayout import TreeLayout
from ..faces import SeqMotifFace



class LayoutPfamDomains(TreeLayout):
    def __init__(self, prop="dom_arq",
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
            dom_arq = node.props.get("dom_arq")
            return dom_arq
        else:
            first_node = next(node.iter_leaves())
            return first_node.props.get('dom_arq')

    def parse_pfam_doms(self, dom_string):
        doms = []
        for d in doms_string.split('|'):
            d_info = d.split('@')
            dom = [int(d_info[1]), int(d_info[2]), "()", 
                   None, None, 'grey', 'grey',
                   "arial|20|black|%s" %(d_info[0])]
            doms.append(dom)
        return doms

    def set_node_style(self, node):
        dom_string = self.get_pfam_doms(node)
        if dom_string:
            doms = self.parse_pfam_doms(dom_string)
            seqFace = SeqMotifFace(seq=None, motifs = doms)
            node.add_face(seqFace, column=self.column, 
                    position="aligned",
                    collapsed_only=(not node.is_leaf()))
