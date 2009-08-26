# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created: Wed Aug 26 15:24:03 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(466, 160)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-20, 120, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.leves_only = QtGui.QCheckBox(Dialog)
        self.leves_only.setGeometry(QtCore.QRect(30, 80, 181, 24))
        self.leves_only.setObjectName("leves_only")
        self.attrType = QtGui.QComboBox(Dialog)
        self.attrType.setGeometry(QtCore.QRect(310, 40, 141, 23))
        self.attrType.setObjectName("attrType")
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 181, 20))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(120, 40, 61, 20))
        self.label_2.setObjectName("label_2")
        self.attrName = QtGui.QLineEdit(Dialog)
        self.attrName.setGeometry(QtCore.QRect(190, 10, 113, 25))
        self.attrName.setObjectName("attrName")
        self.attrValue = QtGui.QLineEdit(Dialog)
        self.attrValue.setGeometry(QtCore.QRect(190, 40, 113, 25))
        self.attrValue.setObjectName("attrValue")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(120, 40, 61, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(120, 40, 61, 20))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.leves_only.setText(QtGui.QApplication.translate("Dialog", "Search only for leaf nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(0, QtGui.QApplication.translate("Dialog", "Exact match", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(1, QtGui.QApplication.translate("Dialog", "Flexible match", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(2, QtGui.QApplication.translate("Dialog", "Regular Expression", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Search nodes with attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "equals to", None, QtGui.QApplication.UnicodeUTF8))
        self.attrName.setText(QtGui.QApplication.translate("Dialog", "name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "equals to", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "equals to", None, QtGui.QApplication.UnicodeUTF8))

