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
from ..evol.model import AVAIL, PARAMS
from argparse import RawTextHelpFormatter

DESC = "Interactively mark tree for CodeML tests... "

def marking_layout(node):
    '''
    layout for interactively marking CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    color_cycle = [u'#E24A33', u'#348ABD', u'#988ED5',
                   u'#777777', u'#FBC15E', u'#8EBA42',
                   u'#FFB5B8']
    node.img_style["size"] = 15
    if hasattr(node, 'mark') and node.mark != '':
        node.img_style["fgcolor"] = color_cycle[(int(node.mark.replace('#', '')) - 1) % 7]
    else:
        node.img_style["fgcolor"] = '#000000'

        
def populate_args(mark_args_p):
    mark_args = mark_args_p.add_argument_group('ETE-MARK OPTIONS')

def run(args):
    from .. import EvolTree

    for nw in args.src_tree_iterator:
        t = EvolTree(nw)
        t.show(layout=marking_layout)
        print(t.write())
