"""
This module implements the interoperability between Phylogeny and
Clade attributes in the phyloXMl schema and the ETE Tree objects.

The PhyloXMLTree class should be use as a substitute for base Clade
and Phylogeny classes.

"""

import sys
from _phyloxml import Clade, Phylogeny, Tag_pattern_
from ete2 import PhyloTree

class PhyloXMLTree(PhyloTree):
    ''' PhyloTree object supporting phyloXML format. '''

    def __repr__(self):
        return "PhyloXML ETE tree <%s>" %hex(hash(self))

    def __init__(self, phyloxml_clade=None, phyloxml_phylogeny=None, **kargs):
        super(PhyloXMLTree, self).__init__(**kargs)
        if not phyloxml_phylogeny:
            self.phyloxml_phylogeny = Phylogeny()
        else:
            self.phyloxml_phylogeny = phyloxml_phylogeny 
        if not phyloxml_clade:
            self.phyloxml_clade = Clade()
        else:
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
            if nodeName_ == 'clade':
                self.build(child_)
            else:
                baseclass.buildChildren(child_, nodeName_)
        elif nodetype == 'clade':
            baseclass = self.phyloxml_clade
            if nodeName_ == 'clade':
                new_node = self.add_child()
                new_node.build(child_)
            else:
                baseclass.buildChildren(child_, nodeName_)
            
    def export(self, outfile=sys.stdout, level=0, namespace_='phy:', name_='Phylogeny', namespacedef_=''):
        if not self.up:
            self.phyloxml_phylogeny.clade = self.phyloxml_clade
            self.phyloxml_clade.clade = self.children
            self.phyloxml_phylogeny.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)
        else:
            self.phyloxml_clade.clade = self.children
            self.phyloxml_clade.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)

