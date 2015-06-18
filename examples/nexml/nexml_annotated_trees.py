from ete3 import Nexml

# Creates and empty NeXML project
p = Nexml()
# Fill it with the tolweb example
p.build_from_file("tolweb.xml")

# extract the first collection of trees
tree_collection = p.trees[0]
# and all the tree instances in it
trees = tree_collection.tree

# For each loaded tree, prints its structure and some of its
# meta-properties
for t in trees:
    print t
    print
    print "Leaf node meta information:\n"
    print
    for meta in  t.children[0].nexml_node.meta:
        print  meta.property, ":", (meta.content)


# Output
# ==========
#
# ---- /-node3(Eurysphindus)
#
# Leaf node meta information:
#
#
# dc:description :
# tbe:AUTHORITY : Leconte
# tbe:AUTHDATE : 1878
# tba:ANCESTORWITHPAGE : 117851
# tba:CHILDCOUNT : 0
# tba:COMBINATION_DATE : null
# tba:CONFIDENCE : 0
# tba:EXTINCT : 0
# tba:HASPAGE : 1
# tba:ID : 117855
# tba:INCOMPLETESUBGROUPS : 0
# tba:IS_NEW_COMBINATION : 0
# tba:ITALICIZENAME : 1
# tba:LEAF : 0
# tba:PHYLESIS : 0
# tba:SHOWAUTHORITY : 0
# tba:SHOWAUTHORITYCONTAINING : 1
