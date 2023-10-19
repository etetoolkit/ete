import numpy as np

from ..parser.text_arraytable import write_arraytable, read_arraytable

__all__ = ["ArrayTable"]


class ArrayTable:
    """Class to work with matrix datasets (like microarrays).

    It allows to load the matrix and access easily row and column vectors.
    """

    def __init__(self, matrix_file=None, mtype="float"):
        self.colNames = []
        self.rowNames = []
        self.colValues = {}
        self.rowValues = {}
        self.matrix = None
        self.mtype = None

        # If matrix file is supplied:
        if matrix_file is not None:
            read_arraytable(matrix_file, mtype=mtype, arraytable_object=self)

    def __repr__(self):
        return "ArrayTable (%s)" % hex(self.__hash__())

    def __str__(self):
        return str(self.matrix)

    def get_row_vector(self, rowname):
        """Return the vector associated to the given row name."""
        return self.rowValues.get(rowname)

    def get_column_vector(self, colname):
        """Return the vector associated to the given column name."""
        return self.colValues.get(colname)

    def get_several_row_vectors(self, rownames):
        """Return a list of vectors associated to several row names."""
        vectors = [self.rowValues[rname] for rname in rownames]
        return np.array(vectors)

    def get_several_column_vectors(self, colnames):
        """Return a list of vectors associated to several column names."""
        vectors = [self.colValues[cname] for cname in colnames]
        return np.array(vectors)

    def remove_column(self, colname):
        """Remove the given column form the current dataset."""
        col_value = self.colValues.pop(colname, None)

        if col_value is None:
            return

        new_indexes = list(range(len(self.colNames)))
        index = self.colNames.index(colname)

        self.colNames.pop(index)
        new_indexes.pop(index)

        newmatrix = self.matrix.swapaxes(0,1)
        newmatrix = newmatrix[new_indexes].swapaxes(0,1)

        self._link_names2matrix(newmatrix)

    def merge_columns(self, groups, grouping_criterion):
        """Return a new ArrayTable with merged columns.

        The columns are merged (grouped) according to the given criterion.

        :param groups: Dictionary in which keys are the new column
            names, and each value is the list of current column names
            to be merged.
        :param grouping_criterion: How to merge numeric values. Can be
            'min', 'max' or 'mean'.

        Example::

           my_groups = {'NewColumn': ['column5', 'column6']}
           new_Array = Array.merge_columns(my_groups, 'max')
        """
        groupings = {'max': get_max_vector,
                     'min': get_min_vector,
                     'mean': get_mean_vector}
        try:
            grouping_f = groupings[grouping_criterion]
        except KeyError:
            raise ValueError(f'grouping_criterion "{grouping_criterion}" not '
                             'supported. Valid ones: %s' % ' '.join(groupings))

        grouped_array = self.__class__()
        grouped_matrix = []
        colNames = []
        alltnames = set([])
        for gname, tnames in groups.items():
            all_vectors=[]
            for tn in tnames:
                if tn not in self.colValues:
                    raise ValueError(f'column not found: {tn}')
                if tn in alltnames:
                    raise ValueError(f'duplicated column name for merging: {tn}')
                alltnames.add(tn)
                vector = self.get_column_vector(tn).astype(float)
                all_vectors.append(vector)
            # Store the group vector = max expression of all items in group
            grouped_matrix.append(grouping_f(all_vectors))
            # store group name
            colNames.append(gname)

        for cname in self.colNames:
            if cname not in alltnames:
                grouped_matrix.append(self.get_column_vector(cname))
                colNames.append(cname)

        grouped_array.rowNames= self.rowNames
        grouped_array.colNames= colNames
        vmatrix = np.array(grouped_matrix).transpose()
        grouped_array._link_names2matrix(vmatrix)
        return grouped_array

    def transpose(self):
        """Return a new ArrayTable in which current matrix is transposed."""
        transposedA = self.__class__()
        transposedM = self.matrix.transpose()
        transposedA.colNames = list(self.rowNames)
        transposedA.rowNames = list(self.colNames)
        transposedA._link_names2matrix(transposedM)

        # Check that everything is ok
        # for n in self.colNames:
        #     print self.get_column_vector(n) ==  transposedA.get_row_vector(n)
        # for n in self.rowNames:
        #     print self.get_row_vector(n) ==  transposedA.get_column_vector(n)
        return transposedA

    def _link_names2matrix(self, m):
        """Synchronize curent column and row names to the given matrix."""
        if len(self.rowNames) != m.shape[0]:
            raise ValueError("Expecting matrix with  %d rows" % m.size[0])

        if len(self.colNames) != m.shape[1]:
            raise ValueError("Expecting matrix with  %d columns" % m.size[1])

        self.matrix = m
        self.colValues.clear()
        self.rowValues.clear()

        # link columns names to vectors
        for i, colname in enumerate(self.colNames):
            self.colValues[colname] = self.matrix[:,i]

        # link row names to vectors
        for i, rowname in enumerate(self.rowNames):
            self.rowValues[rowname] = self.matrix[i,:]

    def write(self, fname, colnames=None):
        write_arraytable(self, fname, colnames=colnames)


def get_centroid_dist(vcenter, vlist, fdist):
    return 2 * sum(fdist(v, vcenter) for v in vlist) / len(vlist)


def get_average_centroid_linkage_dist(vcenter1, vlist1,
                                      vcenter2, vlist2, fdist):
    d1 = sum(fdist(v, vcenter2) for v in vlist1)
    d2 = sum(fdist(v, vcenter1) for v in vlist2)

    return (d1 + d2) / (len(vlist1) + len(vlist2))


def safe_mean(values):
    """Return the mean value and std discarding non finite values."""
    valid_values = [v for v in values if np.isfinite(v)]
    return np.mean(valid_values), np.std(valid_values)


def safe_mean_vector(vectors):
    """Return list of (mean, std) profiles discarding non finite values."""
    # If only one vector, avg = itself
    if len(vectors) == 1:
        return vectors[0], np.zeros(len(vectors[0]))

    safe_mean = []
    safe_std = []
    for i in range(len(vectors[0])):  # take vector length form the first item
        values = [v[i] for v in vectors if np.isfinite(v[i])]

        safe_mean.append(np.mean(values))
        safe_std.append(np.std(values))

    return safe_mean, safe_std


def get_mean_vector(vlist):
    return np.mean(vlist, 0)

def get_median_vector(vlist):
    return np.median(vlist)

def get_max_vector(vlist):
    return np.max(vlist, 0)

def get_min_vector(vlist):
    return np.min(vlist, 0)
