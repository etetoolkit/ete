# We will need to create Qt4 items
from ...treeview.qt import QtCore
from ...treeview.qt import QGraphicsRectItem, QColor, QPen, QBrush
from ...treeview.qt import QGraphicsSimpleTextItem, QFont

from ... import faces, TreeStyle, PhyloTree, TextFace, SequenceFace
from random import random

_aafgcolors = {
    'A':"#000000" ,
    'R':"#000000" ,
    'N':"#000000" ,
    'D':"#000000" ,
    'C':"#000000" ,
    'Q':"#000000" ,
    'E':"#000000" ,
    'G':"#000000" ,
    'H':"#000000" ,
    'I':"#000000" ,
    'L':"#000000" ,
    'K':"#000000" ,
    'M':"#000000" ,
    'F':"#000000" ,
    'P':"#000000" ,
    'S':"#000000" ,
    'T':"#000000" ,
    'W':"#000000" ,
    'Y':"#000000" ,
    'V':"#000000" ,
    'B':"#000000" ,
    'Z':"#000000" ,
    'X':"#000000",
    '.':"#000000",
    '-':"#000000",
}

_aabgcolors = {
    'A':"#C8C8C8" ,
    'R':"#145AFF" ,
    'N':"#00DCDC" ,
    'D':"#E60A0A" ,
    'C':"#E6E600" ,
    'Q':"#00DCDC" ,
    'E':"#E60A0A" ,
    'G':"#EBEBEB" ,
    'H':"#8282D2" ,
    'I':"#0F820F" ,
    'L':"#0F820F" ,
    'K':"#145AFF" ,
    'M':"#E6E600" ,
    'F':"#3232AA" ,
    'P':"#DC9682" ,
    'S':"#FA9600" ,
    'T':"#FA9600" ,
    'W':"#B45AB4" ,
    'Y':"#3232AA" ,
    'V':"#0F820F" ,
    'B':"#FF69B4" ,
    'Z':"#FF69B4" ,
    'X':"#BEA06E",
    '.':"#FFFFFF",
    '-':"#FFFFFF",
    }

_ntfgcolors = {
    'A':'#000000',
    'G':'#000000',
    'I':'#000000',
    'C':'#000000',
    'T':'#000000',
    'U':'#000000',
    '.':"#000000",
    '-':"#000000",
    ' ':"#000000"
    }

_ntbgcolors = {
    'A':'#A0A0FF',
    'G':'#FF7070',
    'I':'#80FFFF',
    'C':'#FF8C4B',
    'T':'#A0FFA0',
    'U':'#FF8080',
    '.':"#FFFFFF",
    '-':"#FFFFFF",
    ' ':"#FFFFFF"
}



def test_layout_evol(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if node.is_leaf():
        if hasattr (node, "sequence"):
            seqface =  SequenceFace(node.sequence, "aa",
                                      codon=node.nt_sequence, fsize=10,
                                      col_w=11, interactive=True)
            faces.add_face_to_node(seqface, node, 1, aligned=True)

def test_layout_phylo_aa(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if node.is_leaf():
        if hasattr (node, "sequence"):
            seqface = SequenceFace(node.sequence, "aa",
                                      fsize=10,
                                      col_w=11, interactive=False)
            faces.add_face_to_node(seqface, node, 1, aligned=True)


def test_layout_phylo_aa_motif(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    special_col = [[10,100],[150,1000],[1000,2000],[3000,4990]]
    if node.is_leaf():
        if hasattr (node, "sequence"):
            seqface = SequenceFace(node.sequence, "aa",
                                      fsize=10,special_col=special_col,
                                      alt_col_w=3,
                                      col_w=11, interactive=True)
            faces.add_face_to_node(seqface, node, 1, aligned=True)


def test_layout_phylo_nt(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if node.is_leaf():
        if hasattr (node, "sequence"):
            seqface =  SequenceFace(node.sequence, "nt",
                                      fsize=10,
                                      col_w=11, interactive=True)
            faces.add_face_to_node(seqface, node, 1, aligned=True)


if __name__ == "__main__":
    tree = PhyloTree('(Orangutan,Human,Chimp);')
    tree.link_to_alignment("""
                           >Chimp
                           HARWLNEKLRCELRTLKKLGLDGYKAVSQYVKGRA
                           >Orangutan
                           DARWINEKLRCVSRTLKKLGLDGYKGVSQYVKGRP
                           >Human
                           DARWHNVKLRCELRTLKKLGLVGFKAVSQFVIRRA
                           """)
    nt_sequences = {"Human"    : "GACGCACGGTGGCACAACGTAAAATTAAGATGTGAATTGAGAACTCTGAAAAAATTGGGACTGGTCGGCTTCAAGGCAGTAAGTCAATTCGTAATACGTCGTGCG",
                    "Chimp"    : "CACGCCCGATGGCTCAACGAAAAGTTAAGATGCGAATTGAGAACTCTGAAAAAATTGGGACTGGACGGCTACAAGGCAGTAAGTCAGTACGTTAAAGGTCGTGCG",
                    "Orangutan": "GATGCACGCTGGATCAACGAAAAGTTAAGATGCGTATCGAGAACTCTGAAAAAATTGGGACTGGACGGCTACAAGGGAGTAAGTCAATACGTTAAAGGTCGTCCG"
                }
    for l in nt_sequences:
        (tree & l).nt_sequence = nt_sequences[l]
    tree.dist = 0
    ts = TreeStyle()
    ts.title.add_face(TextFace("Example for nucleotides...", fsize=15), column=0)
    ts.layout_fn = test_layout_evol
    tree.show(tree_style=ts)

    # Show very large algs
    tree = PhyloTree('(Orangutan,Human,Chimp);')
    tree.link_to_alignment(">Human\n"       + ''.join([_aabgcolors.keys()[int(random() * len (_aabgcolors))] for _ in range(5000)]) + \
                           "\n>Chimp\n"     + ''.join([_aabgcolors.keys()[int(random() * len (_aabgcolors))] for _ in range(5000)]) + \
                           "\n>Orangutan\n" + ''.join([_aabgcolors.keys()[int(random() * len (_aabgcolors))] for _ in range(5000)]))
    tree.dist = 0
    ts = TreeStyle()
    ts.title.add_face(TextFace("better not set interactivity if alg is very large", fsize=15), column=0)
    ts.layout_fn = test_layout_phylo_aa

    tree.show(tree_style=ts)
