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


species_ages = {}

_humanv1 = {
# Basal eukariotes
"Ath":10, # Arabidopsis thaliana
"Cre":10,
"Pfa":10,
"Pyo":10,
"Ddi":10,
"Gth":10,
"Lma":10, # leismania
"Pte":10,

# Fungi
"Ago":9,
"Cal":9,
"Cgl":9,
"Cne":9,
"Dha":9,
"Ecu":9,
"Gze":9,
"Kla":9,
"Ncr":9,
"Sce":9, # S.cerevisiae
"Spb":9,
"Yli":9,

# metazoa non chordates
"Aga":8, # Anopheles
"Dme":8, # Drosophila melanogaster
"Ame":8, # Apis meliferae
"Cel":8, # Caenorabditis elegans
"Cbr":8, # Caenorabditis brigssae

# chordates non vertebrates
"Cin":7, # Ciona intestinalis

# vertebrates non tetrapodes
"Dre":6, # Danio rerio
"Tni":6, # Tetraodom
"Fru":6, # Fugu rubripes

# tetrapodes non birds nor mammals
"Xtr":5, # Xenopus

# birds
"Gga":4, # Chicken

# Mammals non primates
"Mdo":3, # Monodelphis domestica
"Mms":3, # Mouse
"Rno":3, # Rat
"Cfa":3, # Dog
"Bta":3, # Cow

# primates non hominids
"Ptr":2, # chimp
"Mmu":2, # Macaca

# hominids
"Hsa":1, # human
}
species_ages["human_phylome"] = _humanv1
