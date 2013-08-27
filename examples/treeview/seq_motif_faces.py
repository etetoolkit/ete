import sys

from ete_dev import Tree, SeqMotifFace, TreeStyle

def get_example_tree():

    # sample sequence and a list of example motif types     
    seq = "LHGRISQQVEQSRSQVQAIGEKVSLAQAKIEKIKGSKKAIKVFSSAKYPAPERLQEYGSIFTDAQDPGLQRRPRHRIQSKQRPLDERALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSNISSVSSLLLFNTTENLYKKYVFLDPLAGAVTKTHVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPDLGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTPAHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIRQAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHLMSDLFNKLVMRRKGISGKGPGAGDGPGGAFARVSDSIPPLPPPQQPQAEDEDDWES"
    motifs = [
        # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
        [10, 100, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|domain Name"],
        [110, 150, "o", None, 10, "blue", "pink", None],
        [155, 180, "()", None, 10, "blue", "rgradient:purple", None],
        [160, 170, "^", None, 14, "black", "yellow", None],
        [172, 180, "v", None, 12, "black", "rgradient:orange", None],
        [185, 190, "o", None, 12, "black", "brown", None],
        [198, 200, "<>", None, 15, "black", "rgradient:gold", None],
        [210, 240, "compactseq", 2, 10, None, None, None],
        [300, 320, "seq", 10, 10, None, None, None],
        [310, 345, "<>", None, 15, "black", "rgradient:black", None],
    ]
    # Create a random tree and add to each leaf a random set of motifs
    # from the original set
    t = Tree()
    t.populate(10)
    for l in t.iter_leaves():
        seq_motifs = [list(m) for m in motifs] #sample(motifs, randint(2, len(motifs))) 

        seqFace = SeqMotifFace(seq, seq_motifs, intermotif_format="line",
                               seqtail_format="compactseq", scale_factor=1)
        seqFace.margin_bottom = 4
        f = l.add_face(seqFace, 0, "aligned")

    return t, TreeStyle()

if __name__ == '__main__':
    t, ts = get_example_tree()

    #t.render("bubble_map.png", w=600, dpi=300, tree_style=ts)
    t.show(tree_style=ts)
