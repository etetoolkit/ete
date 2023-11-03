import re

_LINE_TYPE_CHECKER = lambda x: x in (0, 1, 2)  # 0 solid, 1 dashed, 2 dotted
_SIZE_CHECKER = lambda x: isinstance(x, int)
_COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
_COLOR_CHECKER = lambda x: x.lower() in SVG_COLORS or re.match(_COLOR_MATCH, x)
_NODE_TYPE_CHECKER = lambda x: x in ["triangle", "circle", "square"]
_BOOL_CHECKER = lambda x: isinstance(x, bool) or x in (0, 1)
_FLOAT_CHECKER = lambda x: isinstance(x, float) or isinstance(x, int)


NODE_STYLE_DEFAULT = [
    ["fgcolor",            "#0030c1",     _COLOR_CHECKER],
    ["bgcolor",            "transparent", _COLOR_CHECKER],
    ["fgopacity",          1,             _FLOAT_CHECKER],
    ["outline_line_color", "#000000",     _COLOR_CHECKER],
    ["outline_line_width", 0.5,           _SIZE_CHECKER],
    ["outline_color",      "#e5e5e5",     _COLOR_CHECKER],
    ["outline_opacity",    0.3,           _FLOAT_CHECKER],
    ["vt_line_color",      "#000000",     _COLOR_CHECKER],
    ["hz_line_color",      "#000000",     _COLOR_CHECKER],
    ["hz_line_type",       0,             _LINE_TYPE_CHECKER],
    ["vt_line_type",       0,             _LINE_TYPE_CHECKER],
    ["size",               0,             _SIZE_CHECKER], # node circle size
    ["shape",              "circle",      _NODE_TYPE_CHECKER],
    ["draw_descendants",   True,          _BOOL_CHECKER],
    ["hz_line_width",      0.5,           _SIZE_CHECKER],
    ["vt_line_width",      0.5,           _SIZE_CHECKER]
]


# _smfaces and faces are registered to allow deepcopy to work on nodes
VALID_NODE_STYLE_KEYS = {i[0] for i in NODE_STYLE_DEFAULT} | {"_smfaces"}

class NodeStyle(dict):
    """
    Dictionary with all valid node graphical attributes.
    """

    def __init__(self, *args, **kargs):
        """
        For all possible parameters, see NODE_STYLE_DEFAULT. Some descriptions:

        :param True draw_descendants: Mark an internal node as a leaf.
        :param 0 hz_line_width: Horizontal line width in pixels. If 0
            it is automatic (normally 1 pixel).
        :param 0 vt_line_width: Vertical line width in pixels. If 0 it
            is automatic (normally 1 pixel).
        """
        super().__init__(*args, **kargs)
        self.init()

    def init(self):
        for key, dvalue, checker in NODE_STYLE_DEFAULT:
            if key not in self:
                self[key] = dvalue
            elif not checker(self[key]):
                raise ValueError("'%s' attribute in node style has not a valid value: %s" %
                                 (key, self[key]))

    def __setitem__(self, i, v):
        if i not in VALID_NODE_STYLE_KEYS:
            raise ValueError("'%s' is not a valid keyword for a NodeStyle instance" % i)

        super().__setitem__(i, v)
