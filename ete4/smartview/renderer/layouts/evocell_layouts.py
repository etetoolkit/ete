from ..faces import RectFace, TextFace
from ..treelayout import TreeLayout

__all__ = [ "LayoutHumanOGs", "LayoutUCSC"]


class LayoutHumanOGs(TreeLayout):
    def __init__(self, name="Human OGs", human_orth_prop="human_orth",
                 column=4, color="#6b92d6"):
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
    def __init__(self, name="UCSC", column=5, 
                 nodecolor="#3f8c3f", nodesize=5,
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
                node.sm_style["fgcolor"] = self.nodecolor
                node.sm_style["size"] = self.nodesize
