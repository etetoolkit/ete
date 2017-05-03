# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
#
#                     ABOUT THE ETE PACKAGE
#                     =====================
#
# ETE is distributed under the GPL copyleft license (2008-2015).
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in
# the toolkit may be available in the documentation.
#
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
#
# #END_LICENSE#############################################################
from __future__ import absolute_import
from .qt import *
from .main import _leaf

class RectPartition(QGraphicsRectItem):
    def __init__(self, *args):
        QGraphicsRectItem.__init__(self, *args)
        self.drawbg = False
        self.nodeRegion = QRectF()
        self.facesRegion = QRectF()
        self.fullRegion = QRectF()

    def paint(self, painter, option, index):
        if self.drawbg:
            painter.setClipRect( option.exposedRect )
            return QGraphicsRectItem.paint(self, painter, option, index)

def get_partition_center(n, n2i, n2f):
        down_h = n2f[n]["branch-bottom"].h
        up_h = n2f[n]["branch-top"].h

        #right_h = max(n2f[n]["branch-right"].h, n.img_style["size"]) /2
        right_h = n2i[n].nodeRegion.height()/2

        up_h = max(right_h, up_h)
        down_h = max(right_h, down_h)

        fullR = n2i[n].fullRegion

        if _leaf(n):
            center = fullR.height()/2
        else:
            first_child_part = n2i[n.children[0]]
            last_child_part = n2i[n.children[-1]]
            c1 = first_child_part.start_y + first_child_part.center
            c2 = last_child_part.start_y + last_child_part.center
            center = c1 + ((c2-c1)/2)

        if up_h > center:
            center = up_h
        elif down_h > fullR.height() - center:
            center = fullR.height() - down_h

        return center

def init_rect_leaf_item(node, n2i, n2f):
    item = n2i[node]
    item.center = get_partition_center(node, n2i, n2f)

def init_rect_node_item(node, n2i, n2f):
    item = n2i[node]
    all_childs_height = sum([n2i[c].fullRegion.height() for c in node.children])
    all_childs_width = max([n2i[c].fullRegion.width() for c in node.children])
    if all_childs_height > item.fullRegion.height():
        item.fullRegion.setHeight(all_childs_height)

    item.fullRegion.setWidth(all_childs_width + item.nodeRegion.width())

    suby = 0
    subx = item.nodeRegion.width()
    if item.nodeRegion.height() > all_childs_height:
        suby += ((item.fullRegion.height() - all_childs_height))/2

    for c in node.children:
        cpart = n2i[c]
        # Sets x and y position of child within parent
        # partition (relative positions)
        cpart.setParentItem(item)
        cpart.setPos(subx, suby)
        cpart.start_y = suby
        suby += cpart.fullRegion.height()
    item.center = get_partition_center(node, n2i, n2f)
