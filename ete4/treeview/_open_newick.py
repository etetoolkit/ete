# Form implementation generated from reading ui file 'open_newick.ui'
#
# Created: Tue Jan 10 15:56:56 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!
from .qt import QtCore, QtGui

class Ui_OpenNewick:
    def setupUi(self, OpenNewick):
        OpenNewick.setObjectName("OpenNewick")
        OpenNewick.resize(569, 353)
        self.comboBox = QtGui.QComboBox(OpenNewick)
        self.comboBox.setGeometry(QtCore.QRect(460, 300, 81, 23))
        self.comboBox.setObjectName("comboBox")
        self.widget = QtGui.QWidget(OpenNewick)
        self.widget.setGeometry(QtCore.QRect(30, 10, 371, 321))
        self.widget.setObjectName("widget")

        self.retranslateUi(OpenNewick)
        QtCore.QMetaObject.connectSlotsByName(OpenNewick)

    def retranslateUi(self, OpenNewick):
        OpenNewick.setWindowTitle(QtGui.QApplication.translate("OpenNewick", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
