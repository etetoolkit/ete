# Form implementation generated from reading ui file 'about.ui'
#
# Created: Tue Jan 10 15:56:58 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!
from .qt import *

class Ui_About:
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(462, 249)
        self.verticalLayoutWidget = QWidget(About)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 441, 208))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.version = QLabel(self.verticalLayoutWidget)
        self.version.setObjectName("version")
        self.verticalLayout.addWidget(self.version)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        About.setWindowTitle(QApplication.translate("About", "Dialog", None))
        self.label.setText(QApplication.translate("About", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/ete icons/ete_logo.png\" /></p>\n"
                                                        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><span style=\" font-size:11pt;\">ETE3: Reconstruction and Analysis Phylogenomics Data</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600;\"><a href=\"http://etetoolkit.org\"><span style=\" text-decoration: underline; color:#0057ae;\">http://etetoolkit.org</span></a></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.version.setText(QApplication.translate("About", "VERSION", None))

from . import ete_resources_rc
