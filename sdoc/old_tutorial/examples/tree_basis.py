from ete3 import Tree
# Creates an empty tree and populates it with some new
# nodes
t = Tree()
A = t.add_child(name="A")
B = t.add_child(name="B")
C = A.add_child(name="C")
D = A.add_child(name="D")
print t
#                    /-C
#          /--------|
#---------|          \-D
#         |
#          \-B
print 'is "t" the root?', t.is_root() # True
print 'is "A" a terminal node?', A.is_leaf() # False
print 'is "B" a terminal node?', B.is_leaf() # True
print 'B.get_tree_root() is "t"?', B.get_tree_root() is t # True
print 'Number of leaves in tree:', len(t) # returns number of leaves under node (3)
print 'is C in tree?', C in t # Returns true
print "All leaf names in tree:", [node.name for node in t]
