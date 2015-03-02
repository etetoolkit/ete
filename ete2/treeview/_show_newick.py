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
# Created: Tue Jan 10 15:56:56 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Newick(object):
    def setupUi(self, Newick):
        Newick.setObjectName("Newick")
        Newick.resize(594, 397)
        self.nwFormat = QtGui.QComboBox(Newick)
        self.nwFormat.setGeometry(QtCore.QRect(200, 20, 51, 23))
        self.nwFormat.setObjectName("nwFormat")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.nwFormat.addItem("")
        self.label = QtGui.QLabel(Newick)
        self.label.setGeometry(QtCore.QRect(100, 20, 91, 20))
        self.label.setObjectName("label")
        self.verticalLayoutWidget = QtGui.QWidget(Newick)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(300, 10, 258, 361))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.newickBox = QtGui.QTextEdit(self.verticalLayoutWidget)
        self.newickBox.setObjectName("newickBox")
        self.verticalLayout.addWidget(self.newickBox)
        self.attrName = QtGui.QLineEdit(Newick)
        self.attrName.setGeometry(QtCore.QRect(20, 80, 113, 25))
        self.attrName.setObjectName("attrName")
        self.pushButton = QtGui.QPushButton(Newick)
        self.pushButton.setGeometry(QtCore.QRect(140, 80, 51, 29))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtGui.QPushButton(Newick)
        self.pushButton_2.setGeometry(QtCore.QRect(200, 80, 51, 29))
        self.pushButton_2.setObjectName("pushButton_2")
        self.features_list = QtGui.QListWidget(Newick)
        self.features_list.setGeometry(QtCore.QRect(20, 120, 231, 251))
        self.features_list.setObjectName("features_list")
        self.label_3 = QtGui.QLabel(Newick)
        self.label_3.setGeometry(QtCore.QRect(60, 60, 191, 20))
        self.label_3.setObjectName("label_3")
        self.useAllFeatures = QtGui.QCheckBox(Newick)
        self.useAllFeatures.setGeometry(QtCore.QRect(20, 370, 221, 24))
        self.useAllFeatures.setObjectName("useAllFeatures")

        self.retranslateUi(Newick)
        QtCore.QObject.connect(self.nwFormat, QtCore.SIGNAL("activated(QString)"), Newick.update_newick)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("released()"), Newick.add_feature)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("released()"), Newick.del_feature)
        QtCore.QObject.connect(self.useAllFeatures, QtCore.SIGNAL("released()"), Newick.set_custom_features)
        QtCore.QMetaObject.connectSlotsByName(Newick)

    def retranslateUi(self, Newick):
        Newick.setWindowTitle(QtGui.QApplication.translate("Newick", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(0, QtGui.QApplication.translate("Newick", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(1, QtGui.QApplication.translate("Newick", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(2, QtGui.QApplication.translate("Newick", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(3, QtGui.QApplication.translate("Newick", "3", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(4, QtGui.QApplication.translate("Newick", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(5, QtGui.QApplication.translate("Newick", "5", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(6, QtGui.QApplication.translate("Newick", "6", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(7, QtGui.QApplication.translate("Newick", "7", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(8, QtGui.QApplication.translate("Newick", "8", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(9, QtGui.QApplication.translate("Newick", "9", None, QtGui.QApplication.UnicodeUTF8))
        self.nwFormat.setItemText(10, QtGui.QApplication.translate("Newick", "100", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Newick", "Newick format", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Newick", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Newick", "Del", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Newick", "Node\'s attribute (NHX format)", None, QtGui.QApplication.UnicodeUTF8))
        self.useAllFeatures.setText(QtGui.QApplication.translate("Newick", "Include all attributes in nodes", None, QtGui.QApplication.UnicodeUTF8))

