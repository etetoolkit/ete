import random
from ete3 import Tree
# Creates a normal tree
t = Tree( '((H:0.3,I:0.1):0.5, A:1, (B:0.4,(C:0.5,(J:1.3, (F:1.2, D:0.1):0.5):0.5):0.5):0.5);' )
print t
# Let's locate some nodes using the get common ancestor method
ancestor=t.get_common_ancestor("J", "F", "C")
# the search_nodes method (I take only the first match )
A = t.search_nodes(name="A")[0]
# and using the shorcut to finding nodes by name
C= t&"C"
H= t&"H"
I= t&"I"
# Let's now add some custom features to our nodes. add_features can be
#  used to add many features at the same time.
C.add_features(vowel=False, confidence=1.0)
A.add_features(vowel=True, confidence=0.5)
ancestor.add_features(nodetype="internal")
# Or, using the oneliner notation
(t&"H").add_features(vowel=False, confidence=0.2)
# But we can automatize this. (note that i will overwrite the previous
# values)
for leaf in t.traverse():
    if leaf.name in "AEIOU":
        leaf.add_features(vowel=True, confidence=random.random())
    else:
        leaf.add_features(vowel=False, confidence=random.random())
# Now we use these information to analyze the tree.
print "This tree has", len(t.search_nodes(vowel=True)), "vowel nodes"
print "Which are", [leaf.name for leaf in t.iter_leaves() if leaf.vowel==True]
# But features may refer to any kind of data, not only simple
# values. For example, we can calculate some values and store them
# within nodes.
#
# Let's detect leaf nodes under "ancestor" with distance higher thatn
# 1. Note that I'm traversing a subtree which starts from "ancestor"
matches = [leaf for leaf in ancestor.traverse() if leaf.dist>1.0]
# And save this pre-computed information into the ancestor node
ancestor.add_feature("long_branch_nodes", matches)
# Prints the precomputed nodes
print "These are nodes under ancestor with long branches", \
    [n.name for n in ancestor.long_branch_nodes]
# We can also use the add_feature() method to dynamically add new features.
label = raw_input("custom label:")
value = raw_input("custom label value:")
ancestor.add_feature(label, value)
print "Ancestor has now the [", label, "] attribute with value [", value, "]"
