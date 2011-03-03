import math

from PyQt4 import QtCore, QtGui, QtSvg

import qt4_circular_render as crender
import qt4_rect_render as rrender

from main import _leaf, NodeStyleDict, _ActionDelegator
from qt4_face_render import update_node_faces, _FaceGroupItem, _TextFaceItem


## | General scheme of node content
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

class _CircleItem(QtGui.QGraphicsEllipseItem, _ActionDelegator):
    def __init__(self, node):
        self.node = node
        d = node.img_style["size"]
        QtGui.QGraphicsEllipseItem.__init__(self, 0, 0, d, d)
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))
        self.setPen(QtGui.QPen(QtGui.QColor(self.node.img_style["fgcolor"])))

class _RectItem(QtGui.QGraphicsRectItem, _ActionDelegator):
    def __init__(self, node):
        self.node = node
        d = node.img_style["size"]
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, d, d)
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))
        self.setPen(QtGui.QPen(QtGui.QColor(self.node.img_style["fgcolor"])))
     
        
        #self.highlight_node()

class _SphereItem(QtGui.QGraphicsEllipseItem, _ActionDelegator):
    def __init__(self, node):
        self.node = node
        d = node.img_style["size"]
        r = d/2
        QtGui.QGraphicsEllipseItem.__init__(self, 0, 0, d, d)
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.node.img_style["fgcolor"])))
        self.setPen(QtGui.QPen(QtGui.QColor(self.node.img_style["fgcolor"])))
        gradient = QtGui.QRadialGradient(r, r, r,(d)/3,(d)/3)
        gradient.setColorAt(0.05, QtCore.Qt.white);
        gradient.setColorAt(0.9, QtGui.QColor(self.node.img_style["fgcolor"]));
        self.setBrush(QtGui.QBrush(gradient))
        # self.setPen(QtCore.Qt.NoPen)
        
class _EmptyItem(QtGui.QGraphicsItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self)
        self.setParentItem(parent)

        # qt4.6+ Only 
        try:
            self.setFlags(QtGui.QGraphicsItem.ItemHasNoContents)
        except: 
            pass

    def boundingRect(self):
        return QtCore.QRectF(0,0,0,0)

    def paint(self, *args, **kargs):
        return

class _TreeItem(QtGui.QGraphicsRectItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsRectItem.__init__(self)
        self.setParentItem(parent)
        self.n2i = {}
        self.n2f = {}
    
class _NodeItem(_EmptyItem):
    def __init__(self, node, parent):
        _EmptyItem.__init__(self, parent)
        self.node = node
        self.nodeRegion = QtCore.QRectF()
        self.facesRegion = QtCore.QRectF()
        self.fullRegion = QtCore.QRectF()
        self.highlighted = False

class _LineItem(QtGui.QGraphicsLineItem):
    def paint(self, painter, option, widget):
        QtGui.QGraphicsLineItem.paint(self, painter, option, widget)

class _PointerItem(QtGui.QGraphicsRectItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsRectItem.__init__(self,0,0,0,0, parent)
        self.color = QtGui.QColor("blue")
        self._active = False
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

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
        self.master_item = QtGui.QGraphicsRectItem(None)
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
        self.setBackgroundBrush(QtGui.QColor("white"))
        #self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

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

    def draw(self):
        pass
        # Get branch scale
        # fnode, max_dist = self.startNode.get_farthest_leaf(topology_only=\
        #                                                        img.force_topology)
        # if max_dist>0:
        #     self.scale =  self.props.tree_width / max_dist
        # else:
        #     self.scale =  1

def render(root_node, img, hide_root=False):
    mode = img.mode
    orientation = img.orientation 

    if not img.scale and img.tree_width:
        fnode, max_dist = root_node.get_farthest_leaf(topology_only=\
                                                          img.force_topology)
        if max_dist>0:
            img.scale =  img.tree_width / max_dist
        else:
            img.scale =  1
        print img.scale

    scale = img.scale
    arc_span = img.arc_span 
    last_rotation = img.arc_start
    layout_fn = img._layout_handler
    
    #parent = QtGui.QGraphicsRectItem(0, 0, 0, 0, None)
    parent = _TreeItem()
    n2i = parent.n2i # node to items
    n2f = parent.n2f # node to faces

    parent.bg_layer =  _EmptyItem(parent)
    parent.tree_layer = _EmptyItem(parent)
    parent.float_layer = _EmptyItem(parent)

    parent.bg_layer.setZValue(0)
    parent.tree_layer.setZValue(2)

    if img.floating_faces_under_tree:
        parent.float_layer.setZValue(1)
    else:
        parent.float_layer.setZValue(3)

    visited = set()
    to_visit = []
    to_visit.append(root_node)

    # This could be used to handle aligned faces in internal
    # nodes.
    virtual_leaves = 0
    for n in root_node.traverse():
        set_style(n, layout_fn)
        if _leaf(n):# or len(n.img_style["_faces"]["aligned"]):
            virtual_leaves += 1
    rot_step = float(arc_span) / virtual_leaves
    #rot_step = float(arc_span) / len([n for n in root_node.traverse() if _leaf(n)])

    # ::: Precalculate values :::
    depth = 1
    while to_visit:
        node = to_visit[-1]
        finished = True
        if node not in n2i:
            # Set style according to layout function
            item = n2i[node] = _NodeItem(node, parent.tree_layer)
            item.setZValue(depth)
            depth += 1 

            if node is root_node and hide_root:
                pass
            else:
                set_node_size(node, n2i, n2f, img)

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

        # :: Post-order visits. Leaves are already visited here ::
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

        if node is not root_node or not hide_root: 
            render_node_content(node, n2i, n2f, img)

    if mode == "circular":
        tree_radius = crender.render_circular(root_node, n2i, rot_step)
        iwidth = tree_radius * 2
        iheight = tree_radius * 2
        parent.moveBy(tree_radius, tree_radius)
        #parent.setRect(-max_r, -max_r, max_r*2, max_r*2) 
        #parent.setRect(0, 0, max_r*2, max_r*2) 
    else:
        iwidth = n2i[root_node].fullRegion.width()
        iheight = n2i[root_node].fullRegion.height()
        tree_radius = iwidth
    
   
    aligned_region_width = render_aligned_faces(n2i, n2f, img, tree_radius, parent)
  
    # If there were aligned faces, we need to re-set main tree size
    if 0 and extra_width:
        if mode == "circular": 
            r = (max_r + extra_width)
            parent.setPos(r, r)
            parent.setRect(0, 0, r, r) 
        if mode == "rect":
            parent.setRect(0, 0, max_r + extra_width, parent.rect().height())

    # Set tree margins
    if mode == "circular": 
        parent.setRect( -tree_radius - img.margin_left,  -tree_radius-img.margin_top, \
                            iwidth + img.margin_left + img.margin_right + aligned_region_width, \
                            iheight + img.margin_top + img.margin_bottom)
    elif mode == "rect": 
        parent.setRect(-img.margin_left,  -img.margin_top, \
                            iwidth + img.margin_left + img.margin_right + aligned_region_width, \
                            iheight + img.margin_top + img.margin_bottom)
        

       
    # Background colors
    render_backgrounds(n2i, n2f, img, tree_radius + aligned_region_width, parent.bg_layer)

    # Place Floating faces
    render_floatings(n2i, n2f, img, parent.float_layer)

    if mode == "circular":
        rotate_inverted_faces(n2i, n2f, img)
    elif mode == "rect" and orientation == 1: 
        parent.setTransform(QtGui.QTransform().scale(-1, 1))
        for faceblock in n2f.itervalues():
            for pos, fb in faceblock.iteritems():
                fb.flip_hz()

    # Draws a border around the tree
    if not img.draw_border:
        parent.setPen(QtGui.QPen(QtCore.Qt.NoPen))
    else:
        parent.setPen(QtGui.QPen(QtGui.QColor("black")))


    return parent, n2i, n2f

def rotate_inverted_faces(n2i, n2f, img):
    for node, faceblock in n2f.iteritems():
        item = n2i[node]
        if item.rotation > 90 and item.rotation < 270:
            for pos, fb in faceblock.iteritems():
                fb.rotate(180)

def render_backgrounds(n2i, n2f, img, max_r, bg_layer):
    for node, item in n2i.iteritems():
        if _leaf(node):
            first_c = n2i[node]
            last_c = n2i[node]
        else:
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]

        if img.mode == "circular":               
            h = item.effective_height
            angle_start = first_c.full_start 
            angle_end = last_c.full_end
            parent_radius = getattr(n2i.get(node.up, None), "radius", 0)
            base = parent_radius + item.nodeRegion.width()

            if node.img_style["node_bgcolor"].upper() != "#FFFFFF":
                bg1 = crender._ArcItem()
                r = math.sqrt(base**2 + h**2) 
                bg1.set_arc(0, 0, parent_radius, r, angle_start, angle_end)
                bg1.setParentItem(item.content.bg)
                bg1.setPen(QtGui.QPen(QtGui.QColor(node.img_style["node_bgcolor"])))
                bg1.setBrush(QtGui.QBrush(QtGui.QColor(node.img_style["node_bgcolor"])))

            if node.img_style["faces_bgcolor"].upper() != "#FFFFFF":
                bg2 = crender._ArcItem()
                r = math.sqrt(base**2 + h**2) 
                bg2.set_arc(0, 0, parent_radius, item.radius, angle_start, angle_end)
                bg2.setParentItem(item.content)
                bg2.setPen(QtGui.QPen(QtGui.QColor(node.img_style["faces_bgcolor"])))
                bg2.setBrush(QtGui.QBrush(QtGui.QColor(node.img_style["faces_bgcolor"])))

            if node.img_style["bgcolor"].upper() != "#FFFFFF":
                bg = crender._ArcItem()
                bg.set_arc(0, 0, parent_radius, max_r, angle_start, angle_end)
                bg.setPen(QtGui.QPen(QtGui.QColor(node.img_style["bgcolor"])))
                bg.setBrush(QtGui.QBrush(QtGui.QColor(node.img_style["bgcolor"])))
                bg.setParentItem(bg_layer)
                bg.setZValue(item.zValue())

        if img.mode == "rect":
            if node.img_style["bgcolor"].upper() != "#FFFFFF":
                bg = QtGui.QGraphicsRectItem()
                pos = item.content.mapToScene(0, 0)
                bg.setPos(pos.x(), pos.y())
                bg.setRect(0, 0, max_r-pos.x(),  item.fullRegion.height())
                bg.setPen(QtGui.QPen(QtGui.QColor(node.img_style["bgcolor"])))
                bg.setBrush(QtGui.QBrush(QtGui.QColor(node.img_style["bgcolor"])))
                bg.setParentItem(bg_layer)
                bg.setZValue(item.zValue())

def set_node_size(node, n2i, n2f, img):
    scale = img.scale
    min_separation = img.min_leaf_separation

    item = n2i[node]
    branch_length = item.branch_length = float(node.dist * scale)

    # Organize faces by groups
    faceblock = update_node_faces(node, n2f)

    if _leaf(node):
        aligned_height = faceblock["aligned"].h
    else: 
        aligned_height = 0

    # Total height required by the node
    h = max(node.img_style["size"], \
                ( (node.img_style["size"]/2) \
                      + node.img_style["hz_line_width"] \
                      + faceblock["branch-top"].h \
                      + faceblock["branch-bottom"].h), \
                faceblock["branch-right"].h, \
                aligned_height, \
                min_separation,\
                )    
    # Total width required by the node
    w = sum([max(branch_length + node.img_style["size"], 
                                      faceblock["branch-top"].w + node.img_style["size"],
                                      faceblock["branch-bottom"].w + node.img_style["size"],
                                      ), 
                                  faceblock["branch-right"].w]
                                 )
    w += node.img_style["vt_line_width"]

    # rightside faces region
    item.facesRegion.setRect(0, 0, faceblock["branch-right"].w, faceblock["branch-right"].h)

    # Node region 
    item.nodeRegion.setRect(0, 0, w, h)

    # Stores real separation between branches, to correctly handle scale changes...
    #if min_real_branch_separation < h:
    #    min_real_branch_separation = h

    # This is the node total region covered by the node
    item.fullRegion.setRect(0, 0, w, h)

def render_node_content(node, n2i, n2f, img):
    style = node.img_style
    item = n2i[node]
    item.content = _EmptyItem(item)
 
    nodeR = item.nodeRegion
    facesR = item.facesRegion
    center = item.center
    branch_length = item.branch_length

    # Node points 
    ball_size = style["size"] 
    ball_start_x = nodeR.width() - facesR.width() - ball_size - 1 # Why -1?? mystery
    if ball_size:
        if node.img_style["shape"] == "sphere":
            node_ball = _SphereItem(node)
        elif node.img_style["shape"] == "circle":
            node_ball = _CircleItem(node)
        elif node.img_style["shape"] == "square":
            node_ball = _RectItem(node)

        node_ball.setPos(ball_start_x, center-(ball_size/2.0))

        from qt4_gui import _BasicNodeActions
        node_ball.delegate = _BasicNodeActions()
        #node_ball.setAcceptsHoverEvents(True)
        #node_ball.setCursor(QtCore.Qt.PointingHandCursor)
        
    else:
        node_ball = None

    # Branch line to parent
    pen = QtGui.QPen()
    set_pen_style(pen, style["hz_line_type"])
    pen.setColor(QtGui.QColor(style["hz_line_color"]))
    pen.setWidth(style["hz_line_width"])
    pen.setCapStyle(QtCore.Qt.FlatCap)
    #pen.setCapStyle(QtCore.Qt.RoundCap)
    #pen.setJoinStyle(QtCore.Qt.RoundJoin)
    hz_line = _LineItem()
    hz_line.setPen(pen)

    # the -vt_line_width is to solve small imperfections in line
    # crosses. 
    hz_line.setLine(-style["vt_line_width"]/2.0, center, 
                    branch_length, center)

    if img.complete_branch_lines_when_necesary:
        extra_line = _LineItem(branch_length, center, ball_start_x, center)
        pen = QtGui.QPen()
        item.extra_branch_line = extra_line
        set_pen_style(pen, img.extra_branch_line_type)
        pen.setColor(QtGui.QColor(img.extra_branch_line_color))
        pen.setCapStyle(QtCore.Qt.FlatCap)
        pen.setWidth(style["hz_line_width"])
        extra_line.setPen(pen)
    else:
        extra_line = None

    # Attach branch-right faces to child 
    fblock_r = n2f[node]["branch-right"]
    fblock_r.render()
    fblock_r.setPos(nodeR.width() - facesR.width(), \
                      center-fblock_r.h/2)
                
    # Attach branch-bottom faces to child 
    fblock_b = n2f[node]["branch-bottom"]
    fblock_b.render()
    fblock_b.setPos(0, center)
        
    # Attach branch-top faces to child 
    fblock_t = n2f[node]["branch-top"]
    fblock_t.render()
    fblock_t.setPos(0, center-fblock_t.h)

    # Vertical line
    if not _leaf(node):
        if img.mode == "circular":
            vt_line = QtGui.QGraphicsPathItem()

        elif img.mode == "rect":
            vt_line = _LineItem(item)
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
        item.vt_line = vt_line
    else:
        vt_line = None

    item.bg = QtGui.QGraphicsItemGroup()
    item.movable_items = [] #QtGui.QGraphicsItemGroup()
    item.static_items = [] #QtGui.QGraphicsItemGroup()

    # Items fow which coordinates are exported in the image map
    item.mapped_items = [node_ball, fblock_r, fblock_b, fblock_t]

    for i in [node_ball, fblock_r, fblock_b, fblock_t]:
        if i:
            #item.movable_items.addToGroup(i)
            item.movable_items.append(i)
            i.setParentItem(item.content) 
            
    for i in [vt_line, extra_line, hz_line]:
        if i:
            #item.static_items.addToGroup(i)
            item.static_items.append(i)
            i.setParentItem(item.content) 

    #item.movable_items.setParentItem(item.content)
    #item.static_items.setParentItem(item.content)

def render_scale(scale):
    length=50
    scaleItem = _EmptyItem()
    scaleItem.setRect(0, 0, length, length)
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
    scale_text = "%0.2f" % float(length/scale)
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

def render_floatings(n2i, n2f, img, float_layer):
    floating_faces = [ [node, fb["float"]] for node, fb in n2f.iteritems() if "float" in fb]
    for node, fb in floating_faces:
        item = n2i[node]
        fb.setParentItem(float_layer)
        if img.mode == "circular":

            # Floatings are positioned over branches 
            crender.rotate_and_displace(fb, item.rotation, fb.h, item.radius - item.nodeRegion.width())

            # Floatings are positioned starting from the node circle 
            #crender.rotate_and_displace(fb, item.rotation, fb.h, item.radius - item.nodeRegion.width())

        elif img.mode == "rect":
            fb.setPos(item.content.mapToScene(0, item.center-(fb.h/2)))

        z = item.zValue()
        if not img.children_faces_on_top:
            z = -z

        fb.setZValue(z)
        fb.update_columns_size()
        fb.render()

def render_aligned_faces(n2i, n2f, img, tree_end_x, parent):
    # Prepares and renders aligned face headers. Used to later
    # place aligned faces
    aligned_faces = [ [node, fb["aligned"]] for node, fb in n2f.iteritems() if fb["aligned"].column2faces]

    if not aligned_faces:
        return 0

    if img.mode == "rect":
        fb_head = _FaceGroupItem(img.aligned_header, None)
        fb_head.setParentItem(parent.tree_layer)

        fb_foot = _FaceGroupItem(img.aligned_foot, None)
        fb_foot.setParentItem(parent.tree_layer)
        surroundings = [[None,fb_foot], [None, fb_head]]
    else:
        surroundings = []

    # Place aligned faces and calculates the max size of each
    # column (needed to place column headers)
    c2max = {}
    for node, fb in aligned_faces + surroundings:
        for c, size in fb.column2size.iteritems():
            c2max[c] = max(size[0], c2max.get(c,0))

    if img.mode == "rect":
        fb_head.set_min_column_widths(c2max)
        fb_head.update_columns_size()
        fb_head.render()
        fb_head.setParentItem(parent.tree_layer)
        fb_head.setPos(tree_end_x, -fb_head.h)
        
        fb_foot.set_min_column_widths(c2max)
        fb_foot.update_columns_size()
        fb_foot.render()
        fb_foot.setParentItem(parent.tree_layer)
        fb_foot.setPos(tree_end_x, parent.rect().height())
    
    # Place aligned faces
    for node, fb in aligned_faces:
        item = n2i[node]
        item.mapped_items.append(fb)
        if img.draw_aligned_faces_as_grid: 
            fb.set_min_column_widths(c2max)
        fb.update_columns_size()
        fb.render()
        fb.setParentItem(item.content)
        if img.mode == "circular":
            if node.up in n2i:
                x = tree_end_x - n2i[node.up].radius 
            else:
                x = tree_end_x
            #fb.moveBy(tree_end_x, 0)
        elif img.mode == "rect":
            x = item.mapFromScene(tree_end_x, 0).x() 
            
        fb.setPos(x, item.center-(fb.h/2))

        if img.draw_guiding_lines and _leaf(node):
            guide_line = _LineItem(item.nodeRegion.width(), item.center, x, item.center)
            pen = QtGui.QPen()
            set_pen_style(pen, img.guiding_lines_type)
            pen.setColor(QtGui.QColor(img.guiding_lines_color))
            pen.setCapStyle(QtCore.Qt.FlatCap)
            pen.setWidth(0)
            guide_line.setPen(pen)
            guide_line.setParentItem(item.content)

    return sum(c2max.values())

def save(scene, imgName, w=None, h=None, header=None, \
             dpi=300, take_region=False):

    ext = imgName.split(".")[-1].upper()
    main_rect = scene.sceneRect()
    print main_rect
    aspect_ratio = main_rect.height() / main_rect.width()

    # auto adjust size
    if w is None and h is None and (ext == "PDF" or ext == "PS"):
        w = dpi * 6.4
        h = w * aspect_ratio
        if h>dpi * 11:
            h = dpi * 11
            w = h / aspect_ratio
    elif w is None and h is None:
        w = main_rect.width()
        h = main_rect.height()
    elif h is None :
        h = w * aspect_ratio
    elif w is None:
        w = h / aspect_ratio

    print w, h, main_rect

    if ext == "SVG": 
        svg = QtSvg.QSvgGenerator()
        svg.setFileName(imgName)
        svg.setSize(QtCore.QSize(w, h))
        svg.setViewBox(QtCore.QRect(0, 0, w, h))
        #svg.setTitle("")
        svg.setDescription("Generated with ETE http://ete.cgenomics.org")

        pp = QtGui.QPainter()
        pp.begin(svg)
        targetRect =  QtCore.QRectF(0, 0, w, h)
        scene.render(pp, scene.sceneRect(), scene.sceneRect())
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

        scene.render(pp, targetRect, scene.sceneRect())
        pp.end()
        return
    else:
        scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("white")));
        targetRect = QtCore.QRectF(0, 0, w, h)
        ii= QtGui.QImage(w, \
                             h, \
                             QtGui.QImage.Format_ARGB32)
        pp = QtGui.QPainter(ii)
        pp.setRenderHint(QtGui.QPainter.Antialiasing)
        pp.setRenderHint(QtGui.QPainter.TextAntialiasing)
        pp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        scene.render(pp, targetRect, scene.sceneRect())
        pp.end()
        ii.save(imgName)

def get_tree_img_map(n2i):
    node_list = []
    face_list = []
    nid = 0
    for n, main_item in n2i.iteritems():
        n.add_feature("_nid", str(nid))
        for item in main_item.mapped_items:
            if isinstance(item, _CircleItem) \
                    or isinstance(item, _SphereItem) \
                    or isinstance(item, _RectItem):

                r = item.boundingRect()
                rect = item.mapToScene(r).boundingRect()
                x1 = rect.x() 
                y1 = rect.y() 
                x2 = rect.x() + rect.width()
                y2 = rect.y() + rect.height()
                node_list.append([x1, y1, x2, y2, nid, None])
            elif isinstance(item, _FaceGroupItem):
                if item.column2faces:
                    for f in item.childItems():
                        r = f.boundingRect()
                        rect = f.mapToScene(r).boundingRect()
                        x1 = rect.x() 
                        y1 = rect.y() 
                        x2 = rect.x() + rect.width()
                        y2 = rect.y() + rect.height()
                        if isinstance(f, _TextFaceItem):
                            face_list.append([x1, y1, x2, y2, nid, str(f.text())])
                        else:
                            face_list.append([x1, y1, x2, y2, nid, None])
                          
        nid += 1
    return {"nodes": node_list, "faces": face_list}
