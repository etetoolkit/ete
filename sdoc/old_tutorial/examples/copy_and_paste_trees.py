from ete2 import Tree
# Loads 3 independent trees
t1 = Tree('(A,(B,C));')
t2 = Tree('((D,E), (F,G));')
t3 = Tree('(H, ((I,J), (K,L)));')
print "Tree1:", t1
#            /-A
#  ---------|
#           |          /-B
#            \--------|
#                      \-C
print "Tree2:", t2
#                      /-D
#            /--------|
#           |          \-E
#  ---------|
#           |          /-F
#            \--------|
#                      \-G
print "Tree3:", t3
#            /-H
#           |
#  ---------|                    /-I
#           |          /--------|
#           |         |          \-J
#            \--------|
#                     |          /-K
#                      \--------|
#                                \-L
# Locates a terminal node in the first tree
A = t1.search_nodes(name='A')[0]
# and adds the two other trees as children.
A.add_child(t2)
A.add_child(t3)
print "Resulting concatenated tree:", t1
#                                          /-D
#                                /--------|
#                               |          \-E
#                      /--------|
#                     |         |          /-F
#                     |          \--------|
#            /--------|                    \-G
#           |         |
#           |         |          /-H
#           |         |         |
#           |          \--------|                    /-I
#           |                   |          /--------|
#  ---------|                   |         |          \-J
#           |                    \--------|
#           |                             |          /-K
#           |                              \--------|
#           |                                        \-L
#           |
#           |          /-B
#            \--------|
#                      \-C
# But remember!!!You should never do things like:
#
# A.add_child(t1)
#
