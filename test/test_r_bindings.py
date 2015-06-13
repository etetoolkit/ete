'''
this functionality is deprecated!
'''

import unittest 

from ete2 import *

### R bindings
def asETE(R_phylo_tree):
    try:
        import rpy2.robjects as robjects
        R = robjects.r
    except ImportError, e:
        print e
        raise Exception ("RPy >= 2.0 is required to connect")

    R.library("ape")
    return Tree( R["write.tree"](R_phylo_tree)[0])

def asRphylo(ETE_tree):
    try:
        import rpy2.robjects as robjects
        R = robjects.r
    except ImportError, e:
        print e
        raise Exception("RPy >= 2.0 is required to connect")

    R.library("ape")
    return R['read.tree'](text=ETE_tree.write())


class Test_R_bindings(unittest.TestCase):
    """ This is experimental """
    def test_ape(self):
        """ Link to R-ape package """
        return # Don't test anything from now
        try:
            import rpy2.robjects as robjects
        except ImportError:
            print "\nNo rpy2 support. Skipping.\n"
            return

        # R
        t1 = Tree(nw_simple1)
        t2 = Tree(nw_simple2)


        R = robjects.r
        R.library("ape")
        CONS =  R["consensus"]([asRphylo(t1), \
                                    asRphylo(t1), \
                                    asRphylo(t1), \
                                    asRphylo(t1), \
                                    asRphylo(t2)])
        t = asETE(CONS)

