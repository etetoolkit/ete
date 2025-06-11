from ete4 import Tree

# Create an empty tree and populate it with some new nodes.
t = Tree()
A = t.add_child(name="A")
B = t.add_child(name="B")
C = A.add_child(name="C")
D = A.add_child(name="D")
print(t)
#  ╭─┬╴C
# ─┤ ╰╴D
#  ╰╴B

print('Is "t" the root?', t.is_root) # True
print('Is "A" a terminal node?', A.is_leaf) # False
print('Is "B" a terminal node?', B.is_leaf) # True
print('B.root is "t"?', B.root is t) # True
print('Number of leaves in tree:', len(t)) # 3
print('Is C in tree?', C in t) # True
print("All leaf names in tree:", [node.name for node in t.leaves()])
