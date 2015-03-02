# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
import random
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QGraphicsSimpleTextItem, QGraphicsPixmapItem, \
    QGraphicsRectItem, QTransform, QBrush, QPen, QColor, QGraphicsItem

from main import FACE_POSITIONS, _leaf
from node_gui_actions import _NodeActions as _ActionDelegator
from math import pi, cos, sin

class _TextFaceItem(QGraphicsSimpleTextItem, _ActionDelegator):
    def __init__(self, face, node, text):
        QGraphicsSimpleTextItem.__init__(self, text)
        _ActionDelegator.__init__(self)
        self.node = node
        self.face = face
        self._bounding_rect = self.face.get_bounding_rect()
        self._real_rect = self.face.get_real_rect()
    def boundingRect(self):
        return self._bounding_rect

class _ImgFaceItem(QGraphicsPixmapItem, _ActionDelegator):
    def __init__(self, face, node, pixmap):
        QGraphicsPixmapItem.__init__(self, pixmap)
        _ActionDelegator.__init__(self)
        self.node = node

class _BackgroundFaceItem(QGraphicsRectItem):
    def __init__(self, face, node):
        QGraphicsRectItem.__init__(self)
        self.node = node

    def paint(self, painter, option, index):
        return
        
class _FaceGroupItem(QGraphicsRectItem): # I was about to name this FaceBookItem :)
    def paint(self, painter, option, index):
        "Avoid little dots in acrobat reader"
        return
    
    def __init__(self, faces, node, as_grid=False):

        # This caused seg. faults. in some computers. No idea why.
        # QtGui.QGraphicsItem.__init__(self, *args, **kargs) 
        QGraphicsRectItem.__init__(self, 0, 0, 0, 0)
        
        self.as_grid = as_grid
        self.c2max_w = {}
        self.r2max_h = {}
        self.node = node
        self.column2faces = faces
        self.column2size = {}
        self.columns = sorted(set(self.column2faces.keys()))
        
        # Two dictionaries containing min column size. Can be used to
        # reserve some space to specific columns and draw FaceBlocks
        # like tables.
        self.column_widths = {}
        self.row_heights = {}

        self.w = 0
        self.h = 0
        # updates the size of this grid
        self.update_columns_size()

    def set_min_column_widths(self, column_widths):
        # column_widths is a dictionary of min column size. Can be
        # used to reserve horizontal space to specific columns
        self.column_widths = column_widths
        self.columns = sorted(set(self.column2faces.keys() + self.column_widths.keys()))

    def set_min_column_heights(self, column_heights):
        # column_widths is a dictionary of min column size. Can be
        # used to reserve vertical space to specific columns
        self.row_heights = column_heights

    #def paint(self, painter, option, index):
    #    return

    def boundingRect(self):
        return QtCore.QRectF(0,0, self.w, self.h)

    def rect(self):
        return QtCore.QRectF(0,0, self.w, self.h)

    def get_size(self):
        return self.w, self.h

    def update_columns_size(self):
        self.sizes = {}
        self.c2height = {}

        for c in self.columns:
            faces = self.column2faces.get(c, [])
            self.sizes[c] = {}
            total_height = 0
            for r, f in enumerate(faces):
                f.node = self.node
                if f.type == "pixmap": 
                    f.update_pixmap()
                elif f.type == "item":
                    f.update_items()
                elif f.type == "text" and f.rotation:
                    f.tight_text = False

                width = f._width() + f.margin_right + f.margin_left
                height = f._height() + f.margin_top + f.margin_bottom
                   
                if f.rotation:
                    if f.rotation == 90 or f.rotation == 270:
                        width, height = height, width
                    elif f.rotation == 180:
                        pass
                    else:
                        x0 =  width/2.0
                        y0 =  height/2.0
                        theta = (f.rotation * pi)/180
                        trans = lambda x, y: (x0+(x-x0)*cos(theta) + (y-y0)*sin(theta), y0-(x-x0)*sin(theta)+(y-y0)*cos(theta))
                        coords = (trans(0,0), trans(0,height), trans(width,0), trans(width,height))
                        x_coords = [e[0] for e in coords]
                        y_coords = [e[1] for e in coords]
                        width = max(x_coords) - min(x_coords)
                        height = max(y_coords) - min(y_coords)

                self.sizes[c][r] = [width, height]
                self.c2max_w[c] = max(self.c2max_w.get(c, 0), width)
                self.r2max_h[r] = max(self.r2max_h.get(r, 0), height)
                total_height += height
            self.c2height[c] = total_height
                    
        if not self.sizes:
            return 

        if self.as_grid:
            self.h = max( [sum([self.r2max_h[r] for r in rows.iterkeys()]) for c, rows in self.sizes.iteritems()])
        else:
            self.h = max( [self.c2height[c] for c in self.sizes.iterkeys()])

        self.w = sum(self.c2max_w.values())
        #self.setRect(0, 0, self.w+random.randint(1,5), self.h)
        #pen = QtGui.QPen()
        #pen.setColor(QtGui.QColor("red"))
        #self.setPen(pen)

    def setup_grid(self, c2max_w=None, r2max_h=None, as_grid=True):
        if c2max_w: 
            self.c2max_w = c2max_w
        
        if r2max_h: 
            self.r2max_h = r2max_h

        # complete missing face columns 
        if self.columns:
            self.columns = range(min(self.c2max_w), max(self.c2max_w)+1)

        self.as_grid = as_grid
        self.update_columns_size()
        return self.c2max_w, self.r2max_h
  

    def render(self):
        x = 0
        for c in self.columns:
            max_w = self.c2max_w[c]
            faces = self.column2faces.get(c, [])

            if self.as_grid:
                y = 0
            else:
                y = (self.h - self.c2height.get(c,0)) / 2

            for r, f in enumerate(faces):
                w, h = self.sizes[c][r]
                if self.as_grid: 
                    max_h = self.r2max_h[r]
                else:
                    max_h = h

                f.node = self.node
                if f.type == "text":
                    obj = _TextFaceItem(f, self.node, f.get_text())
                    font = f._get_font()
                    obj.setFont(font)
                    obj.setBrush(QBrush(QColor(f.fgcolor)))
                elif f.type == "item":
                    obj = f.item
                else:
                    # Loads the pre-generated pixmap
                    obj = _ImgFaceItem(f, self.node, f.pixmap)

                obj.setAcceptsHoverEvents(True)
                obj.setParentItem(self)

                x_offset, y_offset = 0, 0 
               
                if max_w > w:
                    # Horizontally at the left
                    if f.hz_align == 0:
                        x_offset = 0
                    elif f.hz_align == 1:
                        # Horizontally centered
                        x_offset = (max_w - w) / 2  
                    elif f.hz_align == 2:
                        # At the right
                        x_offset = (max_w - w)
                
                if max_h > h:
                    if f.vt_align == 0:
                        # Vertically on top
                        y_offset = 0
                    elif f.vt_align == 1:
                        # Vertically centered
                        y_offset = (max_h - h) / 2
                    elif f.hz_align == 2:
                        # Vertically at bottom
                        y_offset = (max_h - h) 

                # Correct cases in which object faces has negative
                # starting points
                #obj_rect = obj.boundingRect()
                #_pos = obj_rect.topLeft()
                #_x = abs(_pos.x()) if _pos.x() < 0 else 0
                #_y = abs(_pos.y()) if _pos.y() < 0 else 0

                text_y_offset = -obj.boundingRect().y() if f.type == "text" else 0 

                obj.setPos(x + f.margin_left + x_offset,
                           y + y_offset + f.margin_top + text_y_offset)
                
                if f.rotation and f.rotation != 180:
                    fake_rect = obj.boundingRect()
                    fake_w, fake_h = fake_rect.width(), fake_rect.height()
                    self._rotate_item(obj, f.rotation)
                    #wcorr = fake_w/2.0 - w/2.0
                    #ycorr = fake_h/2.0 - h/2.0 
                    #print "Correctopm", fake_w/2.0 - w/2.0, fake_h/2.0 - h/2
                    #obj.moveBy(-wcorr, -ycorr)
                    obj.moveBy(((w/2) - fake_w/2.0), (h/2) - (fake_h/2.0))
                    #r = QGraphicsRectItem(0, 0, w, h)
                    #r.setParentItem(self)

                obj.rotable = f.rotable
                f.inner_background.apply(obj)
                f.inner_border.apply(obj)

                bg = f.background.apply(obj)
                border = f.border.apply(obj)
                if border:
                    border.setRect(x, y, max_w, max_h)
                    border.setParentItem(self)
                if bg:
                    bg.setRect(x, y, max_w, max_h)
                    bg.setParentItem(self)

                if f.opacity < 1:
                    obj.setOpacity(f.opacity)

                if self.as_grid:
                    y += max_h
                else:
                    y += h

                # set label of the face if possible
                try:
                    obj.face_label = f.label
                except AttributeError:
                    pass
                obj.face_type = str(type(f)).split(".")[-1]
                                
            x += max_w

    def _rotate_item(self, item, rotation):
        if hasattr(item, "_real_rect"):
            rect = item._real_rect
        else:
            rect = item.boundingRect()
        x = rect.width()/2
        y = rect.height()/2
        matrix = item.transform()
        #item.setTransform(QTransform().translate(x, y).rotate(rotation).translate(-x, -y))
        item.setTransform(matrix.translate(x, y).rotate(rotation).translate(-x, -y))

    def rotate(self, rotation):
        "rotates item over its own center"
        for obj in self.childItems():
            if hasattr(obj, "rotable") and obj.rotable:
                if hasattr(obj, "_real_rect"):
                    # to avoid incorrect rotation of tightgly wrapped
                    # text items we need to rotate using the real
                    # wrapping rect and revert y_text correction.
                    yoff = obj.boundingRect().y()
                    rect = obj._real_rect
                    # OJO!! this only works for the rotation of text
                    # faces in circular mode. Other cases are
                    # unexplored!!
                    obj.moveBy(0, yoff*2)
                else:
                    yoff = None
                    rect = obj.boundingRect()
                x = rect.width() / 2 
                y = rect.height() / 2
                matrix = obj.transform()
                #obj.setTransform(QTransform().translate(x, y).rotate(rotation).translate(-x, -y))
                obj.setTransform(matrix.translate(x, y).rotate(rotation).translate(-x, -y))
                
    def flip_hz(self):
        for obj in self.childItems():
            rect = obj.boundingRect()
            x =  rect.width() / 2
            y =  rect.height() / 2
            matrix = obj.transform()
            #obj.setTransform(QTransform().translate(x, y).scale(-1,1).translate(-x, -y))
            obj.setTransform(matrix.translate(x, y).scale(-1,1).translate(-x, -y))
            
    def flip_vt(self):
        for obj in self.childItems():
            rect = obj.boundingRect()
            x =  rect.width() / 2
            y =  rect.height() / 2
            matrix = obj.transform()
            #obj.setTransform(QTransform().translate(x, y).scale(1,-1).translate(-x, -y))
            obj.setTransform(matrix.translate(x, y).scale(1,-1).translate(-x, -y))


            
def update_node_faces(node, n2f, img):

    # Organize all faces of this node in FaceGroups objects
    # (tables of faces)
    faceblock = {}

    n2f[node] = faceblock
    for position in FACE_POSITIONS:
        # _temp_faces.position = 
        #  1: [f1, f2, f3], 
        #  2: [f4, f4], 
        #  ... 

        # In case there are fixed faces 
        fixed_faces =  getattr(getattr(node, "faces", None) , position, {})

        # _temp_faces should be initialized by the set_style funcion
        all_faces = getattr(node._temp_faces, position)
        for column, values in fixed_faces.iteritems():
            all_faces.setdefault(column, []).extend(values) 

        if position == "aligned" and img.draw_aligned_faces_as_table:
            as_grid = False
        else:
            as_grid = False

        faceblock[position] = _FaceGroupItem(all_faces, node, as_grid=as_grid)

    # all temp and fixed faces are now referenced by the faceblock, so
    # we can clear the node temp faces (don't want temp faces to be
    # replicated with copy or dumped with cpickle)
    node._temp_faces = None
        
    return faceblock
