from collections import namedtuple, OrderedDict

FACE_POSITIONS = ["branch_right", "branch_top", "branch_bottom", "aligned"]

_FaceAreas = namedtuple('_FaceAreas', FACE_POSITIONS)

def get_FaceAreas(branch_top=None, branch_bottom=None,
                  branch_right=None, aligned=None):
    return _FaceAreas(
            branch_top or _FaceContainer(),
            branch_bottom or _FaceContainer(),
            branch_right or _FaceContainer(),
            aligned or _FaceContainer())


cdef class _FaceContainer(dict):
    """Create a grid of faces.

    You can add faces to different columns.
    """

    def add_face(self, object face, int column):
        """Add the face to the specified column."""
        self.setdefault(column, []).append(face)


cdef class _HeaderFaceContainer(_FaceContainer):
    """Create a grid of faces for a header.

    You can add faces to different columns.
    """

    cdef public dict _grid_dxs

    def __init__(self, facecontainer=None):
        _FaceContainer.__init__(self)

        self._grid_dxs = {}
