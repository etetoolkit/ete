from ete2 import Tree
# Loads a tree. Note that we use format 1 to read internal node names
t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);', format=1)
print "original tree looks like this:"
# This is an alternative way of using "print t". Thus we have a bit
# more of control on how tree is printed. Here i print the tree
# showing internal node names
print t.get_ascii(show_internal=True)
#
#                                        /-H
#                              /D-------|
#                             |          \-K
#                    /B-------|
#                   |         |          /-F
#          /A-------|          \G-------|
#         |         |                    \-I
#         |         |
#         |          \-E
#-NoName--|
#         |                    /-L
#         |          /J-------|
#         |         |         |          /-N
#         |         |          \O-------|
#          \C-------|                    \-Q
#                   |
#                   |          /-P
#                    \M-------|
#                              \-S
# Get pointers to specific nodes
G = t.search_nodes(name="G")[0]
J = t.search_nodes(name="J")[0]
C = t.search_nodes(name="C")[0]
# If we remove J from the tree, the whole partition under J node will
# be detached from the tree and it will be considered an independent
# tree. We can do the same thing using two approaches: J.detach() or
# C.remove_child(J)
removed_node = J.detach() # = C.remove_child(J)
# if we know print the original tree, we will see how J partition is
# no longer there.
print "Tree after REMOVING the node J"
print t.get_ascii(show_internal=True)
#                                        /-H
#                              /D-------|
#                             |          \-K
#                    /B-------|
#                   |         |          /-F
#          /A-------|          \G-------|
#         |         |                    \-I
#         |         |
#-NoName--|          \-E
#         |
#         |                    /-P
#          \C------- /M-------|
#                              \-S
# however, if we DELETE the node G, only G will be eliminated from the
# tree, and all its descendants will then hang from the next upper
# node.
G.delete()
print "Tree after DELETING the node G"
print t.get_ascii(show_internal=True)
#                                        /-H
#                              /D-------|
#                             |          \-K
#                    /B-------|
#                   |         |--F
#          /A-------|         |
#         |         |          \-I
#         |         |
#-NoName--|          \-E
#         |
#         |                    /-P
#          \C------- /M-------|
#                              \-S
