from types import FunctionType, MethodType
from collections import defaultdict


from .faces import SelectedRectFace
from .face_positions import FACE_POSITIONS, AlignedGrid
from ..utils import InvalidUsage
from .nodestyle import NodeStyle


class TreeStyle:
    def __init__(self):
        self.aligned_grid = True
        self.aligned_grid_dxs = defaultdict(lambda: 0)

        self.ultrametric = False

        self.collapse_size = 10

        # Selected face
        self._selected_face = SelectedRectFace
        self._selected_face_pos = "branch_right"

        # Active face
        self._active_face = SelectedRectFace
        self._active_face_pos = "branch_right"

        # Aligned panel headers
        self._aligned_panel_header = AlignedGrid()
        self._aligned_panel_footer = AlignedGrid()

        self._legend = []

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
    def active_face(self):
        return self._active_face

    @active_face.setter
    def active_face(self, face):
        if isinstance(face, Face):
            self._active_face = face
        else:
            raise ValueError(f'{type(face)} is not a valid Face instance')

    @property
    def active_face_pos(self):
        return self._active_face_pos

    @active_face_pos.setter
    def active_face_pos(self, pos):
        if pos in FACE_POSITIONS:
            self._active_face_pos = pos
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

    @property
    def aligned_panel_footer(self):
        return self._aligned_panel_footer

    @aligned_panel_footer.setter
    def aligned_panel_footer(self, value):
        raise invalidUsage('Attribute "aligned_panel_footer" can only be accessed.')

    def add_legend(self, title,
            variable="discrete",
            colormap={},
            value_range=None,
            color_range=None):

        entry = { "title": title, "variable": variable }

        if variable == "discrete" and colormap:
            entry["colormap"] = colormap

        elif variable == "continuous" and value_range and color_range:
            entry = { **entry, "value_range": value_range,
                      "color_range": color_range }
        else:
            return

        self._legend.append(entry)

    def get_legend(self):
        return list(self._legend)
