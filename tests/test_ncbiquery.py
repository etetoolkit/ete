import os
import unittest

from ete4 import PhyloTree, NCBITaxa, ETE_DATA_HOME
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'

class Test_ncbiquery(unittest.TestCase):

  def test_00_update_database(self):

    if not os.path.exists(DATABASE_PATH):
      ncbiquery.update_db(DATABASE_PATH)


  def test_01tree_annotation(self):
    # using name as species attribute
    t = PhyloTree( "((9598, 9606), 10090);", sp_naming_function=lambda name: name)
    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH)
    self.assertEqual(t.props.get('sci_name'), 'Euarchontoglires')

    homi = t['9606'].up
    self.assertEqual(homi.props.get('sci_name'), 'Homininae')
    self.assertEqual(homi.props.get('taxid'), 207598)
    self.assertEqual(homi.props.get('rank'), 'subfamily')
    self.assertEqual(homi.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae'])
    self.assertEqual(homi.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598] )

    human = t['9606']
    self.assertEqual(human.props.get('sci_name'), 'Homo sapiens')
    self.assertEqual(human.props.get('taxid'), 9606)
    self.assertEqual(human.props.get('rank'), 'species')
    self.assertEqual(human.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae', u'Homo', u'Homo sapiens'])
    self.assertEqual(human.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605, 9606])

  def test_02tree_annotation(self):
    # assign species attribute via sp_naming_function
    t = PhyloTree( "((9598|protA, 9606|protB), 10090|propC);", sp_naming_function=lambda name: name.split('|')[0])
    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH, taxid_attr='species')
    
    homi = t['9606|protB'].up
    self.assertEqual(homi.props.get('sci_name'), 'Homininae')
    self.assertEqual(homi.props.get('taxid'), 207598)
    self.assertEqual(homi.props.get('rank'), 'subfamily')
    self.assertEqual(homi.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae'])
    self.assertEqual(homi.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598] )

    human = t['9606|protB']
    self.assertEqual(human.props.get('sci_name'), 'Homo sapiens')
    self.assertEqual(human.props.get('taxid'), 9606)
    self.assertEqual(human.props.get('rank'), 'species')
    self.assertEqual(human.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae', u'Homo', u'Homo sapiens'])
    self.assertEqual(human.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605, 9606])

  def test_03tree_annotation(self):
    # Using custom property as taxonomic identifier 
    t = PhyloTree( "((protA, protB), propC);")
    # add property called "spcode"
    t['protA'].add_prop('spcode', 9598)
    t['protB'].add_prop('spcode', 9606)
    t['propC'].add_prop('spcode', 10090)
    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH, taxid_attr='spcode')
    
    homi = t['protB'].up
    self.assertEqual(homi.props.get('sci_name'), 'Homininae')
    self.assertEqual(homi.props.get('taxid'), 207598)
    self.assertEqual(homi.props.get('rank'), 'subfamily')
    self.assertEqual(homi.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae'])
    self.assertEqual(homi.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598] )

    human = t['protB']
    self.assertEqual(human.props.get('sci_name'), 'Homo sapiens')
    self.assertEqual(human.props.get('taxid'), 9606)
    self.assertEqual(human.props.get('rank'), 'species')
    self.assertEqual(human.props.get('named_lineage'), [u'root', u'cellular organisms', u'Eukaryota', u'Opisthokonta', u'Metazoa', u'Eumetazoa', u'Bilateria', u'Deuterostomia', u'Chordata', u'Craniata', u'Vertebrata', u'Gnathostomata', u'Teleostomi', u'Euteleostomi', u'Sarcopterygii', u'Dipnotetrapodomorpha', u'Tetrapoda', u'Amniota', u'Mammalia', u'Theria', u'Eutheria', u'Boreoeutheria', u'Euarchontoglires', u'Primates', u'Haplorrhini', u'Simiiformes', u'Catarrhini', u'Hominoidea', u'Hominidae', u'Homininae', u'Homo', u'Homo sapiens'])
    self.assertEqual(human.props.get('lineage'), [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605, 9606])

  def test_ncbiquery(self):
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)

    id2name = ncbi.get_taxid_translator(['9606', '7507'])
    self.assertEqual(id2name[7507], 'Mantis religiosa')
    self.assertEqual(id2name[9606], 'Homo sapiens')

    name2id = ncbi.get_name_translator(['Mantis religiosa', 'homo sapiens'])
    self.assertEqual(name2id['Mantis religiosa'], [7507])
    self.assertEqual(name2id['homo sapiens'], [9606])

    name2id = ncbi.get_name_translator(['Bacteria'])
    self.assertEqual(set(name2id['Bacteria']), {2})

    out = ncbi.get_descendant_taxa("9605", intermediate_nodes=True)
    self.assertEqual(set(out), {9606, 63221, 741158, 1425170, 2665952, 2665953, 2813598, 2813599})

    out = ncbi.get_descendant_taxa("9605", intermediate_nodes=False)
    self.assertEqual(set(out), {63221, 741158, 2665953, 1425170, 2813599})

    out = ncbi.get_descendant_taxa("9596", intermediate_nodes=False, rank_limit="species")
    self.assertEqual(set(out), {9597, 9598})

  def test_get_topology(self):
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)
    t1 = ncbi.get_topology([9606, 7507, 9604])
    t2 = ncbi.get_topology([9606, 7507, 678])

    self.assertEqual(sorted(t1.leaf_names()), ["7507", "9606"])
    self.assertEqual(sorted(t2.leaf_names()), ["678", "7507", "9606"])

    # Test taxid synonyms
    self.assertEqual(ncbi.get_topology(["42099"]).write(format_root_node=True), "1223560;")
    # The id 42099 is for https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=42099
    # which corresponds to "Phytopythium vexans DAOM BR484", which has id 1223560
    # https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=1223560

    for target in [9604, 9443, "9443"]:
      t1 = ncbi.get_descendant_taxa(target, return_tree=True)
      t2 = ncbi.get_topology([target])
      t3 = ncbi.get_topology(ncbi.get_descendant_taxa(target))
      t4 = ncbi.get_topology(list(map(str, ncbi.get_descendant_taxa(target))))

      self.assertEqual(set(t1.leaf_names()), set(t2.leaf_names()))
      self.assertEqual(set(t2.leaf_names()), set(t3.leaf_names()))
      self.assertEqual(set(t3.leaf_names()), set(t4.leaf_names()))
      diffs1 = t1.compare(t2, unrooted=True)
      diffs2 = t2.compare(t3, unrooted=True)
      diffs3 = t3.compare(t4, unrooted=True)
      self.assertEqual(diffs1["rf"], 0.0)
      self.assertEqual(diffs2["rf"], 0.0)
      self.assertEqual(diffs3["rf"], 0.0)

  def test_merged_id(self):
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)
    t1 = ncbi.get_lineage(649756)
    self.assertEqual(t1, [1, 131567, 2, 1783272, 1239, 186801, 3085636, 186803, 207244, 649756])
    t2 = ncbi.get_lineage("649756")
    self.assertEqual(t2, [1, 131567, 2, 1783272, 1239, 186801, 3085636, 186803, 207244, 649756])
  
  def test_ignore_unclassified(self):
    # normal case
    tree = PhyloTree('((9606, 9598), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=False)
    self.assertEqual(tree.common_ancestor(['9606', '9598']).props.get("sci_name"), 'Homininae')
    self.assertEqual(tree.common_ancestor(['9606', '10090']).props.get("sci_name"), 'Euarchontoglires')

    # empty case
    tree = PhyloTree('((9606, sample1), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=False)
    self.assertEqual(tree.common_ancestor(['9606', 'sample1']).props.get("sci_name"), '')
    self.assertEqual(tree.common_ancestor(['9606', 'sample1']).props.get("rank"), 'Unknown')
    self.assertEqual(tree.common_ancestor(['9606', '10090']).props.get("sci_name"), '')

    # ignore unclassified
    tree = PhyloTree('((9606, sample1), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=True)
    self.assertEqual(tree.common_ancestor(['9606', 'sample1']).props.get("sci_name"), 'Homo sapiens')
    self.assertEqual(tree.common_ancestor(['9606', 'sample1']).props.get("rank"), 'species')
    self.assertEqual(tree.common_ancestor(['9606', '10090']).props.get("sci_name"), 'Euarchontoglires')

if __name__ == '__main__':
  unittest.main()

