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
import os
import re

from ete_dev import PhyloNode, SeqGroup
from codemlparser import *

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')
from control import label_tree

__all__ = ["CodemlNode", "CodemlTree"]

def _parse_species(name):
    return name[:3]

class CodemlNode(PhyloNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def __init__(self,newick=None,alignment=None,alg_format="fasta",\
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

    def test_models(lnL1,np1,lnL2,np2):
        return chisqprob(2*(float(lnL2)-float(lnL1)),\
                         df=(int (np2)-int(np1)))


    def linktoevolmodel(self,path,model):
        dic = parsePaml(path, model)
        if model == 'fb':
            self._getfreebranch(dic)

    def _getsites(self,path):
        '''
        for models M0, M1, M2, M7, M8
        '''
        K = 0
        EB=False
        EBend=False
        PS=False
        lnL = ''
        for line in open(path,'r'):
            line = line.strip()
            if line.startswith('lnL = '):
                lnL = line.split()[-1]
                if not (EB == False or EB == True):
                    EB['lnL.'+m]=lnL
            if line.startswith('dN/dS for site classes'):
                K = re.sub('.*K=','',line)
                K = int (re.sub('\)','',K))
                if K < 4: m = 'M'+str(K-1)
                else:     m = 'M'+str(K-3)
            if K % 2 == 0:
                if line.startswith('Naive Empirical Bayes'): EB = True
                elif(EB==False):continue
            else:
                if line.startswith('Bayes Empirical Bayes'): EB = True
                elif(EB==False):continue
            if re.match('^ *[0-9]* [A-Z*] *',line)==None and \
                   EBend==False:
                continue
            if re.match('^ *[0-9]* [A-Z*] *',line)==None: PS = True
            EBend=True
            if EB==True:
                EB={'aa.'+m:[], 'w.'+m:[], 'class.'+m:[],
                    'pv.'+m:[],'se.'+m:[], 'lnL.'+m:lnL}
            if PS == False:
                EB['aa.'+m].append(line.split()[1])
                EB['w.' +m].append(re.sub('\+.*','',line).split()[-1])
                if m=='M1'or m=='M7': EB['se.'+m].append('')
                else: EB['se.'+m].append(line.split()[-1])
                classes = map(float,re.sub('\(.*','',line).split()[2:])
                EB['class.'+m].append(\
                    '('+\
                    re.sub('\).*','',re.sub('.*\( *','',line.strip()))\
                    +'/'+str (len (classes))+')')
                EB['pv.'+m].append(str (\
                    max (classes)))
        return EB


    def _getfreebranch(self,dic):
        '''
        to convert tree strings of paml into tree strings readable
        by ETE2_codeml.
        returns same dic with CodemlTree.
        #TODO: be abble to undestand how codeml put ids to tree nodes
        '''
        for k in ['bL','dN','dS','w']:
            if not dic.has_key(k):
                print >> sys.stderr, \
                      "Warning: this file do not cotain info about "\
                      +k+" parameter"
                continue
            if not dic[k].startswith('('):
                print >> sys.stderr, \
                      "Warning: problem with tree string for "\
                      +k+" parameter"
                continue
            t = dic[k]
            if k =='bL':
                T = Tree(t)
                label_tree(T)
                if not T.write(format=9)==self.write(format=9):
                    print >> sys.stderr, \
                          "ERROR: CodemlTree and tree used in "+\
                          "codeml do not match"
                    print T.write(), self.write()
                    break
                self.get_tree_root().dist = 0
                k = 'dist'
            T = Tree(t)
            label_tree(T)
            for n in self.iter_descendants():
                for n2 in T.iter_descendants():
                    if n2.idname == n.idname:
                        n.add_feature(k,n2.dist)

    def alg2paml(tree,alg,outDir='',align = False,formats = ['fasta','phylip','iphylip']):
        '''
        convert alignment file (phylip iphylip fasta) into paml
        format stored in algn file in outDir returns phyloTree object
        '''
        if align:
            try:
                muscle_aligner.main('-i '+alg+' -o '+\
                                    re.sub('\..*','',alg))
                t = PhyloTree(tree,alignment=\
                              re.sub('\..*','_ali.fasta',alg),\
                              alg_format='fasta')
            except:
                sys.exit('ERROR: problem trying to align\n')
        else:
            for f in formats:
                try:
                    t = PhyloTree(tree,alignment=alg,alg_format=f)
                    f = 'ok'
                    break
                except:
                    continue
            if not f == 'ok':
                usage()
                sys.exit('\nERROR: Problem with inputs.\n'+tree)
        if not outDir=='':
            os.system('mkdir -p '+outDir)
            algFile = open(outDir+'/algn','w')
            algFile.write(' '+str(len(t))+' '+\
                          str (len(t.get_leaves()[0].sequence))+'\n')
            for n in t.iter_leaves():
                algFile.write('>'+n.name+'\n')
                algFile.write(n.sequence+'\n')
            algFile.close()
        return t

# cosmetic alias
CodemlTree = CodemlNode

