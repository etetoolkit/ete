from .qt import Qt, QDialog, QMenu, QCursor, QInputDialog
from ..utils import random_color
from . import  _show_newick

class NewickDialog(QDialog):
    def __init__(self, node, *args):
        QDialog.__init__(self, *args)
        self.node = node

    def update_newick(self):
        f = int(self._conf.nwFormat.currentText())

        if self._conf.useAllFeatures.isChecked():
            props = None
        elif self._conf.features_list.count() == 0:
            props = []
        else:
            props = set()
            for i in range(self._conf.features_list.count()):
                props.add(str(self._conf.features_list.item(i).text()))

        nw = self.node.write(parser=f, props=props)
        self._conf.newickBox.setText(nw)

    def add_prop(self):
        aName = str(self._conf.attrName.text()).strip()
        if aName != '' and not self._conf.features_list.findItems(aName, Qt.MatchFlag.MatchCaseSensitive):
            self._conf.features_list.addItem(aName)
            self.update_newick()


    def del_prop(self):
        r = self._conf.features_list.currentRow()
        self._conf.features_list.takeItem(r)
        self.update_newick()

    def set_custom_features(self):
        state = self._conf.useAllFeatures.isChecked()
        self._conf.features_list.setDisabled(state)
        self._conf.attrName.setDisabled(state)
        self.update_newick()



class _NodeActions:
    """ Used to extend QGraphicsItem features """
    def __init__(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptHoverEvents(True)

    def mouseReleaseEvent(self, e):
        if not self.node:
            return

        if e.button() == Qt.MouseButton.RightButton:
            self.showActionPopup()
        elif e.button() == Qt.MouseButton.LeftButton:
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
        contextMenu = QMenu()
        contextMenu.addAction( "Set as outgroup", self.set_as_outgroup)
        contextMenu.addAction( "Copy partition", self.copy_partition)
        contextMenu.addAction( "Cut partition", self.cut_partition)
        if self.scene().view.buffer_node:
            contextMenu.addAction( "Paste partition", self.paste_partition)

        contextMenu.addAction( "Delete node (collapse children)", self.delete_node)
        contextMenu.addAction( "Delete partition", self.detach_node)
        contextMenu.addAction( "Populate subtree", self.populate_partition)
        contextMenu.addAction( "Add children", self.add_children)
        contextMenu.addAction( "Reverse branches", self.reverse_branches)
        if self.node.img_style["draw_descendants"] == False:
            contextMenu.addAction( "Open", self.toggle_collapse)
        else:
            contextMenu.addAction( "Close", self.toggle_collapse)

        if self.node.up is not None and\
                self.scene().tree == self.node:
            contextMenu.addAction( "Back to parent", self.back_to_parent_node)
        else:
            contextMenu.addAction( "Extract", self.set_start_node)

        contextMenu.addAction( "Show newick", self.show_newick)
        contextMenu.exec(QCursor.pos())

    def show_newick(self):
        d = NewickDialog(self.node)
        d._conf = _show_newick.Ui_Newick()
        d._conf.setupUi(d)
        d.update_newick()
        d.exec()
        return False

    def delete_node(self):
        self.node.delete()
        self.scene().GUI.redraw()

    def detach_node(self):
        self.node.detach()
        self.scene().GUI.redraw()

    def reverse_branches(self):
        self.node.reverse_children()
        self.scene().GUI.redraw()

    def add_children(self):
        n, ok = QInputDialog.getInt(None, "Add childs",
                                    "Number of childs to add:", 1, 1)
        if ok:
            for i in range(n):
                ch = self.node.add_child()
        self.scene().GUI.redraw()

    def void(self):
        return True

    def set_as_outgroup(self):
        self.scene().tree.set_outgroup(self.node)
        self.scene().GUI.redraw()

    def toggle_collapse(self):
        self.node.img_style["draw_descendants"] ^= True
        self.scene().GUI.redraw()

    def cut_partition(self):
        self.scene().view.buffer_node = self.node
        self.node.detach()
        self.scene().GUI.redraw()

    def copy_partition(self):
        self.scene().view.buffer_node = self.node.copy('deepcopy')

    def paste_partition(self):
        if self.scene().view.buffer_node:
            self.node.add_child(self.scene().view.buffer_node)
            self.scene().view.buffer_node= None
            self.scene().GUI.redraw()

    def populate_partition(self):
        n, ok = QInputDialog.getInt(None, "Populate partition",
                                    "Number of nodes to add:", 2, 1)
        if ok:
            self.node.populate(n)
            self.scene().GUI.redraw()

    def set_start_node(self):
        self.scene().start_node = self.node
        self.scene().GUI.redraw()

    def back_to_parent_node(self):
        self.scene().start_node = self.node.up
        self.scene().GUI.redraw()
