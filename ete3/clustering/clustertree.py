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

from sys import stderr
from . import clustvalidation
from ..coretype.tree import _translate_nodes
from .. import TreeNode, ArrayTable
from .. import numpy
from six.moves import range

__all__ = ["ClusterNode", "ClusterTree"]

class ClusterNode(TreeNode):
    """ Creates a new Cluster Tree object, which is a collection
    of ClusterNode instances connected in a hierarchical way, and
    representing a clustering result.

    a newick file or string can be passed as the first argument. An
    ArrayTable file or instance can be passed as a second argument.

    Examples:
      t1 = Tree() # creates an empty tree
      t2 = Tree( '(A:1,(B:1,(C:1,D:1):0.5):0.5);' )
      t3 = Tree( '/home/user/myNewickFile.txt' )
    """

    def _set_forbidden(self, value):
        raise ValueError("This attribute can not be manually set.")

    def _get_intra(self):
        if self._silhouette is None:
            self.get_silhouette()
        return self._intracluster_dist

    def _get_inter(self):
        if self._silhouette is None:
            self.get_silhouette()
        return self._intercluster_dist

    def _get_silh(self):
        if self._silhouette is None:
            self.get_silhouette()
        return self._silhouette

    def _get_prof(self):
        if self._profile is None:
            self._calculate_avg_profile()
        return self._profile

    def _get_std(self):
        if self._std_profile is None:
            self._calculate_avg_profile()
        return self._std_profile

    def _set_profile(self, value):
        self._profile = value

    intracluster_dist = property(fget=_get_intra, fset=_set_forbidden)
    intercluster_dist = property(fget=_get_inter, fset=_set_forbidden)
    silhouette = property(fget=_get_silh, fset=_set_forbidden)
    profile = property(fget=_get_prof, fset=_set_profile)
    deviation = property(fget=_get_std, fset=_set_forbidden)

    def __init__(self, newick = None, text_array = None, \
                 fdist=clustvalidation.default_dist):
        # Default dist is spearman_dist when scipy module is loaded
        # otherwise, it is set to euclidean_dist.

        # Initialize basic tree features and loads the newick (if any)
        TreeNode.__init__(self, newick)
        self._fdist = None
        self._silhouette = None
        self._intercluster_dist = None
        self._intracluster_dist = None
        self._profile = None
        self._std_profile = None

        # Cluster especific features
        self.features.add("intercluster_dist")
        self.features.add("intracluster_dist")
        self.features.add("silhouette")
        self.features.add("profile")
        self.features.add("deviation")

        # Initialize tree with array data
        if text_array:
            self.link_to_arraytable(text_array)

        if newick:
            self.set_distance_function(fdist)

    def __repr__(self):
        return "ClusterTree node (%s)" %hex(self.__hash__())

    def set_distance_function(self, fn):
        """ Sets the distance function used to calculate cluster
        distances and silouette index.

        ARGUMENTS:

          fn: a pointer to python function acepting two arrays (numpy) as
          arguments.

        EXAMPLE:

          # A simple euclidean distance
          my_dist_fn = lambda x,y: abs(x-y)
          tree.set_distance_function(my_dist_fn)

          """
        for n in self.traverse():
            n._fdist = fn
            n._silhouette = None
            n._intercluster_dist = None
            n._intracluster_dist = None

    def link_to_arraytable(self, arraytbl):
        """ Allows to link a given arraytable object to the tree
        structure under this node. Row names in the arraytable object
        are expected to match leaf names.

        Returns a list of nodes for with profiles could not been found
        in arraytable.

        """

        # Initialize tree with array data

        if type(arraytbl) == ArrayTable:
            array = arraytbl
        else:
            array = ArrayTable(arraytbl)

        missing_leaves = []
        matrix_values = [i for r in range(len(array.matrix))\
                           for i in array.matrix[r] if numpy.isfinite(i)]

        array._matrix_min = min(matrix_values)
        array._matrix_max = max(matrix_values)

        for n in self.traverse():
            n.arraytable = array
            if n.is_leaf() and n.name in array.rowNames:
                n._profile = array.get_row_vector(n.name)
            elif n.is_leaf():
                n._profile = [numpy.nan]*len(array.colNames)
                missing_leaves.append(n)


        if len(missing_leaves)>0:
            print("""[%d] leaf names could not be mapped to the matrix rows.""" %\
                len(missing_leaves), file=stderr)

        self.arraytable = array

    def iter_leaf_profiles(self):
        """ Returns an iterator over all the profiles associated to
        the leaves under this node."""
        for l in self.iter_leaves():
            yield l.get_profile()[0]

    def get_leaf_profiles(self):
        """ Returns the list of all the profiles associated to the
        leaves under this node."""
        return [l.get_profile()[0] for l in self.iter_leaves()]

    def get_silhouette(self, fdist=None):
        """ Calculates the node's silhouette value by using a given
        distance function. By default, euclidean distance is used. It
        also calculates the deviation profile, mean profile, and
        inter/intra-cluster distances.

        It sets the following features into the analyzed node:
           - node.intracluster
           - node.intercluster
           - node.silhouete

        intracluster distances a(i) are calculated as the Centroid
        Diameter

        intercluster distances b(i) are calculated as the Centroid linkage distance

        ** Rousseeuw, P.J. (1987) Silhouettes: A graphical aid to the
        interpretation and validation of cluster analysis.
        J. Comput. Appl. Math., 20, 53-65.

        """
        if fdist is None:
            fdist = self._fdist

        # Updates internal values
        self._silhouette, self._intracluster_dist, self._intercluster_dist = \
            clustvalidation.get_silhouette_width(fdist, self)
        # And returns them
        return self._silhouette, self._intracluster_dist, self._intercluster_dist

    def get_dunn(self, clusters, fdist=None):
        """ Calculates the Dunn index for the given set of descendant
        nodes.
        """

        if fdist is None:
            fdist = self._fdist
        nodes = _translate_nodes(self, *clusters)
        return clustvalidation.get_dunn_index(fdist, *nodes)

    def _calculate_avg_profile(self):
        """ This internal function updates the mean profile
        associated to an internal node. """

        # Updates internal values
        self._profile, self._std_profile = clustvalidation.get_avg_profile(self)


# cosmetic alias
#: .. currentmodule:: ete3
#
ClusterTree = ClusterNode
