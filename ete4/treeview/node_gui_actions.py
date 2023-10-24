from functools import partial

from .qt import Qt, QDialog, QMenu, QCursor, QInputDialog
from ..utils import random_color
from . import  _show_newick
from ..evol import EvolTree

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

            if isinstance(self.node, EvolTree) and self.node.root._is_mark_mode():
                root = self.node.root
                all_marks = set([getattr(n, "mark", '').replace('#', '').strip()
                                 for n in root.traverse() if n is not self.node])
                all_marks.discard('')

                max_value = max(map(int, all_marks)) if all_marks else 0

                current_mark = getattr(self.node, "mark", "")
                try:
                    current_mark = int(current_mark.replace('#', ''))
                except:
                    current_mark = 0

                if current_mark > max_value:
                    self._gui_unmark_node()
                else:
                    self._gui_mark_node('#%d'% (current_mark + 1))


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

        if isinstance(self.node, EvolTree):
            root = self.node.root
            all_marks = set([getattr(n, "mark", '').replace('#', '').strip()
                             for n in root.traverse() if n is not self.node])
            all_marks.discard('')
            max_value = max(map(int, all_marks)) if all_marks else 1

            current_mark = getattr(self.node, "mark", '').replace('#', '').strip()
            current_mark = int(current_mark) if current_mark != '' else 0

            if current_mark <= max_value:
                mark = "#%d" %(current_mark + 1)
                contextMenu.addAction("ETE-evol: mark node as " + mark, partial(
                    self._gui_mark_node, mark))
                contextMenu.addAction("ETE-evol: mark group as " + mark, partial(
                    self._gui_mark_group, mark))

            if getattr(self.node, "mark", None):
                contextMenu.addAction("ETE-evol: clear mark in node", partial(
                    self._gui_unmark_node))
                contextMenu.addAction("ETE-evol: clear mark in group", partial(
                    self._gui_unmark_group))


        contextMenu.addAction( "Show newick", self.show_newick)
        contextMenu.exec(QCursor.pos())

    def _gui_mark_node(self, mark=None):
        if not mark:
            if self.node.mark:
                mark = '#' + str(int(self.node.mark.replace('#', '')) + 1)
            else:
                mark = '#1'
        self.node.mark_tree([self.node.node_id], marks=[mark])
        self.scene().GUI.redraw()


    def _gui_unmark_node(self):
        self.node.mark = ""
        self.scene().GUI.redraw()

    def _gui_mark_group(self, mark=None):
        self.node.mark_tree([self.node.node_id], marks=[mark])
        for leaf in self.node.descendants():
            leaf.mark_tree([leaf.node_id], marks=[mark])
        self.scene().GUI.redraw()

    def _gui_unmark_group(self):
        self.node.mark = ""
        for leaf in self.node.descendants():
            leaf.mark = ""
        self.scene().GUI.redraw()

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
