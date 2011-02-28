import colorsys
import random
import re
import types 

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)

FACE_POSITIONS = set(["branch-right", "branch-top", "branch-bottom", "float", "aligned"])

__all__  = ["NodeStyleDict", "TreeImage", "_leaf", "add_face_to_node"]

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
    ["size",             6,            _SIZE_CHECKER                            ], # node circle size 
    ["shape",            "sphere",     _NODE_TYPE_CHECKER                       ], 
    ["draw_descendants", True,         _BOOL_CHECKER                            ],
    ["hz_line_width",          1,      _SIZE_CHECKER                            ],
    ["vt_line_width",          1,      _SIZE_CHECKER                            ]
    ]

# _faces and faces are registered to allow deepcopy to work on nodes
VALID_NODE_STYLE_KEYS = set([i[0] for i in NODE_STYLE_DEFAULT]) | set(["_faces", "faces"])

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

      
class NodeStyleDict(dict):
    def __init__(self, *args, **kargs):

        super(NodeStyleDict, self).__init__(*args, **kargs)
        super(NodeStyleDict, self).__setitem__("faces", {})
        self.init()
        self._block_adding_faces = False

    def init(self):
        for key, dvalue, checker in NODE_STYLE_DEFAULT:
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
            
        """ 
        Add faces as a fixed feature of this node style. This faces
        are always rendered.

        face: a Face compatible instance
        Valid positions: %s
        column: an integer number defining face relative position
         """ %FACE_POSITIONS
        self["faces"].setdefault(position, {})
        self["faces"][position].setdefault(int(column), []).append(face)

    def __setitem__(self, i, y):
        if i not in VALID_NODE_STYLE_KEYS:
            raise ValueError("'%s' is not a valid key for NodeStyleDict instances" %i)
        super(NodeStyleDict, self).__setitem__(i, y)

    def clear(self):
        super(NodeStyleDict, self).__setitem__("_faces", {})

class TreeImage(object):

    def __init__(self):

        # :::::::::::::::::::::::::
        # TREE SHAPE AND SIZE
        # :::::::::::::::::::::::::
        
        # Valid modes are : "circular" or "rect"
        self.mode = "circular"

        # Layout function used to dynamically control the aspect of
        # nodes
        self.layout = None
        
        # 0= tree is drawn from left-to-right 1= tree is drawn from
        # right-to-left. This property only has sense when "rect" mode
        # is used.
        self.orientation = 0 
        
        # Scale used to convert branch lengths to pixels. If 'None',
        # the scale will be calculated using the "tree_width"
        # attribute (read bellow)
        self.scale = None

        # Total width, in pixels, that tree branches are allowed to
        # used. This is, the distance in pixels from root to the most
        # distant leaf. If set, this value will be used to
        # automatically calculate the branch scale.
        self.tree_width = 200

        # Min separation, in pixels, between to adjacent branches
        self.min_leaf_separation = 1 

        # When circular trees are drawn, this defines the starting
        # angle (in degrees) from which leaves are distribute
        # (clock-wise) around the total arc. 0 = 3 o'clock
        self.arc_start = 0 

        # Total arc used to draw circular trees (in degrees)
        self.arc_span = 360

        # :::::::::::::::::::::::::
        # TREE BRANCHES
        # :::::::::::::::::::::::::

        # When top-branch and bottom-branch faces are larger than
        # branch length, branch line can be completed. Also, when
        # circular trees are drawn, 
        self.complete_branch_lines_when_necesary = True
        self.extra_branch_line_color = "#cccccc"

        # Convert tree branches to a fixed length, thus allowing to
        # observe the topology of tight nodes
        self.force_topology = False

        # Draw guidelines from leaf nodes to aligned faces
        self.draw_guiding_lines = True

        # Format and color for the guiding lines
        self.guiding_lines_type = 1 # 0 solid, 1 dashed, 2 dotted
        self.guiding_lines_color = "gray"

        # :::::::::::::::::::::::::
        # FACES
        # :::::::::::::::::::::::::

        # Aligned faces will be drawn as a table, considering all
        # columns in all node faces.
        self.draw_aligned_faces_as_grid = True

        # By default, floating faces are expected to be transparent,
        # so they can be plotted directly on the tree image. However,
        # you can also render all floating faces under the tree to
        # ensure total tree topology visibility
        self.floating_faces_under_tree = False

        # When floating faces from different nodes overlap, children
        # faces are drawn on top of parent faces. This can be reversed
        # by setting this attribute to false.
        self.children_faces_on_top = True

        # :::::::::::::::::::::::::
        # Addons
        # :::::::::::::::::::::::::

        # Draw a border around the whole tree
        self.draw_image_border = False

        # Draw the scale 
        self.draw_image_border = False

        # Initialize aligned face headers
        self.aligned_header = FaceHeader()
        self.aligned_foot = FaceHeader()

    def set_layout_fn(self, layout):
        # Validates layout function
        if type(layout) == types.FunctionType or\
                type(layout) == types.MethodType:
            self._layout_fn = layout       
            self._layout_handler = layout
        else:
            try:
                self._layout_handler = getattr(layouts, img.layout_fn)
                self._layout_fn = layout       
            except Exception:
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")
 
    def get_layout_fn(self):
        return self._layout_fn

    layout_fn = property(get_layout_fn, set_layout_fn)
        
class FaceHeader(dict):
    def add_face(self, face, column):
        self.setdefault(int(column), []).append(face)

def _leaf(node):
    collapsed = hasattr(node, "img_style") and not node.img_style["draw_descendants"]
    return collapsed or node.is_leaf()


def add_face_to_node(face, node, column, aligned=False, position="branch-right"):
    """ Links a node with a given face instance.  """
    node.img_style.setdefault("_faces", {})
    if position not in FACE_POSITIONS:
        raise (ValueError, "Incorrect position") 
    if aligned:
        position = "aligned"

    node.img_style["_faces"].setdefault(position, {})
    node.img_style["_faces"][position].setdefault(int(column), []).append(face)

def random_color(base=None):
    s = 0.5#random.random()
    v = 0.5+random.random()/2
    s = random.random()
    v = random.random()
    if not base:
        base = random.random()
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])
