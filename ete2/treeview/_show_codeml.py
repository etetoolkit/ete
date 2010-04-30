# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'show_newick.ui'
#
# Created: Mon Sep 14 11:11:49 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    import QtCore, QtGui


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
        self.newickBox = QtGui.QTextEdit(self.verticalLayoutWidget)
        self.newickBox.setObjectName("newickBox")
        self.verticalLayout.addWidget(self.newickBox)
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
        self.codemlpath = QtGui.QLineEdit(Codeml)
        self.codemlpath.setGeometry(QtCore.QRect(10, 80, 250, 25))
        self.codemlpath.setObjectName("codemlpath")
        self.pushButton.setGeometry(QtCore.QRect(240, 350, 51, 29))
        self.pushButton.setObjectName("pushButton")
        self.retranslateUi(Codeml)
        QtCore.QMetaObject.connectSlotsByName(Codeml)
        QtCore.QObject.connect(self.model, QtCore.SIGNAL("activated(QString)"), Codeml.update_model)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("released()"), Codeml.run)

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
        self.pushButton.setText(QtGui.QApplication.translate("Model", "Run", None, QtGui.QApplication.UnicodeUTF8))
