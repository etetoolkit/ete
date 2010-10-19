import sys

import _nexml as supermod
from _nexml import MixedContainer, AbstractTree, AbstractNode, AbstractEdge, LiteralMeta

from ete2 import PhyloTree

class NexMLTree(PhyloTree):
    ''' Special PhyloTree object with nexml support '''
    def __repr__(self):
        return "NexML ETE tree <%s>" %hex(hash(self))

    def __init__(self, nexml_node=None, nexml_edge=None, nexml_tree=None, **kargs):
        super(NexMLTree, self).__init__(**kargs)
        self.nexml_tree = nexml_tree
        self.nexml_node = nexml_node
        self.nexml_edge = nexml_edge

    def build(self, node):
        self.nexml_tree = AbstractTree()
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
            parent.name = xmledge.source
            child.nexml_edge = xmledge

            if xmledge.length is not None:
                child.dist = float(xmledge.length)
            parent.add_child(child)

        for xmlnode in tree.node:
            # just a warning. I don't know if this can occur
            if xmlnode.id not in nodeid2node: 
                print >>sys.stderr, "unused node", xmlnode.id
                continue

            ete_node = nodeid2node[xmlnode.id]
            ete_node.nexml_node = xmlnode
            
            if xmlnode.id is not None:
                ete_node.name = xmlnode.id
                
            if xmlnode.label is not None:
                ete_node.name += "(" + xmlnode.label + ")"

    def export(self, outfile=sys.stdout, level=0, namespace_='', name_='AbstractTree', namespacedef_=''):
        if self.nexml_tree:
            self.nexml_tree.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)

    def exportChildren(self, outfile, level, namespace_='', name_='AbstractTree'):
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


supermod.AbstractTree.subclass = NexMLTree
# end class AbstractTreeSub

