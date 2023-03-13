import json
from pathlib import Path

from ..treelayout import TreeLayout
from ..faces import RectFace


__all__ = [ "LayoutLastCommonAncestor" ]



with open(Path(__file__).parent / "taxid2color.json") as handle:
    _taxid2color = json.load(handle)

def get_level(node, level=0):
    if node.is_root():
        return level
    else:
        return get_level(node.up, level + 1)



class LayoutLastCommonAncestor(TreeLayout):
    """
    Node properties needed
        :taxid: color
        :sci_name: text shown
    """
    def __init__(self, name="Last common ancestor",
            rect_width=15, column=1000):
        super().__init__(name, aligned_faces=True)

        self.active = True

        self.rect_width = rect_width
        self.column = column

    def get_color(self, node):
        color = node.props.get('sci_name_color', None)
        if color:
            return color

        taxid = node.props.get('taxid', None)
        color = _taxid2color.get(str(taxid))
        if color:
            return color

        return 'lightgray'


    def set_node_style(self, node):
        if node.props.get('sci_name'):
            lca = node.props.get('sci_name')
            color = self.get_color(node)
            
            level = get_level(node, level=self.column)
            lca_face = RectFace(self.rect_width, float('inf'), 
                    color = color, 
                    text = lca,
                    fgcolor = "white",
                    padding_x = 1, padding_y = 1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                collapsed_only=True)
