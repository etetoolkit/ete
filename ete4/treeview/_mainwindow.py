from __future__ import absolute_import
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
from __future__ import absolute_import
#from .qt import QtCore, QtGui
from .qt import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(673, 493)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 673, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setEnabled(True)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea(Qt.TopToolBarArea), self.toolBar)
        self.actionOpen = QAction(MainWindow)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/ete icons/fileopen.png"), QIcon.Normal, QIcon.Off)
        self.actionOpen.setIcon(icon)
        font = QFont()
        self.actionOpen.setFont(font)
        self.actionOpen.setObjectName("actionOpen")
        self.actionPaste_newick = QAction(MainWindow)
        self.actionPaste_newick.setObjectName("actionPaste_newick")
        self.actionSave_image = QAction(MainWindow)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/ete icons/filesave.png"), QIcon.Normal, QIcon.Off)
        self.actionSave_image.setIcon(icon1)
        self.actionSave_image.setObjectName("actionSave_image")
        self.actionSave_region = QAction(MainWindow)
        self.actionSave_region.setObjectName("actionSave_region")
        self.actionBranchLength = QAction(MainWindow)
        self.actionBranchLength.setCheckable(True)
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(":/ete icons/show_dist.png"), QIcon.Normal, QIcon.Off)
        self.actionBranchLength.setIcon(icon2)
        self.actionBranchLength.setObjectName("actionBranchLength")
        self.actionZoomIn = QAction(MainWindow)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(":/ete icons/zoom_in.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomIn.setIcon(icon3)
        self.actionZoomIn.setObjectName("actionZoomIn")
        self.actionZoomOut = QAction(MainWindow)
        icon4 = QIcon()
        icon4.addPixmap(QPixmap(":/ete icons/zoom_out.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomOut.setIcon(icon4)
        self.actionZoomOut.setObjectName("actionZoomOut")
        self.actionETE = QAction(MainWindow)
        self.actionETE.setObjectName("actionETE")
        self.actionForceTopology = QAction(MainWindow)
        self.actionForceTopology.setCheckable(True)
        icon5 = QIcon()
        icon5.addPixmap(QPixmap(":/ete icons/force_topo.png"), QIcon.Normal, QIcon.Off)
        self.actionForceTopology.setIcon(icon5)
        self.actionForceTopology.setProperty("HOLA", False)
        self.actionForceTopology.setObjectName("actionForceTopology")
        self.actionSave_newick = QAction(MainWindow)
        self.actionSave_newick.setIcon(icon1)
        self.actionSave_newick.setObjectName("actionSave_newick")
        self.actionZoomInX = QAction(MainWindow)
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(":/ete icons/x_expand.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomInX.setIcon(icon6)
        self.actionZoomInX.setObjectName("actionZoomInX")
        self.actionZoomOutX = QAction(MainWindow)
        icon7 = QIcon()
        icon7.addPixmap(QPixmap(":/ete icons/x_reduce.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomOutX.setIcon(icon7)
        self.actionZoomOutX.setObjectName("actionZoomOutX")
        self.actionZoomInY = QAction(MainWindow)
        icon8 = QIcon()
        icon8.addPixmap(QPixmap(":/ete icons/y_expand.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomInY.setIcon(icon8)
        self.actionZoomInY.setObjectName("actionZoomInY")
        self.actionZoomOutY = QAction(MainWindow)
        icon9 = QIcon()
        icon9.addPixmap(QPixmap(":/ete icons/y_reduce.png"), QIcon.Normal, QIcon.Off)
        self.actionZoomOutY.setIcon(icon9)
        self.actionZoomOutY.setProperty("actionBranchSupport", False)
        self.actionZoomOutY.setObjectName("actionZoomOutY")
        self.actionFit2tree = QAction(MainWindow)
        icon10 = QIcon()
        icon10.addPixmap(QPixmap(":/ete icons/fit_tree.png"), QIcon.Normal, QIcon.Off)
        self.actionFit2tree.setIcon(icon10)
        self.actionFit2tree.setObjectName("actionFit2tree")
        self.actionFit2region = QAction(MainWindow)
        icon11 = QIcon()
        icon11.addPixmap(QPixmap(":/ete icons/fit_region.png"), QIcon.Normal, QIcon.Off)
        self.actionFit2region.setIcon(icon11)
        self.actionFit2region.setObjectName("actionFit2region")
        self.actionRenderPDF = QAction(MainWindow)
        icon12 = QIcon()
        icon12.addPixmap(QPixmap(":/ete icons/export_pdf.png"), QIcon.Normal, QIcon.Off)
        self.actionRenderPDF.setIcon(icon12)
        self.actionRenderPDF.setObjectName("actionRenderPDF")
        self.actionSearchNode = QAction(MainWindow)
        icon13 = QIcon()
        icon13.addPixmap(QPixmap(":/ete icons/search.png"), QIcon.Normal, QIcon.Off)
        self.actionSearchNode.setIcon(icon13)
        self.actionSearchNode.setObjectName("actionSearchNode")
        self.actionClear_search = QAction(MainWindow)
        icon14 = QIcon()
        icon14.addPixmap(QPixmap(":/ete icons/clean_search.png"), QIcon.Normal, QIcon.Off)
        self.actionClear_search.setIcon(icon14)
        self.actionClear_search.setObjectName("actionClear_search")
        self.actionShow_newick = QAction(MainWindow)
        icon15 = QIcon()
        icon15.addPixmap(QPixmap(":/ete icons/show_newick.png"), QIcon.Normal, QIcon.Off)
        self.actionShow_newick.setIcon(icon15)
        self.actionShow_newick.setObjectName("actionShow_newick")
        self.actionShow_node_attributes_box = QAction(MainWindow)
        self.actionShow_node_attributes_box.setCheckable(True)
        self.actionShow_node_attributes_box.setChecked(True)
        self.actionShow_node_attributes_box.setObjectName("actionShow_node_attributes_box")
        self.actionRender_selected_region = QAction(MainWindow)
        self.actionRender_selected_region.setIcon(icon12)
        self.actionRender_selected_region.setShortcutContext(Qt.WidgetShortcut)
        self.actionRender_selected_region.setObjectName("actionRender_selected_region")
        self.actionBranchSupport = QAction(MainWindow)
        self.actionBranchSupport.setCheckable(True)
        icon16 = QIcon()
        icon16.addPixmap(QPixmap(":/ete icons/show_support.png"), QIcon.Normal, QIcon.Off)
        self.actionBranchSupport.setIcon(icon16)
        self.actionBranchSupport.setObjectName("actionBranchSupport")
        self.actionLeafName = QAction(MainWindow)
        self.actionLeafName.setCheckable(True)
        icon17 = QIcon()
        icon17.addPixmap(QPixmap(":/ete icons/show_names.png"), QIcon.Normal, QIcon.Off)
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
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QApplication.translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(QApplication.translate("MainWindow", "File", None))
        self.menuAbout.setTitle(QApplication.translate("MainWindow", "About", None))
        self.toolBar.setWindowTitle(QApplication.translate("MainWindow", "toolBar", None))
        self.actionOpen.setText(QApplication.translate("MainWindow", "Open newick tree", None))
        self.actionOpen.setShortcut(QApplication.translate("MainWindow", "Ctrl+O", None))
        self.actionPaste_newick.setText(QApplication.translate("MainWindow", "Paste newick", None))
        self.actionPaste_newick.setShortcut(QApplication.translate("MainWindow", "Ctrl+P", None))
        self.actionSave_image.setText(QApplication.translate("MainWindow", "Save Image", None))
        self.actionSave_region.setText(QApplication.translate("MainWindow", "Save region", None))
        self.actionSave_region.setShortcut(QApplication.translate("MainWindow", "Ctrl+A", None))
        self.actionBranchLength.setText(QApplication.translate("MainWindow", "Show branch info", None))
        self.actionBranchLength.setShortcut(QApplication.translate("MainWindow", "L", None))
        self.actionZoomIn.setText(QApplication.translate("MainWindow", "Zoom in", None))
        self.actionZoomIn.setShortcut(QApplication.translate("MainWindow", "Z", None))
        self.actionZoomOut.setText(QApplication.translate("MainWindow", "Zoom out", None))
        self.actionZoomOut.setShortcut(QApplication.translate("MainWindow", "X", None))
        self.actionETE.setText(QApplication.translate("MainWindow", "ETE", None))
        self.actionForceTopology.setText(QApplication.translate("MainWindow", "Force topology", None))
        self.actionForceTopology.setToolTip(QApplication.translate("MainWindow", "Allows to see topology by setting assuming all branch lenghts are 1.0", None))
        self.actionForceTopology.setShortcut(QApplication.translate("MainWindow", "T", None))
        self.actionSave_newick.setText(QApplication.translate("MainWindow", "Save as newick", None))
        self.actionZoomInX.setText(QApplication.translate("MainWindow", "Increase X scale", None))
        self.actionZoomOutX.setText(QApplication.translate("MainWindow", "Decrease X scale", None))
        self.actionZoomInY.setText(QApplication.translate("MainWindow", "Increase Y scale", None))
        self.actionZoomOutY.setText(QApplication.translate("MainWindow", "Decrease Y scale", None))
        self.actionFit2tree.setText(QApplication.translate("MainWindow", "Fit to tree", None))
        self.actionFit2tree.setShortcut(QApplication.translate("MainWindow", "W", None))
        self.actionFit2region.setText(QApplication.translate("MainWindow", "Fit to selection", None))
        self.actionFit2region.setShortcut(QApplication.translate("MainWindow", "R", None))
        self.actionRenderPDF.setText(QApplication.translate("MainWindow", "Render PDF image", None))
        self.actionSearchNode.setText(QApplication.translate("MainWindow", "Search", None))
        self.actionSearchNode.setShortcut(QApplication.translate("MainWindow", "Ctrl+S", None))
        self.actionClear_search.setText(QApplication.translate("MainWindow", "Clear search", None))
        self.actionClear_search.setShortcut(QApplication.translate("MainWindow", "Ctrl+C", None))
        self.actionShow_newick.setText(QApplication.translate("MainWindow", "Show newick", None))
        self.actionShow_newick.setShortcut(QApplication.translate("MainWindow", "N", None))
        self.actionShow_node_attributes_box.setText(QApplication.translate("MainWindow", "Show node attributes box", None))
        self.actionRender_selected_region.setText(QApplication.translate("MainWindow", "Render selected region", None))
        self.actionBranchSupport.setText(QApplication.translate("MainWindow", "Show branch support", None))
        self.actionBranchSupport.setToolTip(QApplication.translate("MainWindow", "Show branch support", None))
        self.actionBranchSupport.setShortcut(QApplication.translate("MainWindow", "S", None))
        self.actionLeafName.setText(QApplication.translate("MainWindow", "Show leaf names", None))
        self.actionLeafName.setToolTip(QApplication.translate("MainWindow", "show leaf names", None))
        self.actionLeafName.setShortcut(QApplication.translate("MainWindow", "N", None))

from . import ete_resources_rc
