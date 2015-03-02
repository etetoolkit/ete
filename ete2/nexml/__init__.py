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
from sys import stdout
import _nexml
from _nexml import *
from _nexml_tree import NexmlTree 

#_nexml.AbstractTree.subclass = NexmlTree
_nexml.FloatTree.subclass = NexmlTree
_nexml.IntTree.subclass = NexmlTree

class Nexml(_nexml.Nexml):
    """ Creates a new nexml project. """
    def __repr__(self):
        return "NeXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        _nexml.Nexml.__init__(self, *args, **kargs)
        
    def build_from_file(self, fname, index_otus=True):
        """ Populate Nexml project with data in a nexml file. """
        doc = _nexml.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = _nexml.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'Nexml'
            rootClass = self.__class__
        #rootObj = rootClass.factory()
        self.build(rootNode)

        # This keeps a pointer from all trees to the parent nexml
        # project. This way I can access other parts, such as otus,
        # etc...
        if index_otus:
            id2taxa = {}
            for taxa in self.get_otus():
                id2taxon = {}
                for taxon in taxa.otu: 
                    id2taxon[taxon.id] = taxon
                id2taxa[taxa.id] = [taxa, id2taxon]

            for trees in self.get_trees():
                for t in trees.get_tree():
                    t.set_nexml_project(self)
                    if trees.otus in id2taxa:
                        t.nexml_otus = id2taxa[trees.otus][0]

    def export(self, outfile=stdout, level=0):
        namespace='xmlns:nex="http://www.nexml.org/2009"'
        return super(Nexml, self).export(outfile=outfile, level=level, namespacedef_=namespace)
      

__all__ = _nexml.__all__ + ["Nexml", "NexmlTree"]
