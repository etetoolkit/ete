import os
import sqlite3
import tempfile
import unittest

from ete4 import NCBITaxa


def _write_db(path):
    db = sqlite3.connect(path)
    db.executescript(
        """
        CREATE TABLE stats (version INT PRIMARY KEY);
        INSERT INTO stats (version) VALUES (2);
        CREATE TABLE species (
            taxid INT PRIMARY KEY,
            parent INT,
            spname VARCHAR(50),
            common VARCHAR(50),
            rank VARCHAR(50),
            track TEXT
        );
        CREATE TABLE merged (taxid_old INT, taxid_new INT);
        INSERT INTO species (taxid, parent, spname, common, rank, track) VALUES
            (1, 1, 'root', '', 'no rank', '1'),
            (2, 1, 'Bacteria', '', 'domain', '1,2'),
            (2074836, 1, 'Arxotrichum gangligerum', '', 'species', '1,2074836');
        INSERT INTO merged (taxid_old, taxid_new) VALUES (2588313, 2074836);
        """
    )
    db.commit()
    db.close()


class TestNCBIGetRank(unittest.TestCase):
    """get_rank must treat one string as one taxid and follow merged ids."""

    def setUp(self):
        handle = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        handle.close()
        self.path = handle.name
        _write_db(self.path)
        self.ncbi = NCBITaxa(dbfile=self.path, update=False)

    def tearDown(self):
        self.ncbi.db.close()
        os.remove(self.path)

    def test_string_is_one_merged_taxid(self):
        """A numeric string is not split into the taxids of its digits."""
        self.assertEqual(self.ncbi.get_rank("2588313"), {2588313: "species"})

    def test_merged_list_keeps_the_requested_id(self):
        """An obsolete id returns the current rank under the id that was asked for."""
        self.assertEqual(
            self.ncbi.get_rank(["2588313", 1]),
            {2588313: "species", 1: "no rank"},
        )

    def test_current_ids_and_unknown_id(self):
        """Current ids keep their own ranks, and an unknown id stays absent."""
        self.assertEqual(self.ncbi.get_rank([1, "2", 999]), {1: "no rank", 2: "domain"})
