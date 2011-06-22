from ete_dev import Phyloxml, phyloxml
import random 

project = Phyloxml()

# Creates a random tree
phylo = phyloxml.PhyloXMLTree()
phylo.populate(5, random_dist=True)
phylo.phyloxml_phylogeny.set_name("test_tree")
# Add the tree to the phyloxml project
project.add_phylogeny(phylo)

print project.get_phylogeny()[0]

#          /-iajom
#     /---|
#    |     \-wiszh
#----|
#    |     /-xrygw
#     \---|
#         |     /-gjlwx
#          \---|
#               \-ijvnk

# Trees can be operated as normal ETE trees
phylo.show()


# Export the project as phyloXML format
project.export()

# <phy:Phyloxml>
#     <phy:phylogeny>
#         <phy:name>test_tree</phy:name>
#         <phy:clade>
#             <phy:name>NoName</phy:name>
#             <phy:confidence type="branch_support">1.0</phy:confidence>
#             <phy:clade>
#                 <phy:name>vnmur</phy:name>
#                 <phy:branch_length>8.952004e-01</phy:branch_length>
#                 <phy:confidence type="branch_support">0.42116997466</phy:confidence>
#             </phy:clade>
#             <phy:clade>
#                 <phy:name>NoName</phy:name>
#                 <phy:branch_length>4.862201e-01</phy:branch_length>
#                 <phy:confidence type="branch_support">0.361907662007</phy:confidence>
#                 <phy:clade>
#                     <phy:name>mrntb</phy:name>
#                     <phy:branch_length>4.952616e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.638935066222</phy:confidence>
#                 </phy:clade>
#                 <phy:clade>
#                     <phy:name>NoName</phy:name>
#                     <phy:branch_length>4.925216e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.786868092056</phy:confidence>
#                     <phy:clade>
#                         <phy:name>selav</phy:name>
#                         <phy:branch_length>9.488587e-01</phy:branch_length>
#                         <phy:confidence type="branch_support">0.283151040908</phy:confidence>
#                     </phy:clade>
#                     <phy:clade>
#                         <phy:name>NoName</phy:name>
#                         <phy:branch_length>8.244555e-01</phy:branch_length>
#                         <phy:confidence type="branch_support">0.756896679656</phy:confidence>
#                         <phy:clade>
#                             <phy:name>wlfpo</phy:name>
#                             <phy:branch_length>8.214268e-01</phy:branch_length>
#                             <phy:confidence type="branch_support">0.143944613883</phy:confidence>
#                         </phy:clade>
#                         <phy:clade>
#                             <phy:name>bsaqu</phy:name>
#                             <phy:branch_length>7.529829e-01</phy:branch_length>
#                             <phy:confidence type="branch_support">0.140360900938</phy:confidence>
#                         </phy:clade>
#                     </phy:clade>
#                 </phy:clade>
#             </phy:clade>
#         </phy:clade>
#     </phy:phylogeny>
# </phy:Phyloxml>
