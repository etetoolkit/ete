import random
from ete4 import Tree

random.seed(42)  # so we reproduce the same results

# Generate a random tree.
t = Tree()
t.populate(10, dist_fn=random.random)

print(t)
#    ╭╴f
#  ╭─┤ ╭─┬╴i
#  │ ╰─┤ ╰╴e
#  │   ╰╴g
# ─┤     ╭─┬╴d
#  │   ╭─┤ ╰─┬╴j
#  │ ╭─┤ │   ╰╴c
#  ╰─┤ │ ╰╴b
#    │ ╰╴h
#    ╰╴a

# Find the midpoint node.
R = t.get_midpoint_outgroup()

# and set it as tree outgroup.
t.set_outgroup(R)

print(t)
#      ╭─┬╴d
#    ╭─┤ ╰─┬╴j
#  ╭─┤ │   ╰╴c
#  │ │ ╰╴b
# ─┤ ╰╴h
#  │ ╭╴a
#  ╰─┤ ╭╴f
#    ╰─┤ ╭─┬╴i
#      ╰─┤ ╰╴e
#        ╰╴g
