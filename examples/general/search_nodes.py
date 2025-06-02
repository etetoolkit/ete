from ete4 import Tree

# Create a tree.
t = Tree('((H:1,I:1):0.5, A:1, (B:1,(C:1,D:1):0.5):0.5);')

print(t)
#  ╭─┬╴H
# ─┤ ╰╴I
#  ├╴A
#  ╰─┬╴B
#    ╰─┬╴C
#      ╰╴D

# Get D.
D = t.search_nodes(name='D')
# Same as
# D = t['D']

# Get all nodes with distance=0.5.
nodes = list(t.search_nodes(dist=0.5))
print(len(nodes), 'nodes have distance=0.5')
