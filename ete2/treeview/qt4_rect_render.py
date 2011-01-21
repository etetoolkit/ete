from PyQt4 import QtCore, QtGui

class RectPartition(QtGui.QGraphicsRectItem):
    def __init__(self, *args):
        QtGui.QGraphicsRectItem.__init__(self, *args)
        self.drawbg = False
        self.nodeRegion = QtCore.QRectF()
        self.facesRegion = QtCore.QRectF()
        self.fullRegion = QtCore.QRectF()

    def paint(self, painter, option, index):
        if self.drawbg:
            painter.setClipRect( option.exposedRect )
            return QtGui.QGraphicsRectItem.paint(self, painter, option, index)

def get_partition_center(n, n2i, n2f):
        down_h = n2f[n]["branch-bottom"].h
        up_h = n2f[n]["branch-top"].h

        right_h = max(n2f[n]["branch-right"].h, n.img_style["size"]) /2
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

    item.fullRegion.setWidth(all_childs_height+item.nodeRegion.width())

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

def draw_tree_surrondings(self):
    # Prepares and renders aligned face headers. Used to latter
    # place aligned faces
    column2max_width = {}
    aligned_face_headers = {}
    aligned_header = self.props.aligned_header
    aligned_foot = self.props.aligned_foot
    all_columns = set(aligned_header.keys() + aligned_foot.keys())
    header_afaces = {}
    foot_afaces = {}
    for c in all_columns:
        if c in aligned_header:
            faces = aligned_header[c]
            fb = _FaceGroupItem({0:faces}, None)
            fb.setParentItem(self.mainItem)
            header_afaces[c] = fb
            column2max_width[c] = fb.w

        if c in aligned_foot:
            faces = aligned_foot[c]
            fb = _FaceGroupItem({0:faces}, None)
            fb.setParentItem(self.mainItem)
            foot_afaces[c] = fb
            column2max_width[c] = max(column2max_width.get(c,0), fb.w)

    # Place aligned faces and calculates the max size of each
    # column (needed to place column headers)
    if self.props.draw_aligned_faces_as_grid: 
        for fb in self.aligned_faces:
            for c, size in fb.column2size.iteritems():
                if size[0] > column2max_width.get(c, 0):
                    column2max_width[c] = size[0]


    # Place aligned faces
    for fb in self.aligned_faces:
        fb.set_min_column_widths(column2max_width)
        fb.update_columns_size()
        fb.render()
        pos = fb.mapFromScene(self.i_width, 0)
        fb.setPos(pos.x(), fb.y())

        if self.props.draw_guidelines:
            guideline = QtGui.QGraphicsLineItem()
            partition = fb.parentItem()
            guideline.setParentItem(partition)
            guideline.setLine(partition.rect().width(), partition.center,\
                              pos.x(), partition.center)
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(self.props.guideline_color))
            set_pen_style(pen, self.props.guideline_type)
            guideline.setPen(pen)

    # Place faces around tree
    x = self.i_width
    y = self.i_height
    max_up_height = 0
    max_down_height = 0
    for c in column2max_width:
        fb_up = header_afaces.get(c, None)
        fb_down = foot_afaces.get(c, None)
        fb_width = 0
        if fb_up: 
            fb_up.render()
            fb_up.setPos(x, -fb_up.h)
            fb_width = fb_up.w 
            max_up_height = max(max_up_height, fb_up.h)
        if fb_down:
            fb_down.render()
            fb_down.setPos(x, y)
            fb_width = max(fb_down.w, fb_width) 
            max_down_height = max(max_down_height, fb_down.h)
        x += column2max_width.get(c, fb_width)

    # updates image size
    self.i_width += sum(column2max_width.values())
    self.i_height += max_down_height + max_up_height
    self.mainItem.moveBy(0, max_up_height)

def _leaf(node):
    """ Returns true if node is a leaf or if draw_descendants style is
    set to false """ 
    if node.is_leaf() or not node.img_style.get("draw_descendants", True):
        return True
    return False

    
