#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

from ete2 import CodemlTree
import sys


ETEPATH = filter (lambda x: '/ete' in x, sys.path)[0]

if ETEPATH == []:
    ETEPATH = '.'
    sys.stder.write('Warning: ETE not found.\n')

expldir = ETEPATH + '/doc/tutorial/examples/'

###
# load tree
T = CodemlTree(expldir + 'measuring_tree.nw')
T.link_to_alignment(expldir + 'alignment_measuring_evol.fasta')

T.show()

###
# run free-branch model, and display result
paml_rep = expldir+'lala/'
T.run_paml(paml_rep,'fb')

T.show()

###
# run site model, and display result
paml_rep = expldir+'lala/'
for model in ['M1', 'M2']:
    T.run_paml(paml_rep,model)

pv = T.get_most_likely('M2', 'M1')
if pv <= 0.05:
    print 'most likely model is model M2, there is positive selection',pv
else:
    print 'most likely model is model M1',pv

###
# tengo que encontrar un ejemplo mas bonito pero bueno.... :P
T.add_histface('M2')
T.add_histface('M1',down = False)

T.show()

###
# re-run without reeeeeeeeee-run
T = CodemlTree(expldir + 'measuring_tree.nw')
T.link_to_alignment(expldir + 'alignment_measuring_evol.fasta')

T.link_to_evol_model(ETEPATH + '/doc/tutorial/examples/lala/fb/out','fb')
T.link_to_evol_model(ETEPATH + '/doc/tutorial/examples/lala/M1/out','M1')
T.link_to_evol_model(ETEPATH + '/doc/tutorial/examples/lala/M2/out','M2')

T.add_histface('M2')
T.add_histface('M1',down = False)

T.show()

###
# mark tree functionality
T.mark_tree([8,7]) # by default will mark with '#1'
T.mark_tree([10,5],marks = ['#2','#3'])
print T.write(format=9)

