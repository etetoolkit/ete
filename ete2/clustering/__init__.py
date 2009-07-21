# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.  
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE). 
# http://ete.cgenomics.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
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
