import re

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)

FACE_POSITIONS = set(["branch-right", "aligned", "branch-top", "branch-bottom"])

__all__  = ["NodeStyleDict", "TreeImage", "_leaf", "add_face_to_node"]

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
        
        self.layout_fn = None

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
                    if isinstance(f, _TextFaceItem):
                        size = f.mapToScene(f.boundingRect().width(), \
                                                f.boundingRect().height())
                        face_list.append([pos.x(),pos.y(),size.x(),size.y(), nid, str(f.text())])
                    else:
                        size = f.mapToScene(f.boundingRect().width(), f.boundingRect().height())
                        face_list.append([pos.x(),pos.y(),size.x(),size.y(), nid, None])
        nid += 1
    return {"nodes": node_list, "faces": face_list}
