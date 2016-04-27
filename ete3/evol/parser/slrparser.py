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
"""
06 Feb 2011

parser for slr outfile
"""
from __future__ import absolute_import

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from re import match

def parse_slr (slrout):
    SLR = {'pv':[],'w':[],'se':[], 'class':[],'note':[]}
    w   = ''
    apv = ''
    seP = ''
    seN = ''
    res = ''
    note= ''
    for line in open (slrout):
        if line.startswith('#'):
            w   = line.strip().split().index('Omega')-1
            apv = line.strip().split().index('Adj.Pval')-1
            res = line.strip().split().index('Result')-1
            note= line.strip().split().index('Note')-1
            try:
                seP = line.strip().split().index('upper')-1
                seN = line.strip().split().index('lower')-1
            except:
                continue
            continue
        SLR['pv' ].append(1-float (line.split()[apv]))
        SLR['w'  ].append(line.split()[w])
        corr = 0
        try:
            if not match('[-+]',line.split()[res]) is None:
                SLR['class'  ].append (5 - line.split()[res].count ('-') + line.split()[res].count ('+'))
            else:
                SLR['class'  ].append(5)
                corr = 1
        except IndexError:
            SLR['class'  ].append(5)
        try:
            SLR['note'  ].append(line.split()[note-corr])
        except IndexError:
            SLR['note'  ].append('')
        if not seN == '':
            SLR['se'].append ([float (SLR['w'][-1]) - float (line.split()[seN]),
                               float (line.split()[seP]) - float (SLR['w'][-1])])
    return {'sites': {'SLR': SLR},
            'n_classes': {'SLR': 8}}
