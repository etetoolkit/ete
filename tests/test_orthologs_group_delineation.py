"""
Test to see if the ETE functions that Ana uses work correctly.
"""

import os
import unittest

from ete4 import PhyloTree, NCBITaxa, ETE_DATA_HOME, update_ete_data


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



def run_preanalysis(tree, taxonomy_db):
    """Manipulate and annotate the tree, and return all node properties."""
    tree.resolve_polytomy()

    root_mid = tree.get_midpoint_outgroup()
    tree.set_outgroup(root_mid)

    tree.dist = 0.01

    # Parsing function used to extract species name from a node’s name.
    tree.set_species_naming_function(lambda x: x.split('.')[0])

    # Add additional information to any internal leaf node (sci_name,
    # taxid, named_lineage, lineage, rank).
    taxonomy_db.annotate_tree(tree, taxid_attr='species')

    annot_props = set()
    for i, node in enumerate(tree.traverse()):
        if not node.is_leaf:
            node.name = '%s-%d' % (make_name(i), get_depth(node))

        annot_props |= set(node.props)

    return sorted(annot_props - {'_speciesFunction'})


class Test_OGD(unittest.TestCase):

    def test_orthologs_group_delineation(self):
        # Get eggnog database and newick to annotate.
        url_base = 'https://github.com/etetoolkit/ete-data/releases/download/v1.0/'
        for fname in ['e6.taxa.sqlite', 'P53.faa.nw']:
            if not os.path.exists(ETE_DATA_HOME + f'/tests/{fname}'):
                update_ete_data(f'./tests/{fname}', url_base + fname)

        tax_db = NCBITaxa(ETE_DATA_HOME + '/tests/e6.taxa.sqlite')
        tree = PhyloTree(open(ETE_DATA_HOME + '/tests/P53.faa.nw'), parser=1)

        annot_props = run_preanalysis(tree, tax_db)  # the preanalysis that Ana does

        for p in ['name', 'dist', 'support']:
            annot_props.remove(p)

        annot_tree_nw = tree.write(props=annot_props, parser=5,
                                   format_root_node=True)

        # Get reference result to compare with.
        if not os.path.exists(ETE_DATA_HOME + f'/tests/annot_tree.nw'):
            update_ete_data(f'./tests/annot_tree.nw',
                            'https://github.com/etetoolkit/ete-data/raw/main/tests/annot_tree.nw')

        with open(ETE_DATA_HOME + f'/tests/annot_tree.nw') as pf:
            self.assertEqual(annot_tree_nw, pf.read())
