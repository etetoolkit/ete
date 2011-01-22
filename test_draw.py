import sys

from ete_dev import Tree
from ete_dev.treeview.main import TreeImage

def ly(node):
    node.img_style["size"] = 10
    node.img_style["shape"] = "square"

I = TreeImage()
I.mode = "circular"
I.scale = 40

n = int(sys.argv[1])

t = Tree()
t.populate(n)
t.show(ly, img_properties=I)
