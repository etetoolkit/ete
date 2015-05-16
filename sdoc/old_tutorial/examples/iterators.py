import time
from ete2 import Tree
# Creates a random tree with 10,000 leaf nodes
tree = Tree()
tree.populate(10000)
# This code should be faster
t1 = time.time()
for leaf in tree.iter_leaves():
    if "aw" in leaf.name:
        print "found a match:", leaf.name,
        break
print "Iterating: ellapsed time:", time.time()-t1
# This slower
t1 = time.time()
for leaf in tree.get_leaves():
    if "aw" in leaf.name:
        print "found a match:", leaf.name,
        break
print "Getting: ellapsed time:", time.time()-t1
# Results in something like:
# found a match: guoaw Iterating: ellapsed time: 0.00436091423035 secs
# found a match: guoaw Getting: ellapsed time: 0.124316930771 secs
