from clustertree import *



def read_newick_file_as_clustering(treefile, arrayfile):
    """ Reads a newick clustering result and the array used to
    generate it. """
    # Loads tree
    t = readNewick.read_newick_file(treefile, nodeInstance=ClusterNode)
    array = readArraytable.read_arraytable(arrayfile)
    # Checks for tree/array compatibility and loads matrix vectors to nodes
    missing_leaves = []
    all_leaves = [t]+t.get_descendants()
    for n in all_leaves:
	n.array     = array
        if len(n.childs)==0:
	    if n.name in array.rowNames:
		n.avg_vector = array.get_row_vector(n.name)
	    else:
		missing_leaves.append(n.name)
    if len(missing_leaves)>0:
        print >>sys.stderr, "%d leaf names (from a total of %d) could not been mapped to the matrix row names!" % \
              ( len(missing_leaves), len(all_leaves) )
    return t, array
