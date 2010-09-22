import sys

import _nexml as supermod
from _nexml import MixedContainer, AbstractNode, AbstractEdge

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

        nodeid2node = {}
        for edge in self.edge:
            child = nodeid2node.setdefault(edge.target, self.__class__() )
            parent = nodeid2node.setdefault(edge.source, self.__class__() )
            child.name = edge.target
            parent.name = edge.source
            child.dist = float(edge.length)
            if edge.id:
                child.add_feature("edgeid", edge.id)
            parent.add_child(child)

        for nname, n in nodeid2node.iteritems():
            if not n.up: 
                self.dist = n.dist
                self.name = n.name
                for c in n.children:
                    self.add_child(c)
                nodeid2node[nname] = self
                n.children = []
                del n

        for node in self.node:
            nodeid2node[node.label].label = node.label
            if node.otu: 
                print node.otu
                nodeid2node[node.label].name = node.otu
        t = parent.get_tree_root()
        print t
        self.export(sys.stderr, 0)
        print len(self.content_)

    def exportChildren(self, outfile, level, namespace_='', name_='AbstractTree'):
        self.content_ = []
        for n in self.traverse():
            # ETE tree NeXML conversion
            if n.is_leaf(): 
                otu = n.name
            else:
                otu = None
            label = getattr(n, "label", n.name) 
            meta = getattr(n, "meta", None) 
            nodeid = getattr(n, "id", None) 
            root = getattr(n, "root", None) 
            about = getattr(n, "about", None) 

            new_node = AbstractNode(id=nodeid, about=about, meta=meta, label=label, otu=otu, root=root)
            obj = self.mixedclass_(MixedContainer.CategoryComplex,
                MixedContainer.TypeNone, 'node', new_node)
            self.content_.append(obj)
            
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


