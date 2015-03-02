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
from svg_colors import random_color
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
        contextMenu.addAction( "Set as outgroup", self.set_as_outgroup)
        contextMenu.addAction( "Copy partition", self.copy_partition)
        contextMenu.addAction( "Cut partition", self.cut_partition)
        if self.scene().view.buffer_node:
            contextMenu.addAction( "Paste partition", self.paste_partition)

        contextMenu.addAction( "Delete node (collapse children)", self.delete_node)
        contextMenu.addAction( "Delete partition", self.detach_node)
        contextMenu.addAction( "Populate subtree", self.populate_partition)
        contextMenu.addAction( "Add children", self.add_children)
        contextMenu.addAction( "Swap branches", self.swap_branches)
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
        self.scene().GUI.redraw()

    def detach_node(self):
        self.node.detach()
        self.scene().GUI.redraw()

    def swap_branches(self):
        self.node.swap_children()
        self.scene().GUI.redraw()

    def add_children(self):
        n,ok = QtGui.QInputDialog.getInteger(None,"Add childs","Number of childs to add:",1,1)
        if ok:
            for i in xrange(n):
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
        n, ok = QtGui.QInputDialog.getInteger(None,"Populate partition","Number of nodes to add:",2,1)
        if ok:
            self.node.populate(n)
            #self.scene().set_style_from(self.scene().tree,self.scene().layout_func)
            self.scene().GUI.redraw()

    def set_start_node(self):
        self.scene().start_node = self.node
        self.scene().GUI.redraw()

    def back_to_parent_node(self):
        self.scene().start_node = self.node.up
        self.scene().GUI.redraw()
