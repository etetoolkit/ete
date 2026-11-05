import os
import sqlite3
from pathlib import Path

import pytest

from ete4.gtdb_taxonomy.gtdbquery import DB_VERSION as GTDB_DB_VERSION
from ete4.gtdb_taxonomy.gtdbquery import GTDBTaxa
from ete4.ncbi_taxonomy.ncbiquery import DB_VERSION as NCBI_DB_VERSION
from ete4.ncbi_taxonomy.ncbiquery import NCBITaxa


def _versioned_db(path, version):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE stats (version INT PRIMARY KEY)")
    db.execute("INSERT INTO stats (version) VALUES (?)", (version,))
    db.execute("CREATE TABLE merged (taxid_old INT, taxid_new INT)")
    db.commit()
    db.close()


def test_ncbi_dbfile_path_is_joined_as_a_string(tmp_path):
    # A Path used to be stored as-is, so opening the traverse cache did
    # dbfile + ".traverse.pkl" and raised TypeError.
    db = tmp_path / "taxa.sqlite"
    _versioned_db(db, NCBI_DB_VERSION)
    taxa = NCBITaxa(dbfile=Path(db), update=False)
    assert taxa.dbfile == os.fspath(db)
    with pytest.raises(FileNotFoundError):
        taxa.get_descendant_taxa(1)


def test_gtdb_dbfile_path_is_stored_as_a_string(tmp_path):
    db = tmp_path / "gtdb.sqlite"
    _versioned_db(db, GTDB_DB_VERSION)
    taxa = GTDBTaxa(dbfile=Path(db))
    assert taxa.dbfile == os.fspath(db)
    assert isinstance(taxa.dbfile, str)
