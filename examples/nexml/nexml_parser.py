from ete_dev import Nexml

p = Nexml()
p.build_from_file("trees.xml")
tree_collection = p.trees[0]
trees = tree_collection.tree

for t in trees:
    print t

