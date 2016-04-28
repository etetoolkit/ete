from __future__ import absolute_import
# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
#
#                     ABOUT THE ETE PACKAGE
#                     =====================
#
# ETE is distributed under the GPL copyleft license (2008-2015).
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in
# the toolkit may be available in the documentation.
#
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
#
# #END_LICENSE#############################################################


import sys
import re
import math
from os import path

from .. import numpy
from ..parser.text_arraytable import write_arraytable, read_arraytable
import six
from six.moves import range

__all__ = ["ArrayTable"]

class ArrayTable(object):
    """This object is thought to work with matrix datasets (like
    microarrays). It allows to load the matrix an access easily to row
    and column vectors. """

    def __repr__(self):
        return "ArrayTable (%s)" %hex(self.__hash__())

    def __str__(self):
        return str(self.matrix)

    def __init__(self, matrix_file=None, mtype="float"):
        self.colNames  = []
        self.rowNames  = []
        self.colValues = {}
        self.rowValues = {}
        self.matrix   = None
        self.mtype = None

        # If matrix file is supplied
        if matrix_file is not None:
            read_arraytable(matrix_file, \
                            mtype=mtype, \
                            arraytable_object = self)

    def get_row_vector(self,rowname):
        """ Returns the vector associated to the given row name """
        return self.rowValues.get(rowname,None)


    def get_column_vector(self,colname):
        """ Returns the vector associated to the given column name """
        return self.colValues.get(colname,None)


    def get_several_column_vectors(self,colnames):
        """ Returns a list of vectors associated to several column names """
        vectors = [self.colValues[cname] for cname in colnames]
        return numpy.array(vectors)

    def get_several_row_vectors(self,rownames):
        """ Returns a list vectors associated to several row names """
        vectors = [self.rowValues[rname] for rname in rownames]
        return numpy.array(vectors)

    def remove_column(self,colname):
        """Removes the given column form the current dataset """
        col_value = self.colValues.pop(colname, None)
        if col_value is not None:
            new_indexes = list(range(len(self.colNames)))
            index = self.colNames.index(colname)
            self.colNames.pop(index)
            new_indexes.pop(index)
            newmatrix = self.matrix.swapaxes(0,1)
            newmatrix = newmatrix[new_indexes].swapaxes(0,1)
            self._link_names2matrix(newmatrix)

    def merge_columns(self, groups, grouping_criterion):
        """ Returns a new ArrayTable object in which columns are
        merged according to a given criterion.

        'groups' argument must be a dictionary in which keys are the
        new column names, and each value is the list of current
        column names to be merged.

        'grouping_criterion' must be 'min', 'max' or 'mean', and
        defines how numeric values will be merged.

        Example:
           my_groups = {'NewColumn':['column5', 'column6']}
           new_Array = Array.merge_columns(my_groups, 'max')

        """

        if grouping_criterion == "max":
            grouping_f = get_max_vector
        elif grouping_criterion == "min":
            grouping_f = get_min_vector
        elif grouping_criterion == "mean":
            grouping_f = get_mean_vector
        else:
            raise ValueError("grouping_criterion not supported. Use max|min|mean ")

        grouped_array = self.__class__()
        grouped_matrix = []
        colNames = []
        alltnames = set([])
        for gname,tnames in six.iteritems(groups):
            all_vectors=[]
            for tn in tnames:
                if tn not in self.colValues:
                    raise ValueError(str(tn)+" column not found.")
                if tn in alltnames:
                    raise ValueError(str(tn)+" duplicated column name for merging")
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
        vmatrix = numpy.array(grouped_matrix).transpose()
        grouped_array._link_names2matrix(vmatrix)
        return grouped_array

    def transpose(self):
        """ Returns a new ArrayTable in which current matrix is transposed. """

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
        """ Synchronize curent column and row names to the given matrix"""
        if len(self.rowNames) != m.shape[0]:
            raise ValueError("Expecting matrix with  %d rows" % m.size[0])

        if len(self.colNames) != m.shape[1]:
            raise ValueError("Expecting matrix with  %d columns" % m.size[1])

        self.matrix = m
        self.colValues.clear()
        self.rowValues.clear()
        # link columns names to vectors
        i = 0
        for colname in self.colNames:
            self.colValues[colname] = self.matrix[:,i]
            i+=1
        # link row names to vectors
        i = 0
        for rowname in self.rowNames:
            self.rowValues[rowname] = self.matrix[i,:]
            i+=1

    def write(self, fname, colnames=None):
        write_arraytable(self, fname, colnames=colnames)



def get_centroid_dist(vcenter,vlist,fdist):
    d = 0.0
    for v in vlist:
        d += fdist(v,vcenter)
    return 2*(d / len(vlist))

def get_average_centroid_linkage_dist(vcenter1,vlist1,vcenter2,vlist2,fdist):
    d1,d2 = 0.0, 0.0
    for v in vlist1:
        d1 += fdist(v,vcenter2)
    for v in vlist2:
        d2 += fdist(v,vcenter1)
    return (d1+d2) / (len(vlist1)+len(vlist2))

def safe_mean(values):
    """ Returns mean value discarding non finite values """
    valid_values = []
    for v in values:
        if numpy.isfinite(v):
            valid_values.append(v)
    return numpy.mean(valid_values), numpy.std(valid_values)

def safe_mean_vector(vectors):
    """ Returns mean profile discarding non finite values """
    # if only one vector, avg = itself
    if len(vectors)==1:
        return vectors[0], numpy.zeros(len(vectors[0]))
    # Takes the vector length form the first item
    length = len(vectors[0])

    safe_mean = []
    safe_std  = []

    for pos in range(length):
        pos_mean = []
        for v in vectors:
            if numpy.isfinite(v[pos]):
                pos_mean.append(v[pos])
        safe_mean.append(numpy.mean(pos_mean))
        safe_std.append(numpy.std(pos_mean))
    return safe_mean, safe_std

def get_mean_vector(vlist):
    a = numpy.array(vlist)
    return numpy.mean(a,0)

def get_median_vector(vlist):
    a = numpy.array(vlist)
    return numpy.median(a)

def get_max_vector(vlist):
    a = numpy.array(vlist)
    return numpy.max(a,0)

def get_min_vector(vlist):
    a = numpy.array(vlist)
    return numpy.min(a,0)
