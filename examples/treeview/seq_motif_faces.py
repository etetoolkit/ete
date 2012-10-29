from ete_dev import Tree, SeqMotifFace

from random import sample, randint
from copy import deepcopy
       
# We will use the same amino acid sequence for all leafs. 
seq = "LHGRISQQVEQSRSQVQAIGEKVSLAQAKIEKIKGSKKAIKVFSSAKYPAPERLQEYGSIFTDAQDPGLQRRPRHRIQSKQRPLDERALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSNISSVSSLLLFNTTENLYKKYVFLDPLAGAVTKTHVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPDLGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTPAHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIRQAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHLMSDLFNKLVMRRKGISGKGPGAGDGPGGAFARVSDSIPPLPPPQQPQAEDEDDWES"

# Create some example motifs referred to the previous sequence. Each
# line represents a new motif, with its shape, size and color configuration.
motifs = [
    # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
    [120, 130, ">",  34, 13, "black", "red", None],
    [145, 150, "<",  60, 5, "black", "green", "Verdana|10|white|Triangle"],
    [10,  30,  "o",  100, 10, "black", "rgradient:blue", None],
    [31,  50,  "[]", 100, 10, "blue", "pink", "Verdana|10|black|DomainName"],
    [55,  80,  "()", 100, 10, "blue", "rgradient:purple", "Verdana|15|black|DomainName"],
    [160, 170, "^",  50, 14, "black", "yellow", None],
    [172, 180, "v",  20, 12, "black", "rgradient:orange", None],
    [185, 190, "o",  12, 12, "black", "brown", "Arial|12|white|Domain"],
    [198, 200, "<>", 15, 15, "black", "rgradient:gold", None],
    [210, 240, "compactseq", 2, 10, None, None, None],
    [300, 320, "seq", 20, 20, None, None, "Courier|10|red|TestName"],
    [340, 350, "<>", 15, 15, "black", "rgradient:black", "Arial|12|black|HOLASEQ"],
]

# Create a random tree and add to each leaf a random set of motifs
# from the original set
t = Tree()
t.populate(20)
for l in t.iter_leaves():
    # For each leaf, we create a random list of motifs from the original list.
    seq_motifs = sample(motifs, randint(2, len(motifs))) 
    # And we add it as a Sequence Motif Face. 
    seqFace = SeqMotifFace(seq, seq_motifs, intermotif_format="line", seqtail_format="compactseq")
    seqFace.margin_bottom = 4
    f = l.add_face(seqFace, 0, "aligned")


t.render("seq_motif_faces.png", w=1000)
#t.show()
