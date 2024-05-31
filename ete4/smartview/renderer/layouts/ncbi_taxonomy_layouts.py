import os
import json

from ..treelayout import TreeLayout
from ..faces import RectFace

from ete4.config import ETE_DATA_HOME, update_ete_data

__all__ = [ "LayoutLastCommonAncestor" ]


def get_level(node, level=0):
    if node.is_root:
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
        color = node.props.get('sci_name_color')
        if color:
            return color

        # Make sure we have the big file with all the colors.
        taxid2color_file = ETE_DATA_HOME + '/taxid2color.json'

        update_ete_data(taxid2color_file, url='layouts/taxid2color.json')

        with open(taxid2color_file) as handle:
            _taxid2color = json.load(handle)

        # Use it to colorize according to taxid.
        taxid = node.props.get('taxid')
        return _taxid2color.get(taxid, 'lightgray')


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
