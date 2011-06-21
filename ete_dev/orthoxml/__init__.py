from sys import stdout
import _orthoxml as main
from _orthoxml import * 

_orthoxml.Orthoxml.subclass = Orthoxml

class Orthoxml(_orthoxml.Phyloxml):
    def __repr__(self):
        return "Orthoxml dataset <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        super(Orthoxml, self).__init__(outfile=outfile, level=level)
        
    def build_from_file(self, fname):
        doc = _orthoxml.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = _orthoxml.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'phyloxml'
            rootClass = self.__class__
        self.build(rootNode)

    def export(self, outfile=stdout, level=0):
        return super(Orthoxml, self).export(outfile=outfile, level=level)


__all__ = _orthoxml.__all__ + ["Orthoxml"]
