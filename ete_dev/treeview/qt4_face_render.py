import random
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QGraphicsSimpleTextItem, QGraphicsPixmapItem, \
    QGraphicsRectItem, QTransform, QBrush, QPen, QColor, QGraphicsItem

from main import FACE_POSITIONS
from node_gui_actions import _NodeActions as _ActionDelegator

class _TextFaceItem(QGraphicsSimpleTextItem, _ActionDelegator):
    def __init__(self, face, node, text):
        QGraphicsSimpleTextItem.__init__(self, text)
        _ActionDelegator.__init__(self)
        self.node = node

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

class _FaceGroupItem(QGraphicsRectItem): # I resisted to name this FaceBookItem :) 
    def __init__(self, faces, node, as_grid=False):

        # This caused seg. faults. in some computers. No idea why.
        # QtGui.QGraphicsItem.__init__(self, *args, **kargs) 
        QGraphicsRectItem.__init__(self)  
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

        for c, faces in self.column2faces.iteritems():
            self.sizes[c] = {}
            total_height = 0
            for r, f in enumerate(faces):
                f.node = self.node
                if f.type == "pixmap": 
                    f.update_pixmap()
                elif f.type == "item":
                    f.update_items()

                width = f._width() + f.margin_right + f.margin_left
                height = f._height() + f.margin_top + f.margin_bottom
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

        self.as_grid = as_grid
        self.update_columns_size()
        return self.c2max_w, self.r2max_h
  

    def render(self):
        x = 0
        for c, max_w in self.c2max_w.iteritems(): 
            faces = self.column2faces.get(c, [])

            if self.as_grid:
                y = 0
            else:
                y = (self.h - self.c2height.get(c,0))/2

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

                # relative alignemnt of faces
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

                obj.setPos(x + f.margin_left + x_offset,\
                               y + y_offset + f.margin_top)

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

            x += max_w

    def rotate(self, rotation):
        "rotates item over its own center"
        for obj in self.childItems():
            if hasattr(obj, "rotable") and obj.rotable:
                rect = obj.boundingRect()
                x =  rect.width()/2
                y =  rect.height()/2
                obj.setTransform(QTransform().translate(x, y).rotate(rotation).translate(-x, -y))

    def flip_hz(self):
        for obj in self.childItems():
            rect = obj.boundingRect()
            x =  rect.width()/2
            y =  rect.height()/2
            obj.setTransform(QTransform().translate(x, y).scale(-1,1).translate(-x, -y))

    def flip_vt(self):
        for obj in self.childItems():
            rect = obj.boundingRect()
            x =  rect.width()/2
            y =  rect.height()/2
            obj.setTransform(QTransform().translate(x, y).scale(1,-1).translate(-x, -y))

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

def _leaf(node):
    collapsed = hasattr(node, "img_style") and not node.img_style["draw_descendants"]
    return collapsed or node.is_leaf()


