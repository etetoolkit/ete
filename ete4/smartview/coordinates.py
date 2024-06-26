from collections import namedtuple

# The convention for coordinates is:
#   x increases to the right, y increases to the bottom.
#
#  +-----> x          +------.
#  |                   \     .
#  |                    \   . a    (the angle thus increases clockwise too)
#  v y                 r \.
#
# This is the convention normally used in computer graphics, including SVGs,
# HTML Canvas, Qt, and PixiJS.
#
# The boxes (shapes) we use are:
#
# * Rectangle            w
#                 x,y +-----+      so (x,y) is its (left,top) corner
#                     |     | h    and (x+w,y+h) its (right,bottom) one
#                     +-----+
#
# * Annular sector       dr
#                  r,a .----.
#                     .     .      so (r,a) is its (inner,smaller-angle) corner
#                      \   . da    and (r+dr,a+da) its (outer,bigger-angle) one
#                       \.

Size = namedtuple('Size', 'dx dy')  # size of a 2D shape (sizes are always >= 0)
Box = namedtuple('Box', 'x y dx dy')  # corner and size of a 2D shape
# They are all "generalized coordinates" (can be radius and angle, say).


def make_box(point, size):
    x, y = point
    dx, dy = size
    return Box(x, y, dx, dy)


def get_xs(box):
    x, _, dx, _ = box
    return x, x + dx


def get_ys(box):
    _, y, _, dy = box
    return y, y + dy
