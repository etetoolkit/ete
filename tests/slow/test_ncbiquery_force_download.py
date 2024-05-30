"""
Test the functionality of ncbiquery.py. To run with pytest.
"""

from ete4 import ETE_DATA_HOME
from ete4.ncbi_taxonomy import ncbiquery

DATABASE_PATH = ETE_DATA_HOME + '/tests/test_ncbiquery.taxa.sqlite'


def test_update_database():
    ncbiquery.update_db(DATABASE_PATH)
    # It will download the full NCBI taxa database and process it. Slow!
    # Should raise an error if things go wrong.
