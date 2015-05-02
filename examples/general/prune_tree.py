from ete3 import Tree
# Let's create simple tree
t = Tree('((((H,K),(F,I)G),E),((L,(N,Q)O),(P,S)));')
print "Original tree looks like this:"
print t
#
#                                        /-H
#                              /--------|
#                             |          \-K
#                    /--------|
#                   |         |          /-F
#          /--------|          \--------|
#         |         |                    \-I
#         |         |
#         |          \-E
#---------|
#         |                    /-L
#         |          /--------|
#         |         |         |          /-N
#         |         |          \--------|
#          \--------|                    \-Q
#                   |
#                   |          /-P
#                    \--------|
#                              \-S
# Prune the tree in order to keep only some leaf nodes.
t.prune(["H","F","E","Q", "P"])
print "Pruned tree"
print t
#
#                              /-F
#                    /--------|
#          /--------|          \-H
#         |         |
#---------|          \-E
#         |
#         |          /-Q
#          \--------|
#                    \-P
# Let's re-create the same tree again
