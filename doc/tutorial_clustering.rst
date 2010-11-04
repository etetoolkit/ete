****************
Clustering Trees
****************

Cluster analysis is the assignment of a set of observations into subsets (called
clusters) so that observations in the same cluster are similar in some sense.
Clustering is a method of unsupervised learning, and a common technique for
statistical data analysis used in many fields, including machine learning, data
mining, pattern recognition, image analysis and bioinformatics. Hierarchical
clustering creates a hierarchy of clusters which may be represented in a tree
structure called a dendrogram. The root of the tree consists of a single cluster
containing all observations, and the leaves correspond to individual
observations. [The Wikipedia porject Jun-2009].

ETE provides the **ClusterTree** instance, which inherits all the basic tree
methods and and adds support for linking clustering trees with the numerical
matrix that were used to compute the clustering. It also implements several
clustering validation techniques that aid in the analysis of cluster quality.
Currently, inter and intra-cluster distances, cluster std.deviation, Silhouette
analysis and Dunn indexes can be computed with ETE. Indeed, this type of trees
can be used, not only as clustering trees, but as any other type requiring
numerical vectors to be associated with tree nodes: i.e.) phylogenetic profiles,
microarray expression datasets or node fingerprint vectors.

ClusterTrees can be linked to a numerical matrix by using the
**link_to_arraytable()** method (in nodes) or by passing the reference to the
matrix (filename or text string) as the **text_arraytable** argument of
PhyloTree constructor. Once this is done, the **node.profile, node.deviation,
node.silhouette, node.dunn, node.intracluster_dist and node.intercluster_dist**
attributes will are automatically available. As well as the
**iter_leaf_profiles()**, **get_leaf_profiles()**, **get_silhouette()** and
**get_dunn()** methods.


Visualization of matrix associated Trees
========================================

Clustering or not, any ClusterTree instance, associated to a numerical matrix,
can be visualized together with the graphical representation of its node's
numeric profiles. To this end, the **ProfileFace** class is provided. This face
type can represent a node's numeric profile in four different ways:

You can create your own layout functions add one or more ProfileFace instances
to any cluster tree node (leaf or internal). Moreover, three basic layouts are
provided that use different styles of ProfileFace instances: **heatmap**,
**line_profiles**, **bar_profiles**, **cbar_profiles**.

.. % 


Performing a Cluster Validation Analysis
========================================

If associated matrix represents the dataset used to produce a given tree,
clustering validation values can be used to assess the quality of partitions. To
do so, you will need to set the distance function that was used to calculate
distances among items (leaf nodes). ETE implements three common distance methods
in bioinformatics : **euclidean**, **pearson** correlation and **spearman**
correlation distances.

In the following example, a microarray clustering result is analyzed using ETE.

The following example illustrates how to implement a custom clustering
validation analysis:

.. % 

