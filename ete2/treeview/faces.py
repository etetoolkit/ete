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
try:
    from PyQt4 import QtCore, QtGui
except:
    import QtCore, QtGui

import numpy

aafgcolors = {
'A':"#000000" ,
'R':"#000000" ,
'N':"#000000" ,
'D':"#000000" ,
'C':"#000000" ,
'Q':"#000000" ,
'E':"#000000" ,
'G':"#000000" ,
'H':"#000000" ,
'I':"#000000" ,
'L':"#000000" ,
'K':"#000000" ,
'M':"#000000" ,
'F':"#000000" ,
'P':"#000000" ,
'S':"#000000" ,
'T':"#000000" ,
'W':"#000000" ,
'Y':"#000000" ,
'V':"#000000" ,
'B':"#000000" ,
'Z':"#000000" ,
'X':"#000000",
'.':"#000000",
'-':"#000000",
}

aabgcolors = {
'A':"#C8C8C8" ,
'R':"#145AFF" ,
'N':"#00DCDC" ,
'D':"#E60A0A" ,
'C':"#E6E600" ,
'Q':"#00DCDC" ,
'E':"#E60A0A" ,
'G':"#EBEBEB" ,
'H':"#8282D2" ,
'I':"#0F820F" ,
'L':"#0F820F" ,
'K':"#145AFF" ,
'M':"#E6E600" ,
'F':"#3232AA" ,
'P':"#DC9682" ,
'S':"#FA9600" ,
'T':"#FA9600" ,
'W':"#B45AB4" ,
'Y':"#3232AA" ,
'V':"#0F820F" ,
'B':"#FF69B4" ,
'Z':"#FF69B4" ,
'X':"#BEA06E",
'.':"#FFFFFF",
'-':"#FFFFFF",
}

ntfgcolors = {
'A':'#000000',
'G':'#000000',
'I':'#000000',
'C':'#000000',
'T':'#000000',
'U':'#000000',
'.':"#000000",
'-':"#000000",
' ':"#000000"

}

ntbgcolors = {
'A':'#A0A0FF',
'G':'#FF7070',
'I':'#80FFFF',
'C':'#FF8C4B',
'T':'#A0FFA0',
'U':'#FF8080',
'.':"#FFFFFF",
'-':"#FFFFFF",
' ':"#FFFFFF"

}

__all__ = ["add_face_to_node", "Face", "TextFace", "AttrFace", "ImgFace", "ProfileFace", "ValidationFace", "SequenceFace"]

try:
    import psyco
    pysco.full()
except:
    pass

FACE_POSITIONS = set(["branch-right", "aligned", "branch-top", "branch-bottom"])

def add_face_to_node(face, node, column, aligned=False, position="branch-right"):
    """ Links a node with a given face instance.  """
    node.img_style.setdefault("_faces", {})
    if position not in FACE_POSITIONS:
        raise (ValueError, "Incorrect position") 
    if aligned:
        position = "aligned"

    node.img_style["_faces"].setdefault(position, {})
    node.img_style["_faces"][position].setdefault(int(column), []).append(face)


class Face(object):
    """ Standard definition of a face node object.

    This class is not functional and it should only be used to create
    other faces objects. By inheriting this class, you set all the
    essential attributes, however the update_pixmap() function is
    required to be reimplemented for convenience.

    """

    def __init__(self):
        self.node        = None
        self.type        = "pixmap"
        self.name        = "unknown"
        self.xmargin     = 0
        self.ymargin     = 0
        self.pixmap      = None
        # self.aligned     = False

    def _size(self):
        if self.pixmap:
            return self._width(),self._height()
        else:
            return 0, 0

    def _width(self):
        if self.pixmap:
            return self.pixmap.width() #+ self.xmargin*2
        else:
            return 0

    def _height(self):
        if self.pixmap:
            return self.pixmap.height() #+ self.ymargin*2
        else:
            return 0

    def load_pixmap_from_file(self, filename):
        self.pixmap = QtGui.QPixmap(filename)

    def update_pixmap(self):
        pass

class TextFace(Face):
    """ Creates a new text face object.

    Arguments description
    ---------------------
    text:     Text to be drawn
    ftype:    Font type, e.g. Arial, Verdana, Courier, (default="Verdana")
    fsize:    Font size, e.g. 10,12,6, (default=10)
    fgcolor:  Foreground font color in RGB name format, e.g. #FF00DD,#000000  (default="#000000")
    bgcolor:  Backgroung font color in RGB name format, e.g. #FFFFFF,#DDDDDD, (default=None)
    penwidth: Penwdith used to draw the text. (default is 0)
    """

    def __init__(self, text, ftype="Verdana", fsize=10, fgcolor="#000000", bgcolor=None, penwidth=0):
        Face.__init__(self)

        if bgcolor is None:
            bgcolor = QtCore.Qt.transparent
        self.pixmap      = None
        self.type        = "text"
        self.text        = str(text)
        self.pen         = QtGui.QPen(QtGui.QColor(fgcolor))
        self.pen.setWidth(penwidth)
        if not bgcolor:
            self.bgcolor = QtGui.QColor(None)
        else:
            self.bgcolor = QtGui.QColor(bgcolor)
        self.fgcolor = QtGui.QColor(fgcolor)
        self.font    = QtGui.QFont(ftype,fsize)

    def _height(self):
        fm = QtGui.QFontMetrics(self.font)
        h =  fm.boundingRect(QtCore.QRect(), \
                                 QtCore.Qt.AlignLeft, \
                                 self.get_text()).height()
        return h
        # Other buggy alternatives
        # fm = QtGui.QFontMetrics(self.font)
        # h = 0
        # for l in lines:
        #     if l == lines[0]:
        #       h+=fm.tightBoundingRect(l).height()
        #     else:
        #       h+=fm.height()
        # return h #+ ((len(lines)-1)*fm.leading())
        #
        # lines = len(self.get_text().split("\n"))
        # return lines*fm.height() + (lines-1 * fm.leading())
        #
        # h =  fm.boundingRect(QtCore.QRect(), \
        #                        QtCore.Qt.AlignLeft, \
        #                        self.get_text()).height()
        # return h



    def _width(self):
        fm = QtGui.QFontMetrics(self.font)
        return fm.size(QtCore.Qt.AlignTop, self.text).width()

    def get_text(self):
        return self.text

class AttrFace(TextFace):
    """ Creates a new text attribute face object.

    Arguments description
    ---------------------
    attr:     Node's attribute that will be drawn as text
    ftype:    Font type, e.g. Arial, Verdana, Courier, (default="Verdana")
    fsize:    Font size, e.g. 10,12,6, (default=10)
    fgcolor:  Foreground font color in RGB name format, e.g. #FF00DD,#000000  (default="#000000")
    bgcolor:  Backgroung font color in RGB name format, e.g. #FFFFFF,#DDDDDD, (default=None)
    penwidth: Penwdith used to draw the text. (default is 0)
    text_prefix: text_rendered before attribute value
    text_suffix: text_rendered after attribute value
    """

    def __init__(self, attr, ftype="Verdana", fsize=10, fgcolor="#000000", \
                     bgcolor=None, penwidth=0, text_prefix="", text_suffix=""):
        Face.__init__(self)
        TextFace.__init__(self, "", ftype, fsize, fgcolor, bgcolor, penwidth)
        self.attr     = attr
        self.type     = "text"
        self.text_prefix = text_prefix
        self.text_suffix = text_suffix

    def _width(self):
        text = self.get_text()
        fm = QtGui.QFontMetrics(self.font)
        return fm.size(QtCore.Qt.AlignTop,text).width()

    def get_text(self):
        return ''.join(map(str, [self.text_prefix, \
                                     getattr(self.node, self.attr), \
                                     self.text_suffix]))



class ImgFace(Face):
    """ Creates a new image face object.

    Arguments description
    ---------------------

    img_file: Image file in png,jpg,bmp format
    """
    def __init__(self,img_file):
        Face.__init__(self)
        self.img_file = img_file
        self.name = "ImageFile"

    def update_pixmap(self):
        self.load_pixmap_from_file(self.img_file)


class ProfileFace(Face):
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
    def __init__(self,max_v,min_v,center_v,width=200,height=40,style="lines",colorscheme=2):
        Face.__init__(self)

        self.width  = width
        self.height = height
        self.max_value = max_v
        self.min_value = min_v
        self.center_v  = center_v
        self.xmargin = 1
        self.ymargin = 1
        self.style = style
        self.colorscheme = colorscheme

    def update_pixmap(self):
        if self.style=="lines":
            self.draw_line_profile()
        elif self.style=="heatmap":
            self.draw_heatmap_profile()
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
        mean_vector = self.node.profile
        deviation_vector = self.node.deviation
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
        mean_vector  = self.node.profile
        deviation_vector = self.node.deviation
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
        mean_vector = self.node.profile
        deviation_vector = self.node.deviation
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
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4
        
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
            mean_y1 = (mean1 - self.min_value) * y_alpha
            # Second Y postions for mean
            mean_y2 = (mean2 - self.min_value) * y_alpha
            # Draw blue mean line
            p.setPen(QtGui.QColor("blue"))
            p.drawLine(x1, profile_height-mean_y1, x2, profile_height-mean_y2)

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


    def draw_heatmap_profile(self):
        # Calculate vector
        vector = self.node.profile
        deviation = self.node.deviation
        # If no vector, skip
        if vector is None:
            return

        colors = self.get_color_gradient()

        leaves = self.node.get_leaves()

        vlength = len(vector)
        # pixels per array position
        img_height = self.height * len(leaves)
        profile_width = self.width - self.xmargin*2
        profile_height= img_height - self.ymargin*2

        x_alpha = float( profile_width / (len(vector)) )

        # Creates a pixmap
        self.pixmap = QtGui.QPixmap(self.width,img_height)
        self.pixmap.fill(QtGui.QColor("white"))
        p = QtGui.QPainter(self.pixmap)

        x2 = self.xmargin
        y  = self.ymargin
        y_step = self.height
        for leaf in leaves:
            mean_vector = leaf.profile
            deviation_vector = leaf.deviation
            # Draw heatmap
            for pos in xrange(vlength):
                # first and second X pixel positions
                x1 = x2
                x2 = x1 + x_alpha
                dev1 =  self.fit_to_scale( deviation_vector[pos]   )
                mean1 = self.fit_to_scale( mean_vector[pos]        )
                # Set heatmap color
                if not numpy.isfinite(mean1):
                    customColor = QtGui.QColor("#000000")
                elif mean1>self.center_v:
                    color_index = int(abs(((self.center_v-mean1)*100)/(self.max_value-self.center_v)))
                    customColor = colors[100+color_index]
                elif mean1<self.center_v:
                    color_index = int(abs(((self.center_v-mean1)*100)/(self.min_value-self.center_v)))
                    customColor = colors[100-color_index]
                else:
                    customColor = colors[-1]

                # Fill bar with custom color
                p.fillRect(x1, y, x_alpha, y_step, QtGui.QBrush(customColor))
            y+= y_step
            x2 = self.xmargin

    def fit_to_scale(self,v):
        if v<self.min_value:
            return float(self.min_value)
        elif v>self.max_value:
            return float(self.max_value)
        else:
            return float(v)

class ValidationFace(Face):
    """ Creates a new clustering validation face """

    def __init__(self,fsize=10):
        Face.__init__(self)
        self.seq  = seq
        self.name = "validation"
        self.fsize= fsize
        self.font = QtGui.QFont("Courier",self.fsize)
        self.style = seqtype

    def update_pixmap(self):
        pass

class SequenceFace(Face):
    """ Creates a new molecular sequence face object.

    Arguments description
    ---------------------
    seq:     Sequence string to be drawn
    seqtype: Type of sequence: "nt" or "aa"
    fsize:   Font size,  (default=10)
    """

    def __init__(self, seq, seqtype, fsize=10, aafg=aafgcolors,  aabg=aabgcolors, ntfg=ntfgcolors, ntbg=ntbgcolors):
        Face.__init__(self)
        self.seq  = seq
        self.name = "sequence"
        self.fsize= fsize
        self.font = QtGui.QFont("Courier", self.fsize)
        self.style = seqtype
        self.aafg = aafg
        self.aabg = aabg
        self.ntfg = ntfg
        self.ntbg = ntbg

    def update_pixmap(self):
        fm = QtGui.QFontMetrics(self.font)
        height = fm.leading() + fm.overlinePos() + fm.underlinePos()
        #width  = fm.size(QtCore.Qt.AlignTop, self.seq).width()
        width = self.fsize * len(self.seq)

        self.pixmap = QtGui.QPixmap(width,height)
        self.pixmap.fill()
        p = QtGui.QPainter(self.pixmap)
        x = 0
        y = height - fm.underlinePos()*2

        p.setFont(self.font)

        for letter in self.seq:
            letter = letter.upper()
            if self.style=="nt":
                letter_brush = QtGui.QBrush(QtGui.QColor(self.ntbg.get(letter,"#ffffff" )))
                letter_pen = QtGui.QPen(QtGui.QColor(self.ntfg.get(letter, "#000000")))
            else:
                letter_brush = QtGui.QBrush(QtGui.QColor(self.aabg.get(letter,"#ffffff" )))
                letter_pen = QtGui.QPen(QtGui.QColor(self.aafg.get(letter,"#000000" )))

            p.setPen(letter_pen)
            p.fillRect(x,0,width, height,letter_brush)
            p.drawText(x, y, letter)
            x += float(width)/len(self.seq)
        p.end()
