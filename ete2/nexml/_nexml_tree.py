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
import sys
from _nexml import MixedContainer, FloatTree, TreeFloatEdge, TreeNode, LiteralMeta
from ete2 import PhyloTree
from ete2.phylo.phylotree import _parse_species
from ete2.parser.newick import read_newick

class Children(list):
    def append(self, item):
        list.append(self, item)
        item.nexml_edge.source = self.node.nexml_node.id
        item.nexml_edge.target = item.nexml_node.id

class NexmlTree(PhyloTree):
    """ 
    Special PhyloTree object with nexml support 
    """

    def __repr__(self):
        return "NexML ETE tree <%s>" %hex(hash(self))

    def _get_dist(self):
        return self.nexml_edge.get_length()
    def _set_dist(self, value):
        try:
            self.nexml_edge.set_length(value)
        except ValueError:
            raise

    def _get_support(self):
        return self._nexml_support.content
    def _set_support(self, value):
        try:
            self._nexml_support.content = float(value)
        except ValueError:
            raise
       
    def _get_name(self):
        return self.nexml_node.get_label()

    def _set_name(self, value):
        try:
            self.nexml_node.set_label(value)
        except ValueError:
            raise

    def _get_children(self):
        return self._children
    def _set_children(self, value):
        if isinstance(value, Children) and \
           len(set([type(n)==type(self) for n in value]))<2:
            self._children = value
        else:
            raise ValueError, "children:wrong type"

    dist = property(fget=_get_dist, fset=_set_dist)
    support = property(fget=_get_support, fset=_set_support)
    children = property(fget=_get_children, fset=_set_children)
    name = property(fget=_get_name, fset=_set_name)

    def __init__(self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species, format=0):

        self.nexml_tree = FloatTree()
        self.nexml_tree.set_anyAttributes_({'xsi:type': 'FloatTree'})
        self.nexml_node = TreeNode()
        self.nexml_edge = TreeFloatEdge()
        self.nexml_node.id = "node_%s" %hash(self)
        self.nexml_edge.id = "edge_%s" %hash(self)
        self.nexml_project = None
        self._nexml_support = LiteralMeta(datatype="float", property="branch_support", content=1.0)
        self.nexml_edge.length = 0.0
        self.nexml_edge.add_meta(self._nexml_support)

        # Initialize empty PhyloTree
        super(NexmlTree, self).__init__()
        self._children = Children()
        self._children.node = self

        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            read_newick(newick, root_node=self, format=format)
            self.set_species_naming_function(sp_naming_function)

    def set_nexml_project(self, nexml_obj):
        self.nexml_project = nexml_obj
        
    def build(self, node):
        self.nexml_tree = FloatTree()
        tree = self.nexml_tree
        tree.build(node)

        # This detects the outgroup of the tree even if the root tag
        # is not set in any node
        rootid = set([e.source for e in tree.edge]) - set([e.target for e in tree.edge])

        nodeid2node = {rootid.pop(): self}
        for xmledge in tree.edge:
            child = nodeid2node.setdefault(xmledge.target, self.__class__() )
            parent = nodeid2node.setdefault(xmledge.source, self.__class__() )
            child.name = xmledge.target
            child.nexml_node.id = xmledge.target
            parent.name = xmledge.source
            parent.nexml_node.id = xmledge.source
            child.nexml_edge = xmledge

            if xmledge.length is not None:
                child.dist = float(xmledge.length)
            parent.add_child(child)

        for xmlnode in tree.node:
            # just a warning. I don't know if this can occur
            if xmlnode.id not in nodeid2node: 
                print >>sys.stderr, "Unused node", xmlnode.id
                continue

            ete_node = nodeid2node[xmlnode.id]
            ete_node.nexml_node = xmlnode

            if xmlnode.label:
                ete_node.name = xmlnode.label
            elif xmlnode.id is not None:
                ete_node.name = xmlnode.id

                
    def export(self, outfile=sys.stdout, level=0, namespace_='', name_='FloatTree', namespacedef_=''):
        if self.nexml_tree:
            info = [(n.nexml_edge, n.nexml_node) for n in self.traverse()]
            self.nexml_node.set_root(True)
            self.nexml_tree.set_edge([i[0] for i in info])
            self.nexml_tree.set_node([i[1] for i in info])
            self.nexml_tree.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)


    def exportChildren(self, outfile, level, namespace_='', name_='FloatTree'):
        sorted_nodes = []
        sorted_edges = []
        for n in self.traverse():
            # process node
            node_obj = self.mixedclass_(MixedContainer.CategoryComplex,
                MixedContainer.TypeNone, 'node', n.nexml_node)
            sorted_nodes.append(node_obj)
            
            # process edge
            if n.nexml_edge: 
                edge_obj = self.mixedclass_(MixedContainer.CategoryComplex,
                    MixedContainer.TypeNone, 'edge', n.nexml_edge)
                sorted_edges.append(edge_obj)

        # process the nodes and edges 
        self.tree.content_ = sorted_nodes + sorted_edges
        for item_ in self.tree.content_:
            item_.export(outfile, level, item_.name, namespace_)

# end class AbstractTreeSub
NexmlNode = NexmlTree
