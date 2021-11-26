from ete4.smartview.ete.faces import RectFace, TextFace
from collections import OrderedDict

__all__ = [ "get_layout_sciname", "get_layout_gnames", "get_layout_ogs_egg5",
        "get_layout_evoltype", "get_layout_lca_rects" ]


def get_level(node, level=0):
    if node.is_root():
        return level
    else:
        return get_level(node.up, level + 1)


def get_layout_sciname():
    def summary(nodes):
        "Return a list of names summarizing the given list of nodes"
        return list(OrderedDict((first_name(node), None) for node in nodes).keys())

    def first_name(tree):
        "Return the name of the first node that has a name"
        sci_names = []
        for node in tree.traverse('preorder'):
            if node.is_leaf():
                sci_name = node.props.get('sci_name')
                sci_names.append(sci_name)
        return next(iter(sci_names))


    def layout_fn(node):
        if node.is_leaf():
           
            sci_name = node.props.get('sci_name')
            name_seq = node.name.split('.',1)[1]

            node.add_face(TextFace(sci_name, color = 'black', padding_x=2),
                column=0, position="branch_right")

            node.add_face(TextFace(name_seq, color = 'grey', padding_x=2),
                column=1, position="branch_right")

        else:
            # Collapsed face
            names = summary(node.children)
            texts = names if len(names) < 6 else (names[:3] + ['...'] + names[-2:])
            for i, text in enumerate(texts):
                node.add_face(TextFace(text, padding_x=2),
                        position="branch_right", column=1, collapsed_only=True)

    layout_fn.__name__ = 'Scientific name'
    layout_fn.contains_aligned_face = True
    return layout_fn


def get_layout_gnames():

    def layout_fn(node):
        if node.props.get('gname'):
            gname= node.props.get('gname')
            color = node.props.get('gname_color')
            gname_face = TextFace(gname, color=color)

            if node.is_leaf():
                node.add_face(gname_face, column = 1, position = "aligned")

            else:
                node.add_face(gname_face, column = 1, position = "aligned", collapsed_only=True) 

    layout_fn.__name__ = 'Gene names'
    layout_fn.contains_aligned_face = True
    return layout_fn


def get_layout_ogs_egg5():

    def layout_fn(node):

        if node.props.get('og_egg5'):
            color = node.props.get('og_egg5_color')
            f = RectFace(10, 10, color=color)

            if node.is_leaf():
                node.add_face(f,  column=2, position="aligned")
            else:
                node.add_face(f,  column=2, position="aligned",  collapsed_only=True)
    
    layout_fn.__name__ = 'OGs egg5'
    layout_fn.contains_aligned_face = True
    return layout_fn


def get_layout_evoltype():
    def layout_fn(node):
        if not node.is_leaf():
            if node.props.get('evoltype_2') == 'S':
                node.img_style["fgcolor"] = 'blue'
                node.img_style["size"] = 2

            elif node.props.get('evoltype_2') == 'D':
                node.img_style["fgcolor"] = 'red'
                node.img_style["size"] = 2

            elif node.props.get('evoltype_2') == 'FD':
                node.img_style["fgcolor"] = 'Coral'
                node.img_style["size"] = 2

            if node.props.get('is_og'):
                node.img_style['size'] = 5
                if node.up.props.get('lca'):
                    color = node.up.props.get('Lca_color')
                else:
                    color = node.props.get('Lca_color')
                node.img_style["fgcolor"] = color

    layout_fn.__name__ = 'Evolution events'
    return layout_fn


def get_layout_lca_rects():

    def layout_fn(node):
       
        if node.props.get('lca_node_name'):
            lca = node.props.get('lca_node_name')
            color = node.props.get('Lca_color')
            level = get_level(node)
            lca_face = RectFace(15, float('inf'), 
                    color=color, 
                    text=lca,
                    fgcolor="white",
                    padding_x=1, padding_y=1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                    collapsed_only=True)

    layout_fn.__name__ = 'Last common ancestor'
    layout_fn.contains_aligned_face = True
    return layout_fn
