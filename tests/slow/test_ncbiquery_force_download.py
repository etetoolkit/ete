"""
Test the functionality of ncbiquery.py. To run with pytest.
"""

import os

from ete4 import PhyloTree, NCBITaxa, ETE_DATA_HOME
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'


def test_update_database():
    ncbiquery.update_db(DATABASE_PATH)
    # It will download the full NCBI taxa database and process it. Slow!
    # Should raise an error if things go wrong.


def test_tree_annotation():
    t = PhyloTree('((9598,9606),10090);',
                  sp_naming_function=lambda name: name)

    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH)

    assert t.props['sci_name'] == 'Euarchontoglires'

    homi = t['9606'].up
    assert homi.props['sci_name'] == 'Homininae'
    assert homi.props['taxid'] == 207598
    assert homi.props['rank'] == 'subfamily'
    assert homi.props['named_lineage'] == [
        'root', 'cellular organisms', 'Eukaryota', 'Opisthokonta', 'Metazoa',
        'Eumetazoa', 'Bilateria', 'Deuterostomia', 'Chordata', 'Craniata',
        'Vertebrata', 'Gnathostomata', 'Teleostomi', 'Euteleostomi',
        'Sarcopterygii', 'Dipnotetrapodomorpha', 'Tetrapoda', 'Amniota',
        'Mammalia', 'Theria', 'Eutheria', 'Boreoeutheria', 'Euarchontoglires',
        'Primates', 'Haplorrhini', 'Simiiformes', 'Catarrhini', 'Hominoidea',
        'Hominidae', 'Homininae']
    assert homi.props['lineage'] == [
        1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742,
        7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347,
        1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598]

    human = t['9606']
    assert human.props['sci_name'] == 'Homo sapiens'
    assert human.props['taxid'] == 9606
    assert human.props['rank'] == 'species'
    assert human.props['named_lineage'] == [
        'root', 'cellular organisms', 'Eukaryota', 'Opisthokonta', 'Metazoa',
        'Eumetazoa', 'Bilateria', 'Deuterostomia', 'Chordata', 'Craniata',
        'Vertebrata', 'Gnathostomata', 'Teleostomi', 'Euteleostomi',
        'Sarcopterygii', 'Dipnotetrapodomorpha', 'Tetrapoda', 'Amniota',
        'Mammalia', 'Theria', 'Eutheria', 'Boreoeutheria', 'Euarchontoglires',
        'Primates', 'Haplorrhini', 'Simiiformes', 'Catarrhini', 'Hominoidea',
        'Hominidae', 'Homininae', 'Homo', 'Homo sapiens']
    assert human.props['lineage'] == [
        1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742,
        7776, 117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347,
        1437010, 314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598,
        9605, 9606]


def test_ncbiquery():
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)

    id2name = ncbi.get_taxid_translator(['9606', '7507'])
    assert id2name[7507] == 'Mantis religiosa'
    assert id2name[9606] == 'Homo sapiens'

    name2id = ncbi.get_name_translator(['Mantis religiosa', 'homo sapiens'])
    assert name2id['Mantis religiosa'] == [7507]
    assert name2id['homo sapiens'] == [9606]

    name2id = ncbi.get_name_translator(['Bacteria'])
    assert set(name2id['Bacteria']) == {2}

    out = ncbi.get_descendant_taxa('9605', intermediate_nodes=True)
    assert set(out) == {9606, 63221, 741158, 1425170, 2665952, 2665953, 2813598, 2813599}

    out = ncbi.get_descendant_taxa('9605', intermediate_nodes=False)
    assert set(out) == {63221, 741158, 2665953, 1425170, 2813599}

    out = ncbi.get_descendant_taxa('9596', intermediate_nodes=False, rank_limit='species')
    assert set(out) == {9597, 9598}


def test_get_topology():
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)

    t1 = ncbi.get_topology([9606, 7507, 9604])
    t2 = ncbi.get_topology([9606, 7507, 678])

    assert sorted(t1.leaf_names()) == ['7507', '9606']
    assert sorted(t2.leaf_names()) == ['678', '7507', '9606']

    # Test taxid synonyms
    assert ncbi.get_topology(['42099']).write(format_root_node=True) == '1223560;'
    # The id 42099 is for https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=42099
    # which corresponds to 'Phytopythium vexans DAOM BR484', which has id 1223560
    # https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=1223560

    for target in [9604, 9443, '9443']:
        t1 = ncbi.get_descendant_taxa(target, return_tree=True)
        t2 = ncbi.get_topology([target])
        t3 = ncbi.get_topology(ncbi.get_descendant_taxa(target))
        t4 = ncbi.get_topology(list(map(str, ncbi.get_descendant_taxa(target))))

        assert (set(t1.leaf_names()) == set(t2.leaf_names()) ==
                set(t3.leaf_names()) == set(t4.leaf_names()))

        diffs1 = t1.compare(t2, unrooted=True)
        diffs2 = t2.compare(t3, unrooted=True)
        diffs3 = t3.compare(t4, unrooted=True)

        assert diffs1['rf'] == diffs2['rf'] == diffs3['rf'] == 0.0


def test_merged_id():
    ncbi = NCBITaxa(dbfile=DATABASE_PATH)

    t1 = ncbi.get_lineage(649756)
    assert t1 == [1, 131567, 2, 1783272, 1239, 186801, 186802, 186803, 207244, 649756]

    t2 = ncbi.get_lineage('649756')
    assert t2 == [1, 131567, 2, 1783272, 1239, 186801, 186802, 186803, 207244, 649756]
