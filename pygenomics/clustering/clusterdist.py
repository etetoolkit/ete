# This is a flag used to build ete2 standalone package.
in_ete_pkg=True
import numpy 
import math 
from scipy import stats

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
    
    for pos in xrange(length):
        pos_mean = []
        for v in vectors:
            if numpy.isfinite(v[pos]):
                pos_mean.append(v[pos])
        safe_mean.append(numpy.mean(pos_mean))
        safe_std.append(numpy.std(pos_mean))
    return safe_mean, safe_std

# ####################
# distance functions
# ####################

def pearson_dist(v1,v2):
    if (v1 == v2).all(): 
        return 0.0
    else:
        return 1.0 - stats.pearsonr(v1,v2)[0]

def spearman_dist(v1,v2):
    if (v1 == v2).all(): 
        return 0.0
    else:
        return 1.0 - stats.spearmanr(v1,v2)[0]

def euclidean_dist(v1,v2):
    if (v1 == v2).all(): 
        return 0.0
    else:
        return math.sqrt( square_euclidean_dist(v1,v2) )

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



__version__="1.0rev95"
__author__="Jaime Huerta-Cepas"
