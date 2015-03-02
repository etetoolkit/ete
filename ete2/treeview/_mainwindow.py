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
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ete_qt4app.ui'
#
# Created: Tue Jan 10 15:56:57 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(673, 493)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 673, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setEnabled(True)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), self.toolBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ete icons/fileopen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon)
        font = QtGui.QFont()
        self.actionOpen.setFont(font)
        self.actionOpen.setObjectName("actionOpen")
        self.actionPaste_newick = QtGui.QAction(MainWindow)
        self.actionPaste_newick.setObjectName("actionPaste_newick")
        self.actionSave_image = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ete icons/filesave.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_image.setIcon(icon1)
        self.actionSave_image.setObjectName("actionSave_image")
        self.actionSave_region = QtGui.QAction(MainWindow)
        self.actionSave_region.setObjectName("actionSave_region")
        self.actionBranchLength = QtGui.QAction(MainWindow)
        self.actionBranchLength.setCheckable(True)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/ete icons/show_dist.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBranchLength.setIcon(icon2)
        self.actionBranchLength.setObjectName("actionBranchLength")
        self.actionZoomIn = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/ete icons/zoom_in.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomIn.setIcon(icon3)
        self.actionZoomIn.setObjectName("actionZoomIn")
        self.actionZoomOut = QtGui.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/ete icons/zoom_out.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomOut.setIcon(icon4)
        self.actionZoomOut.setObjectName("actionZoomOut")
        self.actionETE = QtGui.QAction(MainWindow)
        self.actionETE.setObjectName("actionETE")
        self.actionForceTopology = QtGui.QAction(MainWindow)
        self.actionForceTopology.setCheckable(True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/ete icons/force_topo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionForceTopology.setIcon(icon5)
        self.actionForceTopology.setProperty("HOLA", False)
        self.actionForceTopology.setObjectName("actionForceTopology")
        self.actionSave_newick = QtGui.QAction(MainWindow)
        self.actionSave_newick.setIcon(icon1)
        self.actionSave_newick.setObjectName("actionSave_newick")
        self.actionZoomInX = QtGui.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/ete icons/x_expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomInX.setIcon(icon6)
        self.actionZoomInX.setObjectName("actionZoomInX")
        self.actionZoomOutX = QtGui.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/ete icons/x_reduce.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomOutX.setIcon(icon7)
        self.actionZoomOutX.setObjectName("actionZoomOutX")
        self.actionZoomInY = QtGui.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/ete icons/y_expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomInY.setIcon(icon8)
        self.actionZoomInY.setObjectName("actionZoomInY")
        self.actionZoomOutY = QtGui.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/ete icons/y_reduce.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomOutY.setIcon(icon9)
        self.actionZoomOutY.setProperty("actionBranchSupport", False)
        self.actionZoomOutY.setObjectName("actionZoomOutY")
        self.actionFit2tree = QtGui.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/ete icons/fit_tree.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFit2tree.setIcon(icon10)
        self.actionFit2tree.setObjectName("actionFit2tree")
        self.actionFit2region = QtGui.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/ete icons/fit_region.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFit2region.setIcon(icon11)
        self.actionFit2region.setObjectName("actionFit2region")
        self.actionRenderPDF = QtGui.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/ete icons/export_pdf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRenderPDF.setIcon(icon12)
        self.actionRenderPDF.setObjectName("actionRenderPDF")
        self.actionSearchNode = QtGui.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/ete icons/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSearchNode.setIcon(icon13)
        self.actionSearchNode.setObjectName("actionSearchNode")
        self.actionClear_search = QtGui.QAction(MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/ete icons/clean_search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClear_search.setIcon(icon14)
        self.actionClear_search.setObjectName("actionClear_search")
        self.actionShow_newick = QtGui.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/ete icons/show_newick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShow_newick.setIcon(icon15)
        self.actionShow_newick.setObjectName("actionShow_newick")
        self.actionShow_node_attributes_box = QtGui.QAction(MainWindow)
        self.actionShow_node_attributes_box.setCheckable(True)
        self.actionShow_node_attributes_box.setChecked(True)
        self.actionShow_node_attributes_box.setObjectName("actionShow_node_attributes_box")
        self.actionRender_selected_region = QtGui.QAction(MainWindow)
        self.actionRender_selected_region.setIcon(icon12)
        self.actionRender_selected_region.setShortcutContext(QtCore.Qt.WidgetShortcut)
        self.actionRender_selected_region.setObjectName("actionRender_selected_region")
        self.actionBranchSupport = QtGui.QAction(MainWindow)
        self.actionBranchSupport.setCheckable(True)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/ete icons/show_support.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBranchSupport.setIcon(icon16)
        self.actionBranchSupport.setObjectName("actionBranchSupport")
        self.actionLeafName = QtGui.QAction(MainWindow)
        self.actionLeafName.setCheckable(True)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/ete icons/show_names.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLeafName.setIcon(icon17)
        self.actionLeafName.setObjectName("actionLeafName")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionPaste_newick)
        self.menuFile.addAction(self.actionSave_newick)
        self.menuFile.addAction(self.actionRenderPDF)
        self.menuFile.addAction(self.actionRender_selected_region)
        self.menuAbout.addAction(self.actionETE)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.toolBar.addAction(self.actionZoomIn)
        self.toolBar.addAction(self.actionZoomOut)
        self.toolBar.addAction(self.actionFit2tree)
        self.toolBar.addAction(self.actionFit2region)
        self.toolBar.addAction(self.actionZoomInX)
        self.toolBar.addAction(self.actionZoomOutX)
        self.toolBar.addAction(self.actionZoomInY)
        self.toolBar.addAction(self.actionZoomOutY)
        self.toolBar.addAction(self.actionSearchNode)
        self.toolBar.addAction(self.actionClear_search)
        self.toolBar.addAction(self.actionForceTopology)
        self.toolBar.addAction(self.actionBranchLength)
        self.toolBar.addAction(self.actionBranchSupport)
        self.toolBar.addAction(self.actionLeafName)
        self.toolBar.addAction(self.actionRenderPDF)
        self.toolBar.addAction(self.actionShow_newick)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAbout.setTitle(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open newick tree", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPaste_newick.setText(QtGui.QApplication.translate("MainWindow", "Paste newick", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPaste_newick.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+P", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_image.setText(QtGui.QApplication.translate("MainWindow", "Save Image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_region.setText(QtGui.QApplication.translate("MainWindow", "Save region", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_region.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+A", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchLength.setText(QtGui.QApplication.translate("MainWindow", "Show branch info", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchLength.setShortcut(QtGui.QApplication.translate("MainWindow", "L", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setText(QtGui.QApplication.translate("MainWindow", "Zoom in", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setShortcut(QtGui.QApplication.translate("MainWindow", "Z", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setText(QtGui.QApplication.translate("MainWindow", "Zoom out", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setShortcut(QtGui.QApplication.translate("MainWindow", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.actionETE.setText(QtGui.QApplication.translate("MainWindow", "ETE", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setText(QtGui.QApplication.translate("MainWindow", "Force topology", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setToolTip(QtGui.QApplication.translate("MainWindow", "Allows to see topology by setting assuming all branch lenghts are 1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setShortcut(QtGui.QApplication.translate("MainWindow", "T", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_newick.setText(QtGui.QApplication.translate("MainWindow", "Save as newick", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomInX.setText(QtGui.QApplication.translate("MainWindow", "Increase X scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOutX.setText(QtGui.QApplication.translate("MainWindow", "Decrease X scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomInY.setText(QtGui.QApplication.translate("MainWindow", "Increase Y scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOutY.setText(QtGui.QApplication.translate("MainWindow", "Decrease Y scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFit2tree.setText(QtGui.QApplication.translate("MainWindow", "Fit to tree", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFit2tree.setShortcut(QtGui.QApplication.translate("MainWindow", "W", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFit2region.setText(QtGui.QApplication.translate("MainWindow", "Fit to selection", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFit2region.setShortcut(QtGui.QApplication.translate("MainWindow", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRenderPDF.setText(QtGui.QApplication.translate("MainWindow", "Render PDF image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSearchNode.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSearchNode.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClear_search.setText(QtGui.QApplication.translate("MainWindow", "Clear search", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClear_search.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+C", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_newick.setText(QtGui.QApplication.translate("MainWindow", "Show newick", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_newick.setShortcut(QtGui.QApplication.translate("MainWindow", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_node_attributes_box.setText(QtGui.QApplication.translate("MainWindow", "Show node attributes box", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRender_selected_region.setText(QtGui.QApplication.translate("MainWindow", "Render selected region", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchSupport.setText(QtGui.QApplication.translate("MainWindow", "Show branch support", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchSupport.setToolTip(QtGui.QApplication.translate("MainWindow", "Show branch support", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchSupport.setShortcut(QtGui.QApplication.translate("MainWindow", "S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLeafName.setText(QtGui.QApplication.translate("MainWindow", "Show leaf names", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLeafName.setToolTip(QtGui.QApplication.translate("MainWindow", "show leaf names", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLeafName.setShortcut(QtGui.QApplication.translate("MainWindow", "N", None, QtGui.QApplication.UnicodeUTF8))

import ete_resources_rc
