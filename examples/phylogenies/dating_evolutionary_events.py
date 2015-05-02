from ete3 import PhyloTree
# Creates a gene phylogeny with several duplication events at
# different levels. Note that we are using the default method for
# detecting the species code of leaves (three first lettes in the node
# name are considered the species code).
nw = """
((Dme_001,Dme_002),(((Cfa_001,Mms_001),((((Hsa_001,Hsa_003),Ptr_001)
,Mmu_001),((Hsa_004,Ptr_004),Mmu_004))),(Ptr_002,(Hsa_002,Mmu_002))));
"""
t = PhyloTree(nw)
print "Original tree:",
print t
#
#             /-Dme_001
#   /--------|
#  |          \-Dme_002
#  |
#  |                              /-Cfa_001
#  |                    /--------|
#  |                   |          \-Mms_001
#  |                   |
#--|                   |                                        /-Hsa_001
#  |                   |                              /--------|
#  |          /--------|                    /--------|          \-Hsa_003
#  |         |         |                   |         |
#  |         |         |          /--------|          \-Ptr_001
#  |         |         |         |         |
#  |         |         |         |          \-Mmu_001
#  |         |          \--------|
#   \--------|                   |                    /-Hsa_004
#            |                   |          /--------|
#            |                    \--------|          \-Ptr_004
#            |                             |
#            |                              \-Mmu_004
#            |
#            |          /-Ptr_002
#             \--------|
#                      |          /-Hsa_002
#                       \--------|
#                                 \-Mmu_002
# Create a dictionary with relative ages for the species present in
# the phylogenetic tree.  Note that ages are only relative numbers to
# define which species are older, and that different species can
# belong to the same age.
species2age = {
  'Hsa': 1, # Homo sapiens (Hominids)
  'Ptr': 2, # P. troglodytes (primates)
  'Mmu': 2, # Macaca mulata (primates)
  'Mms': 3, # Mus musculus (mammals)
  'Cfa': 3, # Canis familiaris (mammals)
  'Dme': 4  # Drosophila melanogaster (metazoa)
}
# We can translate each number to its correspondig taxonomic number
age2name = {
  1:"hominids",
  2:"primates",
  3:"mammals",
  4:"metazoa"
}
event1= t.get_common_ancestor("Hsa_001", "Hsa_004")
event2=t.get_common_ancestor("Hsa_001", "Hsa_002")
print
print "The duplication event leading to the human sequences Hsa_001 and "+\
    "Hsa_004 is dated at: ", age2name[event1.get_age(species2age)]
print "The duplication event leading to the human sequences Hsa_001 and "+\
    "Hsa_002 is dated at: ", age2name[event2.get_age(species2age)]
# The duplication event leading to the human sequences Hsa_001 and Hsa_004
# is dated at:  primates
#
# The duplication event leading to the human sequences Hsa_001 and Hsa_002
# is dated at:  mammals
