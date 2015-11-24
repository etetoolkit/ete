import sys
from ete3 import Tree, SeqMotifFace, TreeStyle, add_face_to_node

seq = ("-----------------------------------------------AQAK---IKGSKKAIKVFSSA---"
      "APERLQEYGSIFTDA---GLQRRPRHRIQSK-------ALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSN"
      "ISSVSSLLLFNTTENLYKKYVFLDPLAG----THVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPD"
      "LGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTP"
      "AHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIR"
      "QAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHL--MSDLFNKLVMRRKGISGKGPGAGDGPGGAFA"
      "RVSDSIPPLPPPQQPQAEDED----")

mixed_motifs = [
        # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
        [10, 100, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|long text clipped long text clipped"],
        [101, 150, "o", None, 10, "blue", "pink", None],
        [155, 180, "()", None, 10, "blue", "rgradient:purple", None],
        [160, 190, "^", None, 14, "black", "yellow", None],
        [191, 200, "<>", None, 12, "black", "rgradient:orange", None],
        [201, 250, "o", None, 12, "black", "brown", None],
        [351, 370, "v", None, 15, "black", "rgradient:gold", None],
        [370, 420, "compactseq", 2, 10, None, None, None],
]

simple_motifs = [
        # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
        [10, 60, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|long text clipped long text clipped"],
        [120, 150, "o", None, 10, "blue", "pink", None],
        [200, 300, "()", None, 10, "blue", "red", "arial|8|white|hello"],
]

box_motifs = [
        # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
        [0,  5, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|10"],
        [10, 25, "[]", None, 10, "black", "rgradient:ref", "arial|8|white|10"],
        [30, 45, "[]", None, 10, "black", "rgradient:orange", "arial|8|white|20"],
        [50, 65, "[]", None, 10, "black", "rgradient:pink", "arial|8|white|20"],
        [70, 85, "[]", None, 10, "black", "rgradient:green", "arial|8|white|20"],
        [90, 105, "[]", None, 10, "black", "rgradient:brown", "arial|8|white|20"],
        [110, 125, "[]", None, 10, "black", "rgradient:yellow", "arial|8|white|20"],
]

def get_example_tree():
        # Create a random tree and add to each leaf a random set of motifs
        # from the original set
        t = Tree("( (A, B, C, D, E, F, G), H, I);")

        seqFace = SeqMotifFace(seq, gapcolor="red")
        (t & "A").add_face(seqFace, 0, "aligned")

        seqFace = SeqMotifFace(seq, seq_format="line", gap_format="blank")
        (t & "B").add_face(seqFace, 0, "aligned")

        seqFace = SeqMotifFace(seq, seq_format="line")
        (t & "C").add_face(seqFace, 0, "aligned")
        
        seqFace = SeqMotifFace(seq, seq_format="()")
        (t & "D").add_face(seqFace, 0, "aligned")

        seqFace = SeqMotifFace(seq, motifs=simple_motifs, seq_format="-")
        (t & "E").add_face(seqFace, 0, "aligned")

        seqFace = SeqMotifFace(seq=None, motifs=simple_motifs, gap_format="blank")
        (t & "F").add_face(seqFace, 0, "aligned")

        seqFace = SeqMotifFace(seq, motifs=mixed_motifs, seq_format="-")
        (t & "G").add_face(seqFace, 0, "aligned")

        
        seqFace = SeqMotifFace(seq=None, motifs=box_motifs, gap_format="line")
        (t & "H").add_face(seqFace, 0, "aligned")


        seqFace = SeqMotifFace(seq[30:60], seq_format="seq")
        (t & "I").add_face(seqFace, 0, "aligned")
        
        return t
        
if __name__ == '__main__':
    t = get_example_tree()
    ts = TreeStyle()
    ts.tree_width = 50
    #t.show(tree_style=ts)
    t.render("seq_motif_faces.png", tree_style=ts)
