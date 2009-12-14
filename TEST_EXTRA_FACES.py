# TO RUN THIS SCRIPT:
# Create a symbolic link "ete_dev" pointing to the "ete2" dir.
# Then, execute (within this directory):
# PYTHONPATH=`pwd` python TEST_EXTRA_FACES.py
#

from ete_dev import Tree, faces, layouts
from ete_dev.treeview import drawer
from HistFace import HistFace, CustomProfileFace
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import numpy
import re

seq_fsize = 10



def ly(node):
    layouts.basic(node)
    if node == n:
        faces.add_face_to_node(SEQ,node, 1, aligned=True)

SEQ = faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa")

t =Tree()
t.populate(10)
A1=faces.SequenceFace("HOLAFRANCOISaaaaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa")
A2=faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa", "aa")
N1=faces.SequenceFace("aaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiippppppNNNNNNNNaN", "aa")
N2=faces.SequenceFace("aaaaaaaaNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNaN", "aa")

string = 'aaaaaaaaaaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaa'

values = len (re.sub('[^a]','',string))*[1] + len (re.sub('[^i]','',string))*[0.5]+len (re.sub('[^p]','',string))*[2.2]

AH1 = HistFace(values=values,header='bonjour coucou',mean=1)
profile = numpy.array(values)
deviation = numpy.zeros(len(values))
# Hay que buscar una mejor manera de calcular el ancho
w= 8*len(SEQ.seq)-42 # 42 es el offset que usa el face para poner la escala 

AH2 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="cbars")
AH2.aligned = True

AH3 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="bars")
AH3.aligned = True

AH4 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="lines")
AH4.aligned = True


AH1.aligned = True
A1.aligned=True
A2.aligned=True
N1.aligned=False
N2.aligned=False
n = t.get_leaves()[-1]

flist= [A1,A2,N1,N2]
# Puedes pasar la lista de faces arriba o debajo del arbol cuando
# llamas a show().
t.show(ly, down_faces=[AH2,AH3,AH4,AH1])
#t.render('lolo.pdf',ly, down_faces=[AH1], up_faces=[AH1])
