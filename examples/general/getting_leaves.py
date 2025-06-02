from ete4 import Tree

# Create a basic tree.
t = Tree('(A:0.2,(B:0.4,(C:1.1,D:0.45):0.5):0.1);')

print(t)
# ─┬╴A
#  ╰─┬╴B
#    ╰─┬╴C
#      ╰╴D

# Counts leaves within the tree
nleaves = 0
for leaf in t.leaves():
    nleaves += 1

print('This tree has', nleaves, 'terminal nodes')

# But, like this is much simpler :)
nleaves = len(t)
print('This tree has', nleaves, 'terminal nodes (using len(tree))')

# Count leaves within the tree.
ninternal = 0
for node in t.descendants():
    if not node.is_leaf:
        ninternal +=1

print('This tree has', ninternal,  'internal nodes')

# Count nodes with whose distance is bigger than 0.3.
nnodes = 0
for node in t.descendants():
    if node.dist > 0.3:
        nnodes +=1

print('This tree has', nnodes, 'nodes with a branch length > 0.3')

# or, more pythonic:
nnodes = sum(1 for n in t.descendants() if n.dist > 0.3)
print('This tree has', nnodes, 'nodes with a branch length > 0.3')
