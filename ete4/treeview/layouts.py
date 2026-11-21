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
