from __future__ import absolute_import
from __future__ import print_function
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
import textwrap as twrap 

__all__ = ["CITATIONS"]

class Citator(object):
    def __init__(self):
        self.citations = set()
        
    def add(self, ref):
        self.citations.add(ref)
        
    def show(self):
        wrapper = twrap.TextWrapper(width=75, initial_indent="   ",
                              subsequent_indent="      ",
                              replace_whitespace=False)
        citations = sorted(self.citations)
        print("   ========================================================================")
        print("         The following published software and/or methods were used.        ")
        print("               *** Please, do not forget to cite them! ***                 ")
        print("   ========================================================================")
        for ref in citations:
            print(wrapper.fill(ref.replace("\n", " ").strip()))
         
