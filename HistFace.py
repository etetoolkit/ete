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

import numpy
from PyQt4  import QtCore
from PyQt4  import QtGui
from ete_dev import faces


try:
    from PyQt4 import QtOpenGL
    #USE_GL = True
    USE_GL = False # Temporarily disabled
except ImportError:
    USE_GL = False

from ete_dev import Tree, ClusterTree

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

class HistFace (faces.Face):
    """
    Creates a Histogram object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length.
             default -> ['grey']* len (values)
    header:  title of the histogram
    mean:    represents tha value you want to represent as mean,
             hist wan't be higher than twice this value. This value
             will appear in the Y axe
    fsize:   relative to fsize of the sequence drawn.
             Both by default = 10
    height:  of the histogram default 120


    Others
    ------
    self.aligned values of False won't align histogram, if you set
    it to True.

    """

    def __init__(self, values, colors=[], header='', mean=0, \
                 fsize=11, height = 100):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = mean
        if mean == 0: self.max = max (values)
        else:         self.max = mean*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        self.colors = colors
        self.fsize  = int ((float (fsize)))
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height+25
        self.header = header

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
        width = fm.size(QtCore.Qt.AlignTop, 'A'*(len (self.values))).width()
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        x = (-1 * self._x_offset) 
        y = height - fm.underlinePos()*2

        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        customPen.setStyle(QtCore.Qt.DashLine)
        p.setPen(customPen)
        p.drawLine(x, y-self.mean, x+width, y-self.mean)

        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep

        p.setFont(header_font)
        p.setPen(QtGui.QColor("black"))
        p.drawText(x, y-height+12, self.header)
        p.drawText(x+width+2, y+2, "0")
        p.drawText(x+width+2, y-self.mean+2, str(self.meanVal))

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


class HeatFace (faces.Face):
    """
    Creates a Heatmap object, usually related to a sequence object

    Argument description
    --------------------
    values:  list of vals for each bar of histogram
    color:   color of each bar, must be of same length.
             default -> ['grey']* len (values)
    header:  title of the histogram
    mean:    represents tha value you want to represent as mean,
             hist wan't be higher than twice this value. This value
             will appear in the Y axe
    fsize:   relative to fsize of the sequence drawn.
             Both by default = 10
    height:  of the histogram default 120


    Others
    ------
    self.aligned values of False won't align histogram, if you set
    it to True.
    """

    def __init__(self, values, colors=[], header='', mean=0, \
                 fsize=11, height = 100):
        faces.Face.__init__(self)
        if colors == []: colors = ['grey']*len (values)
        if len (colors) != len (values):
            exit('ERROR: value and color arrays differ in length!!!\n')
        self.mean = (height)/2
        self.meanVal = mean
        if mean == 0: self.max = max (values)
        else:         self.max = mean*2
        self.values = map (lambda x: float(x)/self.max*height, values)
        self.colors = colors
        self.fsize  = int ((float (fsize)))
        self.font   = QtGui.QFont("Courier", self.fsize)
        self.height = height+25
        self.header = header

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
        width = fm.size(QtCore.Qt.AlignTop, 'A'*(len (self.values))).width()
        self.pixmap = QtGui.QPixmap(width+20, height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        # Set the start x and y of the main plot (taking into account
        # header and scale text)
        x = (-1 * self._x_offset) 
        y = height - fm.underlinePos()*2

        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        p.setPen(customPen)
        p.drawLine(x, y, x + width, y)
        customPen.setStyle(QtCore.Qt.DashLine)
        p.setPen(customPen)
        p.drawLine(x, y-self.mean, x+width, y-self.mean)

        customPen.setStyle(QtCore.Qt.SolidLine)
        p.setPen(customPen)
        sep = float (width) / len(self.values)
        posX = x - sep

        p.setFont(header_font)
        p.setPen(QtGui.QColor("black"))
        p.drawText(x, y-height+12, self.header)
        p.drawText(x+width+2, y+2, "0")
        p.drawText(x+width+2, y-self.mean+2, str(self.meanVal))

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









class CustomProfileFace (faces.Face):
    """ Creates a new vector profile face object.

    Arguments description
    ---------------------

    max_v:    maximum value used to build the build the plot scale.
    max_v:    manimum value used to build the build the plot scale.
    center_v: Center value used to scale plot and heat map.
    width:    Plot width in pixels. (defaulf=200)
    height:   Plot width in pixels. (defaulf=40)
    style:    Plot style: "lines", "bars", "cbars" or "heatmap". (default="lines")
    """
    def __init__(self, profile, deviation, max_v, min_v, center_v, width=200, \
                 height=40, style="lines", colorscheme=2):
        faces.Face.__init__(self)

        self.width  = width
        self.height = height
        self.max_value = max_v
        self.min_value = min_v
        self.center_v  = center_v
        self.xmargin = 1
        self.ymargin = 1
        self.style = style
        self.colorscheme = colorscheme
        self.profile_vector = profile
        self.deviation_vector = deviation
        
    def update_pixmap(self):
        '''
        to refresh??
        '''
        if self.style=="lines":
            self.draw_line_profile()
        elif self.style=="bars":
            self.draw_bar_profile()
        elif self.style=="cbars":
            self.draw_centered_bar_profile()

    def get_color_gradient(self):
        colors = []
        if self.colorscheme == 0:
            # Blue and Green
            for a in xrange(100,0,-1):
                color=QtGui.QColor()
                color.setRgb( 200-2*a,255,200-2*a )
                colors.append(color)
            for a in xrange(0,100):
                color=QtGui.QColor()
                color.setRgb( 200-2*a,200-2*a,255 )
                colors.append(color)
#            color=QtGui.QColor()
#            color.setRgb( 0,255,255 )
#            colors.append(color)

        elif self.colorscheme == 1:
            for a in xrange(100,0,-1):
                color=QtGui.QColor()
                color.setRgb( 200-2*a,255,200-2*a )
                colors.append(color)

            for a in xrange(0,100):
                color=QtGui.QColor()
                color.setRgb( 255,200-2*a,200-2*a )
                colors.append(color)
#            color=QtGui.QColor()
#            color.setRgb(255,255,0 )
#            colors.append(color)

        else:
            # Blue and Red
            for a in xrange(100,0,-1):
                color=QtGui.QColor()
                color.setRgb( 200-2*a,200-2*a,255 )
                colors.append(color)
            for a in xrange(0,100):
                color=QtGui.QColor()
                color.setRgb( 255,200-2*a,200-2*a )
                colors.append(color)
#            color=QtGui.QColor()
#            color.setRgb( 255,0,255 )
#            colors.append(color)
        colors.append(QtGui.QColor("white"))

        return colors

    def draw_bar_profile(self):
        # Calculate vector
        mean_vector = self.profile_vector
        deviation_vector = self.deviation_vector
        # If no vector, skip
        if mean_vector is None:
            return

        colors = self.get_color_gradient()

        vlength = len(mean_vector)
        # pixels per array position
        profile_width = self.width - self.xmargin*2 - 40
        profile_height= self.height - self.ymargin*2

        x_alpha = float( profile_width / (len(mean_vector)) )
        y_alpha = float ( profile_height / (self.max_value-self.min_value) )

        # Creates a pixmap
        self.pixmap = QtGui.QPixmap(self.width,self.height)
        self.pixmap.fill(QtGui.QColor("white"))
        p = QtGui.QPainter(self.pixmap)

        x2 = self.xmargin
        y  = self.ymargin

        # Mean and quartiles y positions
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4

        # Draw axis and scale
        p.setPen(QtGui.QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QtGui.QFont("Verdana",8))
        p.drawText(self.xmargin+profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(self.xmargin+profile_width,y+profile_height,"%0.3f" %self.min_value)

        dashedPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor("#ddd")), 0)
        dashedPen.setStyle(QtCore.Qt.DashLine)

        # Draw hz grid
        p.setPen(dashedPen)
        p.drawLine(x2+1, mean_line_y, profile_width-2, mean_line_y )
        p.drawLine(x2+1, line2_y, profile_width-2, line2_y )
        p.drawLine(x2+1, line3_y, profile_width-2, line3_y )


        # Draw bars
        for pos in xrange(vlength):
            # first and second X pixel positions
            x1 = x2
            x2 = x1 + x_alpha

            dev1 =  self.fit_to_scale( deviation_vector[pos]   )
            mean1 = self.fit_to_scale( mean_vector[pos]        )

            # If nan value, skip
            if not numpy.isfinite(mean1):
                continue

            # Set heatmap color
            if mean1>self.center_v:
                color_index = int(abs(((self.center_v-mean1)*100)/(self.max_value-self.center_v)))
                customColor = colors[100+color_index]
            elif mean1<self.center_v:
                color_index = int(abs(((self.center_v-mean1)*100)/(self.min_value-self.center_v)))
                customColor = colors[100-color_index]
            else:
                customColor = colors[0]

            # mean bar high
            mean_y1     = int ( (mean1 - self.min_value) * y_alpha)

            # Draw bar border
            p.setPen(QtGui.QColor("black"))
            #p.drawRect(x1+2,mean_y1, x_alpha-3, profile_height-mean_y1+1)
            # Fill bar with custom color
            p.fillRect(x1+3,profile_height-mean_y1, x_alpha-4, mean_y1-1, QtGui.QBrush(customColor))

            # Draw error bars
            if dev1 != 0:
                dev_up_y1   = int((mean1+dev1 - self.min_value) * y_alpha)
                dev_down_y1 = int((mean1-dev1 - self.min_value) * y_alpha)
                p.drawLine(x1+x_alpha/2, profile_height-dev_up_y1 ,x1+x_alpha/2, profile_height-dev_down_y1 )
                p.drawLine(x1-1+x_alpha/2,  profile_height-dev_up_y1, x1+1+x_alpha/2, profile_height-dev_up_y1 )
                p.drawLine(x1-1+x_alpha/2,  profile_height-dev_down_y1, x1+1+x_alpha/2, profile_height-dev_down_y1 )

    def draw_centered_bar_profile(self):
        # Calculate vector
        mean_vector  = self.profile_vector
        deviation_vector = self.deviation_vector
        # If no vector, skip
        if mean_vector is None:
            return

        colors = self.get_color_gradient()

        vlength = len(mean_vector)
        # pixels per array position
        profile_width = self.width - self.xmargin*2 - 40
        profile_height= self.height - self.ymargin*2

        x_alpha = float( profile_width / (len(mean_vector)) )
        y_alpha_up = float ( (profile_height/2) / (self.max_value-self.center_v) )
        y_alpha_down = float ( (profile_height/2) / (self.min_value-self.center_v) )

        # Creates a pixmap
        self.pixmap = QtGui.QPixmap(self.width,self.height)
        self.pixmap.fill(QtGui.QColor("white"))
        p = QtGui.QPainter(self.pixmap)

        x2 = self.xmargin
        y  = self.ymargin

        # Mean and quartiles y positions
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4

        # Draw axis and scale
        p.setPen(QtGui.QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QtGui.QFont("Verdana",8))
        p.drawText(self.xmargin+profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(self.xmargin+profile_width,y+profile_height,"%0.3f" %self.min_value)
        p.drawText(self.xmargin+profile_width,mean_line_y,"%0.3f" %self.center_v)

        dashedPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor("#ddd")), 0)
        dashedPen.setStyle(QtCore.Qt.DashLine)

        # Draw hz grid
        p.setPen(dashedPen)
        p.drawLine(x2+1, mean_line_y, profile_width-2, mean_line_y )
        p.drawLine(x2+1, line2_y, profile_width-2, line2_y )
        p.drawLine(x2+1, line3_y, profile_width-2, line3_y )


        # Draw bars
        for pos in xrange(vlength):
            # first and second X pixel positions
            x1 = x2
            x2 = x1 + x_alpha

            dev1 =  self.fit_to_scale( deviation_vector[pos]   )
            mean1 = self.fit_to_scale( mean_vector[pos]        )

            # If nan value, skip
            if not numpy.isfinite(mean1):
                continue

            # Set heatmap color
            if mean1>self.center_v:
                color_index = int(abs(((self.center_v-mean1)*100)/(self.max_value-self.center_v)))
                customColor = colors[100+color_index]
            elif mean1<self.center_v:
                color_index = int(abs(((self.center_v-mean1)*100)/(self.min_value-self.center_v)))
                customColor = colors[100-color_index]
            else:
                customColor = colors[0]

            # mean bar high
            if mean1<self.center_v:
                mean_y1 = int(abs((mean1 - self.center_v) * y_alpha_down))
            else:
                mean_y1 = int(abs((mean1 - self.center_v) * y_alpha_up))

            # Draw bar border
            p.setPen(QtGui.QColor("black"))
            #p.drawRect(x1+2,mean_y1, x_alpha-3, profile_height-mean_y1+1)
            # Fill bar with custom color
            if mean1<self.center_v:
                p.fillRect(x1+3, mean_line_y, x_alpha-4, mean_y1, QtGui.QBrush(customColor))
            else:
                p.fillRect(x1+3, mean_line_y-mean_y1, x_alpha-4, mean_y1+1, QtGui.QBrush(customColor))

            # Draw error bars
            if dev1 != 0:
                if mean1<self.center_v:
                    dev_up_y1   = int((mean1+dev1 - self.center_v) * y_alpha_down)
                    dev_down_y1 = int((mean1-dev1 - self.center_v) * y_alpha_down)
                    p.drawLine(x1+x_alpha/2, mean_line_y+dev_up_y1 ,x1+x_alpha/2, mean_line_y+dev_down_y1 )
                    p.drawLine(x1-1+x_alpha/2, mean_line_y+dev_up_y1 ,x1+1+x_alpha/2, mean_line_y+dev_up_y1 )
                    p.drawLine(x1-1+x_alpha/2, mean_line_y+dev_down_y1 ,x1+1+x_alpha/2, mean_line_y+dev_down_y1 )
                else:
                    dev_up_y1   = int((mean1+dev1 - self.center_v) * y_alpha_up)
                    dev_down_y1 = int((mean1-dev1 - self.center_v) * y_alpha_up)
                    p.drawLine(x1+x_alpha/2, mean_line_y-dev_up_y1 ,x1+x_alpha/2, mean_line_y-dev_down_y1 )
                    p.drawLine(x1-1+x_alpha/2, mean_line_y-dev_up_y1 ,x1+1+x_alpha/2, mean_line_y-dev_up_y1 )
                    p.drawLine(x1-1+x_alpha/2, mean_line_y-dev_down_y1 ,x1+1+x_alpha/2, mean_line_y-dev_down_y1 )

    def draw_line_profile(self):
        # Calculate vector
        mean_vector = self.profile_vector
        deviation_vector = self.deviation_vector
        if mean_vector is None:
            return

        vlength = len(mean_vector)
        # pixels per array position
        profile_width = self.width - self.xmargin*2 - 40
        profile_height= self.height - self.ymargin*2


        x_alpha = float( profile_width / (len(mean_vector)-1) )
        y_alpha = float ( profile_height / (self.max_value-self.min_value) )

        # Creates a pixmap
        self.pixmap = QtGui.QPixmap(self.width,self.height)
        self.pixmap.fill(QtGui.QColor("white"))
        p = QtGui.QPainter(self.pixmap)

        x2 = self.xmargin
        y  = self.ymargin

        # Mean and quartiles y positions
        mean_line_y = (self.center_v - self.min_value) * y_alpha
        line2_y     = ((self.center_v+abs(self.min_value/2)) - self.min_value) * y_alpha
        line3_y     = ((self.center_v-abs(self.max_value/2)) - self.min_value) * y_alpha

        # Draw axis and scale
        p.setPen(QtGui.QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QtGui.QFont("Verdana",8))
        p.drawText(self.xmargin+profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(self.xmargin+profile_width,y+profile_height,"%0.3f" %self.min_value)
        p.drawText(self.xmargin+profile_width,mean_line_y+5,"%0.3f" %self.center_v)

        dashedPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor("#ddd")), 0)
        dashedPen.setStyle(QtCore.Qt.DashLine)

        # Draw hz grid
        p.setPen(dashedPen)
        p.drawLine(x2+1, mean_line_y, profile_width-2, mean_line_y )
        p.drawLine(x2+1, line2_y, profile_width-2, line2_y )
        p.drawLine(x2+1, line3_y, profile_width-2, line3_y )

        # Draw lines
        for pos in xrange(0,vlength-1):
            dev1 =  self.fit_to_scale( deviation_vector[pos]   )
            dev2 =  self.fit_to_scale( deviation_vector[pos+1] )
            mean1 = self.fit_to_scale( mean_vector[pos]        )
            mean2 = self.fit_to_scale( mean_vector[pos+1]      )
            # first and second X pixel positions
            x1 = x2
            x2 = x1 + x_alpha

            # Draw vt grid
            if x2 < profile_width:
                p.setPen(dashedPen)
                p.drawLine(x2, y+1, x2, profile_height-2)

            # If nan values, continue
            if not numpy.isfinite(mean1) or not numpy.isfinite(mean2):
                continue

            # First Y postions for mean
            mean_y1     = (mean1 - self.min_value) * y_alpha
            # Second Y postions for mean
            mean_y2     = (mean2 - self.min_value) * y_alpha
            # Draw blue mean line
            p.setPen(QtGui.QColor("blue"))
            p.drawLine(x1,mean_y1, x2, mean_y2)

            if dev1!= 0 and dev2!=0:
                # First Y postions for deviations
                dev_up_y1   = (mean1+dev1 - self.min_value) * y_alpha
                dev_down_y1 = (mean1-dev1 - self.min_value) * y_alpha
                # Second Y postions for deviations
                dev_up_y2   = (mean2+dev2 - self.min_value) * y_alpha
                dev_down_y2 = (mean2-dev2 - self.min_value) * y_alpha
                # Draw red deviation lines
                p.setPen(QtGui.QColor("red"))
                p.drawLine(x1,dev_up_y1, x2, dev_up_y2)
                p.setPen(QtGui.QColor("red"))
                p.drawLine(x1,dev_down_y1, x2, dev_down_y2)

    def fit_to_scale(self,v):
        if v<self.min_value:
            return float(self.min_value)
        elif v>self.max_value:
            return float(self.max_value)
        else:
            return float(v)
