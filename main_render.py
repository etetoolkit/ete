import re
from PyQt4 import QtCore, QtGui

import circular_render as crender
from face_render import update_node_faces
import circular_render as crender
import rect_render as rrender
from ete_dev import faces

import random

FACE_POSITIONS = set(["branch-right", "aligned", "branch-top", "branch-bottom"])

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
## | dist_xoffset    | nodesize |facesRegion |                                       |=======================================||
## |  branch-bottom  |          |            |================================================================================|
## |                                         |=======================================|                                        |
## |                                         |             fullRegion                |                                        |
## |                                         |        nodeRegion                     |                                        |
## |                                         | xdist_offset | nodesize | facesRegion |                                        |
## |                                         |=======================================|                                        |
## |==========================================================================================================================|
##

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)


class TreeImage(object):
    def __init__(self):
        # circular or  rect
        self.mode = "circular"

        # Scale used to convert branch lengths to pixels. None means
        # that it will be estimated using "tree_with".
        self.scale = 10

        # Branch lengths, in pixels, from root node to the most
        # distant leaf. This is used to calculate the scale when this
        # is not manually set.
        self.tree_width = 200  

        # Min separation, in pixels, between to adjacent branches
        self.min_branch_separation = 1 # in pixels

        # Complete lines representing branch lengths to better observe
        # the topology of trees
        self.force_topology = False

        # Aligned faces will be drawn in aligned columns
        self.draw_aligned_faces_as_grid = True

        # Draws guidelines from leaf nodes to aligned faces
        self.draw_guidelines = False
        # Type of guidelines 
        self.guideline_type = 2 # 0 solid, 1 dashed, 2 dotted
        self.guideline_color = "#CCCCCC"

        # Draws a border around the whole tree
        self.draw_image_border = False

        # When top-branch and down-branch faces are larger than scaled
        # branch length, lines are completed
        self.complete_branch_lines = True
        self.extra_branch_line_color = "#cccccc"

        # Shows legend (branch length scale)
        self.show_legend = True

        self.title = None
        self.botton_line_text = None

        # Circular tree properties
        self.arc_start = 0 # 0 degrees = 12 o'clock
        self.arc_span = 360

        self.search_node_bg = "#cccccc"
        self.search_node_fg = "#ff0000"

        # Initialize aligned face headers
        self.aligned_header = FaceHeader() # aligned face_header
        self.aligned_foot = FaceHeader()

class FaceHeader(dict):
    def add_face(self, face, column):
        self.setdefault(int(column), []).append(face)

class TreeFace(faces.Face):
    def __init__(self, tree, img_properties):
        faces.Face.__init__(self)
        self.type = "item"
        self.root_node = tree
        self.img = img_properties
        self.tree_partition = None

    def update_items(self):
        hide_root = False
        if self.root_node is self.node:
            hide_root = True
        self.tree_partition = render(self.root_node, {}, {}, self.img, hide_root)

    def _width(self):
        return self.tree_partition.rect().width()

    def _height(self):
        return self.tree_partition.rect().height()

class RandomFace(faces.Face):
    def __init__(self):
        faces.Face.__init__(self)
        self.type = "item"

    def update_items(self):
        w = random.randint(4, 100)
        h = random.randint(4, 100)
        self.tree_partition = QtGui.QGraphicsRectItem(0,0,w, h)
        self.tree_partition.setBrush(QtGui.QBrush(QtGui.QColor("green")))

    def _width(self):
        return self.tree_partition.rect().width()

    def _height(self):
        return self.tree_partition.rect().height()

class _TextFaceItem(QtGui.QGraphicsSimpleTextItem):
    """ Manage faces on Scene"""
    def __init__(self, face, node, *args):
        QtGui.QGraphicsSimpleTextItem.__init__(self,*args)
        self.node = node

class _ImgFaceItem(QtGui.QGraphicsPixmapItem):
    """ Manage faces on Scene"""
    def __init__(self, face, node, *args):
        QtGui.QGraphicsPixmapItem.__init__(self,*args)
        self.node = node

class _NodeItem(QtGui.QGraphicsRectItem):
    def __init__(self, node):
        self.node = node
        self.radius = node.img_style["size"]/2
        self.diam = self.radius*2
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, self.diam, self.diam)

    def paint(self, p, option, widget):
        #QtGui.QGraphicsRectItem.paint(self, p, option, widget)
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

class NodeStyleDict(dict):
    def __init__(self, *args, **kargs):

        super(NodeStyleDict, self).__init__(*args, **kargs)
        super(NodeStyleDict, self).__setitem__("faces", {})
        self._defaults = [
            ["fgcolor",          "#0030c1",    _COLOR_CHECKER                           ],
            ["bgcolor",          "#FFFFFF",    _COLOR_CHECKER                           ],
            ["vt_line_color",    "#000000",    _COLOR_CHECKER                           ],
            ["hz_line_color",    "#000000",    _COLOR_CHECKER                           ],
            ["hz_line_type",     0,            _LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
            ["vt_line_type",     0,            _LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
            ["size",             6,            _SIZE_CHECKER                            ], # node circle size 
            ["shape",            "sphere",     _NODE_TYPE_CHECKER                       ], 
            ["draw_descendants", True,         _BOOL_CHECKER                            ],
            ["hz_line_width",          0,      _SIZE_CHECKER                            ],
            ["vt_line_width",          0,      _SIZE_CHECKER                            ]
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


def render(root_node, n2i, n2f, img, hide_root=False):
    mode = img.mode
    scale = img.scale
    arc_span = img.arc_span 
    last_rotation = -90 + img.arc_start
    parent = QtGui.QGraphicsRectItem(0, 0, 0, 0)
    visited = set()
    to_visit = []
    to_visit.append(root_node)
    rot_step = float(arc_span) / len([n for n in root_node.traverse() if _leaf(n)])
    # ::: Precalculate values :::
    while to_visit:
        node = to_visit[-1]

        if not hasattr(node, "img_style"):
            node.img_style = NodeStyleDict()
        elif isinstance(node.img_style, NodeStyleDict): 
            node.img_style.init()
        finished = True

        if node not in n2i:
            if mode == "circular":
                # ArcPartition all hang from a same parent item
                item = n2i[node] = crender.ArcPartition(parent)
            elif mode == "rect":
                # RectPartition are nested, so parent will be modified
                # later on
                item = n2i[node] = rrender.RectPartition(parent)

            if node is root_node and hide_root:
                empty = QtCore.QRectF(0,0,1,1)
                item.nodeRegion, item.facesRegion, item.fullRegion = \
                    empty, empty, empty
            else:
                nodeRegion, facesRegion, fullRegion = \
                    get_node_size(node, n2f, scale)
                item.nodeRegion, item.facesRegion, item.fullRegion = \
                    nodeRegion, facesRegion, fullRegion

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

        if node is not root_node or not hide_root: 
            render_node_content(node, n2i, n2f, scale, mode)

    if mode == "circular":
        max_r = crender.render_circular(root_node, n2i, rot_step)
        parent.moveBy(max_r, max_r)
        parent.setRect(-max_r, -max_r, max_r*2, max_r*2) 
    else:
        parent.setRect(n2i[root_node].fullRegion)

    return parent

def get_node_size(node, n2f, scale):
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
    style = node.img_style

    parent_partition = n2i[node]
    partition = QtGui.QGraphicsRectItem(parent_partition)
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
    node_ball = _NodeItem(node)
    node_ball.setParentItem(partition)       
    node_ball.setPos(ball_start_x, center-(ball_size/2))
    node_ball.setAcceptsHoverEvents(True)

    #node_ball.setGraphicsEffect(QtCore.Qt.QGraphicsDropShadowEffect)

    # Branch line to parent
    pen = QtGui.QPen()
    set_pen_style(pen, style["hz_line_type"])
    pen.setColor(QtGui.QColor(style["hz_line_color"]))
    pen.setWidth(style["hz_line_width"])
    pen.setCapStyle(QtCore.Qt.FlatCap)
    hz_line = QtGui.QGraphicsLineItem(partition)
    hz_line.setPen(pen)
    hz_line.setLine(0, center, 
                    branch_length, center)

    #if self.props.complete_branch_lines:
    #    extra_hz_line = QtGui.QGraphicsLineItem(partition)
    #    extra_hz_line.setLine(node.dist_xoffset, center, 
    #                          ball_start_x, center)
    #    color = QtGui.QColor(self.props.extra_branch_line_color)
    #    pen = QtGui.QPen(color)
    #    set_pen_style(pen, style["line_type"])
    #    extra_hz_line.setPen(pen)

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
            vt_line = QtGui.QGraphicsLineItem(parent_partition)
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

def _leaf(node):
    collapsed = hasattr(node, "img_style") and not node.img_style["draw_descendants"]
    return collapsed or node.is_leaf()

def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)

