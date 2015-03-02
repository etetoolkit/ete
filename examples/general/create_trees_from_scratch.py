from ete2 import Tree
t = Tree() # Creates an empty tree
A = t.add_child(name="A") # Adds a new child to the current tree root
                           # and returns it
B = t.add_child(name="B") # Adds a second child to the current tree
                           # root and returns it
C = A.add_child(name="C") # Adds a new child to one of the branches
D = C.add_sister(name="D") # Adds a second child to same branch as
                             # before, but using a sister as the starting
                             # point
R = A.add_child(name="R") # Adds a third child to the
                           # branch. Multifurcations are supported
# Next, I add 6 random leaves to the R branch names_library is an
# optional argument. If no names are provided, they will be generated
# randomly.
R.populate(6, names_library=["r1","r2","r3","r4","r5","r6"])
# Prints the tree topology
print t
#                     /-C
#                    |
#                    |--D
#                    |
#           /--------|                              /-r4
#          |         |                    /--------|
#          |         |          /--------|          \-r3
#          |         |         |         |
#          |         |         |          \-r5
#          |          \--------|
# ---------|                   |                    /-r6
#          |                   |          /--------|
#          |                    \--------|          \-r2
#          |                             |
#          |                              \-r1
#          |
#           \-B
# a common use of the populate method is to quickly create example
# trees from scratch. Here we create a random tree with 100 leaves.
t = Tree()
t.populate(100)
