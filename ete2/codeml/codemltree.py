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
"""
This module defines the PhyloNode dataytype to manage phylogenetic
tree. It inheritates the coretype TreeNode and add some speciall
features to the the node instances.
"""

import sys

from ete_test import PhyloNode, PhyloTree
from ete_test.codeml.codemlparser import parse_paml, get_sites

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')
from control import label_tree

__all__ = ["CodemlNode", "CodemlTree"]

def _parse_species(name):
    '''
    just to return specie name from fasta description
    '''
    return name[:3]

class CodemlNode(PhyloNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def __init__(self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species):
        '''
        freebranch: path to find codeml output of freebranch model.
        '''
        # _update names?
        self._name = "NoName"
        self._species = "Unknown"
        self._speciesFunction = None
        # Caution! native __init__ has to be called after setting
        # _speciesFunction to None!!
        PhyloNode.__init__(self, newick=newick)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloNode constructor during parsing
        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            self.set_species_naming_function(sp_naming_function)
            label_tree(self)

    def link_to_evol_model(self, path, model):
        '''
        link CodemlTree to evolutionary model
          * free-branch model ('fb') will append evol values to tree
          * Site models (M0, M1, M2, M7, M8) will give evol values by site
            and likelihood
        '''
        dic = parse_paml(path, model)
        if model == 'fb':
            self._getfreebranch(dic)
        if model.startswith('M'):
            get_sites(dic['rst'])

    def _getfreebranch(self, dic):
        '''
        to convert tree strings of paml into tree strings readable
        by ETE2_codeml.
        returns same dic with CodemlTree.
        #TODO: be abble to undestand how codeml put ids to tree nodes
        '''
        for evol in ['bL', 'dN', 'dS', 'w']:
            if not dic.has_key(evol):
                print >> sys.stderr, \
                      "Warning: this file do not cotain info about " \
                      + evol + " parameter"
                continue
            if not dic[evol].startswith('('):
                print >> sys.stderr, \
                      "Warning: problem with tree string for "\
                      + evol +" parameter"
                continue
            tdic = dic[evol]
            if evol == 'bL':
                tree = PhyloTree(tdic)
                label_tree(tree)
                if not tree.write(format=9) == self.write(format=9):
                    print >> sys.stderr, \
                          "ERROR: CodemlTree and tree used in "+\
                          "codeml do not match"
                    print tree.write(), self.write()
                    break
                self.get_tree_root().dist = 0
                evol = 'dist'
            tree = PhyloTree(tdic)
            label_tree(tree)
            for node in self.iter_descendants():
                for node2 in tree.iter_descendants():
                    if node2.idname == node.idname:
                        node.add_feature(evol, node2.dist)


# cosmetic alias
CodemlTree = CodemlNode

#git fetch repo-principal"
#git mergetool --tool=meld
#(puedes usar otros programas que no sean meld, pero este mola)
#basicamente lo que tienes que hacer es:
#cp -r myCodemlRepo/ myUpdatedCodemlRepo/
#cd myUpdatedCodemlRepo/


## Don't mess up your current work
#cp -r myCodemlRepo/ myUpdatedCodemlRepo/ 
## Get last master version
#git clone git://gitorious.org/environment-for-tree-exploration/ete.git \
#updatedMainBranch
## Enters the conflic zone
#cd myUpdatedCodemlRepo/
## fetch and merge at the same time
#git pull ../updatedMainBranch/ master
## Solve conflicts 
#git mergetool --tool=meld

