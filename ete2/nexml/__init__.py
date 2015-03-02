from sys import stdout
import _nexml
from _nexml import *
from _nexml_tree import NexmlTree 

#_nexml.AbstractTree.subclass = NexmlTree
_nexml.FloatTree.subclass = NexmlTree
_nexml.IntTree.subclass = NexmlTree

class Nexml(_nexml.Nexml):
    """ Creates a new nexml project. """
    def __repr__(self):
        return "NeXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        _nexml.Nexml.__init__(self, *args, **kargs)
        
    def build_from_file(self, fname, index_otus=True):
        """ Populate Nexml project with data in a nexml file. """
        doc = _nexml.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = _nexml.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'Nexml'
            rootClass = self.__class__
        #rootObj = rootClass.factory()
        self.build(rootNode)

        # This keeps a pointer from all trees to the parent nexml
        # project. This way I can access other parts, such as otus,
        # etc...
        if index_otus:
            id2taxa = {}
            for taxa in self.get_otus():
                id2taxon = {}
                for taxon in taxa.otu: 
                    id2taxon[taxon.id] = taxon
                id2taxa[taxa.id] = [taxa, id2taxon]

            for trees in self.get_trees():
                for t in trees.get_tree():
                    t.set_nexml_project(self)
                    if trees.otus in id2taxa:
                        t.nexml_otus = id2taxa[trees.otus][0]

    def export(self, outfile=stdout, level=0):
        namespace='xmlns:nex="http://www.nexml.org/2009"'
        return super(Nexml, self).export(outfile=outfile, level=level, namespacedef_=namespace)
      

__all__ = _nexml.__all__ + ["Nexml", "NexmlTree"]
