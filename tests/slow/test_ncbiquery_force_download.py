"""
Test the functionality of ncbiquery.py. To run with pytest.
"""

import os

import pytest

from ete4 import ETE_DATA_HOME
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'


def test_update_database():
    ncbiquery.update_db(DATABASE_PATH)
    # It will download the full NCBI taxa database and process it. Slow!
    # Should raise an error if things go wrong.

@pytest.fixture(autouse=True)
def clean_taxdump():
    # remove the taxdump if it exists
    taxdump_location = ETE_DATA_HOME + '/tests/test_ncbiquery.taxdump.tar.gz'
    if os.path.exists(taxdump_location):
        os.remove(taxdump_location)

def test_update_with_taxdump():
    # update the db while using a custom location for the taxdump
    taxdump_location = ETE_DATA_HOME + '/tests/test_ncbiquery.taxdump.tar.gz'
    assert not os.path.exists(taxdump_location)
    ncbiquery.update_db(DATABASE_PATH, taxdump_location)
    assert os.path.exists(taxdump_location)