#!/usr/bin/python
"""
15 Nov 2010

example to illustrate use of sites model, displaying and comparison
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"



from ete_dev import EvolTree

tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print tree

raw_input ('\n   tree and alignment loaded\nHit some key, to start computation of site models M1 and M2.\n')

print 'running model M1'
tree.run_model ('M1')
print 'running model M2'
tree.run_model ('M2')

print '\n\ncomparison of models M1 and M2, pvalue: ' + str(tree.get_most_likely ('M2','M1'))

#tree.show()

print 'by default the hist represented is this one:'

tree.show (histfaces=['M2'])

print 'but we can choose betwen manya others...'

model2 = tree.get_evol_model ('M2')

col2 = {'NS' : 'white', 'RX' : 'white',
        'RX+': 'white', 'CN' : 'white',
        'CN+': 'white', 'PS' : 'white', 'PS+': 'white'}


model2.set_histface (up=False, typ='error', col=col2, lines = [2.5, 1.0, 4.0, 0.5], header = 'Many lines, error boxes, background black',
                     col_lines=['orange', 'yellow', 'red', 'cyan'])

tree.show(histfaces=['M2'])

model2.set_histface (up=False, typ='protamine', lines = [1.0,0.3], col_lines=['black','grey'],
                 extras=['+','-',' ',' ',' ',':P', ' ',' ']*2+[' ']*(len(tree.get_leaves()[0].sequence)-16))
tree.show(histfaces=['M2'])

col = {'NS' : 'grey', 'RX' : 'black',
       'RX+': 'grey', 'CN' : 'black',
       'CN+': 'grey', 'PS' : 'black', 'PS+': 'black'}
model2.set_histface (up=False, typ='hist', col=col, lines = [1.0,0.3], col_lines=['black','grey'])

tree.show(histfaces=['M2'])


print 'running model M7'
tree.run_model ('M7')
print 'running positive selection model M8'
tree.run_model ('M8')
print 'running relaxation model M8a'
tree.run_model ('M8a')
print 'running model M3'
tree.run_model ('M3')

print '\n\ncomparison of models M7 and M8, pvalue: ' + str(tree.get_most_likely ('M8','M7'))
print '\n\ncomparison of models M8a and M8, pvalue: ' + str(tree.get_most_likely ('M8','M8a'))


print 'The End.'
