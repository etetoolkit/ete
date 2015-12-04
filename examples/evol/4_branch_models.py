#!/usr/bin/python
"""
15 Nov 2010

run branches models, contrasting groups of branches over
the rest of the phylogeny.
Test of positive selection and relaxation over them.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


try:
    input = raw_input
except NameError:
    pass


from ete3 import EvolTree
from ete3 import NodeStyle

tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print (tree)

print ('Tree and alignment loaded.')
input ('Tree will be mark in order to contrast Gorilla and Chimpanzee as foreground \nspecies.')

marks = ['1', '3', '7']

tree.mark_tree (marks, ['#1'] * 3)
print (tree.write ())

print ('we can easily colorize marked branches')
# display marked branches in orange
for node in tree.traverse ():
    if not hasattr (node, 'mark'):
        continue
    if node.mark == '':
        continue
    node.img_style = NodeStyle ()
    node.img_style ['bgcolor'] = '#ffaa00'
tree.show()

print ('''now running branch models
free branch models, 2 groups of branches, one with Gorilla and
chimp, the other with the rest of the phylogeny
''')
print ('running branch free...')
tree.run_model ('b_free.137')
print ('running branch neut...')
tree.run_model ('b_neut.137')
print ('running M0 (all branches have the save value of omega)...')
tree.run_model ('M0')

input ('''Now we can do comparisons...
Compare first if we have one or 2 rates of evolution among phylogeny.
LRT between b_free and M0 (that is one or two rates of omega value)
p-value ofthis comparison is:''')
print (tree.get_most_likely ('b_free.137', 'M0'))

input ('''
Now test if foreground rate is significantly different of 1.
(b_free with significantly better likelihood than b_neut)
if significantly different, and higher than one, we will be under
positive selection, if different and lower than 1 we will be under
negative selection. And finally if models are not significantly different
we should accept null hypothesis that omega value on marked branches is
equal to 1, what would be a signal of relaxation.
p-value for difference in rates between marked branches and the rest:''')
print (tree.get_most_likely ('b_free.137', 'M0'))
print ('p-value representing significance that omega is different of 1:')
print (tree.get_most_likely ('b_free.137', 'b_neut.137'))

print ('value of omega in marked branch (frg branch):')
b_free = tree.get_evol_model ('b_free.137')
print (b_free.branches[1]['w'])

print ('and value of omega for background: ')
print (b_free.branches[2]['w'])

print ('we will now run 2 branch models over this tree, one letting the omega \nvalue of foreground species to be free, and the other fixing it at one.\n')

print ("The End.")



