from ete3 import Tree
# generates a random tree
t = Tree();
t.populate(15);
print t
#
#
#                    /-qogjl
#          /--------|
#         |          \-vxbgp
#         |
#         |          /-xyewk
#---------|         |
#         |         |                    /-opben
#         |         |                   |
#         |         |          /--------|                    /-xoryn
#          \--------|         |         |          /--------|
#                   |         |         |         |         |          /-wdima
#                   |         |          \--------|          \--------|
#                   |         |                   |                    \-qxovz
#                   |         |                   |
#                   |         |                    \-isngq
#                    \--------|
#                             |                    /-neqsc
#                             |                   |
#                             |                   |                              /-waxkv
#                             |          /--------|                    /--------|
#                             |         |         |          /--------|          \-djeoh
#                             |         |         |         |         |
#                             |         |          \--------|          \-exmsn
#                              \--------|                   |
#                                       |                   |          /-udspq
#                                       |                    \--------|
#                                       |                              \-buxpw
#                                       |
#                                        \-rkzwd
# Calculate the midpoint node
R = t.get_midpoint_outgroup()
# and set it as tree outgroup
t.set_outgroup(R)
print t
#                              /-opben
#                             |
#                    /--------|                    /-xoryn
#                   |         |          /--------|
#                   |         |         |         |          /-wdima
#                   |          \--------|          \--------|
#          /--------|                   |                    \-qxovz
#         |         |                   |
#         |         |                    \-isngq
#         |         |
#         |         |          /-xyewk
#         |          \--------|
#         |                   |          /-qogjl
#         |                    \--------|
#---------|                              \-vxbgp
#         |
#         |                    /-neqsc
#         |                   |
#         |                   |                              /-waxkv
#         |          /--------|                    /--------|
#         |         |         |          /--------|          \-djeoh
#         |         |         |         |         |
#         |         |          \--------|          \-exmsn
#          \--------|                   |
#                   |                   |          /-udspq
#                   |                    \--------|
#                   |                              \-buxpw
#                   |
#                    \-rkzwd
#
