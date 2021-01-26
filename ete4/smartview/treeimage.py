
from collections import namedtuple
from .utils import timeit


class TreeImage():
    def __init__(self, tree):
        self.tree = tree
                
        # cached information: anything that improves drawing performance        
        self.cache_size_jordi()

    @timeit        
    def cache_size_jordi(self):
        for postorder, n in self.tree.iter_prepostorder():
            if postorder: # I am an internal node and all my descendants have been visited 
                height = sum([ch.size[1] for ch in n.children])
                width = n.dist + max([ch.size[0] for ch in n.children])                
                n.size = (width, height)
                n.d1 = n.size[1] / 2 + ((n.children[0].d1 - n.children[-1].size[1] + n.children[-1].d1) / 2)
               
            else: # First time visiting a node
                if not n.children:                    
                    n.size = (n.dist, 1.0)
                    print(n.size)
                    n.d1 = 0.5
        print (self.tree.size)
