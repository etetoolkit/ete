"""
Test to see if the ETE functions that Ana uses work correctly.

To run with pytest.
"""

import os

from ete4 import PhyloTree, NCBITaxa, ETE_DATA_HOME, update_ete_data
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH  = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'
P53_RAW_PATH   = ETE_DATA_HOME + '/tests/P53.faa.nw'
P53_ANNOT_PATH = ETE_DATA_HOME + '/tests/annot_tree.nw'


# Helper functions.

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def make_name(i):
    """Return a short name corresponding to the index i."""
    # 0 -> 'A', 1 -> 'B', ..., 51 -> 'z', 52 -> 'AA', 53 -> 'AB', ...
    name = ''
    while i >= 0:
        name = chars[i % len(chars)] + name
        i = i // len(chars) - 1
    return name



def get_depth(node):
    """Return the depth of the given node."""
    depth = 0
    while node is not None:
        depth += 1
        node = node.up
    return depth



def run_preanalysis(tree, tax_db):
    """Manipulate and annotate the tree, and return all node properties."""
    tree.resolve_polytomy()

    root_mid = tree.get_midpoint_outgroup()
    tree.set_outgroup(root_mid)

    tree.dist = 0.01

    # Parsing function used to extract species name from a node’s name.
    tree.set_species_naming_function(lambda x: x.split('.')[0])

    # Add additional information to any internal leaf node (sci_name,
    # taxid, named_lineage, lineage, rank).
    tax_db.annotate_tree(tree, taxid_attr='species')

    annot_props = set()
    for i, node in enumerate(tree.traverse()):
        if not node.is_leaf:
            node.name = '%s-%d' % (make_name(i), get_depth(node))

        annot_props |= set(node.props)

    return sorted(annot_props - {'_speciesFunction'})


def test_orthologs_group_delineation():
    # Make sure we have the original raw tree.
    update_ete_data(P53_RAW_PATH, url='tests/P53.faa.nw')

    # Make sure we have the annotated result to compare with.
    update_ete_data(P53_ANNOT_PATH, url='tests/annot_tree.nw')

    # Make sure we have the database file.
    if not os.path.exists(DATABASE_PATH):
        taxdump = ETE_DATA_HOME + '/tests/taxdump_tests.tar.gz'
        update_ete_data(taxdump, url='tests/ncbiquery/taxdump_tests.tar.gz')
        print(f'Generating NCBI database {DATABASE_PATH} ...')
        ncbiquery.update_db(DATABASE_PATH, taxdump)  # sqlite from taxdump

    # Get eggnog database and newick to annotate.
    tax_db = NCBITaxa(DATABASE_PATH)
    tree = PhyloTree(open(P53_RAW_PATH), parser=1)

    annot_props = run_preanalysis(tree, tax_db)  # the preanalysis that Ana does

    for p in ['name', 'dist', 'support']:
        annot_props.remove(p)

    annot_tree_nw = tree.write(props=annot_props, parser=5,
                               format_root_node=True)

    with open(P53_ANNOT_PATH) as f:
        assert len(annot_tree_nw) == len(f.read())
