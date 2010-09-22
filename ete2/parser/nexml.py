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
class AbstractTreeSub(supermod.AbstractTree, PhyloTree):
    def __init__(self, classxx=None, id=None, about=None, meta=None, label=None, node=None, rootedge=None, edge=None, valueOf_=None, mixedclass_=None, content_=None):
        super(AbstractTreeSub, self).__init__(classxx, id, about, meta, label, node, rootedge, edge, valueOf_, mixedclass_, content_, )
        super(PhyloTree, self).__init__()

    def build(self, node):
        super(AbstractTreeSub, self).build(node)

        rootid = set([e.source for e in self.edge]) - set([e.target for e in self.edge])

        nodeid2node = {rootid.pop(): self}
        for edge in self.edge:
            child = nodeid2node.setdefault(edge.target, self.__class__() )
            parent = nodeid2node.setdefault(edge.source, self.__class__() )
            child.name = edge.target
            parent.name = edge.source

            if edge.length is not None:
                child.dist = float(edge.length)

            if edge.id is not None:
                child.add_feature("nexml_edge_id", edge.id)

            if edge.label is not None:
                child.add_feature("nexml_edge_label", edge.id)

            parent.add_child(child)

        for xmlnode in self.node:
            if xmlnode.id not in nodeid2node: 
                print >>sys.stderr, "unused node", xmlnode.id
                continue

            ete_node = nodeid2node[xmlnode.id]
            if xmlnode.id is not None:
                ete_node.add_feature("nexml_node_id", xmlnode.id)
                
            if xmlnode.label is not None:
                ete_node.add_feature("nexml_node_label", xmlnode.label)

            if xmlnode.otu: 
                ete_node.add_feature("nexml_node_otu", xmlnode.otu)

            meta_content = []
            print "META CONTENT", xmlnode.meta
            for meta in xmlnode.meta:
                metaid = meta.id
                prop = meta.anyAttributes_.get("property", None)
                content = meta.anyAttributes_.get("content", None)
                datatype = meta.anyAttributes_.get("datatype", None)
                meta_content.append([metaid, prop, content, datatype])

            ete_node.add_feature("nexml_meta_content", meta_content) 
            print meta_content

        rootid = set([e.source for e in self.edge]) - set([e.target for e in self.edge])
        print rootid

    def exportChildren(self, outfile, level, namespace_='', name_='AbstractTree'):
        self.content_ = []
        for n in self.traverse():
            # ETE tree NeXML conversion
            if n.is_leaf(): 
                node_otu = n.name
            else:
                node_otu = None
            node_label = getattr(n, "nexml_node_label", n.name) 
            node_meta = getattr(n, "nexml_meta_content", []) 
            nodeid = getattr(n, "nexml_node_id", None) 
            node_root = getattr(n, "nexml_node_root", None) 
            node_about = getattr(n, "nexml_node_about", None) 
            edgeid = getattr(n, "nexml_edge_id", None) 
            edge_label = getattr(n, "nexml_edge_label", None) 
            edge_length = getattr(n, "nexml_edge_length", None) 
            edge_about = getattr(n, "nexml_edge_about", None) 
            edge_meta = getattr(n, "nexml_edge_meta", []) 

            edge_source = getattr(n.up, "nexml_node_id", None) 
            
            edge_target = nodeid
            if n.up:
                print n.up.name, n.name, edge_source, edge_target

                
            # Nodes
            node_meta_objs = []
            node_containers = []
            for metaid, prop, content, datatype in node_meta:
                m = LiteralMeta(id=metaid, datatype=datatype, content=content, property=prop)
                node_containers.append( m.mixedclass_(MixedContainer.CategoryComplex,
                                                 MixedContainer.TypeNone, 'meta', m))
                node_meta_objs.append(m)

            new_node = AbstractNode(id=nodeid, about=node_about, meta=node_meta_objs, label=node_label, otu=node_otu, root=node_root)
            new_node.content_.extend(node_containers)
            node_obj = self.mixedclass_(MixedContainer.CategoryComplex,
                MixedContainer.TypeNone, 'node', new_node)

            # Nodes children
            self.content_.append(node_obj)
            
            # Edges
            if edge_source: 
                print "EDGE", edge_source, edge_target
                edge_meta_objs = []
                edge_containers = []
                for metaid, prop, content, datatype in edge_meta:
                    m = LiteralMeta(id=metaid, datatype=datatype, content=content, property=prop)
                    edge_containers.append( m.mixedclass_(MixedContainer.CategoryComplex,
                                                     MixedContainer.TypeNone, 'meta', m))
                    edge_meta_objs.append(m)

                new_edge = AbstractEdge(id=edgeid, about=edge_about, meta=edge_meta_objs, label=edge_label, source=edge_source, length=edge_length, target=edge_target)
                new_node.content_.extend(edge_containers)
                edge_obj = self.mixedclass_(MixedContainer.CategoryComplex,
                    MixedContainer.TypeNone, 'edge', new_edge)

                # Nodes children
                self.content_.append(edge_obj)
            
        for item_ in self.content_:
            item_.export(outfile, level, item_.name, namespace_)

        # super(AbstractTreeSub, self).exportChildren(outfile, level, namespace_, name_)

supermod.AbstractTree.subclass = AbstractTreeSub
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


