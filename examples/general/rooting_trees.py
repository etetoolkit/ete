from ete4 import Tree

# Create an unrooted tree. Note that three branches hang from the root
# node. This usually means that no information is available about
# which of the nodes is more basal.
t = Tree('(A,(H,F),(B,(E,D)));')

print('Unrooted tree:')
print(t)
#  ╭╴A
# ─┼─┬╴H
#  │ ╰╴F
#  ╰─┬╴B
#    ╰─┬╴E
#      ╰╴D

# Let's define the ancestor of E and D as the tree outgroup. Of
# course, the definition of an outgroup will depend on user criteria.
ancestor = t.common_ancestor('E', 'D')

t.set_outgroup(ancestor)

print("Tree rooted at E and D's ancestor is more basal that the others.")
print(t)
#  ╭─┬╴E
# ─┤ ╰╴D
#  ╰─┬╴B
#    ╰─┬╴A
#      ╰─┬╴H
#        ╰╴F

# Note that setting a different outgroup, a different interpretation
# of the tree is possible.
t.set_outgroup(t['A'])

print('Tree rooted at a terminal node:')
print(t)
#  ╭╴A
# ─┤ ╭─┬╴H
#  ╰─┤ ╰╴F
#    ╰─┬╴B
#      ╰─┬╴E
#        ╰╴D
