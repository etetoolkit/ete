from ete4 import Tree

# Loads a tree structure from a newick string. The returned variable
# 't' is the root node for the tree.
t = Tree('(A:1,(B:1,(E:1,D:1):0.5):0.5);')
print(t)
# ─┬╴A
#  ╰─┬╴B
#    ╰─┬╴E
#      ╰╴D

# Load a tree structure from a newick file.
t = Tree(open('genes_tree.nh'))
print(t)
#  ╭╴Ddi0002240
# ─┼╴Dme0014628
#  │ ╭╴Aga0007658
#  ╰─┤ ╭╴Cin0011239
#    │ │   ╭╴Fru0004507
#    ╰─┤ ╭─┤ ╭─┬╴Dre0008391
#      │ │ ╰─┤ ╰╴Dre0008390
#      ╰─┤   ╰╴Dre0008392
#        │ ╭─┬╴Xtr0044988
#        │ │ ╰─┬╴Gga0000982
#        ╰─┤   ╰╴Gga0000981
#          │ ╭╴Mdo0014718
#          ╰─┤ ╭─┬╴Mms0024821
#            ╰─┤ ╰╴Rno0030248
#              │ ╭─┬╴Cfa0016700
#              ╰─┤ ╰╴Bta0018700
#                │ ╭╴Ptr0000001
#                ╰─┤ ╭─┬╴Hsa0010730
#                  ╰─┤ ╰╴Hsa0000001
#                    ╰╴Hsa0010711

# You can also specify the newick format. For instance, for named
# internal nodes we will use the parser 1.
t = Tree('(A:1,(B:1,(E:1,D:1)Internal_1:0.5)Internal_2:0.5)Root;', parser=1)
print(t)
# ─┬╴A
#  ╰─┬╴B
#    ╰─┬╴E
#      ╰╴D
