import _nexml as main
#from _nexml import * 
from _nexml_tree import NexMLTree 

main.AbstractTree.subclass = NexMLTree

class Nexml(main.Phyloxml):
    def __repr__(self):
        return "PhyloXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        main.Phyloxml.__init__(self, *args, **kargs)
        
    def load_from_file(self, fname):
        pass
