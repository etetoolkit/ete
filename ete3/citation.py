# -*- coding: utf-8 -*-

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
from __future__ import print_function
import re
import textwrap as twrap

__all__ = ["Citator"]


class Citator(object):
    REFERENCES = {
        'ETE': u"""Huerta-Cepas J, Serra F, Bork P. ETE 3: Reconstruction, analysis and
        visualization of phylogenomic data. Mol Biol Evol (2016) doi:
        10.1093/molbev/msw046""",
        
        'phyml': u"""Guindon S, Dufayard JF, Lefort V, Anisimova M, Hordijk W, Gascuel O.
        New algorithms and methods to estimate maximum-likelihood phylogenies:
        assessing the performance of PhyML 3.0. Syst Biol. 2010
        May;59(3):307-21.""",
        
        'fasttree': u"""Price MN, Dehal PS, Arkin AP. FastTree 2 -
        approximately maximum-likelihood trees for large alignments. PLoS
        One. 2010 Mar 10;5(3):e9490.""",
        
        'raxml': u"""Stamatakis A. RAxML version 8: a tool for phylogenetic analysis and
        post-analysis of large phylogenies Bioinformatics (2014) 30 (9): 1312-1313.""",
        'mafft': u"""Katoh K, Kuma K, Toh H, Miyata T. MAFFT version 5:
        improvement in accuracy of multiple sequence alignment.  Nucleic Acids
        Res. 2005 Jan 20;33(2):511-8.""",
        
        'trimal': u"""Capella-Gutiérrez S, Silla-Martínez JM, Gabaldón T.
        trimAl: a tool for automated alignment trimming in large-scale
        phylogenetic analyses.  Bioinformatics. 2009 Aug 1;25(15):1972-3.""",
        
        'muscle': u"""Edgar RC. MUSCLE: multiple sequence alignment with
        high accuracy and high throughput.", Nucleic Acids Res. 2004 Mar
        19;32(5):1792-7.""",
        
        'clustalo': u""" Sievers F, Wilm A, Dineen D, Gibson TJ, Karplus
        K, Li W, Lopez R, McWilliam H, Remmert M, Söding J, Thompson JD,
        Higgins DG.  Fast, scalable generation of high-quality protein
        multiple sequence alignments using Clustal Omega.  Mol Syst Biol. 2011
        Oct 11;7:539. doi: 10.1038/msb.2011.75.""",
        
        'dialigntx': u"""Subramanian AR, Kaufmann M, Morgenstern B.
        DIALIGN-TX: greedy and progressive approaches for segment-based
        multiple sequence alignment. Algorithms Mol Biol. 2008 May 27;3:6.""",
        
        'mcoffee': u"""Wallace IM, O'Sullivan O, Higgins DG, Notredame C.
        M-Coffee: combining multiple sequence alignment methods with T-Coffee.
        Nucleic Acids Res. 2006 Mar 23;34(6):1692-9. """,
        
        'tcoffee': u"""Magis C, Taly JF, Bussotti G, Chang JM, Di Tommaso P, Erb I,
        Espinosa-Carrasco J, Notredame C. T-Coffee: Tree-based consistency objective
        function for alignment evaluation. Methods Mol Biol. 2014;1079:117-29.""",

        'jmodeltest': u"""Darriba D, Taboada GL, Doallo R, Posada
        D. jModelTest 2: more models, new heuristics and parallel computing.Nat
        Methods. 2012 Jul 30;9(8):772.""",

        'treeko': u"""Marcet-Houben M, Gabaldón T. TreeKO: a duplication-aware algorithm for the
        comparison of phylogenetic trees. Nucleic Acids Res. 2011 May;39(10):e66. doi:
        10.1093/nar/gkr087.""",

        'iqtree': u"""LT Nguyen, H.A. Schmidt, A. von Haeseler, and BQ Minh (2015) IQ-TREE: A
        fast and effective stochastic algorithm for estimating maximum likelihood
        phylogenies. Mol. Biol. Evol., 32, 268-274.""",

        'pll': u"""T Flouri, F Izquierdo-Carrasco, D. Darriba, AJ Aberer, LT Nguyen,
        B.Q. Minh, A. von Haeseler, and A. Stamatakis (2015) The phylogenetic likelihood
        library. Syst. Biol., 64:356-362.""",

        'ufboot': u"""BQ Minh, MAT Nguyen, and A. von Haeseler (2013) Ultrafast approximation
        for phylogenetic bootstrap. Mol. Biol. Evol., 30:1188-1195.""", 
        
        
        }
    
    def __init__(self):
        self.citations = set()

    def add(self, ref):
        self.citations.add(self.REFERENCES[ref])

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
            print(wrapper.fill(re.sub('[\n \t]+', ' ', ref).strip()))

