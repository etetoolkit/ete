#!/usr/bin/python
"""
15 Nov 2010

example of computation and display of an ancestral sequence
computed under free'ratio model.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from ete2 import TreeStyle
from ete2 import EvolTree
from ete2 import faces


tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print tree

print '\n Running free-ratio model with calculation of ancestral sequences...'

tree.run_model ('fb_anc')
#tree.link_to_evol_model('/tmp/ete2-codeml/fb_anc/out', 'fb_anc')

I = TreeStyle()
I.force_topology             = False
I.draw_aligned_faces_as_table = True
I.draw_guiding_lines = True
I.guiding_lines_type = 2
I.guiding_lines_color = "#CCCCCC"
for n in sorted (tree.get_descendants()+[tree],
                 key=lambda x: x.node_id):
    if n.is_leaf(): continue
    anc_face = faces.SequenceFace (n.sequence, 'aa', fsize=10, bg_colors={})
    I.aligned_foot.add_face(anc_face, 1)
    I.aligned_foot.add_face(faces.TextFace('node_id: #%d '%(n.node_id),
                                           fsize=8), 0)
print 'display result of bs_anc model, with ancestral amino acid sequences.'
tree.show(tree_style=I)

print '\nThe End.'
