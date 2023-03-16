from sys import stdout
from . import _phyloxml as main
from ._phyloxml import *
from ._phyloxml_tree import PhyloxmlTree

_phyloxml.Phylogeny.subclass = PhyloxmlTree

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

    def export(self, outfile=stdout, level=0):
        namespace = 'xmlns:phy="http://www.phyloxml.org/1.10/phyloxml.xsd"'
        return super(Phyloxml, self).export(outfile=outfile, level=level, namespacedef_=namespace)


__all__ = _phyloxml.__all__ + ["Phyloxml", "PhyloxmlTree"]
