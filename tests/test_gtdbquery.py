import os
import unittest

from ete4 import PhyloTree, GTDBTaxa, ETE_DATA_HOME
from ete4.gtdb_taxonomy import gtdbquery
import requests

DATABASE_PATH = ETE_DATA_HOME + '/gtdbtaxa.sqlite'
DEFAULT_GTDBTAXADUMP = ETE_DATA_HOME + '/gtdbdump.tar.gz'


class Test_gtdbquery(unittest.TestCase):

    def test_00_update_database(self):
        gtdb = GTDBTaxa()

        url = ('https://github.com/etetoolkit/ete-data/raw/main'
                   '/gtdb_taxonomy/gtdb202/gtdb202dump.tar.gz')

        print(f'Downloading GTDB database release 202 to {DEFAULT_GTDBTAXADUMP} from {url}')

        with open(DEFAULT_GTDBTAXADUMP, 'wb') as f:
            f.write(requests.get(url).content)

        gtdb.update_taxonomy_database(DEFAULT_GTDBTAXADUMP)

        if not os.path.exists(DATABASE_PATH):
            gtdbquery.update_db(DATABASE_PATH)

    def test_01tree_annotation(self):
        tree = PhyloTree('((c__Alicyclobacillia, c__Bacilli), s__Caballeronia udeis);',
                         sp_naming_function=lambda name: name)
        tree.annotate_gtdb_taxa(dbfile=DATABASE_PATH, taxid_attr='name')

        self.assertEqual(tree.props.get('sci_name'), 'd__Bacteria')

        firmicutes = tree['c__Bacilli'].up
        self.assertEqual(firmicutes.props.get('taxid'), 'p__Firmicutes')
        self.assertEqual(firmicutes.props.get('sci_name'), 'p__Firmicutes')
        self.assertEqual(firmicutes.props.get('rank'), 'phylum')
        self.assertEqual(firmicutes.props.get('named_lineage'),
                         ['root', 'd__Bacteria', 'p__Firmicutes'])

        caballeronia = tree['s__Caballeronia udeis']
        self.assertEqual(caballeronia.props.get('taxid'), 's__Caballeronia udeis')
        self.assertEqual(caballeronia.props.get('sci_name'), 's__Caballeronia udeis')
        self.assertEqual(caballeronia.props.get('rank'), 'species')
        self.assertEqual(caballeronia.props.get('named_lineage'),
                         ['root', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria',
                          'o__Burkholderiales', 'f__Burkholderiaceae', 'g__Caballeronia', 's__Caballeronia udeis'])

    def test_02tree_annotation(self):
        # using name as species attribute
        tree = PhyloTree('((GB_GCA_011358815.1,RS_GCF_003948265.1),(GB_GCA_003344655.1),(GB_GCA_011056255.1));',
                         sp_naming_function=lambda name: name)
        tree.annotate_gtdb_taxa(dbfile=DATABASE_PATH, taxid_attr='species')

        self.assertEqual(tree.props.get('sci_name'), 'g__Korarchaeum')

        cryptofilum = tree['GB_GCA_011358815.1'].up
        self.assertEqual(cryptofilum.props.get('taxid'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('sci_name'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('rank'), 'species')
        self.assertEqual(cryptofilum.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum', 's__Korarchaeum cryptofilum'])

        sp003344655 = tree['GB_GCA_003344655.1']
        self.assertEqual(sp003344655.props.get('taxid'), 'GB_GCA_003344655.1')
        self.assertEqual(sp003344655.props.get('sci_name'), 's__Korarchaeum sp003344655')
        self.assertEqual(sp003344655.props.get('rank'), 'subspecies')
        self.assertEqual(sp003344655.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum',
                            's__Korarchaeum sp003344655', 'GB_GCA_003344655.1'])

    def test_03tree_annotation(self):
        # assign species attribute via sp_naming_function
        tree = PhyloTree('((GB_GCA_011358815.1|protA,RS_GCF_003948265.1|protB),(GB_GCA_003344655.1|protC),(GB_GCA_011056255.1|protD));',
                         sp_naming_function=lambda name: name.split('|')[0])
        tree.annotate_gtdb_taxa(taxid_attr='species')

        self.assertEqual(tree.props.get('sci_name'), 'g__Korarchaeum')

        cryptofilum = tree['GB_GCA_011358815.1|protA'].up
        self.assertEqual(cryptofilum.props.get('taxid'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('sci_name'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('rank'), 'species')
        self.assertEqual(cryptofilum.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum', 's__Korarchaeum cryptofilum'])

        sp003344655 = tree['GB_GCA_003344655.1|protC']
        self.assertEqual(sp003344655.props.get('taxid'), 'GB_GCA_003344655.1')
        self.assertEqual(sp003344655.props.get('sci_name'), 's__Korarchaeum sp003344655')
        self.assertEqual(sp003344655.props.get('rank'), 'subspecies')
        self.assertEqual(sp003344655.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum',
                            's__Korarchaeum sp003344655', 'GB_GCA_003344655.1'])

    def test_04tree_annotation(self):
        # Using custom property as taxonomic identifier
        tree = PhyloTree('((protA:1, protB:1):1,(protC:1),(protD:1):1):1;')
        annotate_dict = {
            'protA': 'GB_GCA_011358815.1',
            'protB': 'RS_GCF_003948265.1',
            'protC': 'GB_GCA_003344655.1',
            'protD': 'GB_GCA_011056255.1',
        }
        for key, value in annotate_dict.items():
            tree[key].add_prop('gtdb_spcode', value)

        tree.annotate_gtdb_taxa(taxid_attr="gtdb_spcode")

        self.assertEqual(tree.props.get('sci_name'), 'g__Korarchaeum')

        cryptofilum = tree['protA'].up
        self.assertEqual(cryptofilum.props.get('taxid'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('sci_name'), 's__Korarchaeum cryptofilum')
        self.assertEqual(cryptofilum.props.get('rank'), 'species')
        self.assertEqual(cryptofilum.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum', 's__Korarchaeum cryptofilum'])

        sp003344655 = tree['protC']
        self.assertEqual(sp003344655.props.get('taxid'), 'GB_GCA_003344655.1')
        self.assertEqual(sp003344655.props.get('sci_name'), 's__Korarchaeum sp003344655')
        self.assertEqual(sp003344655.props.get('rank'), 'subspecies')
        self.assertEqual(sp003344655.props.get('named_lineage'),
                            ['root', 'd__Archaea', 'p__Thermoproteota', 'c__Korarchaeia',
                            'o__Korarchaeales', 'f__Korarchaeaceae', 'g__Korarchaeum',
                            's__Korarchaeum sp003344655', 'GB_GCA_003344655.1'])

    def test_gtdbquery(self):
        gtdb = GTDBTaxa(dbfile=DATABASE_PATH)

        out = gtdb.get_descendant_taxa('c__Thorarchaeia', intermediate_nodes=True)

        self.assertEqual(set(out), set(['o__Thorarchaeales', 'f__Thorarchaeaceae', 'g__B65-G9', 's__B65-G9 sp003662765', 'GB_GCA_003662765.1', 'GB_GCA_003662805.1', 'g__OWC5', 's__OWC5 sp003345555', 'GB_GCA_003345555.1', 's__OWC5 sp003345595', 'GB_GCA_003345595.1', 'g__SMTZ1-45', 's__SMTZ1-45 sp001940705', 'GB_GCA_001940705.1', 's__SMTZ1-45 sp001563335', 'GB_GCA_001563335.1', 's__SMTZ1-45 sp011364905', 'GB_GCA_011364905.1', 's__SMTZ1-45 sp004376265', 'GB_GCA_004376265.1', 's__SMTZ1-45 sp002825515', 'GB_GCA_002825515.1', 'g__SMTZ1-83', 's__SMTZ1-83 sp001563325', 'GB_GCA_001563325.1', 's__SMTZ1-83 sp011364985', 'GB_GCA_011364985.1', 's__SMTZ1-83 sp011365025', 'GB_GCA_011365025.1', 'g__MP8T-1', 's__MP8T-1 sp004524565', 'GB_GCA_004524565.1', 's__MP8T-1 sp004524595', 'GB_GCA_004524595.1', 's__MP8T-1 sp002825465', 'GB_GCA_002825465.1', 's__MP8T-1 sp002825535', 'GB_GCA_002825535.1', 's__MP8T-1 sp003345545', 'GB_GCA_003345545.1', 'g__TEKIR-14', 's__TEKIR-14 sp004524445', 'GB_GCA_004524445.1', 'g__JACAEL01', 's__JACAEL01 sp013388835', 'GB_GCA_013388835.1', 'g__SHMX01', 's__SHMX01 sp008080745', 'GB_GCA_008080745.1', 'g__TEKIR-12S', 's__TEKIR-12S sp004524435', 'GB_GCA_004524435.1', 'g__WTCK01', 's__WTCK01 sp013138615', 'GB_GCA_013138615.1']))

        out = gtdb.get_descendant_taxa('c__Thorarchaeia', intermediate_nodes=False)

        self.assertEqual(set(out), set(['GB_GCA_003662765.1', 'GB_GCA_003662805.1', 'GB_GCA_003345555.1', 'GB_GCA_003345595.1', 'GB_GCA_001940705.1', 'GB_GCA_001563335.1', 'GB_GCA_011364905.1', 'GB_GCA_004376265.1', 'GB_GCA_002825515.1', 'GB_GCA_001563325.1', 'GB_GCA_011364985.1', 'GB_GCA_011365025.1', 'GB_GCA_004524565.1', 'GB_GCA_004524595.1', 'GB_GCA_002825465.1', 'GB_GCA_002825535.1', 'GB_GCA_003345545.1', 'GB_GCA_004524445.1', 'GB_GCA_013388835.1', 'GB_GCA_008080745.1', 'GB_GCA_004524435.1', 'GB_GCA_013138615.1']))

        out = gtdb.get_descendant_taxa('c__Thorarchaeia', intermediate_nodes=False, rank_limit='species')

        self.assertEqual(set(out), set(['s__MP8T-1 sp002825535', 's__MP8T-1 sp003345545', 's__MP8T-1 sp002825465', 's__MP8T-1 sp004524565', 's__MP8T-1 sp004524595', 's__SMTZ1-83 sp011364985', 's__SMTZ1-83 sp011365025', 's__SMTZ1-83 sp001563325', 's__TEKIR-14 sp004524445', 's__SHMX01 sp008080745', 's__OWC5 sp003345595', 's__OWC5 sp003345555', 's__JACAEL01 sp013388835', 's__B65-G9 sp003662765', 's__SMTZ1-45 sp001563335', 's__SMTZ1-45 sp011364905', 's__SMTZ1-45 sp001940705', 's__SMTZ1-45 sp004376265', 's__SMTZ1-45 sp002825515', 's__WTCK01 sp013138615', 's__TEKIR-12S sp004524435']))

    def test_get_topology(self):
        gtdb = GTDBTaxa(dbfile=DATABASE_PATH)
        tree = gtdb.get_topology(['p__Huberarchaeota', 'o__Peptococcales', 'f__Korarchaeaceae', 's__Korarchaeum'],
                                 intermediate_nodes=True, collapse_subspecies=True, annotate=True)
        self.assertEqual(sorted(tree.leaf_names()),
                         ['f__Korarchaeaceae', 'o__Peptococcales', 'p__Huberarchaeota'])

        tree = gtdb.get_topology(['p__Huberarchaeota', 'o__Peptococcales', 'f__Korarchaeaceae', 's__Korarchaeum','RS_GCF_006228565.1', 'GB_GCA_001515945.1'],
                                  intermediate_nodes=True, collapse_subspecies=False, annotate=True)

        # normal case with collapse_subspecies
        tree = gtdb.get_topology(['p__Huberarchaeota', 'o__Peptococcales', 'f__Korarchaeaceae', 's__Korarchaeum','RS_GCF_006228565.1', 'GB_GCA_001515945.1'],
                                  intermediate_nodes=True, collapse_subspecies=True, annotate=True)

    def test_name_lineages(self):
        gtdb = GTDBTaxa(dbfile=DATABASE_PATH)

        out = gtdb.get_name_lineage(['RS_GCF_006228565.1'])

        self.assertEqual(out[0]['RS_GCF_006228565.1'],
                         ['root', 'd__Bacteria', 'p__Firmicutes_B', 'c__Moorellia',
                          'o__Moorellales', 'f__Moorellaceae', 'g__Moorella',
                          's__Moorella thermoacetica', 'RS_GCF_006228565.1'])

        out = gtdb.get_name_lineage(['o__Peptococcales'])

        self.assertEqual(out[0]['o__Peptococcales'],
                         ['root', 'd__Bacteria', 'p__Firmicutes_B', 'c__Peptococcia', 'o__Peptococcales'])

    def test_get_rank(self):
        gtdb = GTDBTaxa(dbfile=DATABASE_PATH)
        ranks = gtdb.get_rank(['c__Thorarchaeia', 'RS_GCF_001477695.1'])
        #{'c__Thorarchaeia': 'class', 'RS_GCF_001477695.1': 'subspecies'}
        self.assertEqual(ranks, {'c__Thorarchaeia': 'class', 'RS_GCF_001477695.1': 'subspecies'})

    def test_ignore_unclassified(self):
        # normal case
        gtdb = GTDBTaxa(dbfile=DATABASE_PATH)
        c__Thorarchaeia = "(((((((GB_GCA_002825535.1),(GB_GCA_003345545.1),(GB_GCA_002825465.1),(GB_GCA_004524565.1),(GB_GCA_004524595.1)),((GB_GCA_011364985.1),(GB_GCA_011365025.1),(GB_GCA_001563325.1)),((GB_GCA_004524445.1)),((GB_GCA_008080745.1)),((GB_GCA_003345595.1),(GB_GCA_003345555.1)),((GB_GCA_013388835.1)),((GB_GCA_003662765.1,GB_GCA_003662805.1)),((GB_GCA_011364905.1),(GB_GCA_001563335.1),(GB_GCA_001940705.1),(GB_GCA_004376265.1),(GB_GCA_002825515.1)),((GB_GCA_013138615.1)),((GB_GCA_004524435.1)))))));"
        t = PhyloTree(c__Thorarchaeia)
        _, _, _= t.annotate_gtdb_taxa(taxid_attr='name', ignore_unclassified=False)

        # case0
        t0 = t['GB_GCA_011364985.1']
        self.assertEqual(t0.props.get("taxid"), 'GB_GCA_011364985.1')
        self.assertEqual(t0.props.get("sci_name"), 's__SMTZ1-83 sp011364985')
        self.assertEqual(t0.props.get("rank"), 'subspecies')

        t0 = t0.up
        self.assertEqual(t0.props.get("taxid"), 's__SMTZ1-83 sp011364985')
        self.assertEqual(t0.props.get("sci_name"), 's__SMTZ1-83 sp011364985')
        self.assertEqual(t0.props.get("rank"), 'species')

        # case1
        ids = ['GB_GCA_001563325.1', 'GB_GCA_011364985.1'] # soley species
        t1 = t.common_ancestor(ids)
        self.assertEqual(t1.props.get("taxid"), 'g__SMTZ1-83')
        self.assertEqual(t1.props.get("sci_name"), 'g__SMTZ1-83')
        self.assertEqual(t1.props.get("rank"), 'genus')
        self.assertEqual(t1.props.get("named_lineage"), ['root', 'd__Archaea', 'p__Asgardarchaeota', 'c__Thorarchaeia', 'o__Thorarchaeales', 'f__Thorarchaeaceae', 'g__SMTZ1-83'])

        # case2
        ids = ['GB_GCA_003662765.1', 'GB_GCA_003662805.1'] # normal hierarchy
        t2 = t.common_ancestor(ids)
        self.assertEqual(t2.props.get("taxid"), 's__B65-G9 sp003662765')
        self.assertEqual(t2.props.get("sci_name"), 's__B65-G9 sp003662765')
        self.assertEqual(t2.props.get("rank"), 'species')
        self.assertEqual(t2.props.get("named_lineage"), ['root', 'd__Archaea', 'p__Asgardarchaeota', 'c__Thorarchaeia', 'o__Thorarchaeales', 'f__Thorarchaeaceae', 'g__B65-G9', 's__B65-G9 sp003662765'])

        # case3
        ids = ['GB_GCA_002825535.1', 'GB_GCA_004524435.1']
        t3 = t.common_ancestor(ids)
        self.assertEqual(t3.props.get("taxid"), 'f__Thorarchaeaceae')
        self.assertEqual(t3.props.get("sci_name"), 'f__Thorarchaeaceae')
        self.assertEqual(t3.props.get("rank"), 'family')

        # ignore unclassified is False
        c__Thorarchaeia = '(((((((GB_GCA_002825535.1),(GB_GCA_003345545.1),(GB_GCA_002825465.1),(GB_GCA_004524565.1),(GB_GCA_004524595.1)),((GB_GCA_011364985.1),(GB_GCA_011365025.1),(GB_GCA_001563325.1)),((GB_GCA_004524445.1)),((GB_GCA_008080745.1)),((GB_GCA_003345595.1),(GB_GCA_003345555.1)),((GB_GCA_013388835.1)),((GB_GCA_003662765.1,GB_GCA_003662805.1)),((GB_GCA_011364905.1),(GB_GCA_001563335.1),(GB_GCA_001940705.1),(GB_GCA_004376265.1),(GB_GCA_002825515.1)),((GB_GCA_013138615.1)),((GB_GCA_004524435.1)))))));'
        t = PhyloTree(c__Thorarchaeia)
        t['GB_GCA_001563325.1'].name = 'sample1'
        _, _, _= t.annotate_gtdb_taxa(taxid_attr='name', ignore_unclassified=False)

        # check nomarl leaf
        self.assertEqual(t['GB_GCA_011364985.1'].props.get("taxid"), 'GB_GCA_011364985.1')
        self.assertEqual(t['GB_GCA_011364985.1'].props.get("sci_name"), 's__SMTZ1-83 sp011364985')

        # check unclassified leaf
        self.assertEqual(t['sample1'].props.get("taxid"), 'sample1')
        self.assertEqual(t['sample1'].props.get("sci_name"), '')
        self.assertEqual(t['sample1'].props.get("rank"), 'Unknown')
        self.assertEqual(t['sample1'].props.get("named_lineage"), [])

        # check ancestor (should be empty)
        ids = ['sample1', 'GB_GCA_011364985.1']
        t1 = t.common_ancestor(ids)
        self.assertEqual(t1.props.get("taxid"), None)
        self.assertEqual(t1.props.get("sci_name"), 'None')
        self.assertEqual(t1.props.get("rank"), 'Unknown')
        self.assertEqual(t1.props.get("named_lineage"), [''])

        self.assertEqual(t.props.get("taxid"), None)
        self.assertEqual(t.props.get("sci_name"), 'None')
        self.assertEqual(t.props.get("rank"), 'Unknown')
        self.assertEqual(t.props.get("named_lineage"), [''])

        # ignore unclassified is True
        c__Thorarchaeia = '(((((((GB_GCA_002825535.1),(GB_GCA_003345545.1),(GB_GCA_002825465.1),(GB_GCA_004524565.1),(GB_GCA_004524595.1)),((GB_GCA_011364985.1),(GB_GCA_011365025.1),(GB_GCA_001563325.1)),((GB_GCA_004524445.1)),((GB_GCA_008080745.1)),((GB_GCA_003345595.1),(GB_GCA_003345555.1)),((GB_GCA_013388835.1)),((GB_GCA_003662765.1,GB_GCA_003662805.1)),((GB_GCA_011364905.1),(GB_GCA_001563335.1),(GB_GCA_001940705.1),(GB_GCA_004376265.1),(GB_GCA_002825515.1)),((GB_GCA_013138615.1)),((GB_GCA_004524435.1)))))));'
        t = PhyloTree(c__Thorarchaeia)
        t['GB_GCA_001563325.1'].name = 'sample1'
        _, _, _= t.annotate_gtdb_taxa(taxid_attr='name', ignore_unclassified=True)

        # check nomarl leaf
        self.assertEqual(t['GB_GCA_011364985.1'].props.get("taxid"), 'GB_GCA_011364985.1')
        self.assertEqual(t['GB_GCA_011364985.1'].props.get("sci_name"), 's__SMTZ1-83 sp011364985')

        # check unclassified leaf
        self.assertEqual(t['sample1'].props.get("taxid"), 'sample1')
        self.assertEqual(t['sample1'].props.get("sci_name"), '')
        self.assertEqual(t['sample1'].props.get("rank"), 'Unknown')
        self.assertEqual(t['sample1'].props.get("named_lineage"), [])

        # check ancestor (should be annotated)
        ids = ['sample1', 'GB_GCA_011364985.1']
        t1 = t.common_ancestor(ids)
        self.assertEqual(t1.props.get("taxid"), 'g__SMTZ1-83')
        self.assertEqual(t1.props.get("sci_name"), 'g__SMTZ1-83')
        self.assertEqual(t1.props.get("rank"), 'genus')
        self.assertEqual(t1.props.get("named_lineage"), ['root', 'd__Archaea', 'p__Asgardarchaeota', 'c__Thorarchaeia', 'o__Thorarchaeales', 'f__Thorarchaeaceae', 'g__SMTZ1-83'])

        self.assertEqual(t.props.get("taxid"), 'f__Thorarchaeaceae')
        self.assertEqual(t.props.get("sci_name"), 'f__Thorarchaeaceae')
        self.assertEqual(t.props.get("rank"), 'family')


if __name__ == '__main__':
    unittest.main()
