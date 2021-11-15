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

from collections import namedtuple, OrderedDict



FACE_POSITIONS = ["branch_right", "branch_top", "branch_bottom", "aligned"]


_FaceAreas = namedtuple('_FaceAreas', FACE_POSITIONS)


def get_FaceAreas(branch_top=None, branch_bottom=None,
        branch_right=None, aligned=None):
    return _FaceAreas(
            branch_top or _FaceContainer(), 
            branch_bottom or _FaceContainer(), 
            branch_right or _FaceContainer(), 
            aligned or _FaceContainer())


cdef class _FaceContainer(dict):
    """
    Use this object to create a grid of faces. You can add faces to different columns.
    """
    def add_face(self, object face, int column):
        """
        add the face **face** to the specified **column**
        """
        self.setdefault(column, []).append(face)
