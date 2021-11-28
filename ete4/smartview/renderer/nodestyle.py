from sys import stderr 
import re

_LINE_TYPE_CHECKER = lambda x: x in (0,1,2)
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: x.lower() in SVG_COLORS or re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["sphere", "circle", "square"]
_BOOL_CHECKER =  lambda x: isinstance(x, bool) or x in (0,1)


NODE_STYLE_DEFAULT = [
    ["fgcolor",          "#0030c1",    _COLOR_CHECKER                           ],
    ["bgcolor",          "#FFFFFF",    _COLOR_CHECKER                           ],
    #["node_bgcolor",     "#FFFFFF",    _COLOR_CHECKER                           ],
    #["partition_bgcolor","#FFFFFF",    _COLOR_CHECKER                           ],
    #["faces_bgcolor",    "#FFFFFF",    _COLOR_CHECKER                           ],
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

# _smfaces and faces are registered to allow deepcopy to work on nodes
VALID_NODE_STYLE_KEYS = set([i[0] for i in NODE_STYLE_DEFAULT]) | set(["_smfaces"])

class NodeStyle(dict):
    """
    .. versionadded:: 2.1

    .. currentmodule:: ete3

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

    def __setitem__(self, i, v):
        # keeps compatible with ETE 2.0 version
        if i == "line_type":
            print("WARNING: [%s] keyword is deprecated and it has been replaced by %s." %\
                (i, "[hz_line_type, vt_line_type]"), file=stderr)
            print("WARNING: Support for this keyword will be removed in next ETE versions.", file=stderr)
            super(NodeStyle, self).__setitem__("hz_line_type", v)
            i = "vt_line_type"

        if i == "vlwidth":
            i = "vt_line_width"
            print("WARNING: [%s] keyword is deprecated and it has been replaced by %s." %\
                (i, "[vt_line_width]"), file=stderr)
            print("WARNING: Support for this keyword will be removed in next ETE versions.", file=stderr)
        if i == "hlwidth":
            i = "hz_line_width"
            print("WARNING: [%s] keyword is deprecated and it has been replaced by %s." %\
                (i, "[hz_line_width]"), file=stderr)
            print("WARNING: Support for this keyword will be removed in next ETE versions.", file=stderr)

        if i not in VALID_NODE_STYLE_KEYS:
            raise ValueError("'%s' is not a valid keyword for a NodeStyle instance" %i)

        super(NodeStyle, self).__setitem__(i, v)
