import random
from ete4 import Tree

# Creates a normal tree
t = Tree('((H:0.3,I:0.1):0.5, A:1,(B:0.4,(C:0.5,(J:1.3,(F:1.2, D:0.1):0.5):0.5):0.5):0.5);')
print(t)

# Let's locate some nodes using the common ancestor method
ancestor = t.common_ancestor('J', 'F', 'C')

# Let's label  leaf nodes
for leaf in t.traverse():
    if leaf.name and leaf.name in 'AEIOU':
        leaf.add_props(vowel=True, confidence=random.random())
    else:
        leaf.add_props(vowel=False, confidence=random.random())

# Let's detect leaf nodes under 'ancestor' with distance higher thatn
# 1. Note that I'm traversing a subtree which starts from 'ancestor'
matches = [leaf for leaf in ancestor.leaves() if leaf.dist > 1]

# And save this pre-computed information into the ancestor node
ancestor.add_prop('long_branch_nodes', matches)

print('\nNHX notation including vowel and confidence attributes\n')
print(t.write(props=['vowel', 'confidence']))

print("\nNHX notation including all node's data\n")
# Note that when all features are requested, only those with values
# equal to text-strings or numbers are considered. 'long_branch_nodes'
# is not included into the newick string.
print(t.write(props=None))

print('\nBasic newick formats are still available\n')
print(t.write(parser=9, props=['vowel']))

# You don't need to do anything speciall to read NHX notation. Just
# specify the newick format and the NHX tags will be automatically
# detected.
nw = """
(((ADH2:0.1[&&NHX:S=human:E=1.1.1.1], ADH1:0.11[&&NHX:S=human:E=1.1.1.1])
:0.05[&&NHX:S=Primates:E=1.1.1.1:D=Y:B=100], ADHY:0.1[&&NHX:S=nematode:
E=1.1.1.1],ADHX:0.12[&&NHX:S=insect:E=1.1.1.1]):0.1[&&NHX:S=Metazoa:
E=1.1.1.1:D=N], (ADH4:0.09[&&NHX:S=yeast:E=1.1.1.1],ADH3:0.13[&&NHX:S=yeast:
E=1.1.1.1], ADH2:0.12[&&NHX:S=yeast:E=1.1.1.1],ADH1:0.11[&&NHX:S=yeast:E=1.1.1.1]):0.1
 [&&NHX:S=Fungi])[&&NHX:E=1.1.1.1:D=N];""".replace('\n', '')

# Loads the NHX example found at http://www.phylosoft.org/NHX/
t = Tree(nw)

# And access node's attributes.
for n in t.traverse():
    if 'S' in n.props:
        print(n.name, n.props['S'])
