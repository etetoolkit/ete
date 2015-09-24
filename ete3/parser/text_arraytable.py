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
from __future__ import absolute_import
from __future__ import print_function

import re
from sys import stderr

from .. import numpy

from six.moves import map

__all__ = ['read_arraytable', 'write_arraytable']

def read_arraytable(matrix_file, mtype="float", arraytable_object = None):
    """ Reads a text tab-delimited matrix from file """

    if arraytable_object is None:
        from ..coretype import arraytable
        A = arraytable.ArrayTable()
    else:
        A = arraytable_object

    A.mtype          = mtype
    temp_matrix         = []
    rowname_counter     = {}
    colname_counter     = {}
    row_dup_flag = False
    col_dup_flag = False

    # if matrix_file has many lines, tries to read it as the matrix
    # itself.
    if len(matrix_file.split("\n"))>1:
        matrix_data = matrix_file.split("\n")
    else:
        matrix_data = open(matrix_file)

    for line in matrix_data:
        # Clean up line
        line = line.strip("\n")
        #line = line.replace(" ","")
        # Skip empty lines
        if not line:
            continue
        # Get fields in line
        fields = line.split("\t")
        # Read column names
        if line[0]=='#' and re.match("#NAMES",fields[0],re.IGNORECASE):
            counter = 0
            for colname in fields[1:]:
                colname = colname.strip()

                # Handle duplicated col names by adding a number
                colname_counter[colname] = colname_counter.get(colname,0) + 1
                if colname in A.colValues:
                    colname += "_%d" % colname_counter[colname]
                    col_dup_flag = True
                # Adds colname
                A.colValues[colname] = None
                A.colNames.append(colname)
            if col_dup_flag:
                print("Duplicated column names were renamed.", file=stderr)

        # Skip comments
        elif line[0]=='#':
            continue

        # Read values (only when column names are loaded)
        elif A.colNames:
            # Checks shape
            if len(fields)-1 != len(A.colNames):
                raise ValueError("Invalid number of columns. Expecting:%d" % len(A.colNames))

            # Extracts row name and remove it from fields
            rowname  = fields.pop(0).strip()

            # Handles duplicated row names by adding a number
            rowname_counter[rowname] = rowname_counter.get(rowname,0) + 1
            if rowname in A.rowValues:
                rowname += "_%d" % rowname_counter[rowname]
                row_dup_names = True

            # Adds row name
            A.rowValues[rowname] = None
            A.rowNames.append(rowname)

            # Reads row values
            values = []
            for f in fields:
                if f.strip()=="":
                    f = numpy.nan
                values.append(f)
            temp_matrix.append(values)
        else:
            raise ValueError("Column names are required.")

    if row_dup_flag:
        print("Duplicated row names were renamed.", file=stderr)

    # Convert all read lines into a numpy matrix
    vmatrix = numpy.array(temp_matrix).astype(A.mtype)

    # Updates indexes to link names and vectors in matrix
    A._link_names2matrix(vmatrix)
    return A

def write_arraytable(A, fname, colnames=None):
    if colnames is None:
        colnames = []
    elif colnames == []:
        colnames = A.colNames

    matrix = A.get_several_column_vectors(colnames)
    matrix = matrix.swapaxes(0,1)
    OUT = open(fname,"w")
    print('\t'.join(["#NAMES"] + colnames), file=OUT)
    counter = 0
    for rname in A.rowNames:
        print('\t'.join(map(str,[rname]+matrix[counter].tolist())), file=OUT)
        counter +=1
    OUT.close()
