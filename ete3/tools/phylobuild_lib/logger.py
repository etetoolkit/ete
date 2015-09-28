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
from __future__ import absolute_import
import logging

__LOGINDENT__ = 0

class IndentedFormatter(logging.Formatter):
    def __init__( self, fmt=None, datefmt=None ):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, rec ):
        rec.indent = ' ' * __LOGINDENT__
        out = logging.Formatter.format(self, rec)
        return out

def set_logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ = x

def logindent(x):
    global __LOGINDENT__
    __LOGINDENT__ += x

def get_logindent():
    return __LOGINDENT__

def get_main_log(handler, level=20):
    # Prepares main log
    log = logging.getLogger("main")
    log.setLevel(level)
    lformat = IndentedFormatter("%(levelname) 4s@@1: - %(indent)s %(message)s")
    logging.addLevelName(10, "@@3,12:DEBUG")
    logging.addLevelName(20, "@@1,3:INFO")
    logging.addLevelName(22, "@@1,3:INFO")
    logging.addLevelName(24, "@@1,3:INFO")
    logging.addLevelName(26, "@@1,3:INFO")
    logging.addLevelName(28, "@@1,3:INFO")
    logging.addLevelName(30, "@@2,11:WRNG")
    logging.addLevelName(40, "@@2,10:ERR ")
    logging.addLevelName(50, "@@2,10:DISASTER")
    log_handler = logging.StreamHandler(handler)
    log_handler.setFormatter(lformat)
    log.addHandler(log_handler)
    return log

