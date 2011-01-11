import re
from PyQt4 import QtCore, QtGui

import circular_render as crender
import face_render as frender
import circular_render as crender

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)

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

class NodeStyleDict(dict):
    def __init__(self, *args, **kargs):

        super(NodeStyleDict, self).__init__(*args, **kargs)
        super(NodeStyleDict, self).__setitem__("faces", {})
        self._defaults = [
            ["fgcolor",          "#0030c1",    _COLOR_CHECKER                           ],
            ["bgcolor",          "#FFFFFF",    _COLOR_CHECKER                           ],
            ["vt_line_color",    "#000000",    _COLOR_CHECKER                           ],
            ["hz_line_color",    "#000000",    _COLOR_CHECKER                           ],
            ["line_type",        0,            _LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
            ["size",             6,            _SIZE_CHECKER                            ], # node circle size 
            ["shape",            "sphere",     _NODE_TYPE_CHECKER                       ], 
            ["draw_descendants", True,         _BOOL_CHECKER                            ],
            ["hlwidth",          1,            _SIZE_CHECKER                            ]
            ]
        self._valid_keys = set([i[0] for i in self._defaults]) 
        self.init()
        self._block_adding_faces = False

    def init(self):
        for key, dvalue, checker in self._defaults:
            if key not in self:
                self[key] = dvalue
            elif not checker(self[key]):
                raise ValueError("'%s' attribute in node style has not a valid value: %s" %\
                                     (key, self[key]))
        super(NodeStyleDict, self).__setitem__("_faces", {})
        # copy fixed faces to the faces dict that will be drawn 
        for pos, values in self["faces"].iteritems():
            for col, faces in values.iteritems():
                self["_faces"].setdefault(pos, {})
                self["_faces"][pos][col] = list(faces)

    def add_fixed_face(self, face, position, column):
        if self._block_adding_faces:
            raise AttributeError("fixed faces cannot be modified while drawing.")
            
        from faces import FACE_POSITIONS
        """ Add faces as a fixed feature of this node style. This
        faces are always rendered. 

        face: a Face compatible instance
        Valid positions: %s
        column: an integer number defining face relative position
         """ %FACE_POSITIONS
        self["faces"].setdefault(position, {})
        self["faces"][position].setdefault(int(column), []).append(face)

    def __setitem__(self, i, y):
        if i not in self._valid_keys:
            raise ValueError("'%s' is not a valid key for NodeStyleDict instances" %i)
        super(NodeStyleDict, self).__setitem__(i, y)

def render(root_node, n2i, n2f, current_mode, scale, parent):
    print "RENDERING", root_node.name
    visited = set()
    to_visit = []
    to_visit.append(root_node)
    arc_span = 360
    last_rotation = -90 # starts rotation from 12 o'clock
    rot_step = float(arc_span) / len(root_node)
    print rot_step, "ROT_STEP"
    max_r = 0
    # ::: Precalculate values :::
    while to_visit:
        node = to_visit[-1]

        if not hasattr(node, "img_style"):
            node.img_style = NodeStyleDict()
        elif isinstance(node.img_style, NodeStyleDict): 
            node.img_style.init()
        hybrid_node = node is not root_node and hasattr(node, "mode") 
        finished = True

        if node not in n2i:
            item = n2i[node] = crender.ArcPartition(parent)
            nodeRegion, facesRegion, fullRegion = \
                get_node_size(node, n2f, scale)
            item.nodeRegion, item.facesRegion, item.fullRegion = \
                nodeRegion, facesRegion, fullRegion

        if not _leaf(node):
            # Render node under a different strategy
            if hybrid_node:
                print "HYBRID", node.name
                render(node, n2i, n2f, node.mode, scale, item)
            else:
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
        # :: Post-order code ::
        if current_mode == "circular": 
            if _leaf(node) or hybrid_node:
                if hybrid_node:
                    angle_use = rot_step
                else:
                    angle_use = rot_step
                crender.init_circular_leaf_item(node, n2i, last_rotation, angle_use)
                last_rotation += angle_use
            else:
                crender.init_circular_node_item(node, n2i)
            if hybrid_node:
                item.nodeRegion.setWidth(item.max_r*2)
                item.nodeRegion.setHeight(item.max_r*2)
            else:
                render_node_content(node, n2i, n2f, scale, current_mode)
    if current_mode == "circular":
        crender.render_circular(root_node, n2i, rot_step)

def get_node_size(node, n2f, scale):
    branch_length = float(node.dist * scale)
    min_branch_separation = 3

    # Organize faces by groups
    faceblock = frender.update_node_faces(node, n2f)

    # Total height required by the node
    h = max(node.img_style["size"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
                                  node.img_style["hlwidth"] + faceblock["branch-top"].h + faceblock["branch-bottom"].h, 
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

    # # Updates the max width spent by aligned faces
    # if faceblock["aligned"].w > self.max_w_aligned_face:
    #     self.max_w_aligned_face = faceblock["aligned"].w
    #  
    # # This prevents adding empty aligned faces from internal
    # # nodes
    # if faceblock["aligned"].column2faces:
    #     self.aligned_faces.append(faceblock["aligned"])

    # rightside faces region
    facesRegion = QtCore.QRectF(0, 0, faceblock["branch-right"].w, faceblock["branch-right"].h)

    # Node region 
    nodeRegion = QtCore.QRectF(0, 0, w, h)
    #if min_real_branch_separation < h:
    #    min_real_branch_separation = h

    #if not _leaf(node):
    #    widths, heights = zip(*[[c.fullRegion.width(),c.fullRegion.height()] \
    #                                for c in node.children])
    #    w += max(widths)
    #    h = max(node.nodeRegion.height(), sum(heights))

    # This is the node total region covered by the node
    fullRegion = QtCore.QRectF(0, 0, w, h)
    return nodeRegion, facesRegion, fullRegion

def render_node_content(node, n2i, n2f, scale, mode):
    #partition = n2i[node]
    style = node.img_style
    branch_length = float(node.dist * scale)
    partition = n2i[node]

    # Draws node background
    #if style["bgcolor"].upper() not in set(["#FFFFFF", "white"]): 
    #    color = QtGui.QColor(style["bgcolor"])
    #    partition.setBrush(color)
    #    partition.setPen(color)
    #    partition.drawbg = True
    


    # Draw node points in partition centers
    ball_size = style["size"] 
    ball_start_x = partition.nodeRegion.width() - partition.facesRegion.width() - ball_size
    node_ball = _NodeItem(node)
    node_ball.setParentItem(partition)       
    node_ball.setPos(ball_start_x, partition.center-(ball_size/2))
    node_ball.setAcceptsHoverEvents(True)

    # Branch line to parent
    color = QtGui.QColor(style["hz_line_color"])
    pen = QtGui.QPen(color)
    set_pen_style(pen, style["line_type"])
    hz_line = QtGui.QGraphicsLineItem(partition)
    hz_line.setPen(pen)
    hz_line.setLine(0, partition.center, 
                    branch_length, partition.center)

    #if self.props.complete_branch_lines:
    #    extra_hz_line = QtGui.QGraphicsLineItem(partition)
    #    extra_hz_line.setLine(node.dist_xoffset, partition.center, 
    #                          ball_start_x, partition.center)
    #    color = QtGui.QColor(self.props.extra_branch_line_color)
    #    pen = QtGui.QPen(color)
    #    set_pen_style(pen, style["line_type"])
    #    extra_hz_line.setPen(pen)

    # Attach branch-right faces to child 
    fblock = n2f[node]["branch-right"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(partition.nodeRegion.width() - partition.facesRegion.width(), \
                      partition.center-fblock.h/2)
                
    # Attach branch-bottom faces to child 
    fblock = n2f[node]["branch-bottom"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(0, partition.center)
        
    # Attach branch-top faces to child 
    fblock = n2f[node]["branch-top"]
    fblock.setParentItem(partition)
    fblock.render()
    fblock.setPos(0, partition.center-fblock.h)

    
    # Vertical Node
    if 0 and not _leaf(node):
        first_c = n2i[node.children[0]]
        last_c = n2i[node.children[-1]]
        if mode == "circular":
            # Used to BG
            full_angle = last_c.full_end - first_c.full_start
            angle_start = last_c.full_end - partition.rotation
            angle_end = partition.rotation - first_c.full_start
            partition.set_arc(parent_radius, h/2, parent_radius, r, angle_start, angle_end)

            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            vt_line = QtGui.QGraphicsPathItem(parent)
            path = QtGui.QPainterPath()
            path.arcMoveTo(-r,-r, r * 2, r * 2, 360-rot_start-angle)
            path.arcTo(-r,-r, r*2, r * 2, 360 - rot_start - angle, angle)
            vt_line.setPath(path)
            
        if mode == "rectangular":
            vt_line = QtGui.QGraphicsLineItem(partition)
            c1 = first_c.start_y + first_c.center
            c2 = last_c.start_y + last_c.center
            vt_line.setLine(partition.nodeRegion.width(), c1,\
                                partition.nodeRegion.width(), c2)            
        # Vt line style
        pen = QtGui.QPen(QtGui.QColor(style["vt_line_color"])) 
        set_pen_style(pen, style["line_type"])
        vt_line.setPen(pen)

    return partition

def _leaf(node):
    return node.is_leaf()

def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)
