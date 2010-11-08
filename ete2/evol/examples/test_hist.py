#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

from ete_dev.evol import EvolTree
import sys, re

typ = 'S'
#while typ != 'L' and typ != 'S':
#    typ = raw_input (\
#        "choose kind of example [L]ong or [S]hort, hit [L] or [S]:\n")

TREE_PATH    = "data/measuring_%s_tree.nw" % (typ)

ALG_PATH     = "data/alignment_%s_measuring_evol.fasta" % (typ)
WORKING_PATH = "data/"

MY_PATH = ''

TREE_PATH = MY_PATH + re.sub('\./', '', TREE_PATH)
ALG_PATH  = MY_PATH + re.sub('\./', '', ALG_PATH )

T = EvolTree (TREE_PATH)
T.link_to_alignment (ALG_PATH)
T.workdir = (WORKING_PATH)
T.link_to_evol_model(T.workdir + '/fb/out','fb')
T.show()
T.link_to_evol_model(T.workdir + '/M1/out','M1')
T.link_to_evol_model(T.workdir + '/M2/out','M2')
T.add_histface('M2', down=False)
T.add_histface('M2',down=True, typ='error',
               lines=[1.0,0.3],col_lines=['black','grey'])

T.show()
sys.stderr.write('\n\nThe End.\n\n')



