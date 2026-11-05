import os
import tempfile
import unittest

from ete4 import EvolTree


class TestEvolTreeNewick(unittest.TestCase):
    """EvolTree has to accept the newick text and files that PhyloTree accepts."""

    def test_newick_string_keeps_topology_species_and_paml_ids(self):
        """A quartet keeps its joins, the species function, and leaf ids."""
        def species(name):
            return name[3:]

        tree = EvolTree("((seq1,seq2),seq3);", sp_naming_function=species)
        leaves = {leaf.name: leaf for leaf in tree.leaves()}
        self.assertEqual(sorted(leaves), ["seq1", "seq2", "seq3"])
        self.assertIs(leaves["seq1"].up, leaves["seq2"].up)
        self.assertIs(leaves["seq1"].up.up, tree)
        self.assertIsNot(leaves["seq3"].up, leaves["seq1"].up)
        self.assertEqual(leaves["seq1"].species, "1")
        self.assertEqual(leaves["seq3"].species, "3")
        self.assertTrue(all(leaf.props.get("node_id") for leaf in leaves.values()))

    def test_newick_path_and_open_file(self):
        """A path and an open file both build the same three leaves."""
        handle = tempfile.NamedTemporaryFile("w", suffix=".nw", delete=False)
        try:
            handle.write("((A,B),C);\n")
            handle.close()
            from_path = EvolTree(handle.name)
            self.assertEqual(sorted(from_path.leaf_names()), ["A", "B", "C"])
            with open(handle.name) as stream:
                from_file = EvolTree(stream)
            self.assertEqual(sorted(from_file.leaf_names()), ["A", "B", "C"])
        finally:
            os.remove(handle.name)
