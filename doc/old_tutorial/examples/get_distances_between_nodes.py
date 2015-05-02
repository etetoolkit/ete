from ete3 import Tree

# Loads a tree with branch lenght information. Note that if no
# distance info is provided in the newick, it will be initialized with
# the default dist value = 1.0
nw = """(((A:0.1, B:0.01):0.001, C:0.0001):1.0,
(((((D:0.00001:0,I:0):0,F:0):0,G:0):0,H:0):0,
E:0.000001):0.0000001):2.0;"""
t = Tree(nw)
print t
#                              /-A
#                    /--------|
#          /--------|          \-B
#         |         |
#         |          \-C
#         |
#         |                                                  /-D
#         |                                        /--------|
#---------|                              /--------|          \-I
#         |                             |         |
#         |                    /--------|          \-F
#         |                   |         |
#         |          /--------|          \-G
#         |         |         |
#          \--------|          \-H
#                   |
#                    \-E
#
# Locate some nodes
A = t&"A"
C = t&"C"
# Calculate distance from current node
print "The distance between A and C is",  A.get_distance("C")
# Calculate distance between two descendants of current node
print "The distance between A and C is",  t.get_distance("A","C")
# Calculate the toplogical distance (number of nodes in between)
print "The number of nodes between A and D is ",  \
    t.get_distance("A","D", topology_only=True)
# Calculate the farthest node from E within the whole structure
farthest, dist = (t&"E").get_farthest_node()
print "The farthest node from E is", farthest.name, "with dist=", dist
# Calculate the farthest node from E within the whole structure,
# regarding the number of nodes in between as distance value
# Note that the result is differnt.
farthest, dist = (t&"E").get_farthest_node(topology_only=True)
print "The farthest (topologically) node from E is", \
    farthest.name, "with", dist, "nodes in between"
# Calculate farthest node from an internal node
farthest, dist = t.get_farthest_node()
print "The farthest node from root is is", farthest.name, "with dist=", dist
#
# The program results in the following information:
#
# The distance between A and C is 0.1011
# The distance between A and C is 0.1011
# The number of nodes between A and D is  8.0
# The farthest node from E is A with dist= 1.1010011
# The farthest (topologically) node from E is I with 5.0 nodes in between
# The farthest node from root is is A with dist= 1.101
