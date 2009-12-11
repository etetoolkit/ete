# TO RUN THIS SCRIPT:
# Create a symbolic link "ete_dev" pointing to the "ete2" dir.
# Then, execute (within this directory):
# PYTHONPATH=`pwd` python TEST_EXTRA_FACES.py
#

from ete_dev import Tree, faces, layouts
from ete_dev.treeview import drawer

def ly(node):
    layouts.basic(node)
    if node == n:
        faces.add_face_to_node(faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa"),node, 1, aligned=True)

t =Tree()
t.populate(10)
A1=faces.SequenceFace("HOLAFRANCOISaaaaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa")
A2=faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa")
N1=faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiippppppNNNNNNNNaN", "aa")
N2=faces.SequenceFace("aaaaaaaaNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNaN", "aa")

A1.aligned=True
A2.aligned=True

N1.aligned=False
N2.aligned=False
n = t.get_leaves()[5]

flist= [A1,A2,N1,N2]
# Puedes pasar la lista de faces arriba o debajo del arbol cuando
# llamas a show().
t.show(ly, up_faces=flist, down_faces=flist)
