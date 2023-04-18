from collections import namedtuple


# Positions in a node where you can put faces (maybe NODE_POSITIONS
# would be a better name).
FACE_POSITIONS = ['branch_right', 'branch_top', 'branch_bottom', 'aligned']

Faces = namedtuple('Faces', FACE_POSITIONS)



cdef class Grid(dict):
    """Grid (dict that for each column assigns a list of items).

    The idea is to use it with faces, like this:

    d[col] == [face1, face2, ...]  # faces stacked in the column col
    """

    def add_face(self, object face, int column=0):
        """Add the given face to the specified column."""
        self.setdefault(column, []).append(face)


cdef class AlignedGrid(Grid):
    """Grid that also allows to store the horizontal size of each column (dxs).

    The idea is to use it for headers and footers in the aligned panel.
    """

    cdef public dict _grid_dxs

    def __init__(self, facecontainer=None):
        super().__init__(self)

        self._grid_dxs = {}


def make_faces():
    """Return a named tuple that for each position can store a grid of faces."""
    return Faces(
        branch_right=Grid(),
        branch_top=Grid(),
        branch_bottom=Grid(),
        aligned=Grid())
