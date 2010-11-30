import sys
from _nexml import MixedContainer, FloatTree, TreeFloatEdge, TreeNode
from ete_dev import PhyloTree


class Children(list):
    def append(self, item):
        list.append(self, item)
        #item.up = self.node
        item.nexml_edge.target = self.node.nexml_node.id
        item.nexml_edge.source = item.nexml_node.id

class NexMLTree(PhyloTree):
    ''' Special PhyloTree object with nexml support '''

    def __repr__(self):
        return "NexML ETE tree <%s>" %hex(hash(self))

    def __init__(self, nexml_node=None, nexml_edge=None, nexml_tree=None, **kargs):
        super(NexMLTree, self).__init__(**kargs)
        self._children = Children()
        self._children.node = self

        if not nexml_tree:
            nexml_tree = FloatTree()
        if not nexml_edge: 
            nexml_edge = TreeFloatEdge()
        if not nexml_node:
            nexml_node = TreeNode()

        self.nexml_tree = nexml_tree
        self.nexml_node = nexml_node
        self.nexml_edge = nexml_edge
        self.nexml_project = None
        self.nexml_node.id = "node_%s" %hash(self)
        self.nexml_edge.id = "edge_%s" %hash(self)
        

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
NexMLNode = NexMLTree
