"""
Test the functionality of ncbiquery.py. To run with pytest.
"""

import os
import pytest

from ete4 import PhyloTree, NCBITaxa, ETE_DATA_HOME, update_ete_data
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'

@pytest.fixture(scope='session', autouse=True)
def execute_before_any_test():
    # Make sure we have the database file.
    if not os.path.exists(DATABASE_PATH):
        taxdump = ETE_DATA_HOME + '/tests/taxdump_tests.tar.gz'
        update_ete_data(taxdump, url='tests/ncbiquery/taxdump_tests.tar.gz')
        print(f'Generating NCBI database {DATABASE_PATH} ...')
        ncbiquery.update_db(DATABASE_PATH, taxdump)  # sqlite from taxdump


# Helper functions and data.

HUMAN_NAMED_LINEAGE = [
    'root', 'cellular organisms', 'Eukaryota', 'Opisthokonta', 'Metazoa',
    'Eumetazoa', 'Bilateria', 'Deuterostomia', 'Chordata', 'Craniata',
    'Vertebrata', 'Gnathostomata', 'Teleostomi', 'Euteleostomi',
    'Sarcopterygii', 'Dipnotetrapodomorpha', 'Tetrapoda', 'Amniota',
    'Mammalia', 'Theria', 'Eutheria', 'Boreoeutheria', 'Euarchontoglires',
    'Primates', 'Haplorrhini', 'Simiiformes', 'Catarrhini', 'Hominoidea',
    'Hominidae', 'Homininae', 'Homo', 'Homo sapiens']

HUMAN_LINEAGE = [
    1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 89593, 7742, 7776,
    117570, 117571, 8287, 1338369, 32523, 32524, 40674, 32525, 9347, 1437010,
    314146, 9443, 376913, 314293, 9526, 314295, 9604, 207598, 9605, 9606]

def assert_homi_props(node):
    """Assert that node has the properties of Homininae."""
    expected = [('sci_name',      'Homininae'),
                ('taxid',         207598),
                ('rank',          'subfamily'),
                ('named_lineage', HUMAN_NAMED_LINEAGE[:-2]),
                ('lineage',       HUMAN_LINEAGE[:-2])]
    for prop, value in expected:
        assert node.props[prop] == value

def assert_human_props(node):
    """Assert that node has the properties of Homo sapiens."""
    expected = [('sci_name',      'Homo sapiens'),
                ('taxid',         9606),
                ('rank',          'species'),
                ('named_lineage', HUMAN_NAMED_LINEAGE),
                ('lineage',       HUMAN_LINEAGE)]
    for prop, value in expected:
        assert node.props[prop] == value


# The actual tests.

def test_01tree_annotation():
    # Using name as species name too.
    t = PhyloTree('((9598, 9606), 10090);',
                  sp_naming_function=lambda name: name)

    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH)

    assert t.props['sci_name'] == 'Euarchontoglires'

    assert_homi_props(t['9606'].up)  # does it have the properties of Homininae?

    assert_human_props(t['9606'])  # does it have the properties of Homo sapiens?


def test_02tree_annotation():
    # Using the first part of name as species name.
    t = PhyloTree('((9598|protA, 9606|protB), 10090|propC);',
                  sp_naming_function=lambda name: name.split('|')[0])

    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH, taxid_attr='species')

    assert_homi_props(t['9606|protB'].up)

    assert_human_props(t['9606|protB'])


def test_03tree_annotation():
    # Using a custom property as taxonomic identifier.
    t = PhyloTree('((protA, protB), propC);')

    # Add property called "spcode".
    t['protA'].add_prop('spcode', 9598)
    t['protB'].add_prop('spcode', 9606)
    t['propC'].add_prop('spcode', 10090)

    t.annotate_ncbi_taxa(dbfile=DATABASE_PATH, taxid_attr='spcode')

    assert_homi_props(t['protB'].up)

    assert_human_props(t['protB'])


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
    assert t1 == [1, 131567, 2, 1783272, 1239, 186801, 3085636, 186803, 207244, 649756]

    t2 = ncbi.get_lineage("649756")
    assert t2 == [1, 131567, 2, 1783272, 1239, 186801, 3085636, 186803, 207244, 649756]


def test_ignore_unclassified():
    # normal case
    tree = PhyloTree('((9606, 9598), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=False)

    assert tree.common_ancestor(['9606', '9598']).props['sci_name'] == 'Homininae'
    assert tree.common_ancestor(['9606', '10090']).props['sci_name'] == 'Euarchontoglires'

    # empty case
    tree = PhyloTree('((9606, sample1), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=False)

    assert tree.common_ancestor(['9606', 'sample1']).props['sci_name'] == ''
    assert tree.common_ancestor(['9606', 'sample1']).props['rank'] == 'Unknown'
    assert tree.common_ancestor(['9606', '10090']).props['sci_name'] == ''

    # ignore unclassified
    tree = PhyloTree('((9606, sample1), 10090);')
    tree.annotate_ncbi_taxa(taxid_attr='name', ignore_unclassified=True)

    assert tree.common_ancestor(['9606', 'sample1']).props['sci_name'] == 'Homo sapiens'
    assert tree.common_ancestor(['9606', 'sample1']).props['rank'] == 'species'
    assert tree.common_ancestor(['9606', '10090']).props['sci_name'] == 'Euarchontoglires'
