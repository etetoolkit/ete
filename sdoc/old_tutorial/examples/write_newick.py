from ete3 import Tree
# Loads a tree with internal node names
t = Tree('(A:1,(B:1,(E:1,D:1)Internal_1:0.5)Internal_2:0.5)Root;', format=1)
# And prints its newick representation omiting all the information but
# the tree topology
print t.write(format=100) # (,(,(,)));
# We can also write into a file
t.write(format=100, outfile="/tmp/tree.new")
