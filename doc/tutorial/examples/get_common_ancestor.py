from ete2 import Tree
#Loads a tree
tree = Tree( '((H:1,I:1):0.5, A:1, (B:1,(C:1,D:1):0.5):0.5);' )
print "this is the original tree:"
print tree
#                    /-H
#          /--------|
#         |          \-I
#         |
#---------|--A
#         |
#         |          /-B
#          \--------|
#                   |          /-C
#                    \--------|
#                              \-D
# Finds the first common ancestor between B and C.
ancestor = tree.get_common_ancestor("D", "C")
print "The ancestor of C and D is:"
print ancestor
#          /-C
#---------|
#          \-D
# You can use more than two nodes in the search
ancestor = tree.get_common_ancestor("B", "C", "D")
print "The ancestor of B, C and D is:"
print ancestor
#          /-B
#---------|
#         |          /-C
#          \--------|
#                    \-D
# Finds the first sister branch of the ancestor node. Because
# multifurcations are allowed, many sister branches are possible.
sisters = ancestor.get_sisters()
print "which has has", len(sisters), "sister nodes"
print "and the first of such sister nodes like this:"
print sisters[0]
#
#          /-H
#---------|
#          \-I
