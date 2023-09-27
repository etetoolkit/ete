from ete4 import PhyloTree

# Create a phylogenetic tree (using default species name encoding).
t = PhyloTree('(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));')

print(t)
#    ╭─┬╴Hsa_001
#  ╭─┤ ╰╴Ptr_001
# ─┤ ╰─┬╴Cfa_001
#  │   ╰╴Mms_001
#  ╰─┬╴Dme_001
#    ╰╴Dme_002

# Print current leaf names and species codes (in deafult mode).
for n in t:
    print('Node:', n.name, '  Species:', n.species)
# Node: Hsa_001   Species: Hsa
# Node: Ptr_001   Species: Ptr
# Node: Cfa_001   Species: Cfa
# Node: Mms_001   Species: Mms
# Node: Dme_001   Species: Dme
# Node: Dme_002   Species: Dme

# We can also use our own leaf name parsing function to obtain species
# names. All we need to do is create a python function that takes
# a node's name as argument and returns its corresponding species name.
def get_species_name(node_name_string):
    # Species code is the first part of leaf name (separated by an
    # underscore character).
    spcode = node_name_string.split('_')[0]

    # We could even translate the code to complete names
    code2name = {
        'Dme':'Drosophila melanogaster',
        'Hsa':'Homo sapiens',
        'Ptr':'Pan troglodytes',
        'Mms':'Mus musculus',
        'Cfa':'Canis familiaris'
    }
    return code2name[spcode]

# Now, let's ask the tree to use our custom species naming function.
t.set_species_naming_function(get_species_name)

for n in t:
    print('Node:', n.name, '  Species:', n.species)
# Node: Hsa_001   Species: Homo sapiens
# Node: Ptr_001   Species: Pan troglodytes
# Node: Cfa_001   Species: Canis familiaris
# Node: Mms_001   Species: Mus musculus
# Node: Dme_001   Species: Drosophila melanogaster
# Node: Dme_002   Species: Drosophila melanogaster

# Of course, you can disable the automatic generation of species
# names. To do so, you can set the species naming function to None.
# This is useful to set the species names manually or for reading them
# from a newick file. Otherwise, the species attribute would be overwriten.
mynewick = """
(((Hsa_001[&&NHX:species=Human],Ptr_001[&&NHX:species=Chimp]),
(Cfa_001[&&NHX:species=Dog],Mms_001[&&NHX:species=Mouse])),
(Dme_001[&&NHX:species=Fly],Dme_002[&&NHX:species=Fly]));
"""

t = PhyloTree(mynewick, sp_naming_function=None)

for n in t:
    print('Node:', n.name, '  Species:', n.species)
# Node: Hsa_001   Species: Human
# Node: Ptr_001   Species: Chimp
# Node: Cfa_001   Species: Dog
# Node: Mms_001   Species: Mouse
# Node: Dme_001   Species: Fly
# Node: Dme_002   Species: Fly

# Of course, once this info is available you can query any internal
# node for species covered.
human_mouse_ancestor = t.common_ancestor(['Hsa_001', 'Mms_001'])

# These are the species under the common ancestor of Human & Mouse:
for species in human_mouse_ancestor.get_species():
    print(species)
# Mouse
# Human
# Chimp
# Dog
