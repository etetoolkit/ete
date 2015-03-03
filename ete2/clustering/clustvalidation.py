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

from ete2 import numpy
from math import sqrt 

def safe_mean(values):
    """ Returns mean value discarding non finite values """
    valid_values = []
    for v in values:
        if numpy.isfinite(v):
            valid_values.append(v)
    return numpy.mean(valid_values), numpy.std(valid_values)

def safe_mean_vector(vectors):
    """ Returns mean profile discarding non finite values.
    """
    # if only one vector, avg = itself
    if len(vectors)==1:
        return vectors[0], numpy.zeros(len(vectors[0]))
    # Takes the vector length form the first item
    length = len(vectors[0])

    safe_mean = []
    safe_std  = []

    for pos in xrange(length):
        pos_mean = []
        for v in vectors:
            if numpy.isfinite(v[pos]):
                pos_mean.append(v[pos])
        safe_mean.append(numpy.mean(pos_mean))
        safe_std.append(numpy.std(pos_mean))
    return numpy.array(safe_mean), numpy.array(safe_std)

def get_silhouette_width(fdist, cluster):
    sisters = cluster.get_sisters()

    # Calculates silhouette
    silhouette = []
    intra_dist = []
    inter_dist = []
    for st in sisters:
        if st.profile is None:
            continue
        for i in cluster.iter_leaves():
            # Skip nodes without profile
            if i._profile is not None:
                # item intraclsuterdist -> Centroid Diameter
                a = fdist(i.profile, cluster.profile)*2
                # intracluster dist -> Centroid Linkage
                b = fdist(i.profile, st.profile)

                if (b-a) == 0.0:
                    s = 0.0
                else:
                    s =  (b-a) / max(a,b)

                intra_dist.append(a)
                inter_dist.append(b)
                silhouette.append(s)

    silhouette, std = safe_mean(silhouette)
    intracluster_dist, std = safe_mean(intra_dist)
    intercluster_dist, std = safe_mean(inter_dist)
    return silhouette, intracluster_dist, intercluster_dist

def get_avg_profile(node):
    """ This internal function updates the mean profile
    associated to an internal node. """

    if not node.is_leaf():
        leaf_vectors = [n._profile for n in  node.get_leaves() \
                            if n._profile is not None]
        if len(leaf_vectors)>0:
            node._profile, node._std_profile = safe_mean_vector(leaf_vectors)
        else:
            node._profile, node._std_profile = None, None
        return node._profile, node._std_profile
    else:
        node._std_profile = [0.0]*len(node._profile)
        return node._profile, [0.0]*len(node._profile)


def get_dunn_index(fdist, *clusters):
    """
    Returns the Dunn index for the given selection of nodes.

    J.C. Dunn. Well separated clusters and optimal fuzzy
    partitions. 1974. J.Cybern. 4. 95-104.

    """

    if len(clusters)<2:
        raise ValueError, "At least 2 clusters are required"

    intra_dist = []
    for c in clusters:
        for i in c.get_leaves():
            if i is not None:
                # item intraclsuterdist -> Centroid Diameter
                a = fdist(i.profile, c.profile)*2
                intra_dist.append(a)
    max_a = numpy.max(intra_dist)
    inter_dist = []
    for i, ci in enumerate(clusters):
        for cj in clusters[i+1:]:
            # intracluster dist -> Centroid Linkage
            b = fdist(ci.profile, cj.profile)
            inter_dist.append(b)
    min_b = numpy.min(inter_dist)

    if max_a == 0.0:
        D = 0.0
    else:
        D = min_b / max_a
    return D



# ####################
# distance functions
# ####################

def pearson_dist(v1, v2):
    if (v1 == v2).all():
        return 0.0
    else:
        return 1.0 - stats.pearsonr(list(v1),list(v2))[0]
 
def spearman_dist(v1, v2):
    if (v1 == v2).all():
        return 0.0
    else:
        return 1.0 - stats.spearmanr(list(v1),list(v2))[0]

def euclidean_dist(v1,v2):
    if (v1 == v2).all():
        return 0.0
    else:
        return sqrt( square_euclidean_dist(v1,v2) )

def square_euclidean_dist(v1,v2):
    if (v1 == v2).all():
        return 0.0
    valids  = 0
    distance= 0.0
    for i in xrange(len(v1)):
        if numpy.isfinite(v1[i]) and numpy.isfinite(v2[i]):
            valids += 1
            d = v1[i]-v2[i]
            distance += d*d
    if valids==0:
        raise ValueError, "Cannot calculate values"
    return  distance/valids

try: 
   from scipy import stats
except ImportError: 
    try:
        import stats
        default_dist = spearman_dist
    except ImportError:
        default_dist = euclidean_dist
else:
    default_dist = spearman_dist
