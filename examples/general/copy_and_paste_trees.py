from ete4 import Tree

# Create 3 independent trees.

t1 = Tree('(A,(B,C));')
t2 = Tree('((D,E), (F,G));')
t3 = Tree('(H, ((I,J), (K,L)));')

print(t1)
# ─┬╴A
#  ╰─┬╴B
#    ╰╴C

print(t2)
#  ╭─┬╴D
# ─┤ ╰╴E
#  ╰─┬╴F
#    ╰╴G

print(t3)
#  ╭╴H
# ─┤ ╭─┬╴I
#  ╰─┤ ╰╴J
#    ╰─┬╴K
#      ╰╴L

# Locate a terminal node in the first tree.
A = next(t1.search_nodes(name='A'))

# and adds the two other trees as children.
A.add_child(t2)
A.add_child(t3)

print('Resulting concatenated tree:')
print(t1)
#      ╭─┬╴D
#    ╭─┤ ╰╴E
#    │ ╰─┬╴F
#  ╭─┤   ╰╴G
#  │ │ ╭╴H
#  │ ╰─┤ ╭─┬╴I
# ─┤   ╰─┤ ╰╴J
#  │     ╰─┬╴K
#  │       ╰╴L
#  ╰─┬╴B
#    ╰╴C

# But remember! You should never do things like:
#
# A.add_child(t1)
