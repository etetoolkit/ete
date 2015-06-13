from ete3 import PhylomeDBConnector
# This connects to the main phylomeDB server (default parameters)
p = PhylomeDBConnector()
# Obtains the phylomeDB internal ID for my gene of interest
idmatches = p.search_id("ENSG00000146556")
# Take the only match (several would be possible)
geneid = idmatches[0]
# Gets the 'geneid' tree in phylome 1 reconstructed using WAG evolutionary model
t, likelihood = p.get_tree(geneid, "WAG", 1)
print t
#
#                         /-Xtr0044988
#                        |
#                        |     /-Gga0000980
#                        |    |
#                    /---|    |               /-Bta0018700
#                   |    |    |              |
#                   |    |    |              |                    /-Hsa0000001
#                   |    |    |              |               /---|
#                   |    |    |          /---|          /---|     \-Hsa0010733
#                   |     \---|         |    |         |    |
#                   |         |         |    |     /---|     \-Hsa0010710
#                   |         |         |    |    |    |
#                   |         |     /---|     \---|     \-Ptr0000001
#               /---|         |    |    |         |
#              |    |         |    |    |          \-Cfa0016699
#              |    |         |    |    |
#              |    |          \---|    |     /-Rno0030248
#              |    |              |     \---|
#              |    |              |          \-Mms0024821
#          /---|    |              |
#         |    |    |               \-Mdo0014718
#         |    |    |
#         |    |    |     /-Dre0008389
#     /---|    |     \---|
#    |    |    |          \-Fru0004507
#    |    |    |
#    |    |     \-Cin0011238
#----|    |
#    |     \-Aga0007658
#    |
#    |--Dme0014628
#    |
#     \-Ddi0002240
#
# Gets the best evolutionary model tree present in the phylome 1 for a given geneid
winner_model, all_likelihoods, t  = p.get_best_tree(geneid, 1)
# As you can see, the best likelihood tree in this case was
# reconstructed using a JTT model rather than the WAG matrix.
