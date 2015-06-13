from ete3 import Tree
t = Tree( '(A:1,(B:1,(C:1,D:1):0.5):0.5);' )
# Browse the tree from a specific leaf to the root
node = t.search_nodes(name="C")[0]
while node:
    print node
    node = node.up
# --C
#           /-C
# ---------|
#           \-D
#
#           /-B
# ---------|
#          |          /-C
#           \--------|
#                     \-D
#
#           /-A
# ---------|
#          |          /-B
#           \--------|
#                    |          /-C
#                     \--------|
#                               \-D
