"""
Tests reading clustering or phylogenetic profile data.
"""

import numpy as np

from ete4 import ArrayTable
from . import datasets as ds


def test_arraytable_parser():
    """Test reading numeric tables and simple manipulations."""
    A = ArrayTable(ds.expression)

    assert (A.get_row_vector("A").tolist() ==
            [-1.23, -0.81, 1.79, 0.78,-0.42,-0.69, 0.58])

    assert (A.get_several_row_vectors(["A", "C"]).tolist() ==
            [[-1.23, -0.81, 1.79, 0.78, -0.42, -0.69, 0.58],
             [-2.19, 0.13, 0.65, -0.51, 0.52, 1.04, 0.36]])

    assert (A.get_column_vector("col4").tolist() ==
            [0.78, 0.36, -0.51, -0.76, 0.07, -0.14, 0.23, -0.3])

    assert (A.get_several_column_vectors(["col2", "col7"]).tolist() ==
            [[-0.81, -0.94, 0.13, -0.98, -0.83, -1.11, -1.17, -1.25],
             [0.58, 1.12, 0.36, 0.93, 0.65, 0.48, 0.26, 0.77]])

    A.remove_column("col4")
    assert A.get_column_vector("col4") is None

    Abis = A.merge_columns({"merged1": ["col1", "col2"],
                            "merged2": ["col5", "col6"]}, "mean")
    assert (np.round(Abis.get_column_vector("merged1"), 3).tolist() ==
            [-1.02, -1.35, -1.03, -1.1, -1.15, -1.075, -1.37, -1.39])

    # TODO: More tests. Jaime, you can do it!
