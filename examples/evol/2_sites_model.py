#!/usr/bin/python
"""
15 Nov 2010

example to illustrate use of sites model, displaying and comparison
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"



from ete3 import EvolTree

tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print (tree)

try:
    input = raw_input
except NameError:
    pass

input ('\n   tree and alignment loaded\n Hit some key, to start computation of site models M1 and M2.\n')

print ('running model M1')
tree.run_model ('M1')
print ('running model M2')
tree.run_model ('M2')

print ('\n\n comparison of models M1 and M2, p-value: ' + str(tree.get_most_likely ('M2','M1')))

#tree.show()

print ('by default the hist represented is this one:')

tree.show (histfaces=['M2'])

print ('but we can choose between many others...')

model2 = tree.get_evol_model ('M2')

col2 = {'NS' : 'black', 'RX' : 'black',
        'RX+': 'black', 'CN' : 'black',
        'CN+': 'black', 'PS' : 'black', 'PS+': 'black'}


model2.set_histface (up=False, kind='curve', colors=col2, ylim=[0,4], hlines = [2.5, 1.0, 4.0, 0.5], header = 'Many lines, error boxes, background black',
                     hlines_col=['orange', 'yellow', 'red', 'cyan'], errors=True)

tree.show(histfaces=['M2'])

model2.set_histface (up=False, kind='stick', hlines = [1.0,0.3], hlines_col=['black','grey'])
tree.show(histfaces=['M2'])

col = {'NS' : 'grey', 'RX' : 'black',
       'RX+': 'grey', 'CN' : 'black',
       'CN+': 'grey', 'PS' : 'black', 'PS+': 'black'}
model2.set_histface (up=False, kind='bar', colors=col, hlines=[1.0,0.3], hlines_col=['black','grey'])

tree.show(histfaces=['M2'])


print ('running model M7')
tree.run_model ('M7')
print ('running positive selection model M8')
tree.run_model ('M8')
print ('running relaxation model M8a')
tree.run_model ('M8a')
print ('running model M3')
tree.run_model ('M3')

print ('\n\n comparison of models M7 and M8, p-value: ' + str(tree.get_most_likely ('M8','M7')))
print ('\n\n comparison of models M8a and M8, p-value: ' + str(tree.get_most_likely ('M8','M8a')))


print ('The End.')
