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
from sys import stdout
from . import _phyloxml as main
from ._phyloxml import *
from ._phyloxml_tree import PhyloxmlTree

_phyloxml.Phylogeny.subclass = PhyloxmlTree

class Phyloxml(_phyloxml.Phyloxml):
    def __repr__(self):
        return "PhyloXML project <%s>" %hex(hash(self))

    def __init__(self, *args, **kargs):
        _phyloxml.Phyloxml.__init__(self, *args, **kargs)

    def build_from_file(self, fname):
        doc = _phyloxml.parsexml_(fname)
        rootNode = doc.getroot()
        rootTag, rootClass = _phyloxml.get_root_tag(rootNode)
        if rootClass is None:
            rootTag = 'phyloxml'
            rootClass = self.__class__
        self.build(rootNode)

    def export(self, outfile=stdout, level=0):
        namespace = 'xmlns:phy="http://www.phyloxml.org/1.10/phyloxml.xsd"'
        return super(Phyloxml, self).export(outfile=outfile, level=level, namespacedef_=namespace)


__all__ = _phyloxml.__all__ + ["Phyloxml", "PhyloxmlTree"]
