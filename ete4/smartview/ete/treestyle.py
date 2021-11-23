from types import FunctionType, MethodType
from collections import defaultdict, namedtuple


from ete4.smartview import SelectedRectFace
from ete4.smartview.ete.face_positions import FACE_POSITIONS, _HeaderFaceContainer
from ete4.smartview.utils import InvalidUsage
from ete4.smartview.ete.layouts.default_layouts import get_layout_leaf_name, get_layout_nleaves,\
        get_layout_branch_length, get_layout_branch_support,\
        get_layout_outline, get_layout_align_link


aligned_panel_header = namedtuple("aligned_panel_header", ["top", "bottom"],
                                  defaults=(_HeaderFaceContainer(), _HeaderFaceContainer()))


class TreeStyle(object):
    def __init__(self):
        self._layout_handler = []
        self.aligned_grid = True
        self.aligned_grid_dxs = defaultdict(lambda: 0)
        self.show_align_link = False

        self.ultrametric = False
        
        self.show_outline = True
        self.show_leaf_name = True
        self.show_nleaves = False
        self.show_branch_length = False
        self.show_branch_support = False
        self.default_layouts = ['Outline', 'Leaf name', 'Number of leaves',
                                'Branch length', 'Branch support',
                                'Aligned panel link']
        # Selected face
        self._selected_face = SelectedRectFace
        self._selected_face_pos = "branch_right"

        # Aligned panel headers
        self._aligned_panel_header = aligned_panel_header()

        
    @property
    def layout_fn(self):
        default_layout = self._get_default_layout()
        return default_layout + self._layout_handler

    @layout_fn.setter
    def layout_fn(self, layout):
        if type(layout) not in set([list, set, tuple, frozenset]):
            layout = [layout]

        for ly in layout:
            # Validates layout function (python function)
            # Consider `callable(ly)`
            if type(ly) == FunctionType or type(ly) == MethodType or ly is None:
                name = ly.__name__
                if name in self.default_layouts:
                    self._update_layout_flags(name, True)
                else:
                    self._layout_handler.append(ly)
            else:
                raise ValueError ("Required layout is not a function pointer nor a valid layout name.")

    @property
    def selected_face(self):
        return self._selected_face

    @selected_face.setter
    def selected_face(self, face):
        if isinstance(face, Face):
            self._selected_face = face
        else:
            raise ValueError(f'{type(face)} is not a valid Face instance')

    @property
    def selected_face_pos(self):
        return self._selected_face_pos

    @selected_face_pos.setter
    def selected_face_pos(self, pos):
        if pos in FACE_POSITIONS:
            self._selected_face_pos = pos
        else:
            raise ValueError(f'{pos} is not a valid Face position. ' +
                    'Please provide one of the following values' + 
                    ', '.join(FACE_POSITIONS + '.'))

    @property
    def aligned_panel_header(self):
        return self._aligned_panel_header

    @aligned_panel_header.setter
    def aligned_panel_header(self, value):
        raise invalidUsage('Attribute "aligned_panel_header" can only be accessed.')

    def del_layout_fn(self, name):
        """ Deletes layout function given its _module:__name__ """
        # Modify flags if name refers to defaults
        module, name = name.split(":")
        if module == "default" and name in self.default_layouts:
            self._update_layout_flags(name, False)
        else:
            for layout in self.layout_fn:
                if layout.__name__ != "<lambda>" and\
                  layout._module == module and layout.__name__ == name:
                    self._layout_handler.remove(layout)

    def _update_layout_flags(self, name, status):
        if name == 'Outline':
            self.show_outline = status
        if name == 'Aligned panel link':
            self.show_align_link = status
        if name == 'Leaf name':
            self.show_leaf_name = status
        if name == 'Number of leaves':
            self.show_nleaves = status
        if name == 'Branch length':
            self.show_branch_length = status
        if name == 'Branch support':
            self.show_branch_support = status

    def _get_default_layout(self):
        layouts = []

        # Set clean node style
        try:
            clean = NodeStyle()
        except:
            from ete4 import NodeStyle
            clean = NodeStyle()

        clean['size'] = 0
        clean['bgcolor'] = 'transparent'
        layouts.append(lambda node: node.set_style(clean))

        if self.show_outline:
            layouts.append(get_layout_outline())
        if self.show_align_link:
            layouts.append(get_layout_align_link())
        if self.show_leaf_name:
            layouts.append(get_layout_leaf_name())
        if self.show_nleaves:
            layouts.append(get_layout_nleaves())
        if self.show_branch_length:
            layouts.append(get_layout_branch_length())
        if self.show_branch_support:
            layouts.append(get_layout_branch_support())
        return layouts
