#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

from ete3.evol import EvolTree
import sys, re

typ = None
while typ != 'L' and typ != 'S':
    typ = raw_input(\
        "choose kind of example [L]ong or [S]hort, hit [L] or [S]:\n").upper()
TREE_PATH    = "data/%s_example/measuring_%s_tree.nw" % (typ, typ)

ALG_PATH     = "data/%s_example/alignment_%s_measuring_evol.fasta" % (typ, typ)
WORKING_PATH = "/tmp/ete3-codeml_example/"

#MY_PATH = '/home/francisco/toolbox/ete3-codeml/doc/tutorial/examples/'
MY_PATH = ''

TREE_PATH = MY_PATH + re.sub('\./', '', TREE_PATH)
ALG_PATH  = MY_PATH + re.sub('\./', '', ALG_PATH )

###
# load tree


print '\n         ----> we create a EvolTree object, and give to him a topology, from',
print TREE_PATH
out = True
while out == True:
    try:
        T = EvolTree(TREE_PATH)
        out = False
    except:
        sys.stderr.write('Bad path for working directory. Enter new path or quit("Q"):\n')
        PATH = raw_input('')
        if PATH.startswith('q') or PATH.startswith('Q'):
            sys.exit()
        TREE_PATH    = "./measuring_%s_tree.nw" % (typ)
        ALG_PATH     = "./alignment_%s_measuring_evol.fasta" % (typ)
        TREE_PATH = PATH + re.sub('\./', '', TREE_PATH)
        ALG_PATH  = PATH + re.sub('\./', '', ALG_PATH )


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
print '\n            ----> and run the free-branch model with run_model function:\n\n%s\n%s\n%s\n'\
      % ('*'*10 + ' doc ' + '*'*10, T.run_model.func_doc, '*'*30)

raw_input("         ====> Hit some key to start free-branch computation with codeml...\n")
T.run_model('fb')
T.show()

###
# run site model, and display result
print '\n\n\n         ----> We are now goingn to run sites model M1 and M2 with run_model function:\n'
raw_input("         ====> hit some key to start")
for model in ['M1', 'M2']:
    print 'running model ' + model
    T.run_model(model)

print '\n\n\n            ----> and use the get_most_likely function to compute the LRT between those models:\n'
print 'get_most_likely function: \n\n'+ '*'*10 + ' doc ' + '*'*10
print '\n' + T.get_most_likely.func_doc
print '*'*30

raw_input("\n         ====> Hit some key to launch LRT")

pv = T.get_most_likely('M2', 'M1')
if pv <= 0.05:
    print '         ---->   -> most likely model is model M2, there is positive selection, pval: ',pv
else:
    print '         ---->   -> most likely model is model M1, pval: ',pv

raw_input("         ====> Hit some key...")

###
# tengo que encontrar un ejemplo mas bonito pero bueno.... :P

print '\n\n\n         ----> We now add histograms to our tree to repesent site models with add_histface function: \n\n%s\n%s\n%s\n'\
      % ('*'*10 + ' doc ' + '*'*10, T.get_evol_model('M2').set_histface.func_doc,'*'*30)
print 'Upper face is an histogram representing values of omega for each column in the alignment,'
print '\
Colors represent significantly conserved sites(cyan to blue), neutral sites(greens), or under \n\
positive selection(orange to red). \n\
Lower face also represents values of omega(red line) and bars represent the error of the estimation.\n\
Also significance of belonging to one class of site can be painted in background(here lightgrey for\n\
evrething significant)\n\
Both representation are done according to BEB estimation of M2, M1 or M7 estimation can also be \n\
drawn but should not be used.\n'
raw_input("         ====> Hit some key to display, histograms of omegas BEB from M2 model...")

col = {'NS' : 'grey',
       'RX' : 'grey',
       'RX+': 'grey',
       'CN' : 'grey',
       'CN+': 'grey',
       'PS' : 'grey',
       'PS+': 'grey'}



T.get_evol_model('M2').set_histface(kind='curve',
                                      colors=col, up = False,
                                      hlines=[1.0,0.3],
                                      hlines_col=['black','grey'])
T.show(histfaces = ['M1', 'M2'])


###
# re-run without reeeeeeeeee-run
print '\n\n\n         ----> Now we have runned once those 3 models, we can load again our tree from'
print '         ----> our tree file and alignment file, and this time load directly oufiles from previous'
print '               with the function link_to_evol_model \n\n%s\n%s\n%s\n' % ('*'*10 + ' doc ' + '*'*10, \
                                                                      T.link_to_evol_model.func_doc, \
                                                                      '*'*30)
raw_input('runs\n         ====> hit some key to see...')
T = EvolTree(TREE_PATH)
T.link_to_alignment(ALG_PATH)
T.workdir = (WORKING_PATH)

T.link_to_evol_model(T.workdir + '/fb/out','fb')
T.link_to_evol_model(T.workdir + '/M1/out','M1')
T.link_to_evol_model(T.workdir + '/M2/out','M2')

T.get_evol_model('M2').set_histface(kind='curve',
                                      colors=col, up = False,
                                      hlines=[1.0,0.3],
                                      hlines_col=['black','grey'])
T.show(histfaces = ['M1', 'M2'])


###
# mark tree functionality
print T.write(format=10)
name = None
while name not in T.get_leaf_names():
    name = raw_input('         ====> As you need to mark some branches to run branch\n\
    models, type the name of one leaf: ')

idname = T.get_leaves_by_name(name)[0].node_id

print '         ----> you want to mark:',name,'that has this idname: ', idname
T.mark_tree([idname]) # by default will mark with '#1'
print 'have a look to the mark: '
print re.sub('#','|',re.sub('[0-9a-zA-Z_(),;]',' ',T.write(format=10)))
print re.sub('#','v',re.sub('[0-9a-zA-Z_(),;]',' ',T.write(format=10)))
print T.write(format=10)
print '\n You have marked the tree with a command like:  T.mark_tree([%d])\n' % (idname)
print '\n%s\n%s\n%s\n' % ('*'*10 + ' doc ' + '*'*10, T.mark_tree.func_doc, \
                                                                      '*'*30)

print '\n\n\n         ----> We are now going to run branch-site models bsA and bsA1:\n\n'
raw_input("         ====> hit some key to start computation with our marked tree")
for model in ['bsA','bsA1']:
    print 'running model ' + model
    T.run_model(model)


print '\n\n\n            ----> again we use the get_most_likely function to compute the LRT between those models:\n'
raw_input("         ====> Hit some key to launch LRT")

pv = T.get_most_likely('bsA', 'bsA1')
if pv <= 0.05:
    print '         ---->   -> most likely model is model bsA, there is positive selection, pval: ',pv
    print '                         ' + name + ' is under positive selection.'
else:
    print '         ---->   -> most likely model is model bsA1, pval of LRT: ',pv
    print '                         ' + name + ' is not under positive selection.'


sys.stderr.write('\n\nThe End.\n\n')



