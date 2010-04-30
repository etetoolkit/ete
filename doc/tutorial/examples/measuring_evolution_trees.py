#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

from ete_dev import CodemlTree
import sys, re

TREE_PATH    = "./measuring_tree.nw"
ALG_PATH     = "./alignment_measuring_evol.fasta"
WORKING_PATH = "/tmp/ete2-codeml_example/"

MY_PATH = '/home/francisco/toolbox/ete/doc/tutorial/examples/'

TREE_PATH = MY_PATH + re.sub('\./', '', TREE_PATH)
ALG_PATH  = MY_PATH + re.sub('\./', '', ALG_PATH )

###
# load tree
print '\n         ----> we create a CodemlTree object, and give to him a topology, from'
print TREE_PATH
T = CodemlTree(TREE_PATH)
print T
print '\n         ----> and an alignment from: \n'+ALG_PATH+'\n\n'
T.link_to_alignment(ALG_PATH)
raw_input("         ====> hit some key to see the Tree with alignment")
T.show()

###
# run free-branch model, and display result
print '\n\n\n         ----> We define now our working directory, that will be created:', \
      WORKING_PATH
T.workdir = (WORKING_PATH)
print '\n            ----> and run the free-branch model:'
raw_input("         ====> Hit some key to start free-branch computation with codeml...\n")
T.run_paml('fb')
T.show()

###
# run site model, and display result
print '\n\n\n         ----> We are now goingn to run sites model M1 and M2:\n\n'
raw_input("         ====> hit some key to start")
for model in ['M1', 'M2']:
    T.run_paml(model)

print '\n\n\n            ----> and use the get_most_likely function to compute the LRT between those models:\n'

raw_input("         ====> Hit some key to launch LRT")

pv = T.get_most_likely('M2', 'M1')
if pv <= 0.05:
    print '         ---->   -> most likely model is model M2, there is positive selection, pval: ',pv
else:
    print '         ---->   -> most likely model is model M1, pval: ',pv

###
# tengo que encontrar un ejemplo mas bonito pero bueno.... :P
print '\n\n\n         ----> We now add histograms to our tree to repesent site models'
raw_input("         ====> Hit some key to display")
T.add_histface('M2')
T.add_histface('M1',down = False)

T.show()


###
# re-run without reeeeeeeeee-run
print '\n\n\n         ----> Now we have runned once those 3 models, we can load again our tree from'
print '         ----> our tree file and alignment file, and this time load directly oufiles from previous'
raw_input('runs\n         ====> hit some key to see.')
T = CodemlTree(TREE_PATH)
T.link_to_alignment(ALG_PATH)
T.workdir = (WORKING_PATH)

T.link_to_evol_model(T.workdir + '/fb/out','fb')
T.link_to_evol_model(T.workdir + '/M1/out','M1')
T.link_to_evol_model(T.workdir + '/M2/out','M2')

T.add_histface('M2')
T.add_histface('M1',down = False)

T.show()

###
# mark tree functionality
print T.write(format=9)
name = raw_input('         ====> As you need to mark some branches to run branch\n\
models, typ the name of one leaf: ')
idname = T.get_leaves_by_name(name)[0].idname
print '         ----> you want to mark:',name,'that has this idname: ', idname
T.mark_tree([idname]) # by default will mark with '#1'
print 'have a look to the mark: '
print re.sub('#','|',re.sub('[0-9a-zA-Z_(),;]',' ',T.write(format=9)))
print re.sub('#','v',re.sub('[0-9a-zA-Z_(),;]',' ',T.write(format=9)))
print T.write(format=9)

print '         ---->  more or less, all we have done here is feasable from the GUI, try it...'
raw_input('hit something to start')

T = CodemlTree(TREE_PATH)
T.link_to_alignment(ALG_PATH)
T.workdir = (WORKING_PATH)
T.show()
