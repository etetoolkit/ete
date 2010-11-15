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

from ete_dev import TreeImageProperties
from ete_dev.evol import EvolTree
from ete_dev import faces


tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print tree

print '\nRunning free-ratio model with calculation of ancestral sequences...'

tree.run_model ('fb_anc')

I = TreeImageProperties()
I.force_topology             = False
I.tree_width                 = 200
I.draw_aligned_faces_as_grid = True
I.draw_guidelines = True
I.guideline_type = 2
I.guideline_color = "#CCCCCC"
I.complete_branch_lines = True
for n in sorted (tree.get_descendants()+[tree],
                 key=lambda x: x.paml_id):
    if n.is_leaf(): continue
    anc_face = faces.SequenceFace (n.sequence, 'aa', fsize=11, aabg={})
    I.aligned_foot.add_face(anc_face, 1)
    I.aligned_foot.add_face(faces.TextFace('paml_id: #%d '%(n.paml_id),
                                           fsize=8), 0)
print 'display result of bs_anc model, with ancestral amino acid sequences.'
tree.show(img_properties=I)

print '\nThe End.'
