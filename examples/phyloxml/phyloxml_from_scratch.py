from ete3 import Phyloxml, phyloxml
import random
project = Phyloxml()

# Creates a random tree
phylo = phyloxml.PhyloxmlTree()
phylo.populate(5, random_branches=True)
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

# <phy:Phyloxml xmlns:phy="http://www.phyloxml.org/1.10/phyloxml.xsd">
#     <phy:phylogeny>
#         <phy:name>test_tree</phy:name>
#         <phy:clade>
#             <phy:name>NoName</phy:name>
#             <phy:branch_length>0.000000e+00</phy:branch_length>
#             <phy:confidence type="branch_support">1.0</phy:confidence>
#             <phy:clade>
#                 <phy:name>NoName</phy:name>
#                 <phy:branch_length>1.665083e-01</phy:branch_length>
#                 <phy:confidence type="branch_support">0.938507980435</phy:confidence>
#                 <phy:clade>
#                     <phy:name>NoName</phy:name>
#                     <phy:branch_length>1.366655e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.791888248212</phy:confidence>
#                     <phy:clade>
#                         <phy:name>ojnfg</phy:name>
#                         <phy:branch_length>2.194209e-01</phy:branch_length>
#                         <phy:confidence type="branch_support">0.304705977822</phy:confidence>
#                     </phy:clade>
#                     <phy:clade>
#                         <phy:name>qrfnz</phy:name>
#                         <phy:branch_length>5.235437e-02</phy:branch_length>
#                         <phy:confidence type="branch_support">0.508533765418</phy:confidence>
#                     </phy:clade>
#                 </phy:clade>
#                 <phy:clade>
#                     <phy:name>shngq</phy:name>
#                     <phy:branch_length>9.740958e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.642187390965</phy:confidence>
#                 </phy:clade>
#             </phy:clade>
#             <phy:clade>
#                 <phy:name>NoName</phy:name>
#                 <phy:branch_length>3.806412e-01</phy:branch_length>
#                 <phy:confidence type="branch_support">0.383619811911</phy:confidence>
#                 <phy:clade>
#                     <phy:name>vfmnk</phy:name>
#                     <phy:branch_length>6.495163e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.141298879514</phy:confidence>
#                 </phy:clade>
#                 <phy:clade>
#                     <phy:name>btexi</phy:name>
#                     <phy:branch_length>5.704955e-01</phy:branch_length>
#                     <phy:confidence type="branch_support">0.951876078012</phy:confidence>
#                 </phy:clade>
#             </phy:clade>
#         </phy:clade>
#     </phy:phylogeny>
# </phy:Phyloxml>
