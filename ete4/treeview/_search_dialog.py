# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created: Tue Jan 10 15:56:57 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!
from .qt import *

class Ui_Dialog:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog.resize(613, 103)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QRect(430, 60, 171, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.leaves_only = QCheckBox(Dialog)
        self.leaves_only.setGeometry(QRect(10, 40, 211, 24))
        self.leaves_only.setChecked(True)
        self.leaves_only.setObjectName("leaves_only")
        self.attrType = QComboBox(Dialog)
        self.attrType.setGeometry(QRect(330, 10, 101, 23))
        self.attrType.setObjectName("attrType")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.attrType.addItem("")
        self.label = QLabel(Dialog)
        self.label.setGeometry(QRect(10, 10, 141, 20))
        self.label.setObjectName("label")
        self.attrName = QLineEdit(Dialog)
        self.attrName.setGeometry(QRect(150, 8, 113, 25))
        self.attrName.setObjectName("attrName")
        self.attrValue = QLineEdit(Dialog)
        self.attrValue.setGeometry(QRect(440, 10, 113, 25))
        self.attrValue.setText("")
        self.attrValue.setObjectName("attrValue")
        self.label_2 = QLabel(Dialog)
        self.label_2.setGeometry(QRect(270, 10, 61, 20))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        Dialog.setTabOrder(self.attrName, self.attrType)
        Dialog.setTabOrder(self.attrType, self.attrValue)
        Dialog.setTabOrder(self.attrValue, self.leaves_only)
        Dialog.setTabOrder(self.leaves_only, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QApplication.translate("Dialog", "Dialog", None))
        self.leaves_only.setText(QApplication.translate("Dialog", "Search only for leaf nodes", None))
        self.attrType.setItemText(0, QApplication.translate("Dialog", "contains", None))
        self.attrType.setItemText(1, QApplication.translate("Dialog", "is", None))
        self.attrType.setItemText(2, QApplication.translate("Dialog", "== ", None))
        self.attrType.setItemText(3, QApplication.translate("Dialog", ">=", None))
        self.attrType.setItemText(4, QApplication.translate("Dialog", ">", None))
        self.attrType.setItemText(5, QApplication.translate("Dialog", "<=", None))
        self.attrType.setItemText(6, QApplication.translate("Dialog", "<", None))
        self.attrType.setItemText(7, QApplication.translate("Dialog", "matches this regular expression", None))
        self.label.setText(QApplication.translate("Dialog", "Search nodes whose                                ", None))
        self.attrName.setText(QApplication.translate("Dialog", "name", None))
        self.label_2.setText(QApplication.translate("Dialog", "attribute", None))
