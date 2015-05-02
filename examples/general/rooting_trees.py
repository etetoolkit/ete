from ete3 import Tree
# Load an unrooted tree. Note that three branches hang from the root
# node. This usually means that no information is available about
# which of nodes is more basal.
t = Tree('(A,(H,F)(B,(E,D)));')
print "Unrooted tree"
print t
#          /-A
#         |
#         |          /-H
#---------|---------|
#         |          \-F
#         |
#         |          /-B
#          \--------|
#                   |          /-E
#                    \--------|
#                              \-D
#
# Let's define that the ancestor of E and D as the tree outgroup.  Of
# course, the definition of an outgroup will depend on user criteria.
ancestor = t.get_common_ancestor("E","D")
t.set_outgroup(ancestor)
print "Tree rooteda at E and D's ancestor is more basal that the others."
print t
#
#                    /-B
#          /--------|
#         |         |          /-A
#         |          \--------|
#         |                   |          /-H
#---------|                    \--------|
#         |                              \-F
#         |
#         |          /-E
#          \--------|
#                    \-D
#
# Note that setting a different outgroup, a different interpretation
# of the tree is possible
t.set_outgroup( t&"A" )
print "Tree rooted at a terminal node"
print t
#                              /-H
#                    /--------|
#                   |          \-F
#          /--------|
#         |         |          /-B
#         |          \--------|
#---------|                   |          /-E
#         |                    \--------|
#         |                              \-D
#         |
#          \-A
