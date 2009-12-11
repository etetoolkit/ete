# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.  
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE). 
# http://ete.cgenomics.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
from sys import stderr, stdout
import time
import re
import math
import random   
import types
import copy
import string 
import numpy
from PyQt4  import QtCore
from PyQt4  import QtGui 
from PyQt4.QtGui import QPrinter
from ete_dev import faces, layouts

try:
    from PyQt4 import QtOpenGL
    #USE_GL = True
    USE_GL = False # Temporarily disabled
except ImportError:
    USE_GL = False

from ete_dev import Tree, PhyloTree, ClusterTree

__all__ = ["show_tree", "render_tree", "TreeImageProperties"]

DEBUG = 0
_QApp = None

_MIN_NODE_STYLE = {
    "fgcolor": "#0030c1",
    "bgcolor": "#FFFFFF",
    "vt_line_color": "#000000",
    "hz_line_color": "#000000",
    "line_type": 0,
    "vlwidth": 1,
    "hlwidth": 1,
    "size":6,
    "shape": "sphere",
    "faces": None, 
    "draw_descendants": 1, 
    "ymargin": 0
}

class HistFace(faces.Face):
    """ Creates a Histogram object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length, default ['grey']* len (values)
    header:  title of the histogram
    mean:    represents tha value you want to represent as mean, hist wan't be higher than twice this value.
             this value will appear in the Y axe
    fsize:   relative to fsize of the sequence drawn, both by default = 10
    height:  of the histogram default 120


    Others
    ------
    self.aligned values of False won't align histogram, if you set it to True.

    """

    def __init__(self, values, colors = [], header = '', mean = 0, \
                 fsize=10, height = 120):

        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            sys.exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height-20)/2
        self.meanVal = mean
        if mean == 0: self.max = max (values)
        else:         self.max = mean*2
        self.values = map (lambda x: \
                           float (x)/self.max * (height-20),values)
        self.colors = colors
        # don't know why font size have to be readjusted compared to sequence face... don't understand :|
        self.fsize  = int ((float (fsize)/6)*8)
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height
        self.header = header

    def update_pixmap(self):
        
        fm = QtGui.QFontMetrics(self.font)
        height = self.height
        width  = fm.size(QtCore.Qt.AlignTop, 'A'*len (self.values)).width()+self.aligned
        self.pixmap = QtGui.QPixmap(width,height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        if self.aligned:
            x = 0+(self.aligned-1)
        else: x = 0
        y = height - fm.underlinePos()*2

        customPen = QtGui.QPen(QtGui.QColor("black"),1)
        p.setPen(customPen)
        p.drawLine(x,y,x+width,y)
        customPen.setStyle(QtCore.Qt.DashLine)
        p.setPen(customPen)
        p.drawLine(x,y-self.mean,x+width,y-self.mean)

        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width-(self.aligned-1)) / len(self.values)
        posX = x - sep
        p.setPen(QtGui.QColor("black"))
        p.setFont(QtGui.QFont("Arial",7))
        p.drawText(x-self.aligned+1, y-float(height)/4, self.header)
        p.drawText(x-5, y+2, "0")
        p.drawText(x-5, y-self.mean+2, str (self.meanVal))

        for i in range (0, len (self.values)):
            val = self.values[i]
            col = self.colors[i]
            posX += sep
            customPen  = QtGui.QPen(QtGui.QColor(col),1)
            p.setPen(customPen)
            if abs(val) <= (self.height-20):
                p.drawLine(posX,y,posX,y-val)
                p.drawLine(posX+6,y,posX+6,y-val)
                p.drawLine(posX+6,y-val,posX,y-val)
            else:
                p.drawLine(posX,y,posX,y-(self.height-20))
                p.drawLine(posX+6,y,posX+6,y-(self.height-20))
                p.drawLine(posX,y-(self.height-10),posX,y-(self.height-15))
                p.drawLine(posX+6,y-(self.height-10),posX+6,y-(self.height-15))
                p.drawLine(posX+6,y-(self.height-10),posX,y-(self.height-10))

            #if col =='grey':
            #    name = QtGui.QGraphicsSimpleTextItem("+")
            #    name.setText("+")
            #    name.setPos(posX,y-5)
            #    name = QtGui.QGraphicsSimpleTextItem("+")
            #    name.setPos(posX,y+1)
            #    
            #if col =='orange':
            #    name = QtGui.QGraphicsSimpleTextItem("+")
            #    name.setParentItem(self.mainItem)
            #    name.setPos(posX,y-5)
            #if col =='blue':
            #    name = QtGui.QGraphicsSimpleTextItem("-")
            #    name.setParentItem(self.mainItem)
            #    name.setPos(posX,y-5)
            #    name = QtGui.QGraphicsSimpleTextItem("-")
            #    name.setParentItem(self.mainItem)
            #    name.setPos(posX,y+1)
            #if col =='cyan':
            #    name = QtGui.QGraphicsSimpleTextItem("-")
            #    name.setParentItem(self.mainItem)
            #    name.setPos(posX,y-5)
