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
#!/usr/bin/python

import unittest
from ..tools.ete_diff import *

class Test_Treediff(unittest.TestCase):
    """ Tests specific methods for trees linked to treediff"""
    def test_treediff_basic(self):
        """ Tests tree-diff basic functionality"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = t1

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(type(difftable),type(list()))
        self.assertEqual(type(difftable[0]),type(list()))
        self.assertEqual(len(difftable[0]),7)
        self.assertEqual(len(difftable),39)
        
    def test_treediff_EUCL_DIST_1(self):
        """ Tests tree-diff EUCL_DIST distance"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((2aaaaaaaaao:1,(2aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(2aaaaaaaaar:1,(2aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((2aaaaaaaaaa:1,2aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(2aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(2aaaaaaaaaj:1,(2aaaaaaaaak:1,2aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,2aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]),39.0)
        
        
    def test_treediff_EUCL_DIST_2(self):
        """ Tests tree-diff EUCL_DIST distance"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]),19.621428668498993)
        
    def test_treediff_EUCL_DIST_3(self):
        """ Tests tree-diff EUCL_DIST diffs"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(sorted([i[4] for i in difftable]),DIFFS)
        
    def test_treediff_RF_DIST_1(self):
        """ Tests tree-diff RF_DIST distance"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((2aaaaaaaaao:1,(2aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(2aaaaaaaaar:1,(2aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((2aaaaaaaaaa:1,2aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(2aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(2aaaaaaaaaj:1,(2aaaaaaaaak:1,2aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,2aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=RF_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]),39.0)
        
    def test_treediff_RF_DIST_2(self):
        """ Tests tree-diff RF_DIST distance"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=RF_DIST, support=False, reduce_matrix=False,extended=None, jobs=1, parallel=None)

        self.assertEqual(sum([i[0] for i in difftable]),10.0)
        
    def test_treediff_extendend_cc(self):
        """ Tests tree-diff Extended distance. Cophenetic Compared"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        
        
        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=RF_DIST, support=False, reduce_matrix=False,extended=cc_distance, jobs=1, parallel=None)

        self.assertEqual(sum([i[1] for i in difftable]),863.9737020175473)
        
    def test_treediff_extendend_be(self):
        """ Tests tree-diff  Extended distance. Branch Extended"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,2aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,2aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((2aaaaaaaaac:1,(2aaaaaaaaad:1,(2aaaaaaaaae:1,(2aaaaaaaaaf:1,(aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((2aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=RF_DIST, support=False, reduce_matrix=False,extended=be_distance, jobs=1, parallel=None)

        self.assertEqual(sum([i[1] for i in difftable]),616.0)
        
    def test_treediff_reports(self):
        """ Tests tree-diff Reports"""
        t1 = Tree('(((aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(aaaaaaaaar:1,(aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(aaaaaaaaaf:1,(aaaaaaaaag:1,aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')

        t2 = Tree('(((2aaaaaaaaao:1,(aaaaaaaaap:1,aaaaaaaaaq:1)1:1)1:1,(2aaaaaaaaar:1,(2aaaaaaaaas:1,aaaaaaaaat:1)1:1)1:1)1:1,((aaaaaaaaaa:1,2aaaaaaaaab:1)1:1,((aaaaaaaaac:1,(aaaaaaaaad:1,(aaaaaaaaae:1,(2aaaaaaaaaf:1,(2aaaaaaaaag:1,2aaaaaaaaah:1)1:1)1:1)1:1)1:1)1:1,((aaaaaaaaai:1,(aaaaaaaaaj:1,(2aaaaaaaaak:1,aaaaaaaaal:1)1:1)1:1)1:1,(2aaaaaaaaam:1,aaaaaaaaan:1)1:1)1:1)1:1)1:1);')
        

        difftable = treediff(t1, t2, attr1 = 'name', attr2 = 'name', dist_fn=EUCL_DIST, support=False, reduce_matrix=False,extended=cc_distance, jobs=1, parallel=None)
        
        rf , rf_max = t1.robinson_foulds(t2)[:2]

        show_difftable_summary(difftable, rf=rf, rf_max=rf_max, extended=cc_distance)
        show_difftable(difftable, extended=cc_distance)
        show_difftable_tab(difftable, extended=cc_distance)
        show_difftable_topo(difftable, 'name', 'name', usecolor=False, extended=cc_distance)

        
        
DIFFS = [set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 set(),
 {'2aaaaaaaaaq', 'aaaaaaaaaq'},
 {'2aaaaaaaaai', 'aaaaaaaaat'},
 {'2aaaaaaaaah', 'aaaaaaaaac'},
 {'2aaaaaaaaaf', 'aaaaaaaaad'},
 {'2aaaaaaaaae', 'aaaaaaaaae'},
 {'2aaaaaaaaad', 'aaaaaaaaaf'},
 {'2aaaaaaaaac', 'aaaaaaaaah'},
 {'2aaaaaaaaat', 'aaaaaaaaai'},
 {'2aaaaaaaaam', 'aaaaaaaaak'},
 {'2aaaaaaaaak', 'aaaaaaaaam'},
 {'2aaaaaaaaaq', 'aaaaaaaaaq'},
 {'2aaaaaaaaat', 'aaaaaaaaat'},
 {'2aaaaaaaaah', 'aaaaaaaaah'},
 {'2aaaaaaaaak', 'aaaaaaaaak'},
 {'2aaaaaaaaam', 'aaaaaaaaam'},
 {'2aaaaaaaaaq', 'aaaaaaaaaq'},
 {'2aaaaaaaaat', 'aaaaaaaaat'},
 {'2aaaaaaaaaf', '2aaaaaaaaah', 'aaaaaaaaaf', 'aaaaaaaaah'},
 {'2aaaaaaaaak', 'aaaaaaaaak'},
 {'2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah'},
 {'2aaaaaaaaai', '2aaaaaaaaak', 'aaaaaaaaai', 'aaaaaaaaak'},
 {'2aaaaaaaaad',
  '2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  'aaaaaaaaad',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah'},
 {'2aaaaaaaaaq', '2aaaaaaaaat', 'aaaaaaaaaq', 'aaaaaaaaat'},
 {'2aaaaaaaaac',
  '2aaaaaaaaad',
  '2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  'aaaaaaaaac',
  'aaaaaaaaad',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah'},
 {'2aaaaaaaaai',
  '2aaaaaaaaak',
  '2aaaaaaaaam',
  'aaaaaaaaai',
  'aaaaaaaaak',
  'aaaaaaaaam'},
 {'2aaaaaaaaac',
  '2aaaaaaaaad',
  '2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  '2aaaaaaaaai',
  '2aaaaaaaaak',
  '2aaaaaaaaam',
  'aaaaaaaaac',
  'aaaaaaaaad',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah',
  'aaaaaaaaai',
  'aaaaaaaaak',
  'aaaaaaaaam'},
 {'2aaaaaaaaac',
  '2aaaaaaaaad',
  '2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  '2aaaaaaaaai',
  '2aaaaaaaaak',
  '2aaaaaaaaam',
  'aaaaaaaaac',
  'aaaaaaaaad',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah',
  'aaaaaaaaai',
  'aaaaaaaaak',
  'aaaaaaaaam'},
 {'2aaaaaaaaac',
  '2aaaaaaaaad',
  '2aaaaaaaaae',
  '2aaaaaaaaaf',
  '2aaaaaaaaah',
  '2aaaaaaaaai',
  '2aaaaaaaaak',
  '2aaaaaaaaam',
  '2aaaaaaaaaq',
  '2aaaaaaaaat',
  'aaaaaaaaac',
  'aaaaaaaaad',
  'aaaaaaaaae',
  'aaaaaaaaaf',
  'aaaaaaaaah',
  'aaaaaaaaai',
  'aaaaaaaaak',
  'aaaaaaaaam',
  'aaaaaaaaaq',
  'aaaaaaaaat'}]      
        

if __name__ == '__main__':
    unittest.main()
