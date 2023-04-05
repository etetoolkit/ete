import sys

from ... import Tree, SeqMotifFace, TreeStyle, add_face_to_node

seq = "LHGRISQQVEQSRSQVQAIGEKVSLAQAKIEKIKGSKKAIKVFSSAKYPAPERLQEYGSIFTDAQDPGLQRRPRHRIQSKQRPLDERALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSNISSVSSLLLFNTTENLYKKYVFLDPLAGAVTKTHVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPDLGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTPAHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIRQAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHLMSDLFNKLVMRRKGISGKGPGAGDGPGGAFARVSDSIPPLPPPQQPQAEDEDDWES"
motifs = [
    # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
    [10, 100, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|domain Name very long so it should be clipped"],
    [101, 150, "o", None, 10, "blue", "pink", None],
    [155, 180, "()", None, 10, "blue", "rgradient:purple", None],
    [160, 190, "^", None, 14, "black", "yellow", None],
    [172, 180, "v", None, 12, "black", "rgradient:orange", None],
    [185, 190, "o", None, 12, "black", "brown", None],
    [198, 200, "<>", None, 15, "black", "rgradient:gold", None],
    [210, 240, "compactseq", 2, 10, None, None, None],
    [300, 320, "seq", 10, 10, None, None, None],
    [310, 420, "<>", None, 30, "black", "rgradient:black", None],
    [1, 420, "()", None, 10, "red", "red", None],
    [11, 30, "()", None, 20, "blue", "blue", None],
    [300, 310, "()", None, 40, "green", "green", None],
    ]

def layout(node):
    if node.is_leaf():
        seqFace = SeqMotifFace(seq, motifs, scale_factor=1)
        add_face_to_node(seqFace, node, 0, position="aligned")


def get_example_tree():
    # Create a random tree and add to each leaf a random set of motifs
    # from the original set
    t = Tree()
    t.populate(10)
    # for l in t.iter_leaves():
    #     seq_motifs = [list(m) for m in motifs] #sample(motifs, randint(2, len(motifs)))

    #     seqFace = SeqMotifFace(seq, seq_motifs, intermotif_format="line",
    #                            seqtail_format="compactseq", scale_factor=1)
    #     seqFace.margin_bottom = 4
    #     f = l.add_face(seqFace, 0, "aligned")

    ts = TreeStyle()
    ts.layout_fn = layout
    return t, ts

if __name__ == '__main__':
    t, ts = get_example_tree()
    t.render("motifs.png", w=1200, dpi=300, tree_style=ts)
    #t.show(tree_style=ts)
