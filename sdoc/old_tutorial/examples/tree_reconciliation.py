from ete2 import PhyloTree

# Loads a gene tree and its corresponding species tree. Note that
# species names in sptree are the 3 firs letters of leaf nodes in
# genetree.
gene_tree_nw = '((Dme_001,Dme_002),(((Cfa_001,Mms_001),((Hsa_001,Ptr_001),Mmu_001)),(Ptr_002,(Hsa_002,Mmu_002))));'
species_tree_nw = "((((Hsa, Ptr), Mmu), (Mms, Cfa)), Dme);"
genetree = PhyloTree(gene_tree_nw)
sptree = PhyloTree(species_tree_nw)
print genetree
#                    /-Dme_001
#          /--------|
#         |          \-Dme_002
#         |
#         |                              /-Cfa_001
#         |                    /--------|
#---------|                   |          \-Mms_001
#         |          /--------|
#         |         |         |                    /-Hsa_001
#         |         |         |          /--------|
#         |         |          \--------|          \-Ptr_001
#          \--------|                   |
#                   |                    \-Mmu_001
#                   |
#                   |          /-Ptr_002
#                    \--------|
#                             |          /-Hsa_002
#                              \--------|
#                                        \-Mmu_002
#
# Let's reconcile our genetree with the species tree
recon_tree, events = genetree.reconcile(sptree)
# a new "reconcilied tree" is returned. As well as the list of
# inferred events.
print "Orthology and Paralogy relationships:"
for ev in events:
    if ev.etype == "S":
        print 'ORTHOLOGY RELATIONSHIP:', ','.join(ev.inparalogs), "<====>", ','.join(ev.orthologs)
    elif ev.etype == "D":
        print 'PARALOGY RELATIONSHIP:', ','.join(ev.inparalogs), "<====>", ','.join(ev.outparalogs)
# And we can explore the resulting reconciled tree
print recon_tree
# You will notice how the reconcilied tree is the same as the gene
# tree with some added branches. They are inferred gene losses.
#
#
#                    /-Dme_001
#          /--------|
#         |          \-Dme_002
#         |
#         |                              /-Cfa_001
#         |                    /--------|
#         |                   |          \-Mms_001
#---------|          /--------|
#         |         |         |                    /-Hsa_001
#         |         |         |          /--------|
#         |         |          \--------|          \-Ptr_001
#         |         |                   |
#         |         |                    \-Mmu_001
#          \--------|
#                   |                    /-Mms
#                   |          /--------|
#                   |         |          \-Cfa
#                   |         |
#                   |         |                              /-Hsa
#                    \--------|                    /--------|
#                             |          /--------|          \-Ptr_002
#                             |         |         |
#                             |         |          \-Mmu
#                              \--------|
#                                       |                    /-Ptr
#                                       |          /--------|
#                                        \--------|          \-Hsa_002
#                                                 |
#                                                  \-Mmu_002
#
# And we can visualize the trees using the default phylogeny
# visualization layout
genetree.show()
recon_tree.show()
