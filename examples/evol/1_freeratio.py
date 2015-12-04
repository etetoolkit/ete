#!/usr/bin/python
"""
15 Nov 2010

first example, load a tree and compute free ratios model,
to find omega value of each branch.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


from ete3 import EvolTree

try:
    input = raw_input
except NameError:
    pass

tree = EvolTree ("data/S_example/measuring_S_tree.nw")

print (tree)

input ('\n   tree loaded, hit some key.\n')

print ('Now, it is necessary to link this tree to an alignment:')

tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

input ('\n   alignment loaded, hit some key to see.\n')

tree.show()

print ('''
we will run free-ratio model that is one of models available through
function run_model:
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
''')
print (tree.run_model.__doc__ +'\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

tree.run_model ('fb.example')

input ('free-ratio model runned, all results are store in a Model object.')

fb = tree.get_evol_model('fb.example')

print ('Have a look to the parameters used to run this model on codeml: ')
print (fb.get_ctrl_string())
input ('hit some key...')


print ('Have a look to run message of codeml: ')
print (fb.run)
input ('hit some key...')

print ('Have a look to log likelihood value of this model, and number of parameters:')
print ('lnL: %s and np: %s' % (fb.lnL, fb.np))
input ('hit some key...')

input ('finally have a look to two layouts available to display free-ratio:')
tree.show()

# have to import layou
from ete3.treeview.layouts import evol_clean_layout

print ('(omega in dark red, 100*(dN)/100*(dS), in grey)')
tree.show (layout=evol_clean_layout)


print ('The End.')
