# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
__all__ = ["EvolEvent"]

class EvolEvent:
    """ Basic evolutionary event. It stores all the information about an
    event(node) ocurred in a phylogenetic tree.

    :attr:`etype` : ``D`` (Duplication), ``S`` (Speciation), ``L`` (gene loss), 

    :attr:`in_seqs` : the list of sequences in one side of the event. 

    :attr:`out_seqs` : the list of sequences in the other side of the event

    :attr:`node` : link to the event node in the tree

    """

    def __init__(self):
        self.etype         = None   # 'S=speciation D=duplication'
        self.in_seqs       = []
        self.out_seqs      = []
        self.dup_score     = None
        self.sos           = None

        # Not documented
        self.inparalogs    = None
        self.outparalogs   = None
        self.outgroup_spcs = None   # outgroup
        self.e_newick      = None   #
        self.root_age      = None   # estimated time for the outgroup node
        self.orthologs     = None
        self.famSize       = None
        self.seed          = None   # Seed ID used to start the phylogenetic pipeline
        self.branch_supports  = []
            


        
