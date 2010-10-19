import _phyloxml as main
from _phyloxml import * 
from _phyloxml_tree import PhyloXMLTree 

main.Phylogeny.subclass = PhyloXMLTree

class Phyloxml(main.Phyloxml):
    def __repr__(self):
        return "PhyloXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        main.Phyloxml.__init__(self, *args, **kargs)
        
    def load_from_file(self, fname):
        doc = main.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = main.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'phyloxml'
            rootClass = self.__class__
        self.build(rootNode)
