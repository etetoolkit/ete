#!/usr/bin/python
"""
07 Nov 2010

layout for codeml trees
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete_dev import faces

def codeml_layout(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    leaf_color = "#000000"
    if not node.is_root() and 'w' in node.features:
        node.img_style["shape"] = 'sphere'
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
        node.img_style["size"] = int ((float(node._w))*6+1)
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
        name = ''
        textface = faces.TextFace(name, "Arial", 12, "#000000")
        faces.add_face_to_node(textface, node, 1)
    else:
        node.dist = float(0)
        node.support = float(0)
    if hasattr(node,"extras"):
        faces.add_face_to_node( faces.AttrFace("extras", "Arial", 7, \
                                               "#000000", None), node, 2 )
    if node.is_leaf():
        if hasattr(node,"highlight"):
            faces.add_face_to_node(faces.AttrFace("name", "Arial", 11, \
                                                  node.highlight, None), \
                                   node, 0 )
        else:
            faces.add_face_to_node( faces.AttrFace("name", "Arial", 11, \
                                                   leaf_color, None), node, 0 )
        if hasattr(node, "sequence"):
            seqface =  faces.SequenceFace(node.sequence, "aa", 11)
            faces.add_face_to_node(seqface, node, 1, aligned=True)



if __name__ == "__main__":
    exit(main())
