from ..treelayout import TreeLayout
from ..faces import RectFace


__all__ = [ "LayoutLastCommonAncestor" ]



def get_level(node, level=0):
    if node.is_root():
        return level
    else:
        return get_level(node.up, level + 1)


class LayoutLastCommonAncestor(TreeLayout):
    def __init__(self, name="Last common ancestor", 
            speciation_color="blue", duplication_color="red"):
        super().__init__(name, aligned_faces=True)

    def set_node_style(self, node):
        if node.props.get('sci_name'):
            lca = node.props.get('sci_name')
            color = node.props.get('sci_name_color', 'lightgray')
            
            level = get_level(node)
            lca_face = RectFace(15, float('inf'), 
                    color = color, 
                    text = lca,
                    fgcolor = "white",
                    padding_x = 1, padding_y = 1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                collapsed_only=True)
