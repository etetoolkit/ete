from ete_dev import Phyloxml

p = Phyloxml()
p.build_from_file("example1.xml")
print p.phylogeny[0]

p = Phyloxml()
p.build_from_file("ncbi_taxonomy_metazoa.xml")
print "Done"
#print p.phylogeny[0]
