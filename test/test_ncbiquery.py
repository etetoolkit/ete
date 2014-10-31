import unittest 

from ete_dev import PhyloTree, NCBITaxa

class Test_ncbiquery(unittest.TestCase):
  
  def test_tree_annotation(self):
    t = PhyloTree( "((9598, 9606), 10090);" )
    t.annotate_ncbi_taxa()
    self.assertEqual(t.spname, 'Euarchontoglires')
    homi = (t&'9606').up
    self.assertEqual(homi.spname, 'Homininae')
    self.assertEqual(homi.taxid, 207598)
    self.assertEqual(homi.rank, 'subfamily')
    self.assertEqual(homi.named_lineage, [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae'])
    self.assertEqual(homi.lineage, [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598] )

    human = t&'9606'
    self.assertEqual(human.spname, 'Homo sapiens')
    self.assertEqual(human.taxid, 9606)
    self.assertEqual(human.rank, 'species')
    self.assertEqual(human.named_lineage, [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae', u'Homo', u'Homo sapiens'])
    self.assertEqual(human.lineage, [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605, 9606])

  def test_ncbi_compare(self):
    t = PhyloTree( "((9606, (9598, 9606)), 10090);", sp_naming_function=lambda x: x.name )
    t.annotate_ncbi_taxa()
    #t.ncbi_compare()

  def test_ncbiquery(self):
    ncbi = NCBITaxa()

    id2name = ncbi.get_taxid_translator(['9606', '7507'])
    self.assertEqual(id2name[7507], 'Mantis religiosa')
    self.assertEqual(id2name[9606], 'Homo sapiens')

    name2id = ncbi.get_name_translator(['Mantis religiosa', 'homo sapiens'])
    self.assertEqual(name2id['Mantis religiosa'], 7507)
    self.assertEqual(name2id['homo sapiens'], 9606)

  def test_get_topology(self):
    ncbi = NCBITaxa()
    t1 = ncbi.get_topology([9606, 7507, 9604])
    t2 = ncbi.get_topology([9606, 7507, 678])

    self.assertEqual(sorted(t1.get_leaf_names()), ["7507", "9606"])
    self.assertEqual(sorted(t2.get_leaf_names()), ["678", "7507", "9606"])


    
    
    

if __name__ == '__main__':
  unittest.main()
