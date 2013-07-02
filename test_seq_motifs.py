import sys
sys.path.insert(0, "./")
from ete_dev import faces, Tree, SeqMotifFace
 
from random import sample, randint
from copy import deepcopy
       
# sample sequence and a list of example motif types     
seq = "LHGRISQQVEQSRSQVQAIGEKVSLAQAKIEKIKGSKKAIKVFSSAKYPAPERLQEYGSIFTDAQDPGLQRRPRHRIQSKQRPLDERALQEKLKDFPVCVSTKPEPEDDAEEGLGGLPSNISSVSSLLLFNTTENLYKKYVFLDPLAGAVTKTHVMLGAETEEKLFDAPLSISKREQLEQQVPENYFYVPDLGQVPEIDVPSYLPDLPGIANDLMYIADLGPGIAPSAPGTIPELPTFHTEVAEPLKVGELGSGMGAGPGTPAHTPSSLDTPHFVFQTYKMGAPPLPPSTAAPVGQGARQDDSSSSASPSVQGAPREVVDPSGGWATLLESIRQAGGIGKAKLRSMKERKLEKQQQKEQEQVRATSQGGHLMSDLFNKLVMRRKGISGKGPGAGDGPGGAFARVSDSIPPLPPPQQPQAEDEDDWES"
motifs = [
    # seq.start, seq.end, shape, width, height, fgcolor, bgcolor
    [120, 180, ">", 34, 13, "black", "red", None],
    [140, 190, "<", 60, 5, "black", "green", None],
#    [10, 30, "o", 100, 10, "black", "rgradient:blue", None],
#    [20, 50, "[]", 100, 10, "blue", "pink", None],
#    [55, 80, "()", 100, 10, "blue", "rgradient:purple", None],
#    [160, 170, "^", 50, 14, "black", "yellow", None],
#    [172, 180, "v", 20, 12, "black", "rgradient:orange", None],
#    [185, 190, "o", 12, 12, "black", "brown", None],
#    [198, 200, "<>", 15, 15, "black", "rgradient:gold", None],
#    [210, 240, "compactseq", 2, 10, None, None, None],
#    [300, 320, "seq", 10, 10, None, None, None],
#    [340, 350, "<>", 15, 15, "black", "rgradient:black", None],
]
# Show usage help for SeqMotifFace
print SeqMotifFace.__doc__
 
# Create a random tree and add to each leaf a random set of motifs
# from the original set
t = Tree()
t.populate(40)
for l in t.iter_leaves():
    seq_motifs = [list(m) for m in motifs] #sample(motifs, randint(2, len(motifs))) 
   
    seqFace = SeqMotifFace(seq, seq_motifs, intermotif_format="line", seqtail_format="compactseq")
    seqFace.margin_bottom = 4
    f = l.add_face(seqFace, 0, "aligned")
    
t.show()
