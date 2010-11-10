import math
import types
import copy
from PyQt4  import QtCore, QtGui, QtSvg
from PyQt4.QtGui import QPrinter

from qt4gui import _PropertiesDialog
import layouts

class _NodeItem(QtGui.QGraphicsRectItem):
    def __init__(self, node):
        self.node = node
        self.radius = node.img_style["size"]/2
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, self.radius*2, self.radius*2)

    def paint(self, p, option, widget):
        #QtGui.QGraphicsRectItem.paint(self, p, option, widget)
        if self.node.img_style["shape"] == "sphere":
            r = self.radius
            gradient = QtGui.QRadialGradient(r, r, r,(r*2)/3,(r*2)/3)
            gradient.setColorAt(0.05, QtCore.Qt.white);
            gradient.setColorAt(0.9, QtGui.QColor(self.node.img_style["fgcolor"]));
            p.setBrush(QtGui.QBrush(gradient))
            p.setPen(QtCore.Qt.NoPen)
            p.drawEllipse(self.rect())
        elif self.node.img_style["shape"] == "square":
            p.fillRect(self.rect(),QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))
        elif self.node.img_style["shape"] == "circle":
            p.setBrush(QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))
            p.setPen(QtGui.QPen(QtGui.QColor(self.node.img_style["fgcolor"])))
            p.drawEllipse(self.rect())

    def hoverEnterEvent (self,e):
        width = self.parentItem().mapFromScene(self.scene().i_width, 0).x()
        height = self.parentItem().rect().height()
        self.scene().highlighter.setRect(QtCore.QRectF(0, 0, \
                                                           width, height))
        self.scene().highlighter.setParentItem(self.parentItem())
        self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
        self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
        pass

    def mouseReleaseEvent(self,e):
        if e.button() == QtCore.Qt.RightButton:
            self.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
            self.scene().propertiesTable.update_properties(self.node)

    def showActionPopup(self):
        contextMenu = QtGui.QMenu()
        if self.node.collapsed:
            contextMenu.addAction( "Expand"           , self.toggle_collapse)
        else:
            contextMenu.addAction( "Collapse"         , self.toggle_collapse)

        contextMenu.addAction( "Set as outgroup"      , self.set_as_outgroup)
        contextMenu.addAction( "Swap branches"        , self.swap_branches)
        contextMenu.addAction( "Delete node"          , self.delete_node)
        contextMenu.addAction( "Delete partition"     , self.detach_node)
        contextMenu.addAction( "Add childs"           , self.add_childs)
        contextMenu.addAction( "Populate partition"   , self.populate_partition)
        if self.node.up is not None and\
                self.scene().startNode == self.node:
            contextMenu.addAction( "Back to parent", self.back_to_parent_node)
        else:
            contextMenu.addAction( "Extract"              , self.set_start_node)

        if self.scene().buffer_node:
            contextMenu.addAction( "Paste partition"  , self.paste_partition)

        contextMenu.addAction( "Cut partition"        , self.cut_partition)
        contextMenu.addAction( "Show newick"        , self.show_newick)
        contextMenu.exec_(QtGui.QCursor.pos())

    def show_newick(self):
        d = NewickDialog(self.node)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec_()
        return False

    def delete_node(self):
        self.node.delete()
        self.scene().draw()

    def detach_node(self):
        self.node.detach()
        self.scene().draw()

    def swap_branches(self):
        self.node.swap_childs()
        self.scene().draw()

    def add_childs(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Add childs","Number of childs to add:",1,1)
        if ok:
            for i in xrange(n):
                ch = self.node.add_child()
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)

    def void(self):
        return True

    def set_as_outgroup(self):
        self.scene().startNode.set_outgroup(self.node)
        self.scene().set_style_from(self.scene().startNode, self.scene().layout_func)
        self.scene().draw()

    def toggle_collapse(self):
        self.node.collapsed ^= True
        self.scene().draw()

    def cut_partition(self):
        self.scene().buffer_node = self.node
        self.node.detach()
        self.scene().draw()

    def paste_partition(self):
        if self.scene().buffer_node:
            self.node.add_child(self.scene().buffer_node)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)
            self.scene().buffer_node= None
            self.scene().draw()

    def populate_partition(self):
        n, ok = QtGui.QInputDialog.getInteger(None,"Populate partition","Number of nodes to add:",2,1)
        if ok:
            self.node.populate(n)
            self.scene().set_style_from(self.scene().startNode,self.scene().layout_func)
            self.scene().draw()

    def set_start_node(self):
        self.scene().startNode = self.node
        self.scene().draw()

    def back_to_parent_node(self):
        self.scene().startNode = self.node.up
        self.scene().draw()

class _ArcItem(QtGui.QGraphicsRectItem):
    def __init__(self, angle_start, angle_span, radius, *args):
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, radius, radius)
        self.angle_start = angle_span
        self.angle_span = angle_span
        self.radius = radius

    def paint(self, painter, option, index):
        rect = QtCore.QRectF(-self.radius, -self.radius, self.radius*2, self.radius*2);
        painter.setPen(self.pen())
        painter.drawArc(rect, self.angle_start, self.angle_span*16)
        painter.drawRect(rect)

class _TextItem(QtGui.QGraphicsSimpleTextItem):
    """ Manage faces on Scene"""
    def __init__(self,face,node,*args):
        QtGui.QGraphicsSimpleTextItem.__init__(self,*args)
        self.node = node
        self.face = face

    def hoverEnterEvent (self,e):
        partition = self.parentItem().parentItem()
        width = partition.mapFromScene(self.scene().i_width, 0).x()
        height = partition.rect().height()
        self.scene().highlighter.setRect(QtCore.QRectF(0, 0, \
                                                           width, height))
        self.scene().highlighter.setParentItem(partition)
        self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
        self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
        pass

    def mouseReleaseEvent(self,e):
        if e.button() == QtCore.Qt.RightButton:
            self.node._QtItem_.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
            self.scene().propertiesTable.update_properties(self.node)

class _FaceGroup(QtGui.QGraphicsItem): # I resisted to name this FaceBook :) 
    def __init__(self, faces, node, column_widths={}, *args, **kargs):
        QtGui.QGraphicsItem.__init__(self, *args, **kargs)
        self.node = node
        self.column2faces = faces
        
        # column_widths is a dictionary of min column size. Can be
        # used to reserve some space to specific columns
        self.set_min_column_widths(column_widths)

        self.w = 0
        self.h = 0
        # updates the size of this grid
        self.update_columns_size()

    def set_min_column_widths(self, column_widths):
        # column_widths is a dictionary of min column size. Can be
        # used to reserve some space to specific columns
        self.column_widths = column_widths
        self.columns = sorted(set(self.column2faces.keys()+self.column_widths.keys()))

    def paint(self, painter, option, index):
        return

    def boundingRect(self):
        return QtCore.QRectF(0,0, self.w, self.h)

    def get_size():
        return self.w, self.h

    def update_columns_size(self):
        self.column2size = {}
        for c in self.columns:
            faces = self.column2faces.get(c, [])
            height = 0
            width = 0
            for f in faces:
                f.node = self.node
                if f.type == "pixmap": 
                    f.update_pixmap()
                height += f._height()
                width = max(width, f._width())
            width = max(width, self.column_widths.get(c, 0))
            self.column2size[c] = (width, height)
        self.w = sum([0]+[size[0] for size in self.column2size.itervalues()])
        self.h = max([0]+[size[1] for size in self.column2size.itervalues()])

    def render(self):
        x = 0
        for c in self.columns:
            faces = self.column2faces.get(c, [])
            w, h = self.column2size[c]
            # Starting y position. Center columns
            y = (self.h / 2) - (h/2)
            for f in faces:
                if f.type == "text":
                    obj = _TextItem(f, self.node, f.get_text())
                    obj.setFont(f.font)
                    obj.setBrush(QtGui.QBrush(f.fgcolor))
                    obj.setParentItem(self)
                    obj.setAcceptsHoverEvents(True)
                else:
                    # Loads the pre-generated pixmap
                    obj = _FaceItem(f, self.node, f.pixmap)
                    obj.setAcceptsHoverEvents(True)
                    obj.setParentItem(self)
                obj.setPos(x, y)
                # Y position is incremented by the height of last face
                # in column
                y += f._height()
            # X position is incremented by the max width of the last
            # processed column.
            x += w

class _FaceItem(QtGui.QGraphicsPixmapItem):
    """ Manage faces on Scene"""
    def __init__(self, face, node, *args):
        QtGui.QGraphicsPixmapItem.__init__(self,*args)
        self.node = node
        self.face = face

    def hoverEnterEvent (self, e):
        partition = self.parentItem().parentItem()
        width = partition.mapFromScene(self.scene().i_width, 0).x()
        height = partition.rect().height()
        self.scene().highlighter.setRect(QtCore.QRectF(0, 0, \
                                                           width, height))
        self.scene().highlighter.setParentItem(partition)
        self.scene().highlighter.setVisible(True)

    def hoverLeaveEvent (self,e):
        self.scene().highlighter.setVisible(False)

    def mousePressEvent(self,e):
        pass

    def mouseReleaseEvent(self,e):
        if self.node:
            if e.button() == QtCore.Qt.RightButton:
                self.node._QtItem_.showActionPopup()
            elif e.button() == QtCore.Qt.LeftButton:
                self.scene().propertiesTable.update_properties(self.node)

class _PartitionItem(QtGui.QGraphicsRectItem):
    def __init__(self, node, *args):
        QtGui.QGraphicsRectItem.__init__(self, *args)
        self.node = node
        self.drawbg = False
    def paint(self, painter, option, index):
        if self.drawbg:
            return QtGui.QGraphicsRectItem.paint(self, painter, option, index)

class _SelectorItem(QtGui.QGraphicsRectItem):
    def __init__(self):
        self.Color = QtGui.QColor("blue")
        self._active = False
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0)

    def paint(self, p, option, widget):
        p.setPen(self.Color)
        p.drawRect(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height())
        return
        # Draw info text
        font = QtGui.QFont("Arial",13)
        text = "%d selected."  % len(self.get_selected_nodes())
        textR = QtGui.QFontMetrics(font).boundingRect(text)
        if  self.rect().width() > textR.width() and \
                self.rect().height() > textR.height()/2 and 0: # OJO !!!!
            p.setPen(QtGui.QPen(self.Color))
            p.setFont(QtGui.QFont("Arial",13))
            p.drawText(self.rect().bottomLeft().x(),self.rect().bottomLeft().y(),text)

    def get_selected_nodes(self):
        selPath = QtGui.QPainterPath()
        selPath.addRect(self.rect())
        self.scene().setSelectionArea(selPath)
        return [i.node for i in self.scene().selectedItems()]

    def setActive(self,bool):
        self._active = bool

    def isActive(self):
        return self._active

class _HighlighterItem(QtGui.QGraphicsRectItem):
    def __init__(self):
        self.Color = QtGui.QColor("red")
        self._active = False
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0)

    def paint(self, p, option, widget):
        p.setPen(self.Color)
        p.drawRect(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height())
        return

class _TreeScene(QtGui.QGraphicsScene):
    def __init__(self, rootnode=None, style=None, *args):
        QtGui.QGraphicsScene.__init__(self,*args)

        self.view = None
        # Config variables
        self.buffer_node = None        # Used to copy and paste
        self.layout_func = None        # Layout function
        self.startNode   = rootnode    # Node to start drawing
        self.scale       = 0           # Tree branch scale used to draw

        # Initialize scene 
        self.max_w_aligned_face = 0    # Stores the max width of aligned faces
        self.aligned_faces = []
        self.min_real_branch_separation = 0
        self.selectors  = []
        self._highlighted_nodes = {}
        self.node2faces = {}
        self.node2item = {}

        # Qt items
        self.selector = None
        self.mainItem = None        # Qt Item which is parent of all other items
        self.propertiesTable = _PropertiesDialog(self)
        self.border = None

    def initialize_tree_scene(self, tree, style, tree_properties):
        self.tree        = tree        # Pointer to original tree
        self.startNode   = tree        # Node to start drawing
        self.max_w_aligned_face = 0    # Stores the max width of aligned faces
        self.aligned_faces = []

        # Load image attributes
        self.props = tree_properties

        # Validates layout function
        if type(style) == types.FunctionType or\
                type(style) == types.MethodType:
            self.layout_func = style
        else:
            try:
                self.layout_func = getattr(layouts,style)
            except:
                raise ValueError, "Required layout is not a function pointer nor a valid layout name."

        # Set the scene background
        self.setBackgroundBrush(QtGui.QColor("white"))

        # Set nodes style
        self.set_style_from(self.startNode,self.layout_func)

        self.propertiesTable.update_properties(self.startNode)

    def highlight_node(self, n):
        self.unhighlight_node(n)
        r = QtGui.QGraphicsRectItem(self.mainItem)
        self._highlighted_nodes[n] = r

        R = n.fullRegion.getRect()
        width = self.i_width-n._x
        r.setRect(QtCore.QRectF(n._x,n._y,width,R[3]))
 
        #r.setRect(0,0, n.fullRegion.width(), n.fullRegion.height())

        #r.setPos(n.scene_pos)
        # Don't know yet why do I have to add 2 pixels :/
        #r.moveBy(0,0)
        r.setZValue(-1)
        r.setPen(QtGui.QColor(self.props.search_node_fg))
        r.setBrush(QtGui.QColor(self.props.search_node_bg))

        # self.view.horizontalScrollBar().setValue(n._x)
        # self.view.verticalScrollBar().setValue(n._y)

    def unhighlight_node(self, n):
        if n in self._highlighted_nodes and \
                self._highlighted_nodes[n] is not None:
            self.removeItem(self._highlighted_nodes[n])
            del self._highlighted_nodes[n]


    def mousePressEvent(self,e):
        self.selector.setRect(e.scenePos().x(),e.scenePos().y(),0,0)
        self.selector.startPoint = QtCore.QPointF(e.scenePos().x(),e.scenePos().y())
        self.selector.setActive(True)
        self.selector.setVisible(True)
        QtGui.QGraphicsScene.mousePressEvent(self,e)

    def mouseReleaseEvent(self,e):
        curr_pos = e.scenePos()
        x = min(self.selector.startPoint.x(),curr_pos.x())
        y = min(self.selector.startPoint.y(),curr_pos.y())
        w = max(self.selector.startPoint.x(),curr_pos.x()) - x
        h = max(self.selector.startPoint.y(),curr_pos.y()) - y
        if self.selector.startPoint == curr_pos:
            self.selector.setVisible(False)
        self.selector.setActive(False)
        QtGui.QGraphicsScene.mouseReleaseEvent(self,e)

    def mouseMoveEvent(self,e):

        curr_pos = e.scenePos()
        if self.selector.isActive():
            x = min(self.selector.startPoint.x(),curr_pos.x())
            y = min(self.selector.startPoint.y(),curr_pos.y())
            w = max(self.selector.startPoint.x(),curr_pos.x()) - x
            h = max(self.selector.startPoint.y(),curr_pos.y()) - y
            self.selector.setRect(x,y,w,h)
        QtGui.QGraphicsScene.mouseMoveEvent(self, e)

    def mouseDoubleClickEvent(self,e):
        QtGui.QGraphicsScene.mouseDoubleClickEvent(self,e)

    def save(self, imgName, w=None, h=None, header=None, \
                 dpi=150, take_region=False):
        ext = imgName.split(".")[-1].upper()

        root = self.startNode
        #aspect_ratio = root.fullRegion.height() / root.fullRegion.width()
        aspect_ratio = self.i_height / self.i_width

        # auto adjust size
        if w is None and h is None and (ext == "PDF" or ext == "PS"):
            w = dpi * 6.4
            h = w * aspect_ratio
            if h>dpi * 11:
                h = dpi * 11
                w = h / aspect_ratio
        elif w is None and h is None:
            w = self.i_width
            h = self.i_height
        elif h is None :
            h = w * aspect_ratio
        elif w is None:
            w = h / aspect_ratio

        if ext == "SVG": 
            svg = QtSvg.QSvgGenerator()
            svg.setFileName(imgName)
            svg.setSize(QtCore.QSize(w, h))
            svg.setViewBox(QtCore.QRect(0, 0, w, h))
            #svg.setTitle("SVG Generator Example Drawing")
            #svg.setDescription("An SVG drawing created by the SVG Generator")
            
            pp = QtGui.QPainter()
            pp.begin(svg)
            targetRect =  QtCore.QRectF(0, 0, w, h)
            self.render(pp, targetRect, self.sceneRect())
            pp.end()

        elif ext == "PDF" or ext == "PS":
            format = QPrinter.PostScriptFormat if ext == "PS" else QPrinter.PdfFormat
            printer = QPrinter(QPrinter.HighResolution)
            printer.setResolution(dpi)
            printer.setOutputFormat(format)
            printer.setPageSize(QPrinter.A4)
            
            pageTopLeft = printer.pageRect().topLeft()
            paperTopLeft = printer.paperRect().topLeft()
            # For PS -> problems with margins
            # print paperTopLeft.x(), paperTopLeft.y()
            # print pageTopLeft.x(), pageTopLeft.y()
            # print  printer.paperRect().height(),  printer.pageRect().height()
            topleft =  pageTopLeft - paperTopLeft

            printer.setFullPage(True);
            printer.setOutputFileName(imgName);
            pp = QtGui.QPainter(printer)
            if header:
                pp.setFont(QtGui.QFont("Verdana",12))
                pp.drawText(topleft.x(),20, header)
                targetRect =  QtCore.QRectF(topleft.x(), 20 + (topleft.y()*2), w, h)
            else:
                targetRect =  QtCore.QRectF(topleft.x(), topleft.y()*2, w, h)

            if take_region:
                self.selector.setVisible(False)
                self.render(pp, targetRect, self.selector.rect())
                self.selector.setVisible(True)
            else:
                self.render(pp, targetRect, self.sceneRect())
            pp.end()
            return
        else:
            targetRect = QtCore.QRectF(0, 0, w, h)
            ii= QtGui.QImage(w, \
                                 h, \
                                 QtGui.QImage.Format_ARGB32)
            pp = QtGui.QPainter(ii)
            pp.setRenderHint(QtGui.QPainter.Antialiasing )
            pp.setRenderHint(QtGui.QPainter.TextAntialiasing)
            pp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            if take_region:
                self.selector.setVisible(False)
                self.render(pp, targetRect, self.selector.rect())
                self.selector.setVisible(True)
            else:
                self.render(pp, targetRect, self.sceneRect())
            pp.end()
            ii.save(imgName)

    def draw_tree_surrondings(self):
        # Prepares and renders aligned face headers. Used to latter
        # place aligned faces
        column2max_width = {}
        aligned_face_headers = {}
        aligned_header = self.props.aligned_face_header
        aligned_foot = self.props.aligned_face_foot
        all_columns = set(aligned_header.keys() + aligned_foot.keys())
        header_afaces = {}
        foot_afaces = {}
        for c in all_columns:
            if c in aligned_header:
                faces = aligned_header[c]
                fb = _FaceGroup({0:faces}, None)
                fb.setParentItem(self.mainItem)
                header_afaces[c] = fb
                column2max_width[c] = fb.w
                
            if c in aligned_foot:
                faces = aligned_foot[c]
                fb = _FaceGroup({0:faces}, None)
                fb.setParentItem(self.mainItem)
                foot_afaces[c] = fb
                column2max_width[c] = max(column2max_width.get(c,0), fb.w)

        # Place aligned faces and calculates the max size of each
        # column (needed to place column headers)
        if self.props.draw_aligned_faces_as_grid: 
            for fb in self.aligned_faces:
                for c, size in fb.column2size.iteritems():
                    if size[0] > column2max_width.get(c, 0):
                        column2max_width[c] = size[0]

        # Place aligned faces
        for fb in self.aligned_faces:
            fb.set_min_column_widths(column2max_width)
            fb.update_columns_size()
            fb.render()
            pos = fb.mapFromScene(self.i_width, 0)
            fb.setPos(pos.x(), fb.y())
        
            if self.props.draw_lines_from_leaves_to_aligned_faces:
                guideline = QtGui.QGraphicsLineItem()
                partition = fb.parentItem()
                guideline.setParentItem(partition)
                guideline.setLine(partition.rect().width(), partition.center,\
                                  pos.x(), partition.center)
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(self.props.line_from_leaves_to_aligned_faces_color))
                set_pen_style(pen, self.props.line_from_leaves_to_aligned_faces_type)
                guideline.setPen(pen)

        # Place faces around tree
        x = self.i_width
        y = self.i_height
        max_up_height = 0
        max_down_height = 0
        for c in column2max_width:
            fb_up = header_afaces.get(c, None)
            fb_down = foot_afaces.get(c, None)
            fb_width = 0
            if fb_up: 
                fb_up.render()
                fb_up.setPos(x, -fb_up.h)
                fb_width = fb_up.w 
                max_up_height = max(max_up_height, fb_up.h)
            if fb_down:
                fb_down.render()
                fb_down.setPos(x, y)
                fb_width = max(fb_down.w, fb_width) 
                max_down_height = max(max_down_height, fb_down.h)
            x += column2max_width.get(c, fb_width)

        # updates image size
        self.i_width += sum(column2max_width.values())
        self.i_height += max_down_height + max_up_height
        self.mainItem.moveBy(0, max_up_height)

    def draw(self):
        # Clean previous items from scene by removing the main parent
        if self.mainItem:
            self.removeItem(self.mainItem)
            self.mainItem = None            
        if self.border:
            self.removeItem(self.border)
            self.border = None
        # Initialize scene 
        self.max_w_aligned_face = 0    # Stores the max width of aligned faces
        self.aligned_faces = []
        self.min_aligned_column_widths = {}

        self.min_real_branch_separation = 0
        self.selectors  = []
        self._highlighted_nodes = {}
        self.node2faces = {}
        self.node2item = {}
        self.node2ballmap = {}

        #Clean_highlighting rects
        for n in self._highlighted_nodes:
            self._highlighted_nodes[n] = None

        # Recreates main parent and add it to scene
        self.mainItem = QtGui.QGraphicsRectItem()
        self.addItem(self.mainItem)
        # Recreates selector item (used to zoom etc...)
        self.selector = _SelectorItem()
        self.selector.setParentItem(self.mainItem)
        self.selector.setVisible(False)
        self.selector.setZValue(2)

        self.highlighter = _HighlighterItem()
        self.highlighter.setParentItem(self.mainItem)
        self.highlighter.setVisible(False)
        self.highlighter.setZValue(2)
        self.min_real_branch_separation = 0

        # Get branch scale
        fnode, max_dist = self.startNode.get_farthest_leaf(topology_only=\
            self.props.force_topology)

        if max_dist>0:
            self.scale =  self.props.tree_width / max_dist
        else:
            self.scale =  1

        #self.update_node_areas(self.startNode)
        self.update_node_areas_rectangular(self.startNode)

        # Get tree picture dimensions
        self.i_width  = self.startNode.fullRegion.width()
        self.i_height = self.startNode.fullRegion.height()
        self.draw_tree_surrondings()

        # Draw scale
        scaleItem = self.get_scale()
        scaleItem.setParentItem(self.mainItem)
        scaleItem.setPos(0, self.i_height)
        self.i_height += scaleItem.rect().height()
        
        #Re-establish node marks
        for n in self._highlighted_nodes:
            self.highlight_node(n)

        self.setSceneRect(0,0, self.i_width, self.i_height)
        # Tree border
        if self.props.draw_image_border:
            self.border = self.addRect(0, 0, self.i_width, self.i_height)

    def get_tree_img_map(self):
        node_list = []
        face_list = []
        nid = 0
        for n, partition in self.node2item.iteritems():
            n.add_feature("_nid", str(nid))
            for item in partition.childItems():
                if isinstance(item, _NodeItem):
                    pos = item.mapToScene(0,0)
                    size = item.mapToScene(item.rect().width(), item.rect().height())
                    node_list.append([pos.x(),pos.y(),size.x(),size.y(), nid, None])
                elif isinstance(item, _FaceGroup):
                    for f in item.childItems():
                        pos = f.mapToScene(0,0)
                        if isinstance(f, _TextItem):
                            size = f.mapToScene(f.boundingRect().width(), \
                                                    f.boundingRect().height())
                            face_list.append([pos.x(),pos.y(),size.x(),size.y(), nid, str(f.text())])
                        else:
                            size = f.mapToScene(f.rect().width(), f.rect().height())
                            face_list.append([pos.x(),pos.y(),size.x(),size.y(), nid, None])
            nid += 1
        return {"nodes": node_list, "faces": face_list}

    def get_scale(self):
        length = 50
        scaleItem = _PartitionItem(None) # Unassociated to nodes
        scaleItem.setRect(0, 0, 50, 50)
        customPen = QtGui.QPen(QtGui.QColor("black"), 1)
        line = QtGui.QGraphicsLineItem(scaleItem)
        line2 = QtGui.QGraphicsLineItem(scaleItem)
        line3 = QtGui.QGraphicsLineItem(scaleItem)
        line.setPen(customPen)
        line2.setPen(customPen)
        line3.setPen(customPen)

        line.setLine(0, 5, length, 5)
        line2.setLine(0, 0, 0, 10)
        line3.setLine(length, 0, length, 10)
        scale_text = "%0.2f" % float(length/self.scale)
        scale = QtGui.QGraphicsSimpleTextItem(scale_text)
        scale.setParentItem(scaleItem)
        scale.setPos(0, 10)
       
        if self.props.force_topology:
            wtext = "Force topology is enabled!\nBranch lengths does not represent original values."
            warning_text = QtGui.QGraphicsSimpleTextItem(wtext)
            warning_text.setFont(QtGui.QFont("Arial", 8))
            warning_text.setBrush( QtGui.QBrush(QtGui.QColor("darkred")))
            warning_text.setPos(0, 32)
            warning_text.setParentItem(scaleItem)
        return scaleItem

    def set_style_from(self, node, layout_func):
        # I import dict at the moment of drawing, otherwise there is a
        # loop of imports between drawer and qt4render
        from drawer import NodeStyleDict 
        for n in node.traverse(): 
            if not hasattr(n, "img_style"):
                n.img_style = NodeStyleDict()
            elif isinstance(n.img_style, NodeStyleDict): 
                n.img_style.init()
            else:
                raise TypeError("img_style attribute in node %s is not of NodeStyleDict type." \
                                    %n.name)
            # Adding fixed faces during drawing is not allowed, since
            # added faces will not be tracked until next execution
            n.img_style._block_adding_faces = True
            try:
                layout_func(n)
            except Exception:
                n.img_style._block_adding_faces = False
                raise

    def update_node_faces(self, node):
        # Organize all faces of this node in FaceGroups objects
        # (tables of faces)
        faceblock = {}
        
        self.node2faces[node] = faceblock
        for position in ["branch-right", "aligned", "branch-top", "branch-bottom"] :
            if position in node.img_style["_faces"]:
                # The value of this is expected to be list of columns of faces
                # c2f = [ [f1, f2, f3], 
                #         [f4, f4]
                #       ]
                if position=="aligned" and not node.is_leaf():
                    faceblock[position] = _FaceGroup({}, node)
                    continue # aligned on internal node does not make sense
                else:
                    faceblock[position] = _FaceGroup(node.img_style["_faces"][position], node)
            else:
                faceblock[position] = _FaceGroup({}, node)
        return faceblock

    def update_node_areas_rectangular(self,root_node):

        ## General scheme on how nodes size are handled
        ## |==========================================================================================================================|
        ## |                                                fullRegion                                                                |       
        ## |             nodeRegion                  |================================================================================|
        ## |                                         |                                fullRegion                                     || 
        ## |                                         |        nodeRegion                     |=======================================||
        ## |                                         |                                       |         fullRegion                   |||
        ## |                                         |                                       |         nodeRegion                   ||| 
        ## |                                         |                         |             | xdist_offset | nodesize | facesRegion|||
        ## |                                         | xdist_offset | nodesize |facesRegion  |=======================================||
        ## |                                         |                         |             |=======================================||
        ## |                                         |                                       |             fullRegion                ||
        ## |                                         |                                       |             nodeRegion                ||
        ## |  branch-top     |          |            |                                       | xdist_offset | nodesize | facesRegion ||
        ## | xdist_offset    | nodesize |facesRegion |                                       |=======================================||
        ## |  branch-bottom  |          |            |================================================================================|
        ## |                                         |=======================================|                                        |
        ## |                                         |             fullRegion                |                                        |
        ## |                                         |        nodeRegion                     |                                        |
        ## |                                         | xdist_offset | nodesize | facesRegion |                                        |
        ## |                                         |=======================================|                                        |
        ## |==========================================================================================================================|
        ##
        ## Rendering means to create all QGraphicsItems that represent
        ## all node features. For this, I use an iterative function
        ## that creates a rectangleItem for each node in which all its
        ## features are included. The same tree node hierarchy is
        ## maintained for setting the parents items of partitions.
        ## Once a node has its partitionItem, elements are added to
        ## such partitionItem, and are positioned relative to the
        ## coordinate system of the parent.
        ## 
        ## A node partition contains the branch to its parent, the
        ## node circle, faces and the vertical line connecting childs

        n2i = self.node2item = {}
        visited = set()
        nodeStack = []
        nodeStack.append(root_node)
        while nodeStack:
            node = nodeStack[-1]
            finished = True
            if not _leaf(node): # node.img_style["draw_descendants"]:
                for c in node.children:
                    if c not in visited:
                        nodeStack.append(c)
                        finished = False
            # Here you have the preorder position of the node. 
            # node.visited_preorder
            if not finished:
                continue

            # Here you have the postorder position of the node. Now is
            # when I want to visit the node
            nodeStack.pop(-1)
            visited.add(node)

            # Branch length converted to pixels
            if self.props.force_topology:
                node.dist_xoffset = float(1.0 * self.scale)
            else:
                node.dist_xoffset = float(node.dist * self.scale)

            # Organize faces by groups
            faceblock = self.update_node_faces(node)

            # Total height required by the node
            h = node.__img_height__ = max(node.img_style["size"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
                                          node.img_style["hlwidth"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
                                          faceblock["branch-right"].h, 
                                          faceblock["aligned"].h, 
                                          self.props.min_branch_separation,
                                          )    

            # Total width required by the node
            w = node.__img_width__ = sum([max(node.dist_xoffset + node.img_style["size"], 
                                              faceblock["branch-top"].w + node.img_style["size"],
                                              faceblock["branch-bottom"].w + node.img_style["size"],
                                              ), 
                                          faceblock["branch-right"].w]
                                         )

            # Updates the max width spent by aligned faces
            if faceblock["aligned"].w > self.max_w_aligned_face:
                self.max_w_aligned_face = faceblock["aligned"].w

            # This prevents adding empty aligned faces from internal
            # nodes
            if faceblock["aligned"].column2faces:
                self.aligned_faces.append(faceblock["aligned"])

            # Rightside faces region
            node.facesRegion = QtCore.QRectF(0, 0, faceblock["branch-right"].w, faceblock["branch-right"].h)

            # Node region 
            node.nodeRegion = QtCore.QRectF(0, 0, w, h)
            if self.min_real_branch_separation < h:
                self.min_real_branch_separation = h

            if not _leaf(node):# node.is_leaf() and node.img_style["draw_descendants"]:
                widths, heights = zip(*[[c.fullRegion.width(),c.fullRegion.height()] \
                                          for c in node.children])
                w += max(widths)
                h = max(node.nodeRegion.height(), sum(heights))

            # This is the node total region covered by the node
            node.fullRegion = QtCore.QRectF(0, 0, w, h)

            # ------------------ RENDERING ---------------------------
            # Creates a rectItem representing the node partition. Its
            # size was calculate in update_node_areas. This partition
            # groups all its child partitions
            partition = self.node2item[node] = \
                _PartitionItem(node, 0, 0, node.fullRegion.width(), node.fullRegion.height())

            # Draw virtual partition grid (for debugging)
            # partition.setPen(QtGui.QColor("yellow"))
            # color = QtGui.QColor("#cccfff")
            # color = QtGui.QColor("#ffffff")
            # partition.setBrush(color)
            # partition.setPen(color)

            # Faceblock parents
            for f in faceblock.values():
                f.setParentItem(partition)

            if _leaf(node): #node.is_leaf() or not node.img_style["draw_descendants"]:
                # Leafs will be processed from parents
                partition.center = self.get_partition_center(node)
                continue
            else:
                parent_partition = partition
                # set position of child partitions
                x = node.nodeRegion.width()
                y = 0
                all_childs_height = sum([c.fullRegion.height() for c in node.children])
                if node.fullRegion.height() > all_childs_height:
                    y += ((node.fullRegion.height() - all_childs_height))/2
                for c in node.children:
                    cpart = n2i[c]
                    # Sets x and y position of child within parent
                    # partition (relative positions)
                    cpart.setParentItem(parent_partition)
                    cpart.start_y = y 
                    cpart.start_x = x
                    cpart.setPos(x, y)

                    # Increment y for the next child within partition
                    y += c.fullRegion.height()
                    # Build all node's associated items
                    self.render_node_partition(c, cpart)
                # set partition center that will be used for parent nodes
                partition.center = self.get_partition_center(node)

        # Render root node and set its positions
        partition = n2i[root_node]
        partition.setParentItem(self.mainItem)
        partition.center = self.get_partition_center(root_node)
        self.render_node_partition(root_node, partition)
        for part in self.node2item.values():
            # save absolute position in scene (used for maps and
            # highlighting)
            abs_pos = part.mapToScene(0, 0)
            part.abs_startx = abs_pos.x()
            part.abs_starty = abs_pos.y()

    def update_node_areas_radial(self,root_node):
        """ UNFINISHED! """

        center_item = QtGui.QGraphicsRectItem(0,0,3,3)
        center_item.setPen(QtGui.QColor("#ff0000"))
        center_item.setBrush(QtGui.QColor("#ff0000"))
        n2a = {}
        angle_step = 360./len(root_node)
        next_angle = 0
        n2i = self.node2item = {}
        visited = set()
        nodeStack = []
        nodeStack.append(root_node)
        while nodeStack:
            node = nodeStack[-1]
            finished = True
            if not _leaf(node): #node.img_style["draw_descendants"]:
                for c in node.children:
                    if c not in visited:
                        nodeStack.append(c)
                        finished = False

            ## Here you have the preorder position of the node. 
            # ... node.before_go_for_childs = blah ...
            if not finished:
                continue

            # Here you have the postorder position of the node. Now is
            # when I want to visit the node
            nodeStack.pop(-1)
            visited.add(node)

            # Branch length converted to pixels
            if self.props.force_topology:
                node.dist_xoffset = 60
            else:
                node.dist_xoffset = float(node.dist * self.scale)

            # Organize faces by groups
            faceblock = self.update_node_faces(node)

            # Total height required by the node
            h = node.__img_height__ = max(node.img_style["size"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
                                          node.img_style["hlwidth"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
                                          faceblock["branch-right"].h, 
                                          faceblock["aligned"].h, 
                                          self.props.min_branch_separation,
                                          )    

            # Total width required by the node
            w = node.__img_width__ = sum([max(node.dist_xoffset + node.img_style["size"], 
                                              faceblock["branch-top"].w + node.img_style["size"],
                                              faceblock["branch-bottom"].w + node.img_style["size"],
                                              ), 
                                          faceblock["branch-right"].w]
                                         )

            # Updates the max width spend by aligned faces
            if faceblock["aligned"].w > self.max_w_aligned_face:
                self.max_w_aligned_face = faceblock["aligned"].w

            # Rightside faces region
            node.facesRegion = QtCore.QRectF(0, 0, faceblock["branch-right"].w, faceblock["branch-right"].h)

            # Node region 
            node.nodeRegion = QtCore.QRectF(0, 0, w, h)
            if self.min_real_branch_separation < h:
                self.min_real_branch_separation = h

            if not _leaf(node): #node.is_leaf() and node.img_style["draw_descendants"]:
                widths, heights = zip(*[[c.fullRegion.width(),c.fullRegion.height()] \
                                          for c in node.children])
                w += max(widths)
                h = max(node.nodeRegion.height(), sum(heights))

            # This is the node total region covered by the node
            node.fullRegion = QtCore.QRectF(0, 0, w, h)
            
            # ------------------ RENDERING ---------------------------
            # Creates a rectItem representing the node partition. Its
            # size was calculate in update_node_areas. This partition
            # groups all its child partitions
           
            partition = self.node2item[node] = \
                _PartitionItem(node, 0, 0, node.fullRegion.width(), node.fullRegion.height())

            # Draw virtual partition grid (for debugging)
            #color = QtGui.QColor("#cccfff")
            #color = QtGui.QColor("#ffffff")
            #partition.setBrush(color)
            #partition.setPen(color)

            if node.is_leaf() or not node.img_style["draw_descendants"]:
                # Leafs will be processed from parents
                partition.angle = next_angle
                partition.angle_start = next_angle
                partition.angle_span = partition.angle_start + angle_step
                next_angle+= angle_step
            else:
                p1 = n2i[node.children[0]]
                p2 = n2i[node.children[-1]]
                partition.angle = p2.angle_start + p2.angle_span - p1.angle_start
                partition.angle_start = p1.angle_start - (p1.angle_span/2)
                partition.angle_span = p2.angle_start - (p2.angle_span/2) - partition.angle_start
    
            #partition.setParentItem(center_item)
            b = node.nodeRegion.height()
            a = node.nodeRegion.width()
            A = partition.angle
            radius = math.sqrt( (b/2*math.atan(A))**2 + a**2  + (b/2)**2 )
            print radius, partition.angle_start

            arc = _ArcItem(partition.angle_start, partition.angle_span, radius)

            n2a[node] = arc            

            for c in node.children:
                cpart = n2i[c]
                cpart.setParentItem(arc)
                carc = n2a[c]
                carc.setParentItem(arc)
                self.render_node_partition(node, cpart)
            
        arc.setParentItem(center_item)
        arc.setPen(QtGui.QColor("#0000ff"))
        center_item.setParentItem(self.mainItem)
        center_item.setPos(200,200)
        # Render root node and set its positions

    def rotate_node(self,node,angle,x=None,y=None):
        if x and y:
            x = node.fullRegion.width()/2
            y = node.fullRegion.height()/2
            node._QtItem_.setTransform(QtGui.QTransform().translate(x, y).rotate(angle).translate(-x, -y));
        else:
            node._QtItem_.rotate(angle)

    def get_partition_center(self, n):
        down = self.node2faces[n]["branch-bottom"].h
        up = self.node2faces[n]["branch-top"].h

        if _leaf(n): #n.is_leaf() or not n.img_style["draw_descendants"]:
            center = n.fullRegion.height()/2
        else:
            first_child_part = self.node2item[n.children[0]]
            last_child_part = self.node2item[n.children[-1]]
            c1 = first_child_part.start_y + first_child_part.center
            c2 = last_child_part.start_y + last_child_part.center
            center = c1+ (c2-c1)/2

        if up > center:
            center = up
        elif down > n.fullRegion.height()-center:
            center = n.fullRegion.height()-down
        return center
            
    def render_node_partition(self, node, partition):
        style = node.img_style
        if style["bgcolor"].upper() not in set(["#FFFFFF", "white"]): 
            color = QtGui.QColor(style["bgcolor"])
            partition.setBrush(color)
            partition.setPen(color)
            partition.drawbg = True

        # Draw partition components 
        # Draw node balls in the partition centers
        ball_size = style["size"] 
        ball_start_x = node.nodeRegion.width() - node.facesRegion.width() - ball_size
        node_ball = _NodeItem(node)
        node_ball.setParentItem(partition)            
        node_ball.setPos(ball_start_x, partition.center-(ball_size/2))
        node_ball.setAcceptsHoverEvents(True)

        self.node2ballmap[node] = node_ball

        # Hz line
        hz_line = QtGui.QGraphicsLineItem(partition)
        hz_line.setLine(0, partition.center, 
                        node.dist_xoffset, partition.center)
        # Hz line style
        color = QtGui.QColor(style["hz_line_color"])
        pen = QtGui.QPen(color)
        set_pen_style(pen, style["line_type"])
        hz_line.setPen(pen)

        if self.props.complete_branch_lines:
            extra_hz_line = QtGui.QGraphicsLineItem(partition)
            extra_hz_line.setLine(node.dist_xoffset, partition.center, 
                            ball_start_x, partition.center)
            color = QtGui.QColor(self.props.extra_branch_line_color)
            pen = QtGui.QPen(color)
            set_pen_style(pen, style["line_type"])
            extra_hz_line.setPen(pen)

        # Attach branch-right faces to child 
        fblock = self.node2faces[node]["branch-right"]
        fblock.setParentItem(partition)
        fblock.render()
        fblock.setPos(node.nodeRegion.width()-node.facesRegion.width(), \
                              partition.center-fblock.h/2)
                
        # Attach branch-bottom faces to child 
        fblock = self.node2faces[node]["branch-bottom"]
        fblock.setParentItem(partition)
        fblock.render()
        fblock.setPos(0, partition.center)
        
        # Attach branch-top faces to child 
        fblock = self.node2faces[node]["branch-top"]
        fblock.setParentItem(partition)
        fblock.render()
        fblock.setPos(0, partition.center-fblock.h)

        if node.is_leaf():
            # Attach aligned faces to node. x position will be
            # modified after rendering the whole tree
            fblock = self.node2faces[node]["aligned"]
            fblock.setParentItem(partition)
            # Rendering is delayed until I know right positions 

        # Vt Line
        if not _leaf(node): #node.is_leaf() and style["draw_descendants"]==1:
            vt_line = QtGui.QGraphicsLineItem(partition)
            first_child_part = self.node2item[node.children[0]]
            last_child_part = self.node2item[node.children[-1]]
            c1 = first_child_part.start_y + first_child_part.center
            c2 = last_child_part.start_y + last_child_part.center
            vt_line.setLine(node.nodeRegion.width(), c1,\
                                node.nodeRegion.width(), c2)            
            # Vt line style
            pen = QtGui.QPen(QtGui.QColor(style["vt_line_color"])) 
            set_pen_style(pen, style["line_type"])
            vt_line.setPen(pen)

def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)

def _leaf(node):
    """ Returns true if node is a leaf or if draw_descendants style is
    set to false """ 
    if node.is_leaf() or not node.img_style.get("draw_descendants", True):
        return True
    return False

    
