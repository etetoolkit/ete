import re
from PyQt4 import QtCore, QtGui

from main import _leaf, NodeStyleDict
from qt4_gui import _PropertiesDialog, _NodeActions
from qt4_face_render import update_node_faces
import qt4_circular_render as crender
import qt4_rect_render as rrender

## | General scheme on nodes attributes
## |==========================================================================================================================|
## |                                                fullRegion                                                                |       
## |             nodeRegion                  |================================================================================|
## |                                         |                                fullRegion                                     || 
## |                                         |        nodeRegion                     |=======================================||
## |                                         |                                       |         fullRegion                   |||
## |                                         |                                       |         nodeRegion                   ||| 
## |                                         |                         |             |branch_length | nodeSize | facesRegion|||
## |                                         | branch_length | nodesize|faces-right  |=======================================||
## |                                         |                         |(facesRegion)|=======================================||
## |                                         |                                       |             fullRegion                ||
## |                                         |                                       |             nodeRegion                ||
## |  faces-top     |          |             |                                       | branch_length | nodeSize | facesRegion||
## | branch_length  | NodeSize |faces-right  |                                       |=======================================||
## |  faces-bottom  |          |(facesRegion)|================================================================================|
## |                                         |=======================================|                                        |
## |                                         |             fullRegion                |                                        |
## |                                         |        nodeRegion                     |                                        |
## |                                         | branch_length | nodeSize | facesRegion|                                        |
## |                                         |=======================================|                                        |
## |==========================================================================================================================|


class _NodePointItem(QtGui.QGraphicsRectItem):
    def __init__(self, node):
        self.node = node
        self.radius = node.img_style["size"]/2
        self.diam = self.radius*2
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, self.diam, self.diam)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    def paint(self, p, option, widget):
        crender.increase()
        p.setClipRect( option.exposedRect )
        if self.node.img_style["shape"] == "sphere":
            r = self.radius
            d = self.diam
            gradient = QtGui.QRadialGradient(r, r, r,(d)/3,(d)/3)
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
            
class _NodeItem(QtGui.QGraphicsItemGroup, _NodeActions):
    def __init__(self, node, parent):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self.node = node
        self.nodeRegion = QtCore.QRectF()
        self.facesRegion = QtCore.QRectF()
        self.fullRegion = QtCore.QRectF()
        self.highlighted = False
        self.setAcceptsHoverEvents(True)

class _LineItem(QtGui.QGraphicsLineItem):
    def paint(self, painter, option, widget):
        QtGui.QGraphicsLineItem.paint(self, painter, option, widget)


def render(root_node, img, hide_root=False):
    n2i = {}
    n2f = {}
    mode = img.mode
    scale = img.scale
    arc_span = img.arc_span 
    last_rotation = -90 + img.arc_start
    layout_fn = img._layout_fn 

    parent = QtGui.QGraphicsRectItem(0, 0, 0, 0)
    visited = set()
    to_visit = []
    to_visit.append(root_node)
    rot_step = float(arc_span) / len([n for n in root_node.traverse() if _leaf(n)])
    # ::: Precalculate values :::
    while to_visit:
        node = to_visit[-1]
        finished = True
        if node not in n2i:
            # Set style according to layout function
            set_style(node, layout_fn)
            item = n2i[node] = _NodeItem(node, parent)
            if mode == "circular":
                # ArcPartition all hang from a same parent item
                item.bg = crender.ArcPartition(item)
                #item.addToGroup(item.bg)
            elif mode == "rect":
            #    # RectPartition are nested, so parent will be modified
            #    # later on
                item.bg = rrender.RectPartition(parent)

            if node is root_node and hide_root:
                pass
            else:
                set_node_size(node, n2i, n2f, scale)
        if not _leaf(node):
            # visit children starting from left most to right
            # most. Very important!! check all children[-1] and
            # children[0]
            for c in reversed(node.children):
                if c not in visited:
                    to_visit.append(c)
                    finished = False
            # :: pre-order code here ::
        if not finished:
            continue
        else:
            to_visit.pop(-1)
            visited.add(node)

        # :: Post-order visits. Leaves are visited before parents ::
        if mode == "circular": 
            if _leaf(node):
                crender.init_circular_leaf_item(node, n2i, n2f, last_rotation, rot_step)
                last_rotation += rot_step
            else:
                crender.init_circular_node_item(node, n2i, n2f)

        elif mode == "rect": 
            if _leaf(node):
                rrender.init_rect_leaf_item(node, n2i, n2f)
            else:
                rrender.init_rect_node_item(node, n2i, n2f)

            item.bg.setRect(item.fullRegion)

        if node is not root_node or not hide_root: 
            render_node_content(node, n2i, n2f, scale, mode)

    if mode == "circular":
        max_r = crender.render_circular(root_node, n2i, rot_step)
        parent.moveBy(max_r, max_r)
        parent.setRect(-max_r, -max_r, max_r*2, max_r*2) 
    else:
        parent.setRect(n2i[root_node].fullRegion)

    return parent, n2i, n2f

def set_node_size(node, n2i, n2f, scale):
    item = n2i[node]
    branch_length = float(node.dist * scale)
    min_branch_separation = 3

    # Organize faces by groups
    faceblock = update_node_faces(node, n2f)

    # Total height required by the node
    h = max(node.img_style["size"], 
            (node.img_style["size"]/2) + node.img_style["hz_line_width"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
            faceblock["branch-right"].h, 
            faceblock["aligned"].h, 
            min_branch_separation,
            )    

    # Total width required by the node
    w = sum([max(branch_length + node.img_style["size"], 
                                      faceblock["branch-top"].w + node.img_style["size"],
                                      faceblock["branch-bottom"].w + node.img_style["size"],
                                      ), 
                                  faceblock["branch-right"].w]
                                 )
    w += node.img_style["vt_line_width"]

    # # Updates the max width spent by aligned faces
    # if faceblock["aligned"].w > self.max_w_aligned_face:
    #     self.max_w_aligned_face = faceblock["aligned"].w
    #  
    # # This prevents adding empty aligned faces from internal
    # # nodes
    # if faceblock["aligned"].column2faces:
    #     self.aligned_faces.append(faceblock["aligned"])

    # rightside faces region
    item.facesRegion.setRect(0, 0, faceblock["branch-right"].w, faceblock["branch-right"].h)

    # Node region 
    item.nodeRegion.setRect(0, 0, w, h)
    #if min_real_branch_separation < h:
    #    min_real_branch_separation = h

    #if not _leaf(node):
    #    widths, heights = zip(*[[c.fullRegion.width(),c.fullRegion.height()] \
    #                                for c in node.children])
    #    w += max(widths)
    #    h = max(node.nodeRegion.height(), sum(heights))

    # This is the node total region covered by the node
    item.fullRegion.setRect(0, 0, w, h)


def render_node_content(node, n2i, n2f, scale, mode):
    style = node.img_style
    parent_partition = n2i[node]
    parent_partition.bg.setAcceptsHoverEvents(False)

    #partition = QtGui.QGraphicsRectItem(parent_partition)
    partition = QtGui.QGraphicsItemGroup(parent_partition)
    parent_partition.content = partition
    
    nodeR = parent_partition.nodeRegion
    facesR = parent_partition.facesRegion
    center = parent_partition.center

    branch_length = float(node.dist * scale)

    # Whole partition background
    if style["bgcolor"].upper() not in set(["#FFFFFF", "white"]): 
        color = QtGui.QColor(style["bgcolor"])
        parent_partition.setBrush(color)
        parent_partition.setPen(color)
        parent_partition.drawbg = True
    
    # Node points in partition centers
    ball_size = style["size"] 
    ball_start_x = nodeR.width() - facesR.width() - ball_size
    node_ball = _NodePointItem(node)
    node_ball.setParentItem(partition)       
    node_ball.setPos(ball_start_x, center-(ball_size/2))


    #node_ball.setGraphicsEffect(QtCore.Qt.QGraphicsDropShadowEffect)

    # Branch line to parent
    pen = QtGui.QPen()
    set_pen_style(pen, style["hz_line_type"])
    pen.setColor(QtGui.QColor(style["hz_line_color"]))
    pen.setWidth(style["hz_line_width"])
    pen.setCapStyle(QtCore.Qt.FlatCap)
    hz_line = _LineItem(partition)
    hz_line.setPen(pen)
    hz_line.setLine(0, center, 
                    branch_length, center)
    #hz_line.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    #if self.props.complete_branch_lines:
    #    extra_hz_line = QtGui.QGraphicsLineItem(partition)
    #    extra_hz_line.setLine(node.dist_xoffset, center, 
    #                          ball_start_x, center)
    #    color = QtGui.QColor(self.props.extra_branch_line_color)
    #    pen = QtGui.QPen(color)
    #    set_pen_style(pen, style["line_type"])
    #    extra_hz_line.setPen(pen)
    return 
    # Attach branch-right faces to child 
    fblock = n2f[node]["branch-right"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(nodeR.width() - facesR.width(), \
                      center-fblock.h/2)
                
    # Attach branch-bottom faces to child 
    fblock = n2f[node]["branch-bottom"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(0, center)
        
    # Attach branch-top faces to child 
    fblock = n2f[node]["branch-top"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(0, center-fblock.h)

    # Vertical line
    if not _leaf(node):
        if mode == "circular":
            vt_line = QtGui.QGraphicsPathItem()
        elif mode == "rect":
            vt_line = _LineItem(parent_partition)
            first_child_part = n2i[node.children[0]]
            last_child_part = n2i[node.children[-1]]
            c1 = first_child_part.start_y + first_child_part.center
            c2 = last_child_part.start_y + last_child_part.center
            vt_line.setLine(nodeR.width(), c1,\
                                nodeR.width(), c2)            

        pen = QtGui.QPen()
        set_pen_style(pen, style["vt_line_type"])
        pen.setColor(QtGui.QColor(style["vt_line_color"]))
        pen.setWidth(style["vt_line_width"])
        pen.setCapStyle(QtCore.Qt.FlatCap)
        vt_line.setPen(pen)
        parent_partition.vt_line = vt_line

    return parent_partition


class _PointerItem(QtGui.QGraphicsRectItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0, parent)
        self.color = QtGui.QColor("blue")
        self._active = False


    def paint(self, p, option, widget):
        p.setPen(self.color)
        p.drawRect(self.rect())
        return

        # Draw info text
        font = QtGui.QFont("Arial",13)
        text = "%d selected."  % len(self.get_selected_nodes())
        textR = QtGui.QFontMetrics(font).boundingRect(text)
        if  self.rect().width() > textR.width() and \
                self.rect().height() > textR.height()/2 and 0: # OJO !!!!
            p.setPen(QtGui.QPen(self.color))
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

class _TreeScene(QtGui.QGraphicsScene):
    def __init__(self):
        QtGui.QGraphicsScene.__init__(self)

    def init_data(self, tree, img, n2i, n2f):
        self.master_item = QtGui.QGraphicsRectItem()
        self.view = None
        self.tree = tree
        self.n2i = n2i
        self.n2f = n2f
        self.img = img
        self.prop_table = None

        # Initialize scene 
        self.buffer_node = None        # Used to copy and paste
        self.pointer  = _PointerItem(self.master_item)
        self.highlighter = QtGui.QGraphicsPathItem(self.master_item)
        self.n2hl = {}

        # Set the scene background
        # self.setBackgroundBrush(QtGui.QColor("white"))
        self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

    def highlight_node(self, n):
        self.unhighlight_node(n)
        fgcolor = "green"
        #bgcolor = "white"
        item = self.n2i[n]
        hl = QtGui.QGraphicsRectItem(item)
        hl.setRect(item.nodeRegion)
        hl.setPen(QtGui.QColor(fgcolor))
        #hl.setBrush(QtGui.QColor(bgcolor))
        self.n2hl[n] = hl

    def unhighlight_node(self, n):
        if n in self.n2hl:
            self.removeItem(self.n2hl[n])
            del self.n2hl[n]

    def mousePressEvent(self,e):
        pos = self.pointer.mapFromScene(e.scenePos())
        self.pointer.setRect(pos.x(),pos.y(),10,10)
        self.pointer.startPoint = QtCore.QPointF(pos.x(), pos.y())
        self.pointer.setActive(True)
        self.pointer.setVisible(True)
        QtGui.QGraphicsScene.mousePressEvent(self,e)

    def mouseReleaseEvent(self,e):
        curr_pos = self.pointer.mapFromScene(e.scenePos())
        x = min(self.pointer.startPoint.x(),curr_pos.x())
        y = min(self.pointer.startPoint.y(),curr_pos.y())
        w = max(self.pointer.startPoint.x(),curr_pos.x()) - x
        h = max(self.pointer.startPoint.y(),curr_pos.y()) - y
        if self.pointer.startPoint == curr_pos:
            self.pointer.setVisible(False)
        self.pointer.setActive(False)
        QtGui.QGraphicsScene.mouseReleaseEvent(self,e)

    def mouseMoveEvent(self,e):
        curr_pos = self.pointer.mapFromScene(e.scenePos())
        if self.pointer.isActive():
            x = min(self.pointer.startPoint.x(),curr_pos.x())
            y = min(self.pointer.startPoint.y(),curr_pos.y())
            w = max(self.pointer.startPoint.x(),curr_pos.x()) - x
            h = max(self.pointer.startPoint.y(),curr_pos.y()) - y
            self.pointer.setRect(x,y,w,h)
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

def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)

def set_style(n, layout_func):
    # I import dict at the moment of drawing, otherwise there is a
    # loop of imports between drawer and qt4render
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
