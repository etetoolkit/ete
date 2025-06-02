from ete4 import Tree

tree = Tree('(A:1,(B:1,(C:1,D:1):0.5):0.5);')

# Print the name of every leaf under the tree root.
print('Leaf names:')
for leaf in tree.leaves():
    print(leaf.name)

# Label nodes as terminal or internal. If internal, saves also the
# number of leaves that it contains.
print('Labeled tree:')
for node in tree.descendants():
    if node.is_leaf:
        node.add_props(ntype='terminal')
    else:
        node.add_props(ntype='internal', size=len(node))

# Get the extended newick of the tree including new node features.
print(tree.write(props=None))
# (A:1[&&NHX:ntype=terminal],(B:1[&&NHX:ntype=terminal],(C:1[&&NHX:ntype=terminal],D:1[&&NHX:ntype=terminal]):0.5[&&NHX:ntype=internal:size=2]):0.5[&&NHX:ntype=internal:size=3]);
