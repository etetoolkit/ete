#!/usr/bin/python
"""
15 Nov 2010

example of tests for different rates among sites in clades
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"



from ete2 import EvolTree
from ete2 import NodeStyle

tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print tree

print 'Tree and alignment loaded.'
raw_input ('Tree will be mark in order to contrast Gorilla and Chimpanzee as foreground \nspecies.')

marks = ['1', 3, '7']

tree.mark_tree (marks, ['#1'] * 3)
print tree.write ()

# display marked branches in orange
for node in tree.traverse ():
    if not hasattr (node, 'mark'):
        continue
    if node.mark == '':
        continue
    node.img_style = NodeStyle()
    node.img_style ['bgcolor'] = '#ffaa00'
tree.show()


print '''now running branch-site models C and D that represents
the addition of one class of sites in on specific branch.
These models must be compared to null models M1 and M3.
if branch-site models are detected to be significantly better,
than, one class of site is evolving at different rate in the marked
clade.
'''

# TODO: re-enable model M3

print 'running branch-site C...'
tree.run_model ('bsC.137')
#print 'running branch-site D...'
#tree.run_model ('bsD.137')
print 'running M1 (all branches have the save value of omega)...'
tree.run_model ('M1')
#print 'running M3 (all branches have the save value of omega)...'
#tree.run_model ('M3')

print '''p-value that, in marked clade, we have one class of site
specifically evolving at a different rate:'''
print tree.get_most_likely ('bsC.137', 'M1')
#print 'p-value representing significance that omega is different of 1:'
#print tree.get_most_likely ('bsD.137', 'M3')


print 'The End.'
