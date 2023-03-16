"""
This module implements the interoperability between Phylogeny and
Clade attributes in the phyloXMl schema and the ETE Tree objects.

The PhyloxmlTree class should be use as a substitute for base Clade
and Phylogeny classes.
"""

import sys
from ._phyloxml import Clade, Phylogeny, Confidence, Tag_pattern_
from .. import PhyloTree

class PhyloxmlTree(PhyloTree):
    """PhyloTree object supporting phyloXML format."""

    def __repr__(self):
        return "PhyloXML ETE tree <%s>" %hex(hash(self))

    def _get_dist(self):
        v = self.phyloxml_clade.get_branch_length_attr()
        if v is None:
            v = self.phyloxml_clade.get_branch_length()
        if v is None:
            self._set_dist(self._dist)
            v = self.phyloxml_clade.get_branch_length_attr()
        return float(v)

    def _set_dist(self, value):
        try:
            self.phyloxml_clade.set_branch_length(float(value))
            self.phyloxml_clade.set_branch_length_attr(float(value))
        except ValueError:
            raise

    def _get_support(self):
        if len(self.phyloxml_clade.confidence) == 0:
                _c = Confidence(valueOf_=1.0, type_="branch_support")
                self.phyloxml_clade.add_confidence(_c)
        return float(self.phyloxml_clade.confidence[0].valueOf_)

    def _set_support(self, value):
        self._get_support()
        self.phyloxml_clade.confidence[0].valueOf_ = float(value)

    def _get_name(self):
        return self.phyloxml_clade.get_name()

    def _set_name(self, value):
        try:
            self.phyloxml_clade.set_name(value)
        except ValueError:
            raise

    def _get_children(self):
        return self.phyloxml_clade.clade

    dist = property(fget=_get_dist, fset=_set_dist)
    support = property(fget=_get_support, fset=_set_support)
    children = property(fget=_get_children)
    name = property(fget=_get_name, fset=_set_name)

    def __init__(self, phyloxml_clade=None, phyloxml_phylogeny=None, **kargs):
        if not phyloxml_phylogeny:
            self.phyloxml_phylogeny = Phylogeny()
        else:
            self.phyloxml_phylogeny = phyloxml_phylogeny
        if not phyloxml_clade:
            self.phyloxml_clade = Clade()
            self.phyloxml_clade.set_branch_length(0.0)
            self.phyloxml_clade.set_name("NoName")
            #self.__support = Confidence(valueOf_=1.0, type_="branch_support")
            #self.phyloxml_clade.add_confidence(self.__support)
        else:
            self.phyloxml_clade = phyloxml_clade
        super(PhyloxmlTree, self).__init__(**kargs)

    def build(self, node):
        nodetype = Tag_pattern_.match(node.tag).groups()[-1]
        if nodetype == 'phylogeny':
            self.phyloxml_phylogeny.buildAttributes(node, node.attrib, [])
        elif nodetype == 'clade':
            if "branch_length" in node.attrib:
                node.attrib["branch_length_attr"] = node.attrib["branch_length"]
            self.phyloxml_clade.buildAttributes(node, node.attrib, [])
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_, nodetype=nodetype)

    def buildChildren(self, child_, node, nodeName_, fromsubclass=False, nodetype=None):
        if nodetype == 'phylogeny':
            baseclass = self.phyloxml_phylogeny
            if nodeName_ == 'clade':
                self.build(child_)
            else:
                baseclass.buildChildren(child_, node, nodeName_)
        elif nodetype == 'clade':
            baseclass = self.phyloxml_clade
            if nodeName_ == 'clade':
                new_node = self.add_child()
                new_node.build(child_)
            else:
                baseclass.buildChildren(child_, node, nodeName_)

    def export(self, outfile=sys.stdout, level=0, namespace_='phy:', name_='Phylogeny', namespacedef_=''):
        if not self.up:
            self.phyloxml_phylogeny.clade = self.phyloxml_clade
            self.phyloxml_clade.clade = self.children
            self.phyloxml_phylogeny.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)
        else:
            self.phyloxml_clade.clade = self.children
            self.phyloxml_clade.export(outfile=outfile, level=level, name_=name_, namespacedef_=namespacedef_)
