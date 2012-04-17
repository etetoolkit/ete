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

from PyQt4    import QtCore
from PyQt4    import QtGui
from ete_dev.treeview  import faces
from re       import sub

try:
    from PyQt4 import QtOpenGL
    #USE_GL = True
    USE_GL = False # Temporarily disabled
except ImportError:
    USE_GL = False

#__all__ = ["show_tree", "render_tree", "TreeImageProperties"]

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

def colorize_rst(vals, winner, classes,col=None):
    '''
    Colorize function, that take in argument a list of values
    corresponding to a list of classes and returns a list of
    colors to paint histogram.
    '''
    col = {'NS' : 'grey',
           'RX' : 'green',
           'RX+': 'green',
           'CN' : 'cyan',
           'CN+': 'blue',
           'PS' : 'orange',
           'PS+': 'red'} if col==None else col
    colors = []
    for i in range (0, len (vals)):
        class1 = classes[i] #int(sub('\/.*', '', sub('\(', '', classes[i])))
        class2 = max (classes)# int(sub('.*\/', '', sub('\)', '', classes[i])))
        pval = float (vals[i])
        if pval < 0.95:
            colors.append(col['NS'])
        elif (class1 != class2 and class1 != 1) \
                 and (winner == 'M2' or winner == 'M8' or winner == 'SLR'):
            if pval < 0.99:
                colors.append(col['RX'])
            else:
                colors.append(col['RX+'])
        elif class1 == 1:
            if pval < 0.99:
                colors.append(col['CN'])
            else:
                colors.append(col['CN+'])
        elif class1 == class2 and (winner == 'M2' or winner == 'M8'):
            if pval < 0.99:
                colors.append(col['PS'])
            else:
                colors.append(col['PS+'])
        elif class1 == class2:
            if pval < 0.99:
                colors.append(col['RX'])
            else:
                colors.append(col['RX+'])
        else:
            colors.append(col['NS'])
    return colors

class HistFace (faces.Face):
    """
    Creates a Histogram object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length.
             default -> ['grey']* len (values)
    header:  title of the histogram
    lines:   represents tha value you want to represent as dashed
             lines, the first if this value will be taken as mean.
             Hist wan't be higher than twice this mean. Values of
             lines will appear in the Y axe
    col_lines: color of lines (and corresponding values).
    fsize:   relative to fsize of the sequence drawn.
             Both by default = 10
    height:  of the histogram default 120


    Others
    ------
    self.aligned values of False won't align histogram, if you set
    it to True.

    """

    def __init__(self, values, errors, colors=[], header='', \
                 fsize=11, height = 100, lines=[0.0], \
                 col_lines = ['black'], extras=[''], col_width=10):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = lines[0]
        if lines == [0]:
            self.max = max (values)
        else:
            self.max = lines[0]*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        self.colors = colors
        self.fsize  = int ((float (fsize)))
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height+25
        self.header = header
        self.lines  = lines
        self.col_lines = col_lines
        self.col_width = col_width

    def update_pixmap(self):
        '''
        to refresh?
        '''
        header_font_size = 8
        # Calculates  header's size
        header_font = QtGui.QFont("Arial", header_font_size) \
                      # could this be modified by the user?
        # Calculates size of main plot
        fm = QtGui.QFontMetrics(self.font)
        height = self.height
        width = self.col_width * len(self.values)
        
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        x = 0 #(-1 * self._x_offset) 
        y = height - fm.underlinePos()*2

        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            customPen.setStyle(QtCore.Qt.DashLine)
            p.setPen(customPen)
            line = line* self.mean/self.meanVal
            p.drawLine(x, y-line, x+width, y-line)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep

        p.setFont(header_font)
        p.setPen(QtGui.QColor("black"))
        p.drawText(x, y-height+12, self.header)
        p.drawText(x+width+2, y+2, "0")
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            p.setPen(customPen)
            p.drawText(x+width+2, \
                       y-line* self.mean/self.meanVal+2, str(line))
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        for i in range (0, len (self.values)):
            val = self.values[i]
            col = self.colors[i]
            posX += sep
            customPen  = QtGui.QPen (QtGui.QColor (col), 1)
            p.setPen(customPen)
            if abs(val) <= (self.height-25):
                p.drawLine(posX, y, posX, y-val)
                p.drawLine(posX+4, y, posX+4, y-val)
                p.drawLine(posX+4, y-val, posX, y-val)
            else:
                p.drawLine(posX+1, y, posX+1, y-(self.height-25))
                p.drawLine(posX+4, y, posX+4, y-(self.height-25))
                p.drawLine(posX+1, y-(self.height-15), \
                           posX+1, y-(self.height-20))
                p.drawLine(posX+4, y-(self.height-15), \
                           posX+4, y-(self.height-20))
                p.drawLine(posX+4, y-(self.height-15), \
                           posX+1, y-(self.height-15))


class LineFaceBG (faces.Face):
    """
    DEPRECATED!!!
    """
    def __init__(self, values, errors, colors=['white'], header='', \
                 fsize=11, height = 100, lines=[0.0], \
                 col_lines = ['black'], extras=[''], col_width=10):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = lines[0]
        if lines == [0]:
            self.max = max (values)
        else:
            self.max = lines[0]*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        if colors == ['white']:
            colors = colors*len(values)
        self.colors = colors
        self.fsize  = int ((float (fsize)))
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height+25
        self.header = header
        self.lines  = lines
        self.col_lines = col_lines
        self.col_width = col_width

    def update_pixmap(self):
        '''
        to refresh?
        '''
        header_font_size = 8
        # Calculates  header's size
        header_font = QtGui.QFont("Arial", header_font_size) \
                      # could this be modified by the user?
        # Calculates size of main plot
        fm = QtGui.QFontMetrics(self.font)
        height = self.height
        width = self.col_width * len(self.values)
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        x = 0 #(-1 * self._x_offset) 
        y = height - fm.underlinePos()*2
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep
        p.setFont(header_font)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        prev = y-self.values[0]
        for i in range (0, len (self.values)):
            val = self.values[i]
            bgcol = self.colors[i]
            posX += sep
            customPen  = QtGui.QPen (QtGui.QColor (bgcol), 1)
            p.setBrush(QtGui.QColor(bgcol))
            p.setPen(customPen)
            p.drawRect(posX, y-(self.height-25), 4+self.fsize/2, \
                       (self.height-25))
            customPen  = QtGui.QPen (QtGui.QColor ("black"), 1.2)
            p.setPen(customPen)
            if abs(val) <= (self.height-25):
                p.drawLine(posX+2+self.fsize/4, y-val, \
                           posX-sep+2+self.fsize/4, prev)
                prev = y-val
            else:
                p.drawLine(posX+2+self.fsize/4, y-(self.height-25), \
                           posX-sep+2+self.fsize/4, prev)
                prev = y-(self.height-25)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            customPen.setStyle(QtCore.Qt.DashLine)
            p.setPen(customPen)
            line = line* self.mean/self.meanVal
            p.drawLine(x, y-line, x+width, y-line)
        p.setPen(QtGui.QColor("black"))
        p.drawText(x, y-height+12, self.header)
        p.drawText(x+width+2, y+2, "0")
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            p.setPen(customPen)
            p.drawText(x+width+2, \
                       y-line* self.mean/self.meanVal+2, str(line))


class ErrorLineFace (faces.Face):
    """
    Creates a Histogram object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length.
             default -> ['grey']* len (values)
    header:  title of the histogram
    lines:   represents tha value you want to represent as dashed
             lines, the first if this value will be taken as mean.
             Hist wan't be higher than twice this mean. Values of
             lines will appear in the Y axe
    col_lines: color of lines (and corresponding values).
    fsize:   relative to fsize of the sequence drawn.
             Both by default = 10
    height:  of the histogram default 120


    Others
    ------
    self.aligned values of False won't align histogram, if you set
    it to True.

    """

    def __init__(self, values, errors, colors=['white'], header='', \
                 fsize=11, height = 100, lines=[0.0], \
                 col_lines = ['black'],num=True, extras=[''], col_width=10):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = lines[0]
        if lines == [0]:
            self.max = max (values)
        else:
            self.max = lines[0]*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        self.errors = map (lambda x: float('0'+str (x))/self.max*height, errors)
        if colors == ['white']:
            colors = colors*len(values)
        self.colors = colors
        self.fsize  = int ((float (fsize)))
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height+25
        self.header = header
        self.lines  = lines
        self.col_lines = col_lines
        self.num = num
        if len (extras) == len (values):
            self.extras = extras
        else:
            self.extras = ['']
        self.col_width = col_width

    def update_pixmap(self):
        '''
        to refresh?
        '''
        header_font_size = 8
        # Calculates  header's size
        header_font = QtGui.QFont("Arial", header_font_size) \
                      # could this be modified by the user?
        # Calculates size of main plot
        fm = QtGui.QFontMetrics(self.font)
        if self.extras != ['']:
            self.height += 10
        height = self.height
        width = self.col_width * len(self.values)
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        x = 0 # (-1 * self._x_offset)
        y = height - fm.underlinePos()*2
        if self.num:
            y -= 8
            height -= 8
        if self.extras != ['']:
            self.height -= 10
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep
        p.setFont(header_font)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        prev = y-self.values[0]
        for i in range (0, len (self.values)):
            val = self.values[i]
            err = self.errors[i]
            bgcol = self.colors[i]
            posX += sep
            customPen  = QtGui.QPen (QtGui.QColor (bgcol), 1)
            p.setBrush(QtGui.QColor(bgcol))
            p.setPen(customPen)
            p.drawRect(posX, y-(self.height-25), 4+self.fsize/2, \
                       (self.height-25))
            customPen  = QtGui.QPen (QtGui.QColor ("red"), 1.2)
            p.setPen(customPen)
            if abs(val) <= (self.height-25):
                p.drawLine(posX+self.fsize/4, y-val, \
                           posX-sep+4+self.fsize/4, prev)
                prev = y-val
            else:
                p.drawLine(posX+self.fsize/4, y-(self.height-25), \
                           posX-sep+4+self.fsize/4, prev)
                prev = y-(self.height-25)
            customPen  = QtGui.QPen (QtGui.QColor ("grey" if bgcol == "white" \
                                                   else "white"), 1.2)
            p.setPen(customPen)
            if abs(val) <= (self.height-25):
                if (abs(val+err)) > (self.height-25):
                    p.drawRect(posX+1+self.fsize/4, y-val, 2, \
                               -((self.height-25)-val))
                else:
                    p.drawRect(posX+1+self.fsize/4, y-val, 2, -err)
                if (abs(val-err)) > (self.height-25):
                    p.drawRect(posX+1+self.fsize/4, y-val, 2, \
                               ((self.height-25)-val))
                else:
                    p.drawRect(posX+1+self.fsize/4, y-val, 2, \
                               err if err<val else val)
            elif (val-err)<(self.height-25):
                p.drawRect(posX+1+self.fsize/4, y-(self.height-25), 2, \
                           (self.height-25)-(val-(err if err<val else val)))
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            customPen.setStyle(QtCore.Qt.DashLine)
            p.setPen(customPen)
            line = line* self.mean/self.meanVal
            p.drawLine(x, y-line, x+width, y-line)
        p.setPen(QtGui.QColor("black"))
        p.drawText(x, y-height+12, self.header)
        p.setFont(QtGui.QFont("Arial", 7))
        p.drawText(x+width+2, y+2, "0")
        if self.extras != ['']:
            posX = x - sep
            for i in range (0, len (self.values)):
                posX += sep
                p.drawText(1+posX-(len(self.extras[i])-1), 20,\
                           str(self.extras[i]))
        if self.num:
            posX = x - sep
            p.drawLine(x+4, y+16, x+4, y+14)
            p.drawText(x+1, y+25, str(1))
            for i in range (0, len (self.values)-1):
                posX += sep
                if (i+1)%5 == 0:
                    p.drawText(posX, y+25, '%2s' % (str(i+1)))
                    p.drawLine(posX+4, y+16, posX+4, y+14)
            p.drawLine(x+width-4, y+16, x+width-4, y+14)
            p.drawText(x+width-1, y+25, str(i+2))
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            p.setPen(customPen)
            p.drawText(x+width+2, \
                       y-line* self.mean/self.meanVal+2, str(line))



class ErrorLineProtamineFace (faces.Face):
    """
    Creates a Histogram object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length.
             default -> ['grey']* len (values)
    header:  title of the histogram
    lines:   represents tha value you want to represent as dashed
             lines, the first if this value will be taken as mean.
             Hist wan't be higher than twice this mean. Values of
             lines will appear in the Y axe
    col_lines: color of lines (and corresponding values).
    fsize:   relative to fsize of the sequence drawn.
             Both by default = 10
    height:  of the histogram default 120

    Others
    ------
    self.aligned values of False won't align histogram, if you set
    it to True.

    """
    def __init__(self, values, errors, colors=['white'], header='', \
                 fsize=11, height = 100, lines=[0.0], \
                 col_lines = ['black'],num=True, extras=[''], col_width=10):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = lines[0]
        if lines == [0]:
            self.max = max (values)
        else:
            self.max = lines[0]*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        if len (errors) == 0:
            errors = [0]*len (values)
        if type (errors[0]) is not list :
            self.errorsP = errors[:]
            self.errorsN = errors[:]
        else:
            self.errorsN, self.errorsP = zip (*errors)
        self.errorsP = map (lambda x: float('0'+str (x))/self.max*height, self.errorsP)
        self.errorsN = map (lambda x: float('0'+str (x))/self.max*height, self.errorsN)
        if colors == ['white']:
            colors = colors*len(values)
        self.colors = colors
        self.font   = QtGui.QFont("Courier", fsize)
        self.height = height+25
        self.header = header
        self.lines  = lines
        self.col_lines = col_lines
        self.num = num
        if len (extras) == len (values):
            self.extras = extras
        else:
            self.extras = ['']
        self._QtItem_ = QtGui.QGraphicsRectItem
        self.col_width = col_width

    def update_pixmap(self):
        '''
        to refresh?
        '''
        header_font_size = 8
        # Calculates  header's size
        header_font = QtGui.QFont("Arial", header_font_size) \
                      # could this be modified by the user?
        # Calculates size of main plot
        fm = QtGui.QFontMetrics(self.font)
        height = self.height
        width = self.col_width * len(self.values)
        
        # x and y start
        x = 0 #(-1 * self._x_offset)
        y = height - fm.underlinePos()*2
        
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        if self.num:
            y      -= 25 ## 8
            height -= 40 ## 8
        customPen = QtGui.QPen (QtGui.QColor("red"), 1)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)        
        p.setPen(customPen)
        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep
        p.setFont(header_font)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen (customPen)
        prev = y-self.values[0]
        ymax = height+15
        for i in range (0, len (self.values)):
            val = self.values[i]
            try:
                errP = self.errorsP[i]
                errN = self.errorsN[i]
            except IndexError:
                errP = 0
                errN = 0
            bgcol = "white"#self.colors[i]
            #bgcol = self.colors[i]
            posX += sep
            customPen  = QtGui.QPen (QtGui.QColor (bgcol), 1)
            p.setBrush (QtGui.QColor(bgcol))
            p.setPen (customPen)
            p.drawRect (posX, y-(ymax), 4+sep/2, (ymax))
            customPen  = QtGui.QPen (QtGui.QColor ("black"), 1.2)
            p.setPen(customPen)
            if abs(val) <= (ymax):
                p.drawLine(posX+sep/4, y-val, \
                           posX-sep+4+sep/4, prev)
                prev = y-val
            else:
                p.drawLine(posX+sep/4, y-(ymax), \
                           posX-sep+4+sep/4, prev)
                prev = y-(ymax)

            customPen  = QtGui.QPen (QtGui.QColor ("grey" if bgcol == "white" \
                                                   else "white"), 1.2)
            p.setPen(customPen)

            # horizontal connector
            if abs(val) <= (ymax):
                # if positive error bar is out of bound
                p.drawLine(posX+2+sep/4-2, y-val, #2, \
                           posX+2+sep/4+2, y-val)
            # error bar
            errP = errP if val+errP <= y else (y-val)
            errN = errN if (val-errN) >= 0 else val
            p.drawLine(posX+2+sep/4, y-(val+errP),
                       posX+2+sep/4, y-(val-errN))

        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            customPen.setStyle(QtCore.Qt.DashLine)
            p.setPen(customPen)
            line = line * self.mean/self.meanVal
            p.drawLine(x, y-line, x+width, y-line)
        p.setPen (QtGui.QColor("black"))
        p.drawText (x, y-height, self.header)
        p.setFont (QtGui.QFont("Arial", 7))
        p.drawText (x+width+2, y+2, "0")

        if self.extras != ['']:
            posX = x - sep
            for i in range (0, len (self.values)):
                cr = self.colors[i] if self.colors[i]!= 'white' else ''
                posX += sep
                if cr.endswith('.'):
                    p.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
                    p.drawText(1+posX-(len(self.extras[i])-1), y+10,\
                               str(self.extras[i]))
                    p.setFont(QtGui.QFont("Arial", 7))
                else:
                    p.drawText(1+posX-(len(self.extras[i])-1), y+10,\
                               str(self.extras[i]))
                if len (str(self.extras[i])) == 1:
                    p.drawLine(posX+2, y+11, posX+4, y+11)
                if len (str(self.extras[i]))>1:
                    p.drawLine(posX, y+11, posX+2, y+11)
                    p.drawLine(posX+4, y+11, posX+6, y+11)
        p.drawLine(x+4, y+14, x+width-4, y+14)
        if self.num:
            posX = x - sep
            p.drawLine(x+4, y+16, x+4, y+14)
            p.drawText(x+1, y+25, str(1))
            for i in range (0, len (self.values)-1):
                posX += sep
                if (i+1)%5 == 0:
                    p.drawText(posX, y+25, '%2s' % (str(i+1)))
                    p.drawLine(posX+4, y+16, posX+4, y+14)
            p.drawLine(x+width-4, y+16, x+width-4, y+14)
            p.drawText(x+width-1, y+25, str(i+2))
        for line, col in zip (self.lines, self.col_lines):
            customPen = QtGui.QPen(QtGui.QColor(col), 1)
            p.setPen(customPen)
            p.drawText(x+width+2, \
                       y-line* self.mean/self.meanVal+2, str(line))


