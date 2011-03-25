from ete_dev import Nexml

# Creates an empty Nexml container
p = Nexml()
# Load data from XML file
p.build_from_file("trees.xml")
# Access to the first collection of trees contained
tree_collection = p.trees[0]
# And to the list of trees within it
trees = tree_collection.tree

# Trees are normal ETE PhyloTree objects. All PhyloTree methods and
# features are available, plus two extra attributes called
# "nexml_node" and "nexml_edge", containing all extra NExML info.
for t in trees:
    print t
    print t.nexml_node



print "tolweb"
p = Nexml()
p.build_from_file("tolweb.xml")
tree_collection = p.trees[0]
trees = tree_collection.tree

for t in trees:
    print t
    print "NODE meta information:"
    for meta in  t.children[0].nexml_node.meta:
        print  meta.property, ":", (meta.content)
