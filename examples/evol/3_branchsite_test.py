#!/usr/bin/python
"""
15 Nov 2010

simple example to mark a tree and comput branch-site test of positive selection
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


from ete_dev import EvolTree


tree = EvolTree ("data/S_example/measuring_S_tree.nw")
tree.link_to_alignment ('data/S_example/alignment_S_measuring_evol.fasta')

print tree

raw_input ('\n   tree and alignment loaded\nHit some key, to start computation of branch site models A and A1 on each branch.\n')

print 'running model M0, for camparison with branch-site models...'
tree.run_model('M0')

# each node/leaf has two kind of identifiers _nid and paml_id, to mark nodes we have to specify
# the _nid of the nodes we want to mark, and the kind of mark in this way:

for leaf in tree:
    leaf._nid
    print '\n---------\nNow working with leaf ' + leaf.name
    tree.mark_tree ([leaf._nid], marks=['#1'])
    print tree.write()
    # to organize a bit, we name model with the name of the marked node
    # any character after the dot, in model name, is not taken into account
    # for computation. (have a look in /tmp/ete2.../bsA.. directory)
    print 'running model bsA and bsA1'
    tree.run_model ('bsA.'+ leaf.name)
    tree.run_model ('bsA1.' + leaf.name)
    print 'p-value of positive selection for sites on this branch is: '
    ps = tree.get_most_likely ('bsA.' + leaf.name, 'bsA1.'+ leaf.name)
    rx = tree.get_most_likely ('bsA1.'+ leaf.name, 'M0')
    print str (ps)
    print 'p-value of relaxation for sites on this branch is: '
    print str (rx)
    if ps<0.05 and float (bsA.wfrg2a)>1:
        print 'we have positive selection on sites on this branch'
    elif rx<0.05 and ps>=0.05:
        print 'we have relaxation on sites on this branch'
    else:
        print 'no signal detected on this branch, best fit for M0'
    print '\nclean tree, remove marks'
    tree.mark_tree (map (lambda x: x._nid, tree.get_descendants()),
                    marks=[''] * len (tree.get_descendants()), verbose=True)

# nothing working yet to get which sites are under positive selection/relaxation,
# have to look at the main outfile or rst outfile

print 'The End.'

