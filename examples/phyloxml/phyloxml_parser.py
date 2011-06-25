from ete_dev import Phyloxml
project = Phyloxml()
project.build_from_file("apaf.xml")

# Each tree contains the same methods as a PhyloTree object
for tree in project.get_phylogeny():
    print tree
    # you can even use rendering options
    tree.show()
    # PhyloXML features are stored in the phyloxml_clade attribute
    for node in tree: 
        if node.phyloxml_clade.get_sequence(): 
            print "Node name:", node.name
            for seq in node.phyloxml_clade.sequence: 
                for domain in seq.domain_architecture.get_domain():
                    domain_data = [domain.valueOf_, domain.get_from(), domain.get_to()]
                    print "   ", '\t'.join(map(str, domain_data))
