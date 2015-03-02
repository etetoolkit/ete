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

# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created: Tue Jan 10 15:56:57 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(613, 103)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(430, 60, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.leaves_only = QtGui.QCheckBox(Dialog)
        self.leaves_only.setGeometry(QtCore.QRect(10, 40, 211, 24))
        self.leaves_only.setChecked(True)
        self.leaves_only.setObjectName("leaves_only")
        self.attrType = QtGui.QComboBox(Dialog)
        self.attrType.setGeometry(QtCore.QRect(330, 10, 101, 23))
        self.attrType.setObjectName("attrType")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 141, 20))
        self.label.setObjectName("label")
        self.attrName = QtGui.QLineEdit(Dialog)
        self.attrName.setGeometry(QtCore.QRect(150, 8, 113, 25))
        self.attrName.setObjectName("attrName")
        self.attrValue = QtGui.QLineEdit(Dialog)
        self.attrValue.setGeometry(QtCore.QRect(440, 10, 113, 25))
        self.attrValue.setText("")
        self.attrValue.setObjectName("attrValue")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(270, 10, 61, 20))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.attrName, self.attrType)
        Dialog.setTabOrder(self.attrType, self.attrValue)
        Dialog.setTabOrder(self.attrValue, self.leaves_only)
        Dialog.setTabOrder(self.leaves_only, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.leaves_only.setText(QtGui.QApplication.translate("Dialog", "Search only for leaf nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(0, QtGui.QApplication.translate("Dialog", "contains", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(1, QtGui.QApplication.translate("Dialog", "is", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(2, QtGui.QApplication.translate("Dialog", "== ", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(3, QtGui.QApplication.translate("Dialog", ">=", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(4, QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(5, QtGui.QApplication.translate("Dialog", "<=", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(6, QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(7, QtGui.QApplication.translate("Dialog", "matches this regular expression", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Search nodes whose                                ", None, QtGui.QApplication.UnicodeUTF8))
        self.attrName.setText(QtGui.QApplication.translate("Dialog", "name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "attribute", None, QtGui.QApplication.UnicodeUTF8))

