import re
from ete_dev import Tree, PhyloTree, ClusterTree

# I currently use qt4 for both rendering and gui
from PyQt4  import QtGui
from qt4gui import _MainApp, _PropertiesDialog
from qt4render import _TreeScene

__all__ = ["show_tree", "render_tree", "TreeImageProperties", "NodeStyleDict"]

_QApp = None

class TreeImageProperties(object):
    def __init__(self):
        self.force_topology             = False
        self.tree_width                 = 200  # This is used to scale
                                               # the tree branches
        self.draw_aligned_faces_as_grid = True
        self.draw_guidelines = False
        self.guideline_type = 2 # 0 solid, 1 dashed, 2 dotted
        self.guideline_color = "#CCCCCC"
        self.draw_image_border = False
        self.complete_branch_lines = True
        self.extra_branch_line_color = "#cccccc"
        self.show_legend = True
        self.min_branch_separation = 1 # in pixels
        self.search_node_bg = "#cccccc"
        self.search_node_fg = "#ff0000"
        self.aligned_header = FaceHeader() # aligned face_header
        self.aligned_foot = FaceHeader()
        self.title = None
        self.botton_line_text = None

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)

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
            ["draw_descendants", True,         _BOOL_CHECKER   ],
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

class FaceHeader(dict):
    def add_face(self, face, column):
        self.setdefault(int(column), []).append(face)

def show_tree(t, layout=None, img_properties=None):
    """ Interactively shows a tree."""
    global _QApp

    if not layout:
        if t.__class__ == PhyloTree:
            layout = "phylogeny"
        elif t.__class__ == ClusterTree:
            layout = "large"
        else:
            layout = "basic"

    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    mainapp = _MainApp(scene)

    if not img_properties:
        img_properties = TreeImageProperties()
    scene.initialize_tree_scene(t, layout, \
                                    tree_properties=img_properties)
    scene.draw()

    mainapp.show()
    _QApp.exec_()

def render_tree(t, imgName, w=None, h=None, layout=None, \
                    img_properties = None, header=None):
    """ Render tree image into a PNG file."""

    if not layout:
        if t.__class__ == PhyloTree:
            layout = "phylogeny"
        elif t.__class__ == ClusterTree:
            layout = "large"
        else:
            layout = "basic"


    global _QApp
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    if not img_properties:
        img_properties = TreeImageProperties()
    scene.initialize_tree_scene(t, layout,
                                tree_properties=img_properties)
    scene.draw()
    imgmap = scene.get_tree_img_map()
    scene.save(imgName, w=w, h=h, header=header)
    return imgmap   
