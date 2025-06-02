from ete4 import Tree

t = Tree('(((A,C),((H,F),(L,M))),((B,(J,K)),(E,D)));')

print('Original tree:')
print(t)
#    ╭─┬╴A
#  ╭─┤ ╰╴C
#  │ │ ╭─┬╴H
#  │ ╰─┤ ╰╴F
# ─┤   ╰─┬╴L
#  │     ╰╴M
#  │ ╭─┬╴B
#  ╰─┤ ╰─┬╴J
#    │   ╰╴K
#    ╰─┬╴E
#      ╰╴D

# Each main branch of the tree is independently rooted.
node1 = t.common_ancestor('A', 'H').detach()
node2 = t.common_ancestor('B', 'D').detach()

node1.set_outgroup('H')
node2.set_outgroup('E')

t = node1 + node2

print('Tree after rooting each node independently:')
print(t)
#    ╭╴H
#  ╭─┤ ╭╴F
#  │ ╰─┤ ╭─┬╴L
# ─┤   ╰─┤ ╰╴M
#  │     ╰─┬╴A
#  │       ╰╴C
#  ╰─┬╴E
#    ╰─┬╴D
#      ╰─┬╴B
#        ╰─┬╴J
#          ╰╴K
