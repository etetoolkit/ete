from main import random_color
from PyQt4  import QtCore, QtGui

class _NodeActions(object):
    """ Used to extend QGraphicsItem features """
    def __init__(self):
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAcceptsHoverEvents(True)
        
    def mouseReleaseEvent(self, e):
        if not self.node: 
            return
        if e.button() == QtCore.Qt.RightButton:
            self.showActionPopup()
        elif e.button() == QtCore.Qt.LeftButton:
            self.scene().view.set_focus(self.node)
            #self.scene().view.prop_table.update_properties(self.node)


    def hoverEnterEvent (self, e):
        if self.node:
            if self.node in self.scene().view.n2hl:
                pass
            else:
                self.scene().view.highlight_node(self.node, fullRegion=True)

    def hoverLeaveEvent(self,e):
        if self.node:
            if self.node in self.scene().view.n2hl:
                self.scene().view.unhighlight_node(self.node, reset=False)
            
    def mousePressEvent(self,e):
        pass
            
    def mouseDoubleClickEvent(self,e):
        if self.node: 
            item = self.scene().n2i[self.node]
            if item.highlighted: 
                self.scene().view.unhighlight_node(self.node, reset=True)
            else:
                self.scene().view.highlight_node(self.node, fullRegion=True, 
                                                 bg=random_color(l=0.5, s=0.5), permanent=True)

    def showActionPopup(self):
        contextMenu = QtGui.QMenu()
        if self.node.img_style["draw_descendants"] == False:
            contextMenu.addAction( "Expand"           , self.toggle_collapse)
        else:
            contextMenu.addAction( "Collapse"         , self.toggle_collapse)

        contextMenu.addAction( "Set as outgroup"      , self.set_as_outgroup)
        contextMenu.addAction( "Swap branches"        , self.swap_branches)
        contextMenu.addAction( "Delete node"          , self.delete_node)
        contextMenu.addAction( "Delete partition"     , self.detach_node)
        contextMenu.addAction( "Add childs"           , self.add_children)
        contextMenu.addAction( "Populate partition"   , self.populate_partition)
        if self.node.up is not None and\
                self.scene().tree == self.node:
            contextMenu.addAction( "Back to parent", self.back_to_parent_node)
        else:
            contextMenu.addAction( "Extract"              , self.set_start_node)

        if self.scene().view.buffer_node:
            contextMenu.addAction( "Paste partition"  , self.paste_partition)

        contextMenu.addAction( "Cut partition"        , self.cut_partition)
        contextMenu.addAction( "Show newick"        , self.show_newick)
        contextMenu.exec_(QtGui.QCursor.pos())

    def show_newick(self):
        d = NewickDialog(self.node)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec_()
        return False

    def delete_node(self):
        self.node.delete()
        self.scene().draw()

    def detach_node(self):
        self.node.detach()
        self.scene().draw()

    def swap_branches(self):
        self.node.swap_children()
        self.scene().draw()

    def add_children(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Add childs","Number of childs to add:",1,1)
        if ok:
            for i in xrange(n):
                ch = self.node.add_child()
        self.scene().draw()

    def void(self):
        return True

    def set_as_outgroup(self):
        self.scene().tree.set_outgroup(self.node)
        self.scene().draw()

    def toggle_collapse(self):
        self.node.img_style["draw_descendants"] ^= True
        self.scene().draw()

    def cut_partition(self):
        self.scene().view.buffer_node = self.node
        self.node.detach()
        self.scene().draw()

    def paste_partition(self):
        if self.scene().view.buffer_node:
            self.node.add_child(self.scene().view.buffer_node)
            self.scene().view.buffer_node= None
            self.scene().draw()

    def populate_partition(self):
        n, ok = QtGui.QInputDialog.getInteger(None,"Populate partition","Number of nodes to add:",2,1)
        if ok:
            self.node.populate(n)
            #self.scene().set_style_from(self.scene().tree,self.scene().layout_func)
            self.scene().draw()

    def set_start_node(self):
        self.scene().start_node = self.node
        self.scene().draw()

    def back_to_parent_node(self):
        self.scene().start_node = self.node.up
        self.scene().draw()
