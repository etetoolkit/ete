import sys
from ete_dev import Phyloxml

p = Phyloxml()
p.build_from_file("example1.xml")
for t in p.phylogeny:
    print t

OUT = open("/tmp/phyloxml.tmp.xml", "w")
p.export(OUT, 0, namespacedef_='xmlns:phy="http://www.phyloxml.org"')
OUT.close()


p = Phyloxml()
p.build_from_file("/tmp/phyloxml.tmp.xml")
for t in p.phylogeny:
    print t

########
p = Phyloxml()
p.build_from_file("apaf.xml")
for t in p.phylogeny:
    print t

OUT = open("/tmp/phyloxml.tmp.xml", "w")
p.export(OUT, 0, namespacedef_='xmlns:phy="http://www.phyloxml.org"')
OUT.close()


p = Phyloxml()
p.build_from_file("/tmp/phyloxml.tmp.xml")
for t in p.phylogeny:
    print t













p = Phyloxml()
p.build_from_file("phyloxml_examples.xml")
for t in p.phylogeny:
    print t


#p = Phyloxml()
#p.build_from_file("ncbi_taxonomy_metazoa.xml")
#print "Done"
#print p.phylogeny[0]
