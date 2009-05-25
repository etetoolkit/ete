import sys

from numpy import nan as NaN # Missing values in array are saved as
			     # NaN values

import clusterdist as AT
from pygenomics import TreeNode, ArrayTable

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

    def __init__(self, newick = None, array_table = None):
	# Initialize basic tree features and loads the newick (if any)
        TreeNode.__init__(self, newick)

	# Cluster especific features
        self._avg_profile = None
        self._std_profile = None
        self.add_feature("intercluster_d", None)
        self.add_feature("intracluster_d", None)
        self.add_feature("silhouette", None)
        self.add_feature("mean_std", None)

	# Initialize tree with array data
	if array_table:
	    self.link_to_arraytable(array_table)

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
	for n in self.traverse():
	    n.arraytable = array
	    if n.is_leaf() and n.name in array.rowNames:
		n._avg_profile = array.get_row_vector(n.name)
	    elif n.is_leaf():
		n._avg_profile = [NaN]*len(array.colNames) 
		missing_leaves.append(n)


	if len(missing_leaves)>0:
	    print >>sys.stderr, \
		"""[%d] leaf names could not be mapped to the matrix rows.""" %\
		len(missing_leaves)

	self.arraytable = array

    def get_profile(self):
	""" Returns the associated profile of this node and its
	standard deviation.

	If node is a leaf: average profile is the leaf profile
	itself and standard deviation vector set to 0.

	If node is internal, avg profile is the average of all leaf
	profiles under the node.
 
	"""
	if self._avg_profile is not None:
	    return self._avg_profile, self._std_profile
	else:
	    self.get_avg_profiles()
	    return self._avg_profile, self._std_profile

    def iter_leaf_profiles(self):
	""" Returns an iterator over all the profiles associated to
	the leaves under this node."""
	for l in self.iter_leaves():
	    yield l.get_profile()[0]

    def get_leaf_profiles(self):
	""" Returns the list of all the profiles associated to the
	leaves under this node."""
	return [l.get_profile()[0] for l in self.iter_leaves()]
    
    def calculate_silhouette(self, fdist=AT.spearman_dist):
        """ Calculates the node's silhouette value by using a given
        distance function. By default, euclidean distance is used. It
        also calculates the deviation profile, mean profile, and
        inter/intra-cluster distances. 

	It sets the following features into the analyzed node:
	   - node.intracluster_d
	   - node.intercluster_d
	   - node.silhouete 

	intracluster distances a(i) are calculated as the centroid
	distance.

	intercluster distances b(i) are calculated as the Average to
	Centroid Linkage.


	** Rousseeuw, P.J. (1987) Silhouettes: A graphical aid to the
	interpretation and validation of cluster analysis.
	J. Comput. Appl. Math., 20, 53-65.

	   """
        
        sisters = self.get_sisters()
        
        # Calculates average vectors
        if  self._avg_profile is None:
            self.get_avg_profile()
            
        for st in sisters:
            if st._avg_profile is None:
                st.get_avg_profile()
        
        # Calculates silhouette
	silhouette = []
        intra_dist = []
        inter_dist = []
        for st in sisters:
            if st._avg_profile is None:
		continue

            for i in self.iter_leaves():
                # Skip nodes with nodes without profile
                if i._avg_profile is not None:
		    # Centroid Diameter
		    a = fdist(i._avg_profile, self._avg_profile)*2 
		    # Centroid Linkage
		    b = fdist(i._avg_profile, st._avg_profile) 
		    if (b-a) == 0.0:
			s = 0.0
		    else:
			s =  (b-a) / max(a,b)
		    intra_dist.append(a)
		    inter_dist.append(b)
		    silhouette.append(s)

        self.silhouette, std     = AT.safe_mean(silhouette)
        self.intracluster_d, std = AT.safe_mean(intra_dist)
        self.intercluster_d, std = AT.safe_mean(inter_dist)
        return self.silhouette, self.intracluster_d, self.intercluster_d

    def get_avg_profile(self):
	""" This internal function updates the mean profile
	associated to an internal node. """

	if not self.is_leaf():
	    leaf_vectors = [n._avg_profile for n in  self.get_leaves() \
				if n._avg_profile is not None]
	    if len(leaf_vectors)>0:
		self._avg_profile, self._std_profile = AT.safe_mean_vector(leaf_vectors)
	    else:
		self._avg_profile, self._std_profile = None, None
	    return self._avg_profile, self._std_profile
	else: 
	    return self._avg_profile, [0.0]*len(self._avg_profile)


# cosmetic alias
ClusterTree = ClusterNode
