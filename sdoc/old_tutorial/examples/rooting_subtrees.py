from ete3 import Tree
t = Tree('(((A,C),((H,F),(L,M))),((B,(J,K))(E,D)));')
print "Original tree:"
print t
#                              /-A
#                    /--------|
#                   |          \-C
#                   |
#          /--------|                    /-H
#         |         |          /--------|
#         |         |         |          \-F
#         |          \--------|
#         |                   |          /-L
#         |                    \--------|
#---------|                              \-M
#         |
#         |                    /-B
#         |          /--------|
#         |         |         |          /-J
#         |         |          \--------|
#          \--------|                    \-K
#                   |
#                   |          /-E
#                    \--------|
#                              \-D
#
# Each main branch of the tree is independently rooted.
node1 = t.get_common_ancestor("A","H")
node2 = t.get_common_ancestor("B","D")
node1.set_outgroup("H")
node2.set_outgroup("E")
print "Tree after rooting each node independently:"
print t
#
#                              /-F
#                             |
#                    /--------|                    /-L
#                   |         |          /--------|
#                   |         |         |          \-M
#                   |          \--------|
#          /--------|                   |          /-A
#         |         |                    \--------|
#         |         |                              \-C
#         |         |
#         |          \-H
#---------|
#         |                    /-D
#         |          /--------|
#         |         |         |          /-B
#         |         |          \--------|
#          \--------|                   |          /-J
#                   |                    \--------|
#                   |                              \-K
#                   |
#                    \-E
