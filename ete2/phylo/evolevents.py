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
    event(node) ocurred in a phylogenetic tree. """
    def __init__(self):
        self.etype         = None   # 'S=speciation D=duplication'
        self.seed          = None   # Seed ID used to start the phylogenetic pipeline
        self.outgroup_spcs = None   # outgroup
        self.e_newick      = None   # 
        self.dup_score     = None   # 
        self.root_age      = None   # estimated time for the outgroup node
        self.inparalogs    = None   
        self.outparalogs   = None 
        self.orthologs     = None 
        self.famSize       = None
        self.allseqs       = []     # all ids grouped by this event
        self.in_seqs       = []
        self.out_seqs      = []
	self.branch_supports  = []

