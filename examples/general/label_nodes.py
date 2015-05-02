from ete3 import Tree
tree = Tree( '(A:1,(B:1,(C:1,D:1):0.5):0.5);' )
# Prints the name of every leaf under the tree root
print "Leaf names:"
for leaf in tree.get_leaves():
    print leaf.name
# Label nodes as terminal or internal. If internal, saves also the
# number of leaves that it contains.
print "Labeled tree:"
for node in tree.get_descendants():
    if node.is_leaf():
        node.add_features(ntype="terminal")
    else:
        node.add_features(ntype="internal", size=len(node))
# Gets the extended newick of the tree including new node features
print tree.write(features=[])
