#START_LICENSE###########################################################
#END_LICENSE#############################################################

from PyQt4.QtGui import (QGraphicsRectItem, QGraphicsLineItem,
                         QGraphicsPolygonItem, QGraphicsEllipseItem,
                         QPen, QColor, QBrush, QPolygonF, QFont,
                         QPixmap, QFontMetrics, QPainter,
                         QRadialGradient, QGraphicsSimpleTextItem,
                         QGraphicsItem)
from PyQt4.QtCore import Qt,  QPointF, QRect, QRectF

from numpy import isfinite as _isfinite, ceil

from main import add_face_to_node, _Background, _Border, COLOR_SCHEMES

isfinite = lambda n: n and _isfinite(n)

_aafgcolors = {
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

_aabgcolors = {
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

_ntfgcolors = {
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

_ntbgcolors = {
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

__all__ = ["Face", "TextFace", "AttrFace", "ImgFace",
           "ProfileFace", "SequenceFace", "TreeFace",
           "RandomFace", "DynamicItemFace", "StaticItemFace",
           "CircleFace", "PieChartFace", "BarChartFace", "SeqMotifFace"]

class Face(object):
    """Base Face object. All Face types (i.e. TextFace, SeqMotifFace,
    etc.) inherit the following options:

    :param 0 margin_left: in pixels
    :param 0 margin_right: in pixels
    :param 0 margin_top: in pixels
    :param 0 margin_bottom: in pixels 
    :param 1.0 opacity: a float number in the (0,1) range
    :param True rotable: If True, face will be rotated when necessary
      (i.e. when circular mode is enabled and face occupies an inverted position.)
    :param 0 hz_align: 0 left, 1 center, 2 right
    :param 1 vt_align: 0 top, 1 center, 2 bottom
    :param background.color: background color of face plus all its margins.
    :param inner_background.color: background color of the face excluding margins
    :param border: Border around face margins.
    :param inner_border: Border around face excluding margins.
    
    **border and inner_border sub-parameters:**
    
    :param 0 (inner\_)border.type: 0=solid, 1=dashed, 2=dotted
    :param None (inner\_)border.width: a positive integer number. Zero
                             indicates a cosmetic pen. This means that
                             the pen width is always drawn one pixel
                             wide, independent of the transformation
                             set on the painter. A "None" value means
                             invisible border.
    :param black (inner\_)border.color: RGB or color name in :data:`SVG_COLORS`

    See also specific options for each face type.
    
    """

    def __init__(self):
        self.node        = None
        self.type = "pixmap" # pixmap, text or item

        self.margin_left = 0
        self.margin_right = 0
        self.margin_top = 0
        self.margin_bottom = 0
        self.pixmap = None
        self.opacity = 1.0
        self.rotable = True
        self.hz_align = 0 # 0 left, 1 center, 2 right
        self.vt_align = 1
        self.background = _Background()
        self.border = _Border()
        self.inner_border = _Border()
        self.inner_background = _Background()

    def _size(self):
        if self.pixmap:
            return self._width(),self._height()
        else:
            return 0, 0

    def _width(self):
        if self.pixmap:
            return self.pixmap.width()
        else:
            return 0

    def _height(self):
        if self.pixmap:
            return self.pixmap.height()
        else:
            return 0

    def load_pixmap_from_file(self, filename):
        self.pixmap = QPixmap(filename)

    def update_pixmap(self):
        pass
     
        
class TextFace(Face):
    """Static text Face object

    .. currentmodule:: ete_dev
    
    :param text:     Text to be drawn
    :param ftype:    Font type, e.g. Arial, Verdana, Courier
    :param fsize:    Font size, e.g. 10,12,6, (default=10)
    :param fgcolor:  Foreground font color. RGB code or color name in :data:`SVG_COLORS` 
    :param penwidth: Penwdith used to draw the text.
    :param fstyle: "normal" or "italic"
    
    :param True tight_text: When False, boundaries of the text are
    approximated according to general font metrics, producing slightly
    worse aligned text faces but improving the performance of tree
    visualization in scenes with a lot of text faces.
    """
        
    def _load_bounding_rect(self, txt=None):
        if txt is None:
            txt= self.get_text()
        fm = QFontMetrics(self._get_font())
        tx_w = fm.width(txt)
        if self.tight_text:
            textr = fm.tightBoundingRect(self.get_text())
            down = textr.height() + textr.y()
            up = textr.height() - down
            asc = fm.ascent()
            des = fm.descent()
            center = (asc + des) / 2.0
            xcenter = ((up+down)/2.0) + asc - up
            self._bounding_rect = QRectF(0, asc - up, tx_w, textr.height())
            self._real_rect = QRectF(0, 0, tx_w, textr.height())
        else:
            textr = fm.boundingRect(txt)
            self._bounding_rect = QRectF(0, 0, tx_w, textr.height())
            self._real_rect = QRectF(0, 0, tx_w, textr.height())
            
    def _get_text(self):
        return self._text
        
    def _set_text(self, txt):
        self._text = txt
        
    def get_bounding_rect(self):
        if not self._bounding_rect:
            self._load_bounding_rect()
        return self._bounding_rect
        
    def get_real_rect(self):
        if not self._real_rect:
            self._load_bounding_rect()
        return self._bounding_rect
        
    text = property(_get_text, _set_text)
    def __init__(self, text, ftype="Verdana", fsize=10,
                 fgcolor="black", penwidth=0, fstyle="normal",
                 tight_text=True):
        self._text = ""
        self._bounding_rect = None
        self._real_rect = None
        
        Face.__init__(self)
        self.pixmap = None
        self.type = "text"
        self.fgcolor = fgcolor
        self.ftype = ftype 
        self.fsize = fsize
        self.fstyle = fstyle
        self.penwidth = penwidth
        self.tight_text = tight_text
        if text:
            self.text = text

    def _get_font(self):
        font = QFont(self.ftype, self.fsize)
        if self.fstyle == "italic":
            font.setStyle(QFont.StyleItalic)
        elif self.fstyle == "oblique":
            font.setStyle(QFont.StyleOblique)
        return font

    def _height(self):
        return self.get_bounding_rect().height()

    def _width(self):
        return self.get_bounding_rect().width()

    def get_text(self):
        return self._text

class AttrFace(TextFace):
    """ 

    Dynamic text Face. Text rendered is taken from the value of a
    given node attribute.

    :param attr:     Node's attribute that will be drawn as text
    :param ftype:    Font type, e.g. Arial, Verdana, Courier, (default="Verdana")
    :param fsize:    Font size, e.g. 10,12,6, (default=10)
    :param fgcolor:  Foreground font color. RGB code or name in :data:`SVG_COLORS` 
    :param penwidth: Penwdith used to draw the text. (default is 0)
    :param text_prefix: text_rendered before attribute value
    :param text_suffix: text_rendered after attribute value
    :param formatter: a text string defining a python formater to
      process the attribute value before renderer. e.g. "%0.2f"
    :param fstyle: "normal" or "italic" 
    """
   
    def get_text(self):
        if self.attr_formatter:
            text = self.attr_formatter % getattr(self.node, self.attr)
        else:
            text = str(getattr(self.node, self.attr))
        text = ''.join(map(str, [self.text_prefix, \
                                     text, \
                                     self.text_suffix]))
        return text
        
    def get_bounding_rect(self):
        current_text = self.get_text()
        if current_text != self._bounding_rect_text:
            self._load_bounding_rect(current_text)
            self._bounding_rect_text = current_text
        return self._bounding_rect

    def get_real_rect(self):
        current_text = self.get_text()
        if current_text != self._bounding_rect_text:
            self._load_bounding_rect(current_text)
            self._bounding_rect_text = current_text
        return self._real_rect
    
    def __init__(self, attr, ftype="Verdana", fsize=10,
                 fgcolor="black", penwidth=0, text_prefix="",
                 text_suffix="", formatter=None, fstyle="normal",
                 tight_text=True):
        
        Face.__init__(self)
        TextFace.__init__(self, None, ftype, fsize, fgcolor, penwidth,
                          fstyle, tight_text)
        self.attr = attr
        self.type  = "text"
        self.text_prefix = text_prefix
        self.text_suffix = text_suffix
        self.attr_formatter = formatter
        self._bounding_rect_text = ""
        
class ImgFace(Face):
    """Creates a node Face using an external image file.

    :param img_file: path to the image file. 
    :param None width: if provided, image will be scaled to this width (in pixels)
    :param None height: if provided, image will be scaled to this height (in pixels)

    If only one dimension value (width or height) is provided, the other
    will be calculated to keep aspect ratio. 

    """
    
    def __init__(self, img_file, width=None, height=None):
        Face.__init__(self)
        self.img_file = img_file
        self.width = width
        self.height = height
        
    def update_pixmap(self):
        self.pixmap = QPixmap(self.img_file)
        
        if self.width or self.height:
            w, h = self.width, self.height
            ratio = self.pixmap.width() / float(self.pixmap.height())
            if not w:
                w = ratio * h
            if not h:
                h = w  / ratio
            self.pixmap = self.pixmap.scaled(w, h)

class ProfileFace(Face):
    """ 
    A profile Face for ClusterNodes 

    :param max_v: maximum value used to build the build the plot scale.
    :param max_v: minimum value used to build the build the plot scale.
    :param center_v: Center value used to scale plot and heatmap.
    :param 200 width:  Plot width in pixels. 
    :param 40 height: Plot width in pixels. 
    :param lines style: Plot style: "lines", "bars", "cbars" or "heatmap".

    :param 2 colorscheme: colors used to create the gradient from
      min values to max values. 0=green & blue; 1=green & red; 2=red &
      blue. In all three cases, missing values are rendered in black
      and transition color (values=center) is white.
    """

    def __init__(self,max_v,min_v,center_v,width=200,height=40,style="lines", colorscheme=2):
        Face.__init__(self)

        self.width  = width
        self.height = height
        self.max_value = max_v
        self.min_value = min_v
        self.center_v  = center_v
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
                color=QColor()
                color.setRgb( 200-2*a,255,200-2*a )
                colors.append(color)

            colors.append(QColor("white"))

            for a in xrange(0,100):
                color=QColor()
                color.setRgb( 200-2*a,200-2*a,255 )
                colors.append(color)
#            color=QColor()
#            color.setRgb( 0,255,255 )
#            colors.append(color)

        elif self.colorscheme == 1:
            for a in xrange(100,0,-1):
                color=QColor()
                color.setRgb( 200-2*a,255,200-2*a )
                colors.append(color)

            colors.append(QColor("white"))

            for a in xrange(0,100):
                color=QColor()
                color.setRgb( 255,200-2*a,200-2*a )
                colors.append(color)
#            color=QColor()
#            color.setRgb(255,255,0 )
#            colors.append(color)

        else:
            # Blue and Red
            for a in xrange(100,0,-1):
                color=QColor()
                color.setRgb( 200-2*a,200-2*a,255 )
                colors.append(color)

            colors.append(QColor("white"))

            for a in xrange(0,100):
                color=QColor()
                color.setRgb( 255,200-2*a,200-2*a )
                colors.append(color)

#            color=QColor()
#            color.setRgb( 255,0,255 )
#            colors.append(color)

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
        profile_width = self.width  - 40
        profile_height= self.height 

        x_alpha = float( profile_width / (len(mean_vector)) )
        y_alpha = float ( (profile_height-1) / (self.max_value-self.min_value) )

        # Creates a pixmap
        self.pixmap = QPixmap(self.width,self.height)
        self.pixmap.fill(QColor("white"))
        p = QPainter(self.pixmap)

        x2 = 0 
        y  = 0

        # Mean and quartiles y positions
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4

        # Draw axis and scale
        p.setPen(QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QFont("Verdana",8))
        p.drawText(profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(profile_width,y+profile_height,"%0.3f" %self.min_value)

        dashedPen = QPen(QBrush(QColor("#ddd")), 0)
        dashedPen.setStyle(Qt.DashLine)

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

            dev1 =  self.fit_to_scale(deviation_vector[pos])
            mean1 = self.fit_to_scale(mean_vector[pos])

            # If nan value, skip
            if not isfinite(mean1):
                continue

            # Set heatmap color
            if mean1 > self.center_v:
                color_index = abs(int(ceil(((self.center_v - mean1) * 100) / (self.max_value - self.center_v))))
                customColor = colors[100 + color_index]
            elif mean1 < self.center_v:
                color_index = abs(int(ceil(((self.center_v - mean1) * 100) / (self.min_value - self.center_v))))
                customColor = colors[100 - color_index]
            else:
                customColor = colors[100]

            # mean bar high
            mean_y1     = int ( (mean1 - self.min_value) * y_alpha)

            # Draw bar border
            p.setPen(QColor("black"))
            #p.drawRect(x1+2,mean_y1, x_alpha-3, profile_height-mean_y1+1)
            # Fill bar with custom color
            p.fillRect(x1+3,profile_height-mean_y1, x_alpha-4, mean_y1-1, QBrush(customColor))

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
        profile_width = self.width - 40
        profile_height= self.height

        x_alpha = float( profile_width / (len(mean_vector)) )
        y_alpha_up = float ( ((profile_height-1)/2) / (self.max_value-self.center_v) )
        y_alpha_down = float ( ((profile_height-1)/2) / (self.min_value-self.center_v) )

        # Creates a pixmap
        self.pixmap = QPixmap(self.width,self.height)
        self.pixmap.fill(QColor("white"))
        p = QPainter(self.pixmap)

        x2 = 0
        y  = 0 

        # Mean and quartiles y positions
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4

        # Draw axis and scale
        p.setPen(QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QFont("Verdana",8))
        p.drawText(profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(profile_width,y+profile_height,"%0.3f" %self.min_value)
        p.drawText(profile_width,mean_line_y,"%0.3f" %self.center_v)

        dashedPen = QPen(QBrush(QColor("#ddd")), 0)
        dashedPen.setStyle(Qt.DashLine)

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
            if not isfinite(mean1):
                continue

            # Set heatmap color
            if mean1>self.center_v:
                color_index = abs(int(ceil(((self.center_v-mean1)*100)/(self.max_value-self.center_v))))
                customColor = colors[100 + color_index]

                #print mean1, color_index, len(colors), "%x" %colors[100 + color_index].rgb()
                #print abs(((self.center_v-mean1)*100)/(self.max_value-self.center_v))
                #print round(((self.center_v-mean1)*100)/(self.max_value-self.center_v))

            elif mean1<self.center_v:
                color_index = abs(int(ceil(((self.center_v-mean1)*100)/(self.min_value-self.center_v))))
                customColor = colors[100 - color_index]
            else:
                customColor = colors[100]

            # mean bar high
            if mean1 < self.center_v:
                mean_y1 = int(abs((mean1 - self.center_v) * y_alpha_down))
            else:
                mean_y1 = int(abs((mean1 - self.center_v) * y_alpha_up))

            # Draw bar border
            p.setPen(QColor("black"))
            #p.drawRect(x1+2,mean_y1, x_alpha-3, profile_height-mean_y1+1)
            # Fill bar with custom color
            if mean1<self.center_v:
                p.fillRect(x1+3, mean_line_y, x_alpha-4, mean_y1, QBrush(customColor))
            else:
                p.fillRect(x1+3, mean_line_y-mean_y1, x_alpha-4, mean_y1+1, QBrush(customColor))

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
        profile_width = self.width - 40
        profile_height= self.height 


        x_alpha = float( profile_width / (len(mean_vector)-1) )
        y_alpha = float ( (profile_height-1) / (self.max_value-self.min_value) )

        # Creates a pixmap
        self.pixmap = QPixmap(self.width,self.height)
        self.pixmap.fill(QColor("white"))
        p = QPainter(self.pixmap)

        x2 = 0
        y  = 0

        # Mean and quartiles y positions
        mean_line_y = y + profile_height/2
        line2_y     = mean_line_y + profile_height/4
        line3_y     = mean_line_y - profile_height/4
        
        # Draw axis and scale
        p.setPen(QColor("black"))
        p.drawRect(x2,y,profile_width, profile_height-1)
        p.setFont(QFont("Verdana",8))
        p.drawText(profile_width,y+10,"%0.3f" %self.max_value)
        p.drawText(profile_width,y+profile_height,"%0.3f" %self.min_value)
        p.drawText(profile_width,mean_line_y+5,"%0.3f" %self.center_v)

        dashedPen = QPen(QBrush(QColor("#ddd")), 0)
        dashedPen.setStyle(Qt.DashLine)

        # Draw hz grid
        p.setPen(dashedPen)
        p.drawLine(x2+1, mean_line_y, profile_width-2, mean_line_y )
        p.drawLine(x2+1, line2_y, profile_width-2, line2_y )
        p.drawLine(x2+1, line3_y, profile_width-2, line3_y )

        # Draw lines
        for pos in xrange(0,vlength-1):
            dev1 =  self.fit_to_scale(mean_vector[pos] + deviation_vector[pos])
            dev2 =  self.fit_to_scale(mean_vector[pos+1] + deviation_vector[pos+1])
            mean1 = self.fit_to_scale(mean_vector[pos])
            mean2 = self.fit_to_scale(mean_vector[pos+1])
            # first and second X pixel positions
            x1 = x2
            x2 = x1 + x_alpha

            # Draw vt grid
            if x2 < profile_width:
                p.setPen(dashedPen)
                p.drawLine(x2, y+1, x2, profile_height-2)

            # If nan values, continue
            if not isfinite(mean1) or not isfinite(mean2):
                continue

            # First Y postions for mean
            mean_y1 = (mean1 - self.min_value) * y_alpha
            # Second Y postions for mean
            mean_y2 = (mean2 - self.min_value) * y_alpha
            if dev1!= 0 and dev2!=0:
                # First Y postions for deviations
                dev_y1   = (dev1 - self.min_value) * y_alpha
                # Second Y postions for deviations
                dev_y2   = (dev2 - self.min_value) * y_alpha
                # Draw red deviation lines
                p.setPen(QColor("red"))
                p.drawLine(x1, profile_height-dev_y1, x2, profile_height-dev_y2)
                p.drawLine(x1, profile_height+dev_y1, x2, profile_height+dev_y2)
            # Draw blue mean line
            p.setPen(QColor("blue"))
            p.drawLine(x1, profile_height-mean_y1, x2, profile_height-mean_y2)
 

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
        profile_width = self.width 
        profile_height= img_height 

        x_alpha = float( profile_width / (len(vector)) )

        # Creates a pixmap
        self.pixmap = QPixmap(self.width,img_height)
        self.pixmap.fill(QColor("white"))
        p = QPainter(self.pixmap)

        x2 = 0
        y  = 0
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
                if not isfinite(mean1):
                    customColor = QColor("black")
                elif mean1>self.center_v:
                    color_index = abs(int(ceil(((self.center_v-mean1)*100)/(self.max_value-self.center_v))))
                    customColor = colors[100 + color_index]
                elif mean1<self.center_v:
                    color_index = abs(int(ceil(((self.center_v-mean1)*100)/(self.min_value-self.center_v))))
                    customColor = colors[100 - color_index]
                else:
                    customColor = colors[100]

                # Fill bar with custom color
                p.fillRect(x1, y, x_alpha, y_step, QBrush(customColor))
            y+= y_step
            x2 = 0

    def fit_to_scale(self,v):
        if v<self.min_value:
            return float(self.min_value)
        elif v>self.max_value:
            return float(self.max_value)
        else:
            return float(v)


class OLD_SequenceFace(Face):
    """ Creates a new molecular sequence face object.


    :param seq:  Sequence string to be drawn
    :param seqtype: Type of sequence: "nt" or "aa"
    :param fsize:   Font size,  (default=10)

    You can set custom colors for aminoacids or nucleotides: 

    :param aafg: a dictionary in which keys are aa codes and values
      are foreground RGB colors

    :param aabg: a dictionary in which keys are aa codes and values
      are background RGB colors

    :param ntfg: a dictionary in which keys are nucleotides codes
      and values are foreground RGB colors

    :param ntbg: a dictionary in which keys are nucleotides codes and values
      are background RGB colors

    """

    def __init__(self, seq, seqtype, fsize=10, aafg=None,  \
                     aabg=None, ntfg=None, ntbg=None):

        Face.__init__(self)
        self.seq  = seq
        self.fsize= fsize
        self.fsize = fsize
        self.style = seqtype

        if not aafg:
            aafg = _aafgcolors
        if not aabg: 
            aabg = _aabgcolors
        if not ntfg:
            ntfg = _ntfgcolors
        if not ntbg:
            ntbg = _ntbgcolors

        self.aafg = aafg
        self.aabg = aabg
        self.ntfg = ntfg
        self.ntbg = ntbg

    def update_pixmap(self):
        font = QFont("Courier", self.fsize)
        fm = QFontMetrics(font)
        height = fm.leading() + fm.overlinePos() + fm.underlinePos()
        #width  = fm.size(Qt.AlignTop, self.seq).width()
        width = self.fsize * len(self.seq)

        self.pixmap = QPixmap(width,height)
        self.pixmap.fill()
        p = QPainter(self.pixmap)
        x = 0
        y = height - fm.underlinePos()*2

        p.setFont(font)

        for letter in self.seq:
            letter = letter.upper()
               
            if self.style=="nt":
                letter_brush = QBrush(QColor(self.ntbg.get(letter,"white" )))
                letter_pen = QPen(QColor(self.ntfg.get(letter, "black")))
            else:
                letter_brush = QBrush(QColor(self.aabg.get(letter,"white" )))
                letter_pen = QPen(QColor(self.aafg.get(letter,"black" )))

            p.setPen(letter_pen)
            p.fillRect(x,0,width, height,letter_brush)
            p.drawText(x, y, letter)
            x += float(width)/len(self.seq)
        p.end()

class TreeFace(Face):
    """ 
    .. versionadded:: 2.1

    Creates a Face containing a Tree object. Yes, a tree within a tree :)

    :param tree: An ETE Tree instance (Tree, PhyloTree, etc...)
    :param tree_style: A TreeStyle instance defining how tree show be drawn 
    
    """
    def __init__(self, tree, tree_style):
        Face.__init__(self)
        self.type = "item"
        self.root_node = tree
        self.img = tree_style
        self.item = None

    def update_items(self):
        from qt4_render import render, init_tree_style
        ts = init_tree_style(self.root_node, self.img)
        hide_root = False
        if self.root_node is self.node:
            hide_root = True
        self.item, self.n2i, self.n2f = render(self.root_node, ts, hide_root)

    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class _SphereItem(QGraphicsEllipseItem):
    def __init__(self, radius, color, solid=False):
        r = radius
        d = r*2 
        QGraphicsEllipseItem.__init__(self, 0, 0, d, d)
        self.gradient = QRadialGradient(r, r, r,(d)/3,(d)/3)
        self.gradient.setColorAt(0.05, Qt.white)
        self.gradient.setColorAt(1, QColor(color))
        if solid:
            self.setBrush(QBrush(QColor(color)))
        else:
            self.setBrush(QBrush(self.gradient))
        self.setPen(QPen(QColor(color)))
        #self.setPen(Qt.NoPen)

class CircleFace(Face):
    """
    .. versionadded:: 2.1

    Creates a Circle or Sphere Face.

    :param radius: integer number defining the radius of the face
    :param color: Color used to fill the circle. RGB code or name in :data:`SVG_COLORS` 
    :param "circle" style: Valid values are "circle" or "sphere"
    """

    def __init__(self, radius, color, style="circle"):
        Face.__init__(self)
        self.radius = radius
        self.style = style
        self.color = color
        self.type = "item"
        self.rotable = False

    def update_items(self):
        if self.style == "circle":
            self.item = _SphereItem(self.radius, self.color, solid=True)
        elif self.style == "sphere":
            self.item = _SphereItem(self.radius, self.color)

    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class StaticItemFace(Face):
    """
    .. versionadded:: 2.1

    Creates a face based on an external QtGraphicsItem object.
    QGraphicsItem object is expected to be independent from tree node
    properties, so its content is assumed to be static (drawn only
    once, no updates when tree changes). 

    :param item: an object based on QGraphicsItem
    """
    def __init__(self, item):
        Face.__init__(self)
        self.type = "item"
        self.item = item

    def update_items(self):
        return 

    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class DynamicItemFace(Face):
    """
    .. versionadded:: 2.1

    Creates a face based on an external QGraphicsItem object whose
    content depends on the node that is linked to. 

    :param constructor: A pointer to a method (function or class
      constructor) returning a QGraphicsItem based
      object. "constructor" method is expected to receive a node
      instance as the first argument. The rest of arguments passed to
      ItemFace are optional and will passed also to the constructor
      function.
    """

    def __init__(self, constructor, *args, **kargs):
        Face.__init__(self)
        self.type = "item"
        self.item = None
        self.constructor = constructor
        self.args = args
        self.kargs = kargs

    def update_items(self):
        self.item = self.constructor(self.node, self.args, self.kargs)

    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class RandomFace(Face):
    def __init__(self):
        Face.__init__(self)
        self.type = "item"

    def update_items(self):
        import random
        w = random.randint(4, 100)
        h = random.randint(4, 100)
        self.tree_partition = QGraphicsRectItem(0,0,w, h)
        self.tree_partition.setBrush(QBrush(QColor("green")))

    def _width(self):
        return self.tree_partition.rect().width()

    def _height(self):
        return self.tree_partition.rect().height()

class _PieChartItem(QGraphicsRectItem):
    def __init__(self, percents, width, height, colors, line_color=None):
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        self.percents = percents
        self.colors = colors
        self.line_color = line_color
        
    def paint(self, painter, option, widget):
        a = 5760
        angle_start = 0
        if not self.line_color:
            painter.setPen(Qt.NoPen)
        else:
            painter.setPen(QColor(self.line_color))
            
        for i, p in enumerate(self.percents):
            col = self.colors[i]
            painter.setBrush(QBrush(QColor(col)))
            angle_span = (p/100.) * a
            painter.drawPie(self.rect(), angle_start, angle_span )
            angle_start += angle_span


class PieChartFace(StaticItemFace):
    """ 
    .. versionadded:: 2.2

    :param percents: a list of values summing up 100. 
    :param width: width of the piechart 
    :param height: height of the piechart
    :param colors: a list of colors (same length as percents)
   
    """
    def __init__(self, percents, width, height, colors=None, line_color=None):
        Face.__init__(self)
        if round(sum(percents)) > 100:
            raise ValueError("PieChartItem: percentage values > 100")

        self.type = "item"
        self.item = None
        self.percents = percents
        if not colors:
            colors = COLOR_SCHEMES["paired"]
        self.colors =  colors
        self.width = width
        self.height = height
        self.line_color = line_color
        
    def update_items(self):
        self.item = _PieChartItem(self.percents, self.width,
                                  self.height, self.colors, self.line_color)
        
    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class BarChartFace(Face):
    """ 
    .. versionadded:: 2.2

    :param percents: a list of values summing up 100. 
    :param width: width of the piechart 
    :param height: height of the piechart
    :param colors: a list of colors (same length as percents)
   
    """
    def __init__(self, values, deviations=None, width=200, height=100, colors=None, labels=None, min_value=0, max_value=None):
        Face.__init__(self)
        self.type = "item"
        self.item = None
        self.values = values
        if not deviations:
            self.deviations = [0] * len(values)
        else:
            self.deviations = deviations

        if not colors:
            colors = COLOR_SCHEMES["paired"]
        self.colors =  colors
       
        
        self.width = width
        self.height = height
        self.labels = labels
        self.max_value = max_value
        self.min_value = min_value
        self.margin_left = 1
        self.margin_right = 1
        self.margin_top = 2
        self.margin_bottom = 2
        
    def update_items(self):
        self.item = _BarChartItem(self.values, self.deviations, self.width,
                                  self.height, self.colors, self.labels, 
                                  self.min_value, self.max_value)
        
    def _width(self):
        return self.item.rect().width()

    def _height(self):
        return self.item.rect().height()


class _BarChartItem(QGraphicsRectItem):
    def __init__(self, values, deviations, width, height, colors, labels, min_value, max_value):
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        self.values = values
        self.colors = colors
        self.width = width
        self.height = height
        self.draw_border = False
        self.draw_grid = False
        self.draw_scale = True
        self.labels = labels
        self.max_value = max_value
        self.min_value = min_value
        self.deviations = deviations
        
    def paint(self, p, option, widget):
        colors = self.colors
        values = self.values
        deviations = self.deviations

        spacer = 3
        spacing_length = (spacer*(len(values)-1))
        height=  self.height 
        
        if self.max_value is None:
            max_value = max([v+d for v,d in zip(values, deviations) if isfinite(v)])
        else:
            max_value = self.max_value

        if self.min_value is None:
            min_value = min([v+d for v,d in zip(values, deviations) if isfinite(v)])
        else:
            min_value = 0
            
        scale_length = 0
        scale_margin = 2
        if self.draw_scale: 
            p.setFont(QFont("Verdana", 8))
            max_string = "%g" %max_value
            min_string = "%g" %min_value
            fm = QFontMetrics(p.font())
            max_string_metrics = fm.boundingRect(QRect(), \
                                                 Qt.AlignLeft, \
                                                 max_string)
            min_string_metrics = fm.boundingRect(QRect(), \
                                                 Qt.AlignLeft, \
                                                 min_string)
            scale_length = scale_margin + max(max_string_metrics.width(),
                              min_string_metrics.width())
        

        real_width = self.width - scale_length
        x_alpha = float((real_width - spacing_length) / (len(values))) 
        if x_alpha < 1:
            raise ValueError("BarChartFace is too small")
        
        y_alpha = float ( (height-1) / float(max_value - min_value) )
        x = 0 
        y  = 0

        # Mean and quartiles y positions
        mean_line_y = y + height / 2
        line2_y     = mean_line_y  + height/4
        line3_y     = mean_line_y - height/4

        if self.draw_border:
            p.setPen(QColor("black"))
            p.drawRect(x, y, real_width + scale_margin - 1 , height)
            
        if self.draw_scale: 
            p.drawText(real_width + scale_margin, max_string_metrics.height(), max_string)
            p.drawText(real_width + scale_margin, height - 2, min_string)
            p.drawLine(real_width + scale_margin - 1, 0, real_width + scale_margin - 1, height)
            p.drawLine(real_width + scale_margin - 1, 0, real_width + scale_margin + 2, y)
            p.drawLine(real_width + scale_margin - 1, height, real_width + scale_margin + 2, height)
            
        if self.draw_grid: 
            dashedPen = QPen(QBrush(QColor("#ddd")), 0)
            dashedPen.setStyle(Qt.DashLine)
            p.setPen(dashedPen)
            p.drawLine(x+1, mean_line_y, real_width - 2, mean_line_y )
            p.drawLine(x+1, line2_y, real_width - 2, line2_y )
            p.drawLine(x+1, line3_y, real_width - 2, line3_y )

        # Draw bars
        for pos in xrange(len(values)):
            # first and second X pixel positions
            x1 = x
            x = x1 + x_alpha + spacer

            std =  deviations[pos]
            val = values[pos]

            # If nan value, skip
            if not isfinite(val):
                continue

            color = QColor(colors[pos])
            # mean bar high
            mean_y1     = int((val - min_value) * y_alpha)
            # Draw bar border
            p.setPen(QColor("black"))

            # Fill bar with custom color
            p.fillRect(x1, height-mean_y1, x_alpha, mean_y1 - 1, QBrush(color))

            # Draw error bars
            if std != 0:
                dev_up_y1   = int((val + std - min_value) * y_alpha)
                dev_down_y1 = int((val - std - min_value) * y_alpha)
                center_x = x1 + (x_alpha / 2)
                p.drawLine(center_x, height - dev_up_y1, center_x, height - dev_down_y1)
                p.drawLine(center_x + 1, height - dev_up_y1, center_x -1, height - dev_up_y1)
                p.drawLine(center_x + 1, height - dev_down_y1, center_x -1, height - dev_down_y1)

            if self.labels: 
                p.save()
                p.translate(x1, -height-30)
                p.rotate(90)
                p.drawText(0, 0, str(self.labels[pos]))
                p.restore()


class QGraphicsTriangleItem(QGraphicsPolygonItem):
    def __init__(self, width, height, orientation=1):
        tri = QPolygonF()
        if orientation == 1:
            tri.append(QPointF(0, 0))
            tri.append(QPointF(0, height))
            tri.append(QPointF(width, height / 2.0))
            tri.append(QPointF(0, 0))
        elif orientation == 2:
            tri.append(QPointF(0, 0))
            tri.append(QPointF(width, 0))
            tri.append(QPointF(width / 2.0, height))
            tri.append(QPointF(0, 0))
        elif orientation == 3:
            tri.append(QPointF(0, height / 2.0))
            tri.append(QPointF(width, 0))
            tri.append(QPointF(width, height))
            tri.append(QPointF(0, height / 2.0))
        elif orientation == 4:
            tri.append(QPointF(0, height))
            tri.append(QPointF(width, height))
            tri.append(QPointF(width / 2.0, 0))
            tri.append(QPointF(0, height))
                       
        QGraphicsPolygonItem.__init__(self, tri)

class QGraphicsDiamondItem(QGraphicsPolygonItem):
    def __init__(self, width, height):
        pol = QPolygonF()
        pol.append(QPointF(width / 2.0, 0))
        pol.append(QPointF(width, height / 2.0))
        pol.append(QPointF(width / 2.0, height))
        pol.append(QPointF(0, height / 2.0))
        pol.append(QPointF(width / 2.0, 0))
        QGraphicsPolygonItem.__init__(self, pol)

class QGraphicsRoundRectItem(QGraphicsRectItem):
    def __init__(self, *args, **kargs):
        QGraphicsRectItem.__init__(self, *args, **kargs)
    def paint(self, p, option, widget):
        p.setPen(self.pen())
        p.setBrush(self.brush())
        p.drawRoundedRect(self.rect(), 3, 3)

class SequenceItem(QGraphicsRectItem):
    def __init__(self, seq, seqtype="aa", poswidth=1, posheight=10,
                 draw_text=False):
        QGraphicsRectItem.__init__(self)
        self.seq = seq
        self.seqtype = seqtype
        self.poswidth = poswidth
        self.posheight = posheight
        self.draw_text = draw_text
        if seqtype == "aa":
            self.fg = _aafgcolors
            self.bg = _aabgcolors
        elif seqtype == "nt":
            self.fg = _ntfgcolors
            self.bg = _ntbgcolors
        self.setRect(0, 0, len(seq) * poswidth, posheight)

    def paint(self, p, option, widget):
        x, y = 0, 0
        fsize = (min(self.poswidth, self.posheight) - 2)
        p.setFont(QFont("Courier", fsize))
        p.setPen(QColor("black"))
        for letter in self.seq:
            br = QBrush(QColor(self.bg.get(letter, "white")))
            p.fillRect(x, 0, self.poswidth, self.posheight, br)
            if letter == "-" or letter == ".":
                p.drawLine(x, self.posheight/2, x+self.poswidth, self.posheight/2)
            elif self.draw_text and self.poswidth > 8:
                p.drawText(x + 2, self.posheight - 2, letter)
            x += self.poswidth
            
class SeqMotifFace(StaticItemFace):
    """.. versionadded:: 2.2

    Creates a face based on an amino acid or nucleotide sequence and a
    list of motif regions.

    :param None seq: a text string containing an aa or nt sequence. If
        not provided, ``seq`` and ``compactseq`` motif modes will not be
        available.

    :param None motifs: a list of motif regions referred to original
        sequence. Each motif is defined as a list containing the
        following information:

        ::
    
          motifs = [[seq.start, seq.end, shape, width, height, fgcolor, bgcolor],
                   [seq.start, seq.end, shape, width, height, fgcolor, bgcolor],
                   ...
                  ]
    
        Where:
    
         * **seq.start:** Motif start position referred to the full sequence
         * **seq.end:** Motif end position referred to the full sequence
         * **shape:** Shape used to draw the motif. Available values are:
    
            * ``o`` = circle or ellipse
            * ``>``  = triangle (base to the left)
            * ``<``  = triangle (base to the left)
            * ``^``  = triangle (base at bottom)
            * ``v``  = triangle (base on top )
            * ``<>`` = diamond
            * ``[]`` = rectangle
            * ``()`` = round corner rectangle
            * ``seq`` = Show a color and the corresponding letter of each sequence position
            * ``compactseq`` = Show a color for each sequence position
               
         * **width:** total width of the motif (or sequence position width if seq motif type)
         * **height:** total height of the motif (or sequence position height if seq motif type)
         * **fgcolor:** color for the motif shape border
         * **bgcolor:** motif background color. Color code or name can be preceded with the "rgradient:" tag to create a radial gradient effect.

    :param line intermotif_format: How should spaces among motifs be filled. Available values are: "line", "blank", "none" and "seq", "compactseq".
    :param none seqtail_format: How should remaining tail sequence be drawn. Available values are: "line", "seq", "compactseq" or "none"
    :param compactseq seq_format: How should sequence be rendered in case no motif regions are provided. Available values are: "seq" and "compactseq"
    """

    def __init__(self, seq=None, motifs=None, seqtype="aa",
                 intermotif_format="line", seqtail_format="none",
                 seq_format="compactseq"):
        
        StaticItemFace.__init__(self, None)
        self.seq  = seq or []
        self.motifs = motifs
        self.intermotif_format = intermotif_format
        self.seqtail_format = seqtail_format
        self.seq_format = seq_format
        if seqtype == "aa":
            self.fg = _aafgcolors
            self.bg = _aabgcolors
        elif seqtype == "nt":
            self.fg = _ntfgcolors
            self.bg = _ntbgcolors

        self.build_regions()

    def build_regions(self): 
        # Sort regions
        seq = self.seq or []
        motifs = self.motifs
        if not motifs:
            if self.seq_format == "seq":
                motifs = [[1, len(seq), "seq", 10, 10, None, None]]
            elif self.seq_format == "compactseq":
                motifs = [[1, len(seq), "compactseq", 1, 10, None, None]]
        motifs.sort()
        intermotif = self.intermotif_format
        self.regions = []
        current_pos = 0
        end = 0
        for mf in motifs:
            start, end, typ, w, h, fg, bg = mf
            start -= 1
            if start < current_pos:
                print current_pos, start, mf
                raise ValueError("Overlaping motifs are not supported")
            if start > current_pos:
                if intermotif == "blank": 
                    self.regions.append([current_pos, start, " ", 1, 1, None, None])
                elif intermotif == "line":
                    self.regions.append([current_pos, start, "-", 1, 1, "black", None])
                elif intermotif == "seq":
                    # Colors are read from built-in dictionary
                    self.regions.append([current_pos, start, "seq", 10, 10, None, None])
                elif intermotif == "compactseq":
                    # Colors are read from built-in dictionary
                    self.regions.append([current_pos, start, "compactseq", 1, 10, None, None])
                elif intermotif == "none":
                    self.regions.append([current_pos, start, " ", 0, 0, None, None]) 
            self.regions.append(mf)
            current_pos = end

        if len(seq) > end:
            if self.seqtail_format == "line":
                self.regions.append([end, len(seq), "-", 1, 1, "black", None])
            elif self.seqtail_format == "seq":
                self.regions.append([end, len(seq), "seq", 10, 10, None, None])
            elif self.seqtail_format == "compactseq":
                self.regions.append([end, len(seq), "compactseq", 1, 10, None, None])




def make_regions(seq, motifs):
    poswidth = 2
    posheight = 4
    motifposwidth = 12
    motifposheight = 12
    
    #Sort regions
    regions = []
    current_pos = 0
    end = 0
    for mf in motifs:
        start, end = mf
        start -= 1
        if start < current_pos:
            print current_pos, start, mf
            raise ValueError("Overlaping motifs are not supported")
        if start > current_pos:
            regions.append([current_pos, start, "s"])
        regions.append([start, end, "m"])
        current_pos = end
    if len(seq) > end:
        regions.append([end, len(seq), "s"])
    
    return regions

class SequencePlotFace(StaticItemFace):
    """
    To draw plots, usually correlated to columns in alignment
    
    :argument values : a list of values
    :argument None errors : a list of errors associated to each value. elements of the list can contain a list with lower and upper error, if they are different.
    :argument None colors : a list of colors associated to each value
    :argument None header : a title for the plot
    :argument bar kind : kind of plot, one of bar, curve or sticks.
    :argument None fsize : font size for header and labels
    :argument 100 height : height of the plot (excluding labels)
    :argument None hlines : list of y values of horizontal dashed lines to be drawn across plot
    :argument None hlines_col: list of colors associated to each horizontal line
    :argument None col_width : width of a column in the alignment
    :argument red error_col : color of error bars
    """
    def __init__(self, values, errors=None, colors=None, header='',
                 fsize=9, height = 100, hlines=None, kind='bar',
                 hlines_col = None, extras=None, col_width=11,
                 ylim=None, xlabel='', ylabel=''):
        
        self.col_w = float(col_width)
        self.height = height
        self.values = [float(v) for v in values]
        self.width = self.col_w * len (self.values)
        self.errors = errors if errors else []
        self.colors = colors if colors else ['gray'] * len(self.values)
        self.header = header
        self.fsize = fsize
        if ylim:
            self.ylim = tuple((float(y) for y in ylim))
        else:
            dif = (max(self.values) - min(self.values))/20
            if dif >= 1:
                self.ylim = (int(min(self.values)-0.5), int(max(self.values)+0.5))
            else:
                from math import log10
                exp = str(-int(log10(min(self.values))-0.5))
                self.ylim = (float(int(min(self.values)*float('1e'+exp)-0.5))/float('1e'+exp),
                             float(int(max(self.values)/float('1e'+exp)+0.5))/float('1e'+exp))
        self.xlabel = xlabel
        self.ylabel = ylabel

        if self.errors:
            if type(self.errors[0]) is list or type(self.errors[0]) is tuple:
                self._up_err = [float(e[1]) for e in self.errors]
                self._dw_err = [float(-e[0]) for e in self.errors]
            else:
                self._up_err = [float(e) for e in self.errors]
                self._dw_err = [float(-e) for e in self.errors]
        if kind == 'bar':
            self.draw_fun = self.draw_bar
        elif kind == 'stick':
            self.draw_fun = self.draw_stick
        elif kind == 'curve':
            self.draw_fun = self.draw_curve
        else:
            raise('kind %s not yet implemented... ;)'%kind)
        
        self.hlines = [float(h) for h in hlines] if hlines else [1.0]
        self.hlines_col = hlines_col if hlines_col else ['black']*len(self.hlines)

        self.extras = extras if extras else ['']
        if len (self.extras) != len (self.values):
            self.extras = ['']
        
        super(SequencePlotFace,
              self).__init__(QGraphicsRectItem(-40, 0, self.width+40,
                                                     self.height+50))
        self.item.setPen(QPen(QColor('white')))

    def update_items(self):
        # draw lines
        for line, col in zip(self.hlines, self.hlines_col):
            self.draw_hlines(line, col)
        # draw plot
        width = self.col_w
        for i, val in enumerate(self.values):
            self.draw_fun(width * i + self.col_w / 2 , val, i)
        # draw error bars
        if self.errors:
            for i in range(len(self.errors)):
                self.draw_errors(width * i + self.col_w / 2 , i)
        # draw x axis
        self.draw_x_axis()
        # draw y axis
        self.draw_y_axis()
        # put header
        self.write_header()

    def write_header(self):
        text = QGraphicsSimpleTextItem(self.header)
        text.setFont(QFont("Arial", self.fsize))
        text.setParentItem(self.item)
        text.setPos(0, 5)
        
    def draw_y_axis(self):
        lineItem = QGraphicsLineItem(0, self.coordY(self.ylim[0]),
                                     0, self.coordY(self.ylim[1]),
                                     parent=self.item)
        lineItem.setPen(QPen(QColor('black')))
        lineItem.setZValue(10)
        max_w = 0
        for y in set(self.hlines + list(self.ylim)):
            lineItem = QGraphicsLineItem(0, self.coordY(y),
                                               -5, self.coordY(y),
                                               parent=self.item)
            lineItem.setPen(QPen(QColor('black')))
            lineItem.setZValue(10)
            text = QGraphicsSimpleTextItem(str(y))
            text.setFont(QFont("Arial", self.fsize-2))
            text.setParentItem(self.item)
            tw = text.boundingRect().width()
            max_w = tw if tw > max_w else max_w
            th = text.boundingRect().height()
            # Center text according to masterItem size
            text.setPos(-tw - 5, self.coordY(y)-th/2)
        if self.ylabel:
            text = QGraphicsSimpleTextItem(self.ylabel)
            text.setFont(QFont("Arial", self.fsize-1))
            text.setParentItem(self.item)
            text.rotate(-90)
            tw = text.boundingRect().width()
            th = text.boundingRect().height()
            # Center text according to masterItem size
            text.setPos(-th -5-max_w, tw/2+self.coordY(sum(self.ylim)/2))
      
    def draw_x_axis(self):
        lineItem = QGraphicsLineItem(self.col_w/2,
                                           self.coordY(self.ylim[0])+2,
                                           self.width-self.col_w/2,
                                           self.coordY(self.ylim[0])+2,
                                           parent=self.item)
        lineItem.setPen(QPen(QColor('black')))
        lineItem.setZValue(10)
        all_vals = range(0, len(self.values), 5)
        if (len(self.values)-1)%5:
            all_vals += [len(self.values)-1]
        for x in all_vals:
            lineItem = QGraphicsLineItem(0, self.coordY(self.ylim[0])+2,
                                               0, self.coordY(self.ylim[0])+6,
                                               parent=self.item)
            lineItem.setX(x*self.col_w + self.col_w/2)
            lineItem.setPen(QPen(QColor('black')))
            lineItem.setZValue(10)
            text = QGraphicsSimpleTextItem(str(x))
            text.setFont(QFont("Arial", self.fsize-2))
            text.setParentItem(self.item)
            tw = text.boundingRect().width()
            # Center text according to masterItem size
            text.setPos(x*self.col_w-tw/2 + self.col_w/2,
                        self.coordY(self.ylim[0])+6)
        
    def coordY(self, y):
        """
return the transformation of Y according to mean value
(that is last element of lines)
"""
        y_offset = 30
        if self.ylim[1] <= y: return y_offset
        if self.ylim[1] == 0: return self.height + y_offset
        if self.ylim[0] >= y: return self.height + y_offset
        #return self.height - y * self.height / self.ylim[1]
        return self.height + y_offset - (y-self.ylim[0]) / (self.ylim[1]-self.ylim[0]) * self.height
            
    def draw_hlines (self, line, col):
        lineItem = QGraphicsLineItem(0, self.coordY(line),
                                           self.width, self.coordY(line),
                                           parent=self.item)
        lineItem.setPen(QPen(QColor(col), 1, Qt.DashLine))
        lineItem.setZValue(10)

    def draw_bar(self, x, y, i):
        h = self.coordY(self.ylim[0])#self.height
        coordY = self.coordY
        item = self.item
        # if value stands out of bound
        if y < self.ylim[0]: return
        if y < self.ylim[1]:
            # left line
            lineItem = QGraphicsLineItem(0, h, 0, coordY(y), parent=item)
            lineItem.setX(x-3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # right line
            lineItem = QGraphicsLineItem(0, h, 0, coordY(y), parent=item)
            lineItem.setX(x+3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # top line
            lineItem = QGraphicsLineItem(0, coordY(y), 6, coordY(y), parent=item)
            lineItem.setX(x-3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
        else:
            # lower left line
            lineItem = QGraphicsLineItem(0, h, 0, coordY(y), parent=item)
            lineItem.setX(x-3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # lower right line
            lineItem = QGraphicsLineItem(0, h, 0, coordY(y), parent=item)
            lineItem.setX(x+3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # upper left line
            lineItem = QGraphicsLineItem(0, coordY(y)-4, 0, coordY(y)-7, parent=item)
            lineItem.setX(x-3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # upper right line
            lineItem = QGraphicsLineItem(0, coordY(y)-4, 0, coordY(y)-7, parent=item)
            lineItem.setX(x+3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
            # top line
            lineItem = QGraphicsLineItem(0, coordY(y)-7, 6, coordY(y)-7, parent=item)
            lineItem.setX(x-3)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))
        
    def draw_stick(self, x, y, i):
        lineItem = QGraphicsLineItem(0, self.coordY(self.ylim[0]),
                                           0, self.coordY(y),
                                           parent=self.item)
        lineItem.setX(x)
        lineItem.setPen(QPen(QColor(self.colors[i]),2))

    def draw_errors(self, x, i):
        lower = self.values[i]+self._dw_err[i]
        upper = self.values[i]+self._up_err[i]
        lineItem = QGraphicsLineItem(0, self.coordY(lower), 0,
                                           self.coordY(upper), parent=self.item)
        lineItem.setX(x)
        lineItem.setPen(QPen(QColor('black'),1))
        
    def draw_curve(self, x, y, i):
        # top line
        lineItem = QGraphicsLineItem(0, self.coordY(y), 4,
                                           self.coordY(y), parent=self.item)
        lineItem.setX(x-2)
        lineItem.setPen(QPen(QColor(self.colors[i]),2))
        if i > 0:
            prev = self.values[i-1] if i>0 else self.values[i]
            lineItem = QGraphicsLineItem(0, self.coordY(prev), self.col_w-4,
                                               self.coordY(y), parent=self.item)
            lineItem.setX(x - self.col_w+2)
            lineItem.setPen(QPen(QColor(self.colors[i]),2))


                
class SequenceFace(StaticItemFace, Face):
    """ Creates a new molecular sequence face object.


:argument seq: Sequence string to be drawn
:argument seqtype: Type of sequence: "nt" or "aa"
:argument fsize: Font size, (default=10)

You can set custom colors for amino-acids or nucleotides:

:argument None codon : a string that corresponds to the reverse translation of the amino-acid sequence
:argument None col_w : width of the column (if col_w is lower than font size, letter wont be displayed)
:argument None fg_colors : dictionary of colors for foreground, with as keys each possible character in sequences, and as value the colors
:argument None bg_colors : dictionary of colors for background, with as keys each possible character in sequences, and as value the colors
:argument 3 alt_col_w : works together with special_col option, defines the width of given columns
:argument None special_col : list of lists containing the bounds of columns to be displayed with alt_col_w as width
:argument False interactive : more info can be displayed when mouse over sequence

"""
    def __init__(self, seq, seqtype="aa", fsize=10,
                 fg_colors=None, bg_colors=None,
                 codon=None, col_w=None, alt_col_w=3,
                 special_col=None, interactive=False):
        self.seq = seq
        self.codon = codon
        self.fsize = fsize
        self.style = seqtype
        self.col_w = float(self.fsize + 1) if col_w is None else float(col_w)
        self.alt_col_w = float(alt_col_w)
        self.special_col = special_col if special_col else []
        self.width = 0 # will store the width of the whole sequence
        self.interact = interactive

        if self.style == "aa":
            if not fg_colors:
                fg_colors = _aafgcolors
            if not bg_colors:
                bg_colors = _aabgcolors
        else:
            if not fg_colors:
                fg_colors = _ntfgcolors
            if not bg_colors:
                bg_colors = _ntbgcolors

        def __init_col(color_dic):
            """to speed up the drawing of colored rectangles and characters"""
            new_color_dic = {}
            for car in color_dic:
                new_color_dic[car] = QBrush(QColor(color_dic[car]))
            return new_color_dic
            
        self.fg_col = __init_col(fg_colors)
        self.bg_col = __init_col(bg_colors)
            
        # for future?
        self.row_h = 13.0

        super(SequenceFace,
              self).__init__(QGraphicsRectItem(0, 0, self.width,
                                               self.row_h))

       
    def update_items(self):
        #self.item = QGraphicsRectItem(0,0,self._total_w, self.row_h)
        seq_width = 0
        nopen = QPen(Qt.NoPen)
        font = QFont("Courier", self.fsize)
        rect_cls = self.InteractiveLetterItem if self.interact \
                   else QGraphicsRectItem
        for i, letter in enumerate(self.seq):
            width = self.col_w
            for reg in self.special_col:
                if reg[0] < i <= reg[1]:
                    width = self.alt_col_w
                    break
            #load interactive item if called correspondingly
            rectitem = rect_cls(0, 0, width, self.row_h, parent=self.item)
            rectitem.setX(seq_width) # to give correct X to children item
            rectitem.setBrush(self.bg_col[letter])
            rectitem.setPen(nopen)
            if self.interact:
                if self.codon:
                    rectitem.codon = '%s, %d: %s' % (self.seq[i], i,
                                                     self.codon[i*3:i*3+3])
                else:
                    rectitem.codon = '%s, %d' % (self.seq[i], i)
            # write letter if enough space
            if width >= self.fsize:
                text = QGraphicsSimpleTextItem(letter, parent=rectitem)
                text.setFont(font)
                text.setBrush(self.fg_col[letter])
                # Center text according to rectitem size
                txtw = text.boundingRect().width()
                txth = text.boundingRect().height()
                text.setPos((width - txtw)/2, (self.row_h - txth)/2)
            seq_width += width
        self.width = seq_width
    class InteractiveLetterItem(QGraphicsRectItem):
        """This is a class"""
        def __init__(self, *arg, **karg):
            QGraphicsRectItem.__init__(self, *arg, **karg)
            self.codon = None
            self.label = None
            self.setAcceptsHoverEvents(True)
    
        def hoverEnterEvent (self, e):
            """ when mouse is over"""
            if not self.label:
                self.label = QGraphicsRectItem(parent=self)
                #self.label.setY(-18)
                self.label.setX(11)
                self.label.setBrush(QBrush(QColor("white")))
                self.label.text = QGraphicsSimpleTextItem(parent=self.label)
    
            self.setZValue(1)
            self.label.text.setText(self.codon)
            self.label.setRect(self.label.text.boundingRect())
            self.label.setVisible(True)
    
        def hoverLeaveEvent(self, e):
            """when mouse leaves area"""
            if self.label:
                self.label.setVisible(False)
                self.setZValue(0)
                
