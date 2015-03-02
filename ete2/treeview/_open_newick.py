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

# Form implementation generated from reading ui file 'open_newick.ui'
#
# Created: Tue Jan 10 15:56:56 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_OpenNewick(object):
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

