# We will need to create Qt4 items
from PyQt4       import QtCore
from PyQt4.QtGui import QGraphicsRectItem, QColor, QPen, QBrush
from PyQt4.QtGui import QGraphicsSimpleTextItem, QFont

from ... import faces, TreeStyle, PhyloTree, TextFace
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


class MySequenceFace(faces.StaticItemFace):
    """ Creates a new molecular sequence face object.


    :argument seq:  Sequence string to be drawn
    :argument seqtype: Type of sequence: "nt" or "aa"
    :argument fsize:   Font size,  (default=10)

    You can set custom colors for amino-acids or nucleotides:

    :argument None  codon       : a string that corresponds to the reverse translation of the amino-acid sequence
    :argument 11    col_w       : width of the column (if col_w is lower than font size, letter wont be displayed)
    :argument None  fg_colors   : dictionary of colors for foreground, with as keys each possible character in sequences, and as value the colors
    :argument None  bg_colors   : dictionary of colors for background, with as keys each possible character in sequences, and as value the colors
    :argument 3     alt_col_w   : works together with special_col option, defines the width of given columns
    :argument None  special_col : list of lists containing the bounds of columns to be displayed with alt_col_w as width
    :argument False interactive : more info can be displayed when mouse over sequence

    """
    def __init__(self, seq, seqtype="aa", fsize=10,
                 fg_colors=None, bg_colors=None,
                 codon=None, col_w=11, alt_col_w=3,
                 special_col=None, interactive=False):
        self.seq         = seq
        self.codon       = codon
        self.fsize       = fsize
        self.style       = seqtype
        self.col_w       = float(col_w)
        self.alt_col_w   = float(alt_col_w)
        self.special_col = special_col if special_col else []
        self.width       = 0 # will store the width of the whole sequence
        self.interact    = interactive

        if self.style == "aa":
            if not fg_colors:
                fg_colors = _aafgcolors
            if not bg_colors:
                bg_colors = _aabgcolors
        else:
            if not fg_colors:
                fg_colors = _ntfgcolors
            if not bg_colors:
                bg_colors = _ntbgcolors

        self.fg_col = self.__init_col(fg_colors)
        self.bg_col = self.__init_col(bg_colors)

        # for future?
        self.row_h       = 13.0

        super(MySequenceFace,
              self).__init__(QGraphicsRectItem(0, 0, self.width, self.row_h))

    def __init_col(self, color_dic):
        """to speed up the drawing of colored rectangles and characters"""
        new_color_dic = {}
        for car in color_dic:
            new_color_dic[car] = QBrush(QColor(color_dic[car]))
        return new_color_dic

    def update_items(self):
        #self.item = QGraphicsRectItem(0,0,self._total_w, self.row_h)
        seq_width = 0
        nopen = QPen(QtCore.Qt.NoPen)
        font = QFont("Courier", self.fsize)
        rect_cls = self.InteractiveLetterItem if self.interact else QGraphicsRectItem
        for i, letter in enumerate(self.seq):
            width = self.col_w
            for m in self.special_col:
                if m[0] < i <= m[1]:
                    width = self.alt_col_w
                    break
            #load interactive item if called correspondingly
            rectItem = rect_cls(0, 0, width, self.row_h, parent=self.item)
            rectItem.setX(seq_width) # to give correct X to children item
            rectItem.setBrush(self.bg_col[letter])
            rectItem.setPen(nopen)
            if self.interact:
                if self.codon:
                    rectItem.codon = '%s, %d: %s' % (self.seq[i], i,
                                                     self.codon[i*3:i*3+3])
                else:
                    rectItem.codon = '%s, %d' % (self.seq[i], i)
            # write letter if enough space
            if width >= self.fsize:
                text = QGraphicsSimpleTextItem(letter, parent=rectItem)
                text.setFont(font)
                text.setBrush(self.fg_col[letter])
                # Center text according to rectItem size
                tw = text.boundingRect().width()
                th = text.boundingRect().height()
                text.setPos((width - tw)/2, (self.row_h - th)/2)
            seq_width += width
        self.width = seq_width

    class InteractiveLetterItem(QGraphicsRectItem):
        """This is a class"""
        def __init__(self, *arg, **karg):
            QGraphicsRectItem.__init__(self, *arg, **karg)
            self.codon = None
            self.label = None
            self.setAcceptsHoverEvents(True)

        def hoverEnterEvent (self, e):
            """ when mouse is over"""
            if not self.label:
                self.label = QGraphicsRectItem(parent=self)
                #self.label.setY(-18)
                self.label.setX(11)
                self.label.setBrush(QBrush(QColor("white")))
                self.label.text = QGraphicsSimpleTextItem(parent=self.label)

            self.setZValue(1)
            self.label.text.setText(self.codon)
            self.label.setRect(self.label.text.boundingRect())
            self.label.setVisible(True)

        def hoverLeaveEvent(self, e):
            """when mouse leaves area"""
            if self.label:
                self.label.setVisible(False)
                self.setZValue(0)



def test_layout_evol(node):
    '''
    layout for CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    if node.is_leaf():
        if hasattr (node, "sequence"):
            seqface =  MySequenceFace(node.sequence, "aa",
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
            seqface =  MySequenceFace(node.sequence, "aa",
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
            seqface =  MySequenceFace(node.sequence, "aa",
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
            seqface =  MySequenceFace(node.sequence, "nt",
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
