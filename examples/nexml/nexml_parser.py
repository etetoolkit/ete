from ete3 import Nexml
# Create an empty Nexml project
nexml_project = Nexml()

# Load content from NeXML file
nexml_project.build_from_file("trees.xml")

# All XML elements are within the project instance.
# exist in each element to access their attributes.
print "Loaded Taxa:"
for taxa in  nexml_project.get_otus():
    for otu in taxa.get_otu():
        print "OTU:", otu.id

# Extracts all the collection of trees in the project
tree_collections = nexml_project.get_trees()
# Select the first collection
collection_1 = tree_collections[0]

# print the topology of every tree
for tree in  collection_1.get_tree():
    # trees contain all the nexml information in their "nexml_node",
    # "nexml_tree", and "nexml_edge" attributes.
    print "Tree id", tree.nexml_tree.id
    print tree
    for node in tree.traverse():
        print "node", node.nexml_node.id, "is associated with", node.nexml_node.otu, "OTU"


# Output:
# ==========
# Loaded Taxa:
# OTU: t1
# OTU: t2
# OTU: t3
# OTU: t4
# OTU: t5
# Tree id tree1
#
#                /-n5(n5)
#           /---|
#          |     \-n6(n6)
#      /---|
#     |    |     /-n8(n8)
# ----|     \---|
#     |          \-n9(n9)
#     |
#      \-n2(n2)
# node n1 is associated with None OTU
# node n3 is associated with None OTU
# node n2 is associated with t1 OTU
# node n4 is associated with None OTU
# node n7 is associated with None OTU
# node n5 is associated with t3 OTU
# node n6 is associated with t2 OTU
# node n8 is associated with t5 OTU
# node n9 is associated with t4 OTU
# Tree id tree2
#
#                /-tree2n5(n5)
#           /---|
#          |     \-tree2n6(n6)
#      /---|
#     |    |     /-tree2n8(n8)
# ----|     \---|
#     |          \-tree2n9(n9)
#     |
#      \-tree2n2(n2)
# node tree2n1 is associated with None OTU
# node tree2n3 is associated with None OTU
# node tree2n2 is associated with t1 OTU
# node tree2n4 is associated with None OTU
# node tree2n7 is associated with None OTU
# node tree2n5 is associated with t3 OTU
# node tree2n6 is associated with t2 OTU
# node tree2n8 is associated with t5 OTU
# node tree2n9 is associated with t4 OTU
