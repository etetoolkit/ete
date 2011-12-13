import colorsys
import random
import re
import types 

from PyQt4.QtGui import *
from PyQt4 import QtCore

from svg_colors import SVG_COLORS

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: x.lower() in SVG_COLORS or re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)

FACE_POSITIONS = set(["branch-right", "branch-top", "branch-bottom", "float", "float-behind", "aligned"])

__all__  = ["NodeStyle", "TreeStyle", "FaceContainer", "_leaf", "add_face_to_node"]

NODE_STYLE_DEFAULT = [
    ["fgcolor",          "#0030c1",    _COLOR_CHECKER                           ],
    ["bgcolor",          "#FFFFFF",    _COLOR_CHECKER                           ],
    ["node_bgcolor",     "#FFFFFF",    _COLOR_CHECKER                           ],
    ["partition_bgcolor","#FFFFFF",    _COLOR_CHECKER                           ],
    ["faces_bgcolor",    "#FFFFFF",    _COLOR_CHECKER                           ],    
    ["vt_line_color",    "#000000",    _COLOR_CHECKER                           ],
    ["hz_line_color",    "#000000",    _COLOR_CHECKER                           ],
    ["hz_line_type",     0,            _LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
    ["vt_line_type",     0,            _LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
    ["size",             3,            _SIZE_CHECKER                            ], # node circle size 
    ["shape",            "circle",     _NODE_TYPE_CHECKER                       ], 
    ["draw_descendants", True,         _BOOL_CHECKER                            ],
    ["hz_line_width",          0,      _SIZE_CHECKER                            ],
    ["vt_line_width",          0,      _SIZE_CHECKER                            ]
    ]

TREE_STYLE_CHECKER = {
    "mode": lambda x: x.lower() in set(["c", "r"]),
    }

# _faces and faces are registered to allow deepcopy to work on nodes
VALID_NODE_STYLE_KEYS = set([i[0] for i in NODE_STYLE_DEFAULT]) | set(["_faces"])

class _Border(object):
    def __init__(self):
        self.width = None
        self.type = 0
        self.color = None 

    def apply(self, item):
        if self.width is not None:
            r = item.boundingRect()
            border = QGraphicsRectItem(r)
            border.setParentItem(item)
            pen = QPen()
            set_pen_style(pen, self.type)
            pen.setWidth(self.width)
            pen.setCapStyle(QtCore.Qt.FlatCap)
            pen.setColor(QColor(self.color))
            border.setPen(pen)
            return border
        else:
            return None

class _Background(object):
    """ 
    Set the background of the object
    
    :param color: RGB color code or :data:`SVG_COLORS`

    """
    def __init__(self):
        self.color = None

    def apply(self, item):
        if self.color: 
            r = item.boundingRect()
            bg = QGraphicsRectItem(r)
            bg.setParentItem(item)
            pen = QPen(QColor(self.color))
            brush = QBrush(QColor(self.color))
            bg.setPen(pen)
            bg.setBrush(brush)
            bg.setFlag(QGraphicsItem.ItemStacksBehindParent)
            return bg
        else:
            return None
        


class _ActionDelegator(object):
    """ Used to associate GUI Functions to nodes and faces """ 

    def get_delegate(self):
        return self._delegate

    def set_delegate(self, delegate):
        if hasattr(delegate, "init"):
            delegate.init(self)

        for attr in dir(delegate):
            if not attr.startswith("_") and attr != "init" :
                fn = getattr(delegate, attr)
                setattr(self, attr, types.MethodType(fn, self))
        self._delegate = delegate

    delegate = property(get_delegate, set_delegate)

    def __init__(self):
        self._delegate = None
      
class NodeStyle(dict):
    """ 
    .. versionadded:: 2.1    

    .. currentmodule:: ete_dev

    A dictionary with all valid node graphical attributes.  

    :argument #0030c1 fgcolor: RGB code or name in :data:`SVG_COLORS` 
    :argument #FFFFFF bgcolor: RGB code or name in :data:`SVG_COLORS` 
    :argument #FFFFFF node_bgcolor: RGB code or name in :data:`SVG_COLORS` 
    :argument #FFFFFF partition_bgcolor: RGB code or name in :data:`SVG_COLORS` 
    :argument #FFFFFF faces_bgcolor: RGB code or name in :data:`SVG_COLORS` 
    :argument #000000 vt_line_color: RGB code or name in :data:`SVG_COLORS` 
    :argument #000000 hz_line_color: RGB code or name in :data:`SVG_COLORS` 
    :argument 0 hz_line_type: integer number
    :argument 0 vt_line_type: integer number
    :argument 3 size: integer number
    :argument "circle" shape: "circle", "square" or "sphere"
    :argument True draw_descendants: Mark an internal node as a leaf. 

    :argument 0 hz_line_width: integer number representing the width
                               of the line in pixels.  A line width of
                               zero indicates a cosmetic pen. This
                               means that the pen width is always
                               drawn one pixel wide, independent of
                               the transformation set on the painter.

    :argument 0 vt_line_width: integer number representing the width
                               of the line in pixels.  A line width of
                               zero indicates a cosmetic pen. This
                               means that the pen width is always
                               drawn one pixel wide, independent of
                               the transformation set on the painter.
    
    """

    def __init__(self, *args, **kargs):
        super(NodeStyle, self).__init__(*args, **kargs)
        self.init()
        #self._block_adding_faces = False

    def init(self):
        for key, dvalue, checker in NODE_STYLE_DEFAULT:
            if key not in self:
                self[key] = dvalue
            elif not checker(self[key]):
                raise ValueError("'%s' attribute in node style has not a valid value: %s" %\
                                     (key, self[key]))
    # 
    #    #super(NodeStyle, self).__setitem__("_faces", {})
    #    # copy fixed faces to the faces dict that will be drawn 
    #    #for pos, values in self["faces"].iteritems():
    #    #    for col, faces in values.iteritems():
    #    #        self["_faces"].setdefault(pos, {})
    #    #        self["_faces"][pos][col] = list(faces)

    def __setitem__(self, i, v):
        if i not in VALID_NODE_STYLE_KEYS:
            raise ValueError("'%s' is not a valid key for a NodeStyle instance" %i)
        super(NodeStyle, self).__setitem__(i, v)

    #def clear(self):
    #    super(NodeStyle, self).__setitem__("_faces", {})

class TreeStyle(object):
    """ 
    .. versionadded:: 2.1

    .. currentmodule:: ete_dev

    Contains all the general image properties used to render a tree

    **TREE SHAPE AND IMAGE DESIGN**
        
    :var "r" mode: Valid modes are 'c'(ircular)  or 'r'(ectangular).

    :var "False" allow_face_overlap: This option applies only for
      circular mode. It prevents aligned faces to overlap each other
      by increasing the radius of the circular tree. In very large
      trees, this may produce huge image representations. By setting
      this option to *True*, you will obtain smaller images in which
      aligned faces (typically node names) may overlap. 

    :var None layout_fn: Layout function used to dynamically control
      the aspect of nodes. Valid values are: None or a pointer to a method,
      function, etc.
                   
    :var 0 orientation: If 0, tree is drawn from left-to-right. If
       1, tree is drawn from right-to-left. This property only makes
       sense when "r" mode is used.
    
    :var 0 rotation: Tree figure will be rotate X degrees (clock-wise rotation)

    :var None scale: Scale used to convert branch lengths to
      pixels. If 'None', the scale will be calculated using the
      "tree_width" attribute (read bellow)


    :var 200 tree_width: Total width, in pixels, that tree
      branches are allowed to used. This is, the distance in
      pixels from root to the most distant leaf. If set, this
      value will be used to automatically calculate the branch
      scale.  In practice, increasing this number will cause an
      X-zoom in.

    :var 1 min_leaf_separation: Min separation, in pixels, between
      two adjacent branches

    :var 0 branch_vertical_margin: Leaf branch separation margin,
      in pixels. This will add a separation of X pixels between
      adjacent leaf branches. In practice this produces a Y-zoom
      in.

    :var 0 arc_start: When circular trees are drawn, this defines
      the starting angle (in degrees) from which leaves are
      distributed (clock-wise) around the total arc. 0 = 3 o'clock

    :var 360 arc_span: Total arc used to draw circular trees (in
      degrees)

    :var 0 margin_left: Left tree image margin, in pixels
    :var 0 margin_right: Right tree image margin, in pixels
    :var 0 margin_top: Top tree image margin, in pixels
    :var 0 margin_bottom: Bottom tree image margin, in pixels

    **TREE BRANCHES**

    :var True complete_branch_lines_when_necesary: True or False.
      When top-branch and bottom-branch faces are larger than
      branch length, branch line can be completed. Also, when
      circular trees are drawn
    :var 2 extra_branch_line_type:  0 solid, 1 dashed, 2 dotted
    :var "gray" extra_branch_line_color": RGB code or name in
      :data:`SVG_COLORS`
    
    :var False force_topology: Convert tree branches to a fixed length, thus allowing to
      observe the topology of tight nodes


    :var True draw_guiding_lines: Draw guidelines from leaf nodes
      to aligned faces
    
    :var 2 guiding_lines_type: 0 solid, 1 dashed, 2 dotted
    :var "gray" guiding_lines_color: RGB code or name in :data:`SVG_COLORS` 

    **FACES**

    :var True draw_aligned_faces_as_table: Aligned faces will be
      drawn as a table, considering all columns in all node faces.

    :var True children_faces_on_top: When floating faces from
      different nodes overlap, children faces are drawn on top of
      parent faces. This can be reversed by setting this attribute
      to false.

    **Addons**

    :var False show_border: Draw a border around the whole tree

    :var True show_scale: Include the scale legend in the tree
      image

    :var False show_leaf_name: Automatically adds a text Face to
      leaf nodes showing their names

    :var False show_branch_length: Automatically adds branch
      length information on top of branches

    :var False show_branch_support: Automatically adds branch
      support text in the bottom of tree branches

    Initialize aligned face headers

    :var aligned_header: a :class:`FaceContainer` aligned to the end
      of the tree and placed at the top part.

    :var aligned_foot: a :class:`FaceContainer` aligned to the end
      of the tree and placed at the bottom part.

    :var legend: a :class:`FaceContainer` with an arbitrary number of faces
      representing the legend of the figure. 
    :var 4 legend_position=4: TopLeft corner if 1, TopRight
      if 2, BottomLeft if 3, BottomRight if 4
    
    :var title: A text string that will be draw as the Tree title

    """
   
    def __init__(self):
        # :::::::::::::::::::::::::
        # TREE SHAPE AND SIZE
        # :::::::::::::::::::::::::
        
        # Valid modes are : "c" or "r"
        self.mode = "r"

        # Applies only for circular mode. It prevents aligned faces to
        # overlap each other by increasing the radius. 
        self.allow_face_overlap = False

        # Layout function used to dynamically control the aspect of
        # nodes
        self.layout_fn = None
        
        # 0= tree is drawn from left-to-right 1= tree is drawn from
        # right-to-left. This property only has sense when "r" mode
        # is used.
        self.orientation = 0 

        # Tree rotation in degrees (clock-wise rotation)
        self.rotation = 0 
       
        # Scale used to convert branch lengths to pixels. If 'None',
        # the scale will be calculated using the "tree_width"
        # attribute (read bellow)
        self.scale = None

        # Total width, in pixels, that tree branches are allowed to
        # used. This is, the distance in pixels from root to the most
        # distant leaf. If set, this value will be used to
        # automatically calculate the branch scale.  In practice,
        # increasing this number will cause an X-zoom in.
        self.tree_width = 200

        # Min separation, in pixels, between to adjacent branches
        self.min_leaf_separation = 1 

        # Leaf branch separation margin, in pixels. This will add a
        # separation of X pixels between adjacent leaf branches. In
        # practice this produces a Y-zoom in.
        self.branch_vertical_margin = 0

        # When circular trees are drawn, this defines the starting
        # angle (in degrees) from which leaves are distributed
        # (clock-wise) around the total arc. 0 = 3 o'clock
        self.arc_start = 0 

        # Total arc used to draw circular trees (in degrees)
        self.arc_span = 360

        # Margins around tree picture
        self.margin_left = 1
        self.margin_right = 1
        self.margin_top = 1
        self.margin_bottom = 1

        # :::::::::::::::::::::::::
        # TREE BRANCHES
        # :::::::::::::::::::::::::

        # When top-branch and bottom-branch faces are larger than
        # branch length, branch line can be completed. Also, when
        # circular trees are drawn, 
        self.complete_branch_lines_when_necesary = True
        self.extra_branch_line_type = 2 # 0 solid, 1 dashed, 2 dotted
        self.extra_branch_line_color = "gray" 

        # Convert tree branches to a fixed length, thus allowing to
        # observe the topology of tight nodes
        self.force_topology = False

        # Draw guidelines from leaf nodes to aligned faces
        self.draw_guiding_lines = True

        # Format and color for the guiding lines
        self.guiding_lines_type = 2 # 0 solid, 1 dashed, 2 dotted
        self.guiding_lines_color = "gray"

        # :::::::::::::::::::::::::
        # FACES
        # :::::::::::::::::::::::::

        # Aligned faces will be drawn as a table, considering all
        # columns in all node faces.
        self.draw_aligned_faces_as_table = True
        self.aligned_table_style = 0 # 0 = full grid (rows and
                                     # columns), 1 = semigrid ( rows
                                     # are merged )

        # When floating faces from different nodes overlap, children
        # faces are drawn on top of parent faces. This can be reversed
        # by setting this attribute to false.
        self.children_faces_on_top = True

        # :::::::::::::::::::::::::
        # Addons
        # :::::::::::::::::::::::::

        # Draw a border around the whole tree
        self.show_border = False

        # Draw the scale 
        self.show_scale = True

        # Initialize aligned face headers
        self.aligned_header = FaceContainer()
        self.aligned_foot = FaceContainer()

        self.show_leaf_name = True
        self.show_branch_length = False
        self.show_branch_support = False

        self.legend = FaceContainer()
        self.legend_position = 2

        # A text string that will be draw as the Tree title
        self.title = FaceContainer()
        self.__closed__ = 1

    def set_layout_fn(self, layout):
        # Validates layout function
        if type(layout) == types.FunctionType or\
                type(layout) == types.MethodType or layout is None:
            #self._layout_fn = layout       
            self._layout_handler = layout
        else:
            try:
                import layouts
                self._layout_handler = getattr(layouts, layout)
                #self._layout_fn = layout       
            except Exception, e:
                print e
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")
 
    def get_layout_fn(self):
        return self._layout_handler

    layout_fn = property(get_layout_fn, set_layout_fn)

    def __setattr__(self, attr, val):
        if hasattr(self, attr) or not getattr(self, "__closed__", 0):
            if TREE_STYLE_CHECKER.get(attr, lambda x: True)(val):
                object.__setattr__(self, attr, val)
            else:
                raise ValueError("[%s] wrong type" %attr)
        else:
            raise ValueError("[%s] option is not supported" %attr)
        
class _FaceAreas(object):
    def __init__(self):
        for a in FACE_POSITIONS:
            setattr(self, a, FaceContainer())

    def __setattr__(self, attr, val):
        if attr not in FACE_POSITIONS:
            raise AttributeError("Face area [%s] not in %s" %(attr, FACE_POSITIONS) )
        return super(_FaceAreas, self).__setattr__(attr, val)

    def __getattr__(self, attr):
        if attr not in FACE_POSITIONS:
            raise AttributeError("Face area [%s] not in %s" %(attr, FACE_POSITIONS) )
        return super(_FaceAreas, self).__getattr__(attr)

class FaceContainer(dict):
    """
    .. versionadded:: 2.1

    Use this object to create a grid of faces. You can add faces to different columns. 
    """
    def add_face(self, face, column):
        """ 
        add the face **face** to the specified **column**
        """
        self.setdefault(int(column), []).append(face)

def _leaf(node):
    collapsed = hasattr(node, "img_style") and not node.img_style["draw_descendants"]
    return collapsed or node.is_leaf()

def add_face_to_node(face, node, column, aligned=False, position="branch-right"):
    """ 
    .. currentmodule:: ete_dev.treeview.faces

    Adds a Face to a given node. 

    :argument face: A :class:`Face` instance

    .. currentmodule:: ete_dev

    :argument node: a tree node instance (:class:`TreeNode`, :class:`phylo.PhyloNode`, etc.)
    :argument column: An integer number starting from 0
    :argument "branch-right" position: Possible values are
      "branch-right", "branch-top", "branch-bottom", "float", "aligned"
    """ 

    ## ADD HERE SOME TYPE CHECK FOR node and face

    # to stay 2.0 compatible 
    if aligned == True:
        position = "aligned"

    if getattr(node, "_temp_faces", None):
        getattr(node._temp_faces, position).add_face(face, column)
    else:
        print node
        print getattr(node, "_temp_faces", None)
        raise Exception("This function can only be called within a layout function. Use node.add_face() instead")

def random_color(base=None):
    s = 0.5#random.random()
    v = 0.5+random.random()/2
    s = random.random()
    v = random.random()
    if not base:
        base = random.random()
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])


def set_pen_style(pen, line_style):
    if line_style == 0:
        pen.setStyle(QtCore.Qt.SolidLine)
    elif line_style == 1:
        pen.setStyle(QtCore.Qt.DashLine)
    elif line_style == 2:
        pen.setStyle(QtCore.Qt.DotLine)
     

def save(scene, imgName, w=None, h=None, dpi=300,\
             take_region=False, units="px"):

    ext = imgName.split(".")[-1].upper()
    main_rect = scene.sceneRect()
    aspect_ratio = main_rect.height() / main_rect.width()

    # auto adjust size    
    if not w and not h:
        units = "mm"
        w = 205 
        h = 292
        ratio_mode = QtCore.Qt.KeepAspectRatio
    elif w and h: 
        ratio_mode = QtCore.Qt.IgnoreAspectRatio
    elif h is None :
        h = w * aspect_ratio
        ratio_mode = QtCore.Qt.KeepAspectRatio
    elif w is None:
        w = h / aspect_ratio
        ratio_mode = QtCore.Qt.KeepAspectRatio
    
    # Adjust to resolution
    if units == "mm":
        if w: 
            w = w * 0.0393700787 * dpi
        if h: 
            h = h * 0.0393700787 * dpi
    elif units == "in":
        if w: 
            w = w * dpi
        if h: 
            h = h * dpi
    elif units == "px":
        pass
    else:
        raise Exception("wrong unit format")

    if ext == "SVG": 
        from PyQt4 import QtSvg
        svg = QtSvg.QSvgGenerator()
        svg.setFileName(imgName)
        targetRect = QtCore.QRectF(0, 0, w, h)
        svg.setSize(QtCore.QSize(w, h))
        svg.setViewBox(targetRect)
        svg.setTitle("Generated with ETE http://ete.cgenomics.org")
        svg.setDescription("Generated with ETE http://ete.cgenomics.org")

        pp = QPainter()
        pp.begin(svg)
        scene.render(pp, targetRect, scene.sceneRect(), ratio_mode)
        pp.end() 
        # Fix a very annoying problem with Radial gradients in
        # inkscape and browsers...
        temp_compatible_code = open(imgName).read().replace("xml:id=", "id=")
        compatible_code = re.sub('font-size="(\d+)"', 'font-size="\\1pt"', temp_compatible_code)
        open(imgName, "w").write(compatible_code)
        # End of fix

    elif ext == "PDF" or ext == "PS":
        if ext == "PS":
            format = QPrinter.PostScriptFormat
        else:
            format = QPrinter.PdfFormat

        printer = QPrinter(QPrinter.HighResolution)
        printer.setResolution(dpi)
        printer.setOutputFormat(format)
        #printer.setPageSize(QPrinter.A4)
        printer.setPaperSize(QtCore.QSizeF(w, h), QPrinter.DevicePixel)
        printer.setPageMargins(0, 0, 0, 0, QPrinter.DevicePixel) 

        #pageTopLeft = printer.pageRect().topLeft()
        #paperTopLeft = printer.paperRect().topLeft()
        # For PS -> problems with margins
        #print paperTopLeft.x(), paperTopLeft.y()
        #print pageTopLeft.x(), pageTopLeft.y()
        # print  printer.paperRect().height(),  printer.pageRect().height()
        #topleft =  pageTopLeft - paperTopLeft

        printer.setFullPage(True);
        printer.setOutputFileName(imgName);
        pp = QPainter(printer)
        targetRect =  QtCore.QRectF(0, 0 , w, h)
        scene.render(pp, targetRect, scene.sceneRect(), ratio_mode)
    else:
        targetRect = QtCore.QRectF(0, 0, w, h)
        ii= QImage(w, h, QImage.Format_ARGB32)
        ii.fill(QColor(QtCore.Qt.white).rgb())
        ii.setDotsPerMeterX(dpi / 0.0254) # Convert inches to meters
        ii.setDotsPerMeterY(dpi / 0.0254)
        pp = QPainter(ii)
        pp.setRenderHint(QPainter.Antialiasing)
        pp.setRenderHint(QPainter.TextAntialiasing)
        pp.setRenderHint(QPainter.SmoothPixmapTransform)

        scene.render(pp, targetRect, scene.sceneRect(), ratio_mode)
        pp.end()
        ii.save(imgName)

