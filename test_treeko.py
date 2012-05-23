import sys
from collections import defaultdict
from ete_dev import PhyloTree

if len(sys.argv) > 1:
    t = PhyloTree(sys.argv[1])
else:
    t = PhyloTree()
    #t.populate(5000, reuse_names=True, names_library=map(lambda x: "%03d" %x, range(100)))

    #t.populate(5000, reuse_names=True, names_library=["aaa", "bbb", "ccc","dddd"])
    #t.set_species_naming_function(lambda x: x[:3])    
    #t = PhyloTree("((((Kla0008018:0.226825,(Kwa0003593:0.270871,(((((((Sce0006606:0.020101,(Smi0000169:0.045626,Sku0001100:0.091634)0.9:0.021336)0.473:0.004546,Spa0001368:0)0.806:0.040152,Sba0000063:0.059101)0.967:0.124536,Sca0004780:0.57162)0.36:0.045976,Cgl0005705:0.244154)0.94:0.080608,(((Spa0003632:0.005291,Sce0012358:0.019313)0.879:0.014349,Smi0005102:0.031246)0.028:0.000541,(Sba0002319:0.027948,Sku0001858:0.037758)0.873:0.023849)0.995:0.14497)0.859:0.056767,(Sca0004490:0.235469,Kpo0005032:0.313188)0.699:0.077825)0.807:0.085287)0.523:0.049374)0.606:0.167197,Ago0006484:0.438321)0.976:0.605273,Cal0012751:1.95721)0.975:0.332581,(Cal0010356:0.478947,((Ago0007434:1.13211,Kwa0002043:1.20443)0.282:0.216219,(Skl0001126:0.276168,Cgl0008719:0.5381)0.454:0.191735)0.934:0.438082)0.975:0.332581);")     
    #t = PhyloTree("((((((AAA1, AAA2),((BBB1,BBB2), AAA3)D1),(CCC1,CCC2)), AAA8)D2, (((AAA5, AAA6),((BBB5,BBB6), AAA4)D3),(CCC3,CCC4)))D4, D);", format=1)
    t = PhyloTree("((((((((AAA1, AAA2:0.111)a1,(((BBB1,ZZZ1)a2,MMM1)a3,AAA4)a4)a5, AAA3)a6,(AAA4, (AAA5, XXX1)a8)a9)a10,DDD)a11,DDD)a12,DDD)a13,DDD)root;", format=1)
    print t.get_ascii()
    
ntrees, ndups, sp_trees = t.get_speciation_trees(map_features=["dist"])

for sptree in sp_trees:
    print sptree.get_ascii(attributes=["dist"])

