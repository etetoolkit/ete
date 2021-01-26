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

# Form implementation generated from reading ui file 'show_newick.ui'
#
# Created: Mon Sep 14 11:11:49 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!
from __future__ import absolute_import
from .qt import QtCore, QtGui

class Ui_Codeml(object):
    def setupUi(self, Codeml):
        Codeml.setObjectName("Codeml")
        Codeml.resize(594, 397)
        self.model = QtGui.QComboBox(Codeml)
        self.model.setGeometry(QtCore.QRect(120,110, 110, 23))
        self.model.setObjectName("model")
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.model.addItem(QtCore.QString())
        self.label = QtGui.QLabel(Codeml)
        self.label.setGeometry(QtCore.QRect(30, 110, 91, 20))
        self.label.setObjectName("label")
        self.verticalLayoutWidget = QtGui.QWidget(Codeml)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(300, 10, 258, 361))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ctrlBox = QtGui.QTextEdit(self.verticalLayoutWidget)
        self.ctrlBox.setObjectName("ctrlBox")
        self.verticalLayout.addWidget(self.ctrlBox)
        self.pushButton = QtGui.QPushButton(Codeml)
        self.label_2 = QtGui.QLabel(Codeml)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 160, 20))
        self.label_2.setObjectName("label_2")
        self.workdir = QtGui.QLineEdit(Codeml)
        self.workdir.setGeometry(QtCore.QRect(10, 40, 250, 25))
        self.workdir.setObjectName("workdir")
        self.label_3 = QtGui.QLabel(Codeml)
        self.label_3.setGeometry(QtCore.QRect(10, 60, 160, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(Codeml)
        self.label_4.setGeometry(QtCore.QRect(35, 273, 260, 20))
        self.label_4.setObjectName("label_4")
        self.useprerun = QtGui.QCheckBox(Codeml)
        self.useprerun.setGeometry(QtCore.QRect(10, 270, 221, 24))
        self.useprerun.setObjectName("useprerun")
        self.label_5 = QtGui.QLabel(Codeml)
        self.label_5.setGeometry(QtCore.QRect(35, 293, 260, 20))
        self.label_5.setObjectName("label_5")
        self.display = QtGui.QCheckBox(Codeml)
        self.display.setGeometry(QtCore.QRect(10, 290, 221, 24))
        self.display.setObjectName("display")
        self.codemlpath = QtGui.QLineEdit(Codeml)
        self.codemlpath.setGeometry(QtCore.QRect(10, 80, 250, 25))
        self.codemlpath.setObjectName("codemlpath")
        self.pushButton.setGeometry(QtCore.QRect(240, 350, 51, 29))
        self.pushButton.setObjectName("pushButton")
        self.retranslateUi(Codeml)
        QtCore.QMetaObject.connectSlotsByName(Codeml)
        self.model.activate.connect(Codeml.update_model)
        self.pushButton.released.connect(Codeml.run)

        #QtCore.QObject.connect(self.model, QtCore.SIGNAL("activated(QString)"), Codeml.update_model)
        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("released()"), Codeml.run)

    def retranslateUi(self, Codeml):
        Codeml.setWindowTitle(QtGui.QApplication.translate("Codeml", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(0, QtGui.QApplication.translate("Model", "M0"            , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(1, QtGui.QApplication.translate("Model", "M1"            , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(2, QtGui.QApplication.translate("Model", "M2"            , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(3, QtGui.QApplication.translate("Model", "M7"            , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(4, QtGui.QApplication.translate("Model", "M8"            , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(5, QtGui.QApplication.translate("Model", "free-branch"   , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(6, QtGui.QApplication.translate("Model", "branch-site.A" , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(7, QtGui.QApplication.translate("Model", "branch-site.A1", None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(8, QtGui.QApplication.translate("Model", "branch-free"   , None, QtGui.QApplication.UnicodeUTF8))
        self.model.setItemText(9, QtGui.QApplication.translate("Model", "branch-neut"   , None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Model", "Model to test: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Codeml", "Codeml working directory:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Codeml", "Path to Codeml executable: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Codeml", "Search for already runned data.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Codeml", "Display resulting info, as histogram (only for sites models.)", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Model", "Run", None, QtGui.QApplication.UnicodeUTF8))
