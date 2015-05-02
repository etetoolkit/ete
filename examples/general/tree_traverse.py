from ete3 import Tree
t = Tree( '(A:1,(B:1,(C:1,D:1):0.5):0.5);' )
# Visit nodes in preorder (this is the default strategy)
for n in t.traverse():
    print n
# It Will visit the nodes in the following order:
#           /-A
# ---------|
#          |          /-B
#           \--------|
#                    |          /-C
#                     \--------|
#                               \-D
# --A
#           /-B
# ---------|
#          |          /-C
#           \--------|
#                     \-D
# --B
#           /-C
# ---------|
#           \-D
# --C
# --D
# Visit nodes in postorder
for n in t.traverse("postorder"):
    print n
# It Will visit the nodes in the following order:
# --A
# --B
# --C
# --D
#           /-C
# ---------|
#           \-D
#           /-B
# ---------|
#          |          /-C
#           \--------|
#                     \-D
#           /-A
# ---------|
#          |          /-B
#           \--------|
#                    |          /-C
#                     \--------|
#                               \-D
