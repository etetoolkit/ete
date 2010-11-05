from ete_dev import Phyloxml

p = Phyloxml()
p.build_from_file("example1.xml")
for t in p.phylogeny:
    print t

p = Phyloxml()
p.build_from_file("phyloxml_examples.xml")
for t in p.phylogeny:
    print t


p = Phyloxml()
p.build_from_file("ncbi_taxonomy_metazoa.xml")
print "Done"
#print p.phylogeny[0]
