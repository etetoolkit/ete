from ete4 import Tree

t = Tree()  # creates an empty tree

A = t.add_child(name='A')  # adds a new child to the current tree root
B = t.add_child(name='B')  # adds a second child to the current tree root

C = A.add_child(name='C')  # adds a new child to one of the branches

D = C.add_sister(name='D') # adds a second child to same branch as before
                           # but using a sister as the starting point

R = A.add_child(name='R')  # adds a third child to the branch (multifurcation)

# Next, I add 6 random leaves to the R branch names_library is an
# optional argument. If no names are provided, they will be generated
# randomly.
R.populate(6, names=['r1', 'r2', 'r3', 'r4', 'r5', 'r6'])

print(t)
#    ╭╴C
#    ├╴D
#  ╭─┤   ╭─┬╴r2
#  │ │ ╭─┤ ╰╴r3
#  │ ╰─┤ ╰─┬╴r5
# ─┤   │   ╰╴r6
#  │   ╰─┬╴r4
#  │     ╰╴r1
#  ╰╴B
