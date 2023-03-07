from ..faces import RectFace, TextFace
from ..treelayout import TreeLayout

__all__ = [ "LayoutHumanOGs", "LayoutUCSC", "LayoutUCSCtrans"]


class LayoutHumanOGs(TreeLayout):
    def __init__(self, name="Human OGs", human_orth_prop="human_orth",
                 column=5, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.human_orth_prop = human_orth_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            human_orth = node.props.get(self.human_orth_prop)
            if human_orth:
                human_orth = " ".join(human_orth.split('|'))
                human_orth_face = TextFace(human_orth, color=self.color)
                node.add_face(human_orth_face, column=self.column, position="aligned")

class LayoutUCSC(TreeLayout):
    def __init__(self, name="UCSC", column=6, 
                 nodecolor="#800000", nodesize=5,
                 textcolor="#c43b5d"):
        super().__init__(name)
        self.aligned_faces = True
        self.column = column
        self.nodecolor = nodecolor
        self.nodesize = nodesize
        self.textcolor = textcolor

    def set_node_style(self, node):
         if node.is_leaf():
            if node.props.get('UCSC'):
                ucsc = node.props.get('UCSC')
                ucsc_face = TextFace(ucsc, color=self.textcolor)
                node.add_face(ucsc_face, column=self.column, position="aligned")
                node.sm_style["bgcolor"] = self.nodecolor # highligh clade
                while (node):
                    node = node.up
                    if node:
                        node.sm_style["hz_line_width"] = self.nodesize

class LayoutUCSCtrans(TreeLayout):
    def __init__(self, name="UCSC Trans", ucsc_trans_prop="ucsc_trans",
                 column=4, color="#6b92d6"):
        super().__init__(name)
        self.aligned_faces = True
        self.ucsc_trans_prop = ucsc_trans_prop
        self.column = column
        self.color = color

    def set_node_style(self, node):
        if node.is_leaf():
            ucsc_trans = node.props.get(self.ucsc_trans_prop)
            if ucsc_trans:
                ucsc_trans = " ".join(ucsc_trans.split('|'))
                ucsc_trans_face = TextFace(ucsc_trans, color=self.color)
                node.add_face(ucsc_trans_face, column=self.column, position="aligned")
