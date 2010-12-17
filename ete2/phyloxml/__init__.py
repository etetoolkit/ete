import _phyloxml as main
from _phyloxml import * 
from _phyloxml_tree import PhyloXMLTree 

_phyloxml.Phylogeny.subclass = PhyloXMLTree

class Phyloxml(_phyloxml.Phyloxml):
    def __repr__(self):
        return "PhyloXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        _phyloxml.Phyloxml.__init__(self, *args, **kargs)
        
    def build_from_file(self, fname):
        doc = _phyloxml.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = _phyloxml.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'phyloxml'
            rootClass = self.__class__
        self.build(rootNode)


__all__ = _phyloxml.__all__ + ["Phyloxml", "PhyloXMLTree"]
