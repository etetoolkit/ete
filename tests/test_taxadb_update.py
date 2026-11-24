"""Updating a taxonomy database replaces the file, and open objects see the new one."""

import os
import shutil

from ete4 import NCBITaxa, ETE_DATA_HOME, update_ete_data
from ete4.ncbi_taxonomy import ncbiquery


def test_update_replaces_db(tmp_path):
    taxdump = ETE_DATA_HOME + '/tests/taxdump_tests.tar.gz'
    update_ete_data(taxdump, url='tests/ncbiquery/taxdump_tests.tar.gz')

    dbfile = str(tmp_path / 'taxa.sqlite')
    cwd = os.getcwd()
    os.chdir(tmp_path)  # update_db writes its .tab files in the current dir
    try:
        ncbiquery.update_db(dbfile, taxdump)
        ncbi = NCBITaxa(dbfile=dbfile)
        assert ncbi.get_taxid_translator([9606]) == {9606: 'Homo sapiens'}

        inode = os.stat(dbfile).st_ino
        ncbi.update_taxonomy_database(taxdump)  # rebuild over the existing file
        assert os.stat(dbfile).st_ino != inode  # replaced, not modified in place
        assert not os.path.exists(dbfile + '.tmp')
        assert ncbi.get_taxid_translator([9606]) == {9606: 'Homo sapiens'}  # reconnected
        assert ncbi.db.execute('PRAGMA integrity_check').fetchone() == ('ok',)
    finally:
        os.chdir(cwd)
