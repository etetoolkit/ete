from ..faces import RectFace, TextFace

__all__ = [ "get_layout_human_og", "get_layout_UCSC"]

def get_layout_human_og():
    column = 1
    rect_width = 15
    def layout_fn(node):
        
        if node.is_leaf():
            if node.props.get('human_orth'):
                human_orth = " ".join(node.props.get('human_orth').split('|'))
                human_orth_face = TextFace(human_orth, color="blue")
                node.add_face(human_orth_face, column = 4, position = "aligned")

    layout_fn.__name__ = 'Human OGs'
    layout_fn.contains_aligned_face = True
    return layout_fn

def get_layout_UCSC():
    column = 1
    rect_width = 15
    def layout_fn(node):
        
        if node.is_leaf():
            if node.props.get('UCSC'):
                ucsc = node.props.get('UCSC')
                ucsc_face = TextFace(ucsc, color="red")
                node.add_face(ucsc_face, column = 5, position = "aligned")
                node.sm_style["fgcolor"] = "green"
                node.sm_style["size"] = 10

    layout_fn.__name__ = 'UCSC'
    layout_fn.contains_aligned_face = True
    return layout_fn