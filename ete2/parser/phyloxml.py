#!/usr/bin/env python

#
# Generated Fri Sep 24 10:48:32 2010 by generateDS.py version 2.2a.
#

import sys

import _phyloxml as supermod
from _phyloxml import Clade, Phylogeny, Tag_pattern_
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

class PhyloXMLTree(PhyloTree):
    ''' PhyloTree object supporting phyloXML format. '''
    def __init__(self, phyloxml_clade=Clade(), phyloxml_phylogeny=Phylogeny(), **kargs):
        super(PhyloXMLTree, self).__init__(**kargs)
        self.phyloxml_phylogeny = phyloxml_phylogeny
        self.phyloxml_clade = phyloxml_clade

    def build(self, node):
        nodetype = Tag_pattern_.match(node.tag).groups()[-1]
        if nodetype == 'phylogeny':
            self.phyloxml_phylogeny.buildAttributes(node, node.attrib, [])
        elif nodetype == 'clade':
            self.phyloxml_clade.buildAttributes(node, node.attrib, [])

        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_, nodetype=nodetype)

    def buildChildren(self, child_, nodeName_, from_subclass=False, nodetype=None):
        if nodetype == 'phylogeny':
            baseclass = self.phyloxml_phylogeny
        elif nodetype == 'clade':
            baseclass = self.phyloxml_clade

        if nodeName_ == 'clade':
            new_node = self.add_child()
            new_node.build(child_)
            new_node.name = new_node.phyloxml_clade.taxonomy[0].id.valueOf_  # fix this
        else:
            baseclass.buildChildren(child_, nodeName_)
            
    def export(self, outfile=sys.stdout, level=0, namespace_='phy:', name_='Phylogeny', namespacedef_=''):
        if level==0:
            self.phyloxml_phylogeny.clade = self._children
            self.phyloxml_phylogeny.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)
        else:
            self.phyloxml_clade.clade = self._children
            self.phyloxml_clade.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)

supermod.Phylogeny.subclass = PhyloXMLTree
# end class PhyloXMLTree


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
        rootTag = 'phyloxml'
        rootClass = supermod.Phyloxml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    #doc = None
    #sys.stdout.write('<?xml version="1.0" ?>\n')
    #rootObj.export(sys.stdout, 0, name_=rootTag,
    #    namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'phyloxml'
        rootClass = supermod.Phyloxml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'phyloxml'
        rootClass = supermod.Phyloxml
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from ??? import *\n\n')
    sys.stdout.write('import ??? as model_\n\n')
    sys.stdout.write('rootObj = model_.phyloxml(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="phyloxml")
    sys.stdout.write(')\n')
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


