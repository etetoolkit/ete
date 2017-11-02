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
# Created: Tue Jan 10 15:56:56 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!
from __future__ import absolute_import
from .qt import *

class Ui_Newick(object):
    def setupUi(self, Newick):
        Newick.setObjectName("Newick")
        Newick.resize(594, 397)
        self.nwFormat = QComboBox(Newick)
        self.nwFormat.setGeometry(QRect(200, 20, 51, 23))
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
        self.label = QLabel(Newick)
        self.label.setGeometry(QRect(100, 20, 91, 20))
        self.label.setObjectName("label")
        self.verticalLayoutWidget = QWidget(Newick)
        self.verticalLayoutWidget.setGeometry(QRect(300, 10, 258, 361))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.newickBox = QTextEdit(self.verticalLayoutWidget)
        self.newickBox.setObjectName("newickBox")
        self.verticalLayout.addWidget(self.newickBox)
        self.attrName = QLineEdit(Newick)
        self.attrName.setGeometry(QRect(20, 80, 113, 25))
        self.attrName.setObjectName("attrName")
        self.pushButton = QPushButton(Newick)
        self.pushButton.setGeometry(QRect(140, 80, 51, 29))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QPushButton(Newick)
        self.pushButton_2.setGeometry(QRect(200, 80, 51, 29))
        self.pushButton_2.setObjectName("pushButton_2")
        self.features_list = QListWidget(Newick)
        self.features_list.setGeometry(QRect(20, 120, 231, 251))
        self.features_list.setObjectName("features_list")
        self.label_3 = QLabel(Newick)
        self.label_3.setGeometry(QRect(60, 60, 191, 20))
        self.label_3.setObjectName("label_3")
        self.useAllFeatures = QCheckBox(Newick)
        self.useAllFeatures.setGeometry(QRect(20, 370, 221, 24))
        self.useAllFeatures.setObjectName("useAllFeatures")

        self.retranslateUi(Newick)
        self.nwFormat.activated.connect(Newick.update_newick)
        self.pushButton.released.connect(Newick.add_feature)
        self.pushButton_2.released.connect(Newick.del_feature)
        self.useAllFeatures.released.connect(Newick.set_custom_features)
        
        #QObject.connect(self.nwFormat, SIGNAL("activated(QString)"), Newick.update_newick)
        #QObject.connect(self.pushButton, SIGNAL("released()"), Newick.add_feature)
        #QObject.connect(self.pushButton_2, SIGNAL("released()"), Newick.del_feature)
        #QObject.connect(self.useAllFeatures, SIGNAL("released()"), Newick.set_custom_features)
        #QMetaObject.connectSlotsByName(Newick)

    def retranslateUi(self, Newick):
        Newick.setWindowTitle(QApplication.translate("Newick", "Dialog", None))
        self.nwFormat.setItemText(0, QApplication.translate("Newick", "0", None))
        self.nwFormat.setItemText(1, QApplication.translate("Newick", "1", None))
        self.nwFormat.setItemText(2, QApplication.translate("Newick", "2", None))
        self.nwFormat.setItemText(3, QApplication.translate("Newick", "3", None))
        self.nwFormat.setItemText(4, QApplication.translate("Newick", "4", None))
        self.nwFormat.setItemText(5, QApplication.translate("Newick", "5", None))
        self.nwFormat.setItemText(6, QApplication.translate("Newick", "6", None))
        self.nwFormat.setItemText(7, QApplication.translate("Newick", "7", None))
        self.nwFormat.setItemText(8, QApplication.translate("Newick", "8", None))
        self.nwFormat.setItemText(9, QApplication.translate("Newick", "9", None))
        self.nwFormat.setItemText(10, QApplication.translate("Newick", "100", None))
        self.label.setText(QApplication.translate("Newick", "Newick format", None))
        self.pushButton.setText(QApplication.translate("Newick", "Add", None))
        self.pushButton_2.setText(QApplication.translate("Newick", "Del", None))
        self.label_3.setText(QApplication.translate("Newick", "Node\'s attribute (NHX format)", None))
        self.useAllFeatures.setText(QApplication.translate("Newick", "Include all attributes in nodes", None))

