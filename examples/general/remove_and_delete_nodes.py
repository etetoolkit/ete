from ete4 import Tree

# Loads a tree. Note that we use parser 1 to read internal node names.
t = Tree('((((H,K)D,(F,I)G)B,E)A,((L,(N,Q)O)J,(P,S)M)C);', parser=1)

print('Original tree looks like this:')
# This is an alternative to 'print(t)', with more of control on how it
# is printed. Here we print the tree showing internal node names.
print(t.to_str(show_internal=True, props=['name']))
#                ╭╴H
#            ╭╴D╶┤
#            │   ╰╴K
#        ╭╴B╶┤
#        │   │   ╭╴F
#    ╭╴A╶┤   ╰╴G╶┤
#    │   │       ╰╴I
#    │   │
#    │   ╰╴E
# ╴⊗╶┤
#    │       ╭╴L
#    │   ╭╴J╶┤
#    │   │   │   ╭╴N
#    │   │   ╰╴O╶┤
#    ╰╴C╶┤       ╰╴Q
#        │
#        │   ╭╴P
#        ╰╴M╶┤
#            ╰╴S

# Get specific nodes.
G = t['G']  # same as  next(t.search_nodes(name='G'))
J = t['J']
C = t['C']

# If we detach J from the tree, the whole partition under J node will
# be detached from the tree and it will be considered an independent
# tree. We can do the same thing using two approaches: J.detach() or
# C.remove_child(J).
removed_node = J.detach() # same as C.remove_child(J)

# If we know print the original tree, we will see how J partition is
# no longer there.
print('Tree after DETACHING the node J:')
print(t.to_str(show_internal=True, props=['name']))
#                ╭╴H
#            ╭╴D╶┤
#            │   ╰╴K
#        ╭╴B╶┤
#        │   │   ╭╴F
#    ╭╴A╶┤   ╰╴G╶┤
#    │   │       ╰╴I
#    │   │
# ╴⊗╶┤   ╰╴E
#    │
#    │       ╭╴P
#    ╰╴C╶╌╴M╶┤
#            ╰╴S

# However, if we DELETE the node G, only G will be eliminated from the
# tree, and all its descendants will then hang from the next upper
# node.
G.delete()
print('Tree after DELETING the node G:')
print(t.to_str(show_internal=True, props=['name']))
#                ╭╴H
#            ╭╴D╶┤
#            │   ╰╴K
#        ╭╴B╶┤
#        │   ├╴F
#    ╭╴A╶┤   │
#    │   │   ╰╴I
#    │   │
# ╴⊗╶┤   ╰╴E
#    │
#    │       ╭╴P
#    ╰╴C╶╌╴M╶┤
#            ╰╴S
