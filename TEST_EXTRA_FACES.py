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
from random import random as rdm
seq_fsize = 10



def ly(node):
    layouts.basic(node)
    if node == n:
        faces.add_face_to_node(SEQ,node, 1, aligned=True)

SEQ = faces.SequenceFace("aaaaaaaaaHOHOHOHOHOaaaaaaaaaaaaaaaiiiiiiiipppppppppppppaaaTTFFGGTTTXXXX", "aa")

t =Tree()
t.populate(10)

values = []

for a in range (0,len(SEQ.seq)): values.append(rdm()*3)

colors = map(lambda x: (x>1.8)*'red'+(x<0.5)*'blue',values)


AH1 = HistFace(values=values,mean=1.35,colors=colors,header='yo chaud lapin')

profile = numpy.array(values)
deviation = numpy.zeros(len(values))

# Hay que buscar una mejor manera de calcular el ancho
# esto no funciona... le pasa como a mi antes, haz 2 t.show() seguidos,
# y te va a cambiar el espaciamiento de la secuencis... no se porque pero es asi....
w= 8*len(SEQ.seq)-42 + 10 # 42 es el offset que usa el face para poner la escala 

AH2 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="cbars")
AH2.aligned = True

AH3 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="bars")
AH3.aligned = True

AH4 = CustomProfileFace(profile, deviation, 3, 0, numpy.mean(profile), width = w,style="lines")
AH4.aligned = True

AH1.aligned = True

n = t.get_leaves()[-1]

t.show(ly, down_faces=[AH2,AH3,AH4],up_faces=[AH1])




