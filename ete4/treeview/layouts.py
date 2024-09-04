import numpy
from . import faces

def basic(node):
    if node.is_leaf:
        node.img_style["size"]=2
        node.img_style["shape"] = "square"
        faces.add_face_to_node(faces.AttrFace("name","Arial",10,"#4f8f0f",None), node, 0 )

def phylogeny(node):
    leaf_color = "#000000"
    node.img_style["shape"] = "square"
    node.img_style["size"] = 2
    if hasattr(node,"evoltype"):
        if node.evoltype == 'D':
            node.img_style["fgcolor"] = "#FF0000"
            node.img_style["hz_line_color"] = "#FF0000"
            node.img_style["vt_line_color"] = "#FF0000"
        elif node.evoltype == 'S':
            node.img_style["fgcolor"] = "#1d176e"
            node.img_style["hz_line_color"] = "#1d176e"
            node.img_style["vt_line_color"] = "#1d176e"
        elif node.evoltype == 'L':
            node.img_style["fgcolor"] = "#777777"
            node.img_style["vt_line_color"] = "#777777"
            node.img_style["hz_line_color"] = "#777777"
            node.img_style["hz_line_type"] = 1
            node.img_style["vt_line_type"] = 1
            leaf_color = "#777777"

    if node.is_leaf:
        node.img_style["shape"] = "square"
        node.img_style["size"] = 2
        node.img_style["fgcolor"] = leaf_color
        faces.add_face_to_node( faces.AttrFace("name","Arial",11,leaf_color,None), node, 0 )
        if hasattr(node,"sequence"):
            SequenceFace =  faces.SequenceFace(node.sequence,"aa",13)
            faces.add_face_to_node(SequenceFace, node, 1, aligned=True)
    else:
        node.img_style["size"] = 2

def large(node):
    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] = 0


def evol_layout(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    leaf_color = "#000000"
    if not node.is_root and 'w' in node.props:
        node.img_style["shape"] = 'circle'
        if (node.w > 900):
            node._w = 3
        elif (node.w > 100):
            node._w = 2.5
        elif (node.w > 10) :
            node._w = 2
        elif (node.w > 1):
            node._w = 1.5
        else:
            node._w = node.w
        node.img_style["size"] = int ((float(node._w))*6+2)
        if node._w == 3   :
            node.img_style["fgcolor"] = "#c10000"
        if node._w == 2.5 :
            node.img_style["fgcolor"] = "#FF5A02"
        if node._w == 2   :
            node.img_style["fgcolor"] = "#FFA200"
        if node._w == 1.5 :
            node.img_style["fgcolor"] = "#E9BF00"
        if node._w  < 0.2 :
            node.img_style["fgcolor"] = "#000000"
    if hasattr(node,"extras"):
        faces.add_face_to_node( faces.AttrFace("extras", "Arial", 7, \
                                               "#000000", None), node, 2 )
    if hasattr (node, "sequence"):
        seqface =  faces.SequenceFace(node.sequence, interactive=True,
                                      codon=node.nt_sequence)
        faces.add_face_to_node(seqface, node, 1, aligned=True)


def evol_clean_layout(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    leaf_color = "#000000"
    node.img_style["size"] = 2
    if node.is_leaf:
        #if hasattr (node,"highlight"):
        #    faces.add_face_to_node(faces.AttrFace("name", "Arial", 9, \
        #                                          node.highlight,
        #                                          None), \
        #                           node, 0 )
        #else:
        #    leaface = faces.AttrFace("name", "Arial", 9, leaf_color, None)
        #    leaface.margin_right = 10
        #    faces.add_face_to_node (leaface, node, 0)
        if hasattr (node, "sequence"):
            seqface =  faces.SequenceFace(node.sequence, interactive=True,
                                          codon=node.nt_sequence)
            faces.add_face_to_node(seqface, node, 1, aligned=True)
    if hasattr(node, 'dN'):
        faces.add_face_to_node (faces.TextFace('%.4f'%(node.w), fsize=6,
                                               fgcolor="#7D2D2D"),
                                node, 0, position="branch-top")
        faces.add_face_to_node (faces.TextFace('%.2f/%.2f'% (100*node.dN,
                                                             100*node.dS),
                                              fsize=6, fgcolor="#787878"),
                                node, 0, position="branch-bottom")
    if hasattr(node,"extras"):
        faces.add_face_to_node( faces.AttrFace("extras", "Arial", 7, \
                                               "#000000", None), node, 2 )
