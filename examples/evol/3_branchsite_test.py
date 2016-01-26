#!/usr/bin/python
"""
15 Nov 2010

simple example to mark a tree and compute branch-site test of positive selection
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

tree = EvolTree("data/L_example/measuring_L_tree.nw")
tree.link_to_alignment('data/L_example/alignment_L_measuring_evol.fasta')

print (tree)

# input('\n   tree and alignment loaded\nHit some key, to start computation of branch site models A and A1 on each branch.\n')

print ('running model M0, for comparison with branch-site models...')
tree.run_model('M0')

# each node/leaf has two kind of identifiers node_id and paml_id, to mark nodes we have to specify
# the node_id of the nodes we want to mark, and the kind of mark in this way:

for leaf in tree:
    leaf.node_id
    print ('\n---------\nNow working with leaf ' + leaf.name)
    tree.mark_tree([leaf.node_id], marks=['#1'])
    print (tree.write())
    # to organize a bit, we name model with the name of the marked node
    # any character after the dot, in model name, is not taken into account
    # for computation. (have a look in /tmp/ete3.../bsA.. directory)
    print ('running model bsA and bsA1')
    tree.run_model('bsA.'+ leaf.name)
    tree.run_model('bsA1.' + leaf.name)
    print ('p-value of positive selection for sites on this branch is: ')
    ps = tree.get_most_likely('bsA.' + leaf.name, 'bsA1.'+ leaf.name)
    rx = tree.get_most_likely('bsA1.'+ leaf.name, 'M0')
    print (str(ps))
    print ('p-value of relaxation for sites on this branch is: ')
    print (str(rx))
    model = tree.get_evol_model("bsA." + leaf.name)
    if ps < 0.05 and float(model.classes['foreground w'][2]) > 1:
        print ('we have positive selection on sites on this branch')
        tree.show(histfaces=['bsA.' + leaf.name])
    elif rx<0.05 and ps>=0.05:
        print ('we have relaxation on sites on this branch')
    else:
        print ('no signal detected on this branch, best fit for M0')
    print ('\nclean tree, remove marks')
    tree.mark_tree(map(lambda x: x.node_id, tree.get_descendants()),
                    marks=[''] * len(tree.get_descendants()), verbose=True)

# nothing working yet to get which sites are under positive selection/relaxation,
# have to look at the main outfile or rst outfile

print ('The End.')
