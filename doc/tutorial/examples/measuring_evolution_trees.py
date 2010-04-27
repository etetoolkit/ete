#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

from ete2 import CodemlTree



expldir = '/home/francisco/toolbox/ete/doc/tutorial/examples/'
algn = expldir+'alignment_measuring_evol.fasta'

###
# load tree
T = CodemlTree('(Saguinus_imperator,((Hylobates_lar,(Gorilla_gorilla,(Pan_paniscus,Pan_troglodytes))),(Macaca_fascicularis,Papio_cynocephalus)));')
T.link_to_alignment(algn)

T.show()

###
# run free-branch model, and display result
paml_rep = expldir+'lala/'
T.run_paml(paml_rep,'fb')

T.show()

###
# mark tree functionality
T.mark_tree([8,7]) # by default will mark with '#1'
T.mark_tree([10,5],marks = ['#2','#3'])
print T.write(format=9)
