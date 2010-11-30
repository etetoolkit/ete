import _nexml as main
from _nexml import * 
from _nexml_tree import NexMLTree 

main.AbstractTree.subclass = NexMLTree
main.FloatTree.subclass = NexMLTree
main.IntTree.subclass = NexMLTree

class Nexml(main.Nexml):
    def __repr__(self):
        return "NeXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        main.Nexml.__init__(self, *args, **kargs)
        
    def build_from_file(self, fname, index_otus=True):
        doc = main.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = main.get_root_tag(rootNode)
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
