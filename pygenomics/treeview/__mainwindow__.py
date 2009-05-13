# This is a flag used to build ete2 standalone package.
in_ete_pkg=True
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ete_qt4app.ui'
#
# Created: Sun Feb 15 20:26:27 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,728,707).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0,63,728,621))
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,728,30))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuDrawing_Options = QtGui.QMenu(self.menubar)
        self.menuDrawing_Options.setObjectName("menuDrawing_Options")

        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,684,728,23))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setGeometry(QtCore.QRect(0,30,728,33))
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")

        self.actionPaste_newick = QtGui.QAction(MainWindow)
        self.actionPaste_newick.setObjectName("actionPaste_newick")

        self.actionSave_image = QtGui.QAction(MainWindow)
        self.actionSave_image.setObjectName("actionSave_image")

        self.actionSave_region = QtGui.QAction(MainWindow)
        self.actionSave_region.setObjectName("actionSave_region")

        self.actionBranchLength = QtGui.QAction(MainWindow)
        self.actionBranchLength.setObjectName("actionBranchLength")

        self.actionZoomIn = QtGui.QAction(MainWindow)
        self.actionZoomIn.setObjectName("actionZoomIn")

        self.actionZoomOut = QtGui.QAction(MainWindow)
        self.actionZoomOut.setObjectName("actionZoomOut")

        self.actionNative_scale = QtGui.QAction(MainWindow)
        self.actionNative_scale.setObjectName("actionNative_scale")

        self.actionShow_topology = QtGui.QAction(MainWindow)
        self.actionShow_topology.setObjectName("actionShow_topology")

        self.actionETE = QtGui.QAction(MainWindow)
        self.actionETE.setObjectName("actionETE")

        self.actionBranch_sclae = QtGui.QAction(MainWindow)
        self.actionBranch_sclae.setObjectName("actionBranch_sclae")

        self.actionBranch_scale = QtGui.QAction(MainWindow)
        self.actionBranch_scale.setObjectName("actionBranch_scale")

        self.actionForceTopology = QtGui.QAction(MainWindow)
        self.actionForceTopology.setObjectName("actionForceTopology")

        self.actionChange_scale = QtGui.QAction(MainWindow)
        self.actionChange_scale.setObjectName("actionChange_scale")

        self.actionSave_newick = QtGui.QAction(MainWindow)
        self.actionSave_newick.setObjectName("actionSave_newick")

        self.actionBranchSupport = QtGui.QAction(MainWindow)
        self.actionBranchSupport.setObjectName("actionBranchSupport")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionPaste_newick)
        self.menuFile.addAction(self.actionSave_image)
        self.menuFile.addAction(self.actionSave_region)
        self.menuFile.addAction(self.actionSave_newick)
        self.menuDrawing_Options.addAction(self.actionBranchLength)
        self.menuDrawing_Options.addAction(self.actionBranchSupport)
        self.menuDrawing_Options.addAction(self.actionForceTopology)
        self.menuDrawing_Options.addAction(self.actionZoomIn)
        self.menuDrawing_Options.addAction(self.actionZoomOut)
        self.menuAbout.addAction(self.actionETE)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDrawing_Options.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.toolBar.addAction(self.actionOpen)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuDrawing_Options.setTitle(QtGui.QApplication.translate("MainWindow", "Drawing Options", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAbout.setTitle(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPaste_newick.setText(QtGui.QApplication.translate("MainWindow", "Paste newick", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_image.setText(QtGui.QApplication.translate("MainWindow", "Save tree image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_region.setText(QtGui.QApplication.translate("MainWindow", "Save selection as image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchLength.setText(QtGui.QApplication.translate("MainWindow", "Show branch lenghts", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchLength.setShortcut(QtGui.QApplication.translate("MainWindow", "L", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setText(QtGui.QApplication.translate("MainWindow", "Zoom in", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setShortcut(QtGui.QApplication.translate("MainWindow", "Z", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setText(QtGui.QApplication.translate("MainWindow", "Zoom out", None, QtGui.QApplication.UnicodeUTF8))
        self.actionZoomOut.setShortcut(QtGui.QApplication.translate("MainWindow", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNative_scale.setText(QtGui.QApplication.translate("MainWindow", "Native scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNative_scale.setShortcut(QtGui.QApplication.translate("MainWindow", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_topology.setText(QtGui.QApplication.translate("MainWindow", "Show topology", None, QtGui.QApplication.UnicodeUTF8))
        self.actionShow_topology.setShortcut(QtGui.QApplication.translate("MainWindow", "T", None, QtGui.QApplication.UnicodeUTF8))
        self.actionETE.setText(QtGui.QApplication.translate("MainWindow", "ETE", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranch_sclae.setText(QtGui.QApplication.translate("MainWindow", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranch_scale.setText(QtGui.QApplication.translate("MainWindow", "Branch scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setText(QtGui.QApplication.translate("MainWindow", "Force showing topology", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setToolTip(QtGui.QApplication.translate("MainWindow", "Allows to see topology by setting assuming all branch lenghts are 1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.actionForceTopology.setShortcut(QtGui.QApplication.translate("MainWindow", "T", None, QtGui.QApplication.UnicodeUTF8))
        self.actionChange_scale.setText(QtGui.QApplication.translate("MainWindow", "Change scale", None, QtGui.QApplication.UnicodeUTF8))
        self.actionChange_scale.setShortcut(QtGui.QApplication.translate("MainWindow", "S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_newick.setText(QtGui.QApplication.translate("MainWindow", "Save newick", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBranchSupport.setText(QtGui.QApplication.translate("MainWindow", "Show branch support", None, QtGui.QApplication.UnicodeUTF8))

