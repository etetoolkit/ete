import sys

import _nexml as supermod
from _nexml import MixedContainer, AbstractNode, AbstractEdge, LiteralMeta

from ete_dev import PhyloTree

etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class NexMLTree(PhyloTree):
    ''' Special PhyloTree object with nexml support '''
    def __init__(self, nexml_node=None, nexml_edge=None, nexml_tree=None, **kargs):
        super(NexMLTree, self).__init__(**kargs)
        self.nexml_tree = nexml_tree
        self.nexml_node = nexml_node
        self.nexml_edge = nexml_edge

    def build(self, node):
        self.nexml_tree = supermod.AbstractTree()
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

        print self
        

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

class NexMLTree2(supermod.AbstractTree, PhyloTree):
    def __init__(self, classxx=None, id=None, about=None, meta=None, label=None, node=None, rootedge=None, edge=None, valueOf_=None, mixedclass_=None, content_=None):
        super(NexMLTree, self).__init__(classxx, id, about, meta, label, node, rootedge, edge, valueOf_, mixedclass_, content_, )
        super(PhyloTree, self).__init__()
        self.nexml_node = None
        self.nexml_edge = None

    def build(self, node):
        super(NexMLTree, self).build(node)

        # This detects the outgroup of the tree even if the root tag
        # is not set in any node
        rootid = set([e.source for e in self.edge]) - set([e.target for e in self.edge])

        nodeid2node = {rootid.pop(): self}
        for xmledge in self.edge:
            child = nodeid2node.setdefault(xmledge.target, self.__class__() )
            parent = nodeid2node.setdefault(xmledge.source, self.__class__() )
            child.name = xmledge.target
            parent.name = xmledge.source
            child.edge = xmledge

            if xmledge.length is not None:
                child.dist = float(xmledge.length)
            parent.add_child(child)

        for xmlnode in self.node:
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

        print self

    def exportChildren(self, outfile, level, namespace_='', name_='AbstractTree'):
        self.content_ = []
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
        self.content_.extend(sorted_nodes + sorted_edges)
        for item_ in self.content_:
            item_.export(outfile, level, item_.name, namespace_)


supermod.AbstractTree.subclass = NexMLTree
# end class AbstractTreeSub

def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Nexml'
        rootClass = supermod.Nexml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    # doc = None
    # sys.stdout.write('<?xml version="1.0" ?>\n')
    # rootObj.export(sys.stdout, 0, name_=rootTag,
    #               namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Nexml'
        rootClass = supermod.Nexml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_=rootTag,
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'Nexml'
        rootClass = supermod.Nexml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from ??? import *\n\n')
##     sys.stdout.write('import ??? as model_\n\n')
##     sys.stdout.write('rootObj = model_.Nexml(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="Nexml")
##     sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


