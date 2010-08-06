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
this module defines the PhyloNode dataytype to manage phylogenetic
tree. It inheritates the coretype TreeNode and add some speciall
features to the the node instances.
"""
import os
import sys

from ete2 import PhyloNode, PhyloTree
from ete2.codeml.codemlparser import parse_paml, get_sites
from ete2.codeml.control import controlGenerator
from ete2.codeml.utils import mkdir_p, translate, colorize_rst, label_tree
from ete2.parser.newick import write_newick

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
                 sp_naming_function=_parse_species, rst=None):
        '''
        freebranch: path to find codeml output of freebranch model.
        '''
        # _update names?
        self._name = "NoName"
        self._species = "Unknown"
        self._speciesFunction = None
        self._dic = {}
        self.up_faces = []
        self.down_faces = []
        self.workdir = '/tmp/ete2-codeml/'
        self.codemlpath = 'codeml'
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
        self.mark_tree([])

    def link_to_alignment(self, alignment, alg_format="fasta", nucleotides=True, ndata=1):
        '''
        same function as for phyloTree, but translate sequences if nucleotides
        '''
        super(CodemlTree, self).link_to_alignment(alignment, alg_format="fasta")
        for leaf in self.iter_leaves():
            leaf.nt_sequence = str(leaf.sequence)
            if nucleotides:
                leaf.sequence = translate(leaf.nt_sequence)

    def show(self, layout=None, \
             image_properties=None, up_faces=[], down_faces=[]):
        '''
        call super show adding up and down faces
        '''
        super(CodemlTree, self).show(layout=layout, up_faces=self.up_faces, \
                                     down_faces=self.down_faces)

    def render(self, filename, layout=None, w=None, h=None, \
               img_properties=None, header=None):
        '''
        call super show adding up and down faces
        '''
        super(CodemlTree, self).render(filename, layout=layout, \
                                       up_faces=self.up_faces, \
                                       down_faces = self.down_faces, w=w, h=h)

    def run_paml(self, model, ctrl_string='', gappy=True, rst='rst', \
                 ndata=1, keep=True, paml=False):
        '''
        to run paml, needs tree linked to alignment.
        model name needs to start by one of:
           * fb
           * M0
           * M1
           * M2
           * M7
           * M8
           * M8a
           * bsA
           * bsA1
           * bsB
           * bsC
           * bsD
           * b_free
           * b_neut

        e.g.: b_free_lala.vs.lele, will launch one free branch model, and store 
        it in "WORK_DIR/b_free_lala.vs.lele" directory
        
        WARNING: this functionality needs to create a working directory in "rep"
        WARNING: you need to have codeml in your path
        TODO: add feature lnL to nodes for branch tests. e.g.: "n.add_features"
        TODO: add possibility to avoid local minima of lnL by rerunning with other
        starting values of omega, alpha etc...
        
        '''
        from subprocess import Popen, PIPE
        fullpath = os.path.join(self.workdir, model)
        os.system("mkdir -p %s" %fullpath)
        # write tree file
        if model.startswith('b'):
            open(fullpath+'/tree','w').write(\
                self.write(format=9))
        else:
            open(fullpath+'/tree','w').write(\
                super(CodemlTree, self).write(format=9))
        # write algn file
        self._write_ali(fullpath, paml)
        if ctrl_string == '':
            ctrl_string = controlGenerator(model, gappy=gappy, ndata=ndata)
        ctrl = open(fullpath+'/tmp.ctl', 'w')
        ctrl.write(ctrl_string)
        ctrl.close()
        hlddir = os.getcwd()
        os.chdir(fullpath)
        proc = Popen([self.codemlpath, 'tmp.ctl'], stdout=PIPE)
        run, err = proc.communicate()
        if err is not None:
            print >> stderr, err + \
                  "ERROR: codeml not found!!!\n" + \
                  "       define your variable CodemlTree.codemlpath"
            return 1
        os.chdir(hlddir)
        if keep:
            self.link_to_evol_model(os.path.join(fullpath,'out'), model, rst=rst)
            self._dic[model]['codeml_run'] = run

    def _write_ali(self, fullpath, paml=False):
        '''
        just to write alignment
        '''
        if not paml:
            seqs = []
            nams = []
            try:
                for leaf in self.iter_leaves():
                    nams.append(leaf.name)
                    seqs.append(leaf.nt_sequence)
            except AttributeError:
                print >> sys.stderr, \
                "ERROR: you first need to link your tree to an alignment.\n" + \
                self.link_to_alignment.func_doc
                return 1
            if float(sum(map(len, seqs)) != len (seqs)* len(seqs[0])):
                print >> sys.stderr, \
                      "ERROR: sequences of different length"
                sys.exit()
            if len (self) != len (seqs):
                print >> sys.stderr, \
                      "ERROR: number of sequences different of number of leaves"
                sys.exit()
            algn = open(fullpath+'/algn','w')
            algn.write(' %d %d\n' % (len (seqs), len (seqs[0])))
            for spe in range(len (seqs)):
                algn.write('>%s\n%s\n' % (nams[spe], seqs[spe]))
            algn.close()
        else:
            algn = open(fullpath+'/algn','w')
            for line in open(paml, 'r'):
                algn.write(line)
            algn.close()

    def mark_tree(self, node_ids, **kargs):
        '''
        function to mark branches on tree in order that paml could interpret it.
        takes a "marks" argument that should be a list of #1,#1,#2
        e.g.: t=Tree.mark_tree([2,3], marks=["#1","#2"])
        '''
        from re import match
        if kargs.has_key('marks'):
            marks = list(kargs['marks'])
        else:
            marks = ['#1']*len (node_ids)
        for node in self.iter_descendants():
            if node.idname in node_ids:
                if ('.' in marks[node_ids.index(node.idname)] or \
                       match ('#[0-9][0-9]*', \
                              marks[node_ids.index(node.idname)])==None)\
                              and not kargs.has_key('silent'):
                    print >> sys.stderr, \
                          'WARNING: marks should be "#" sign directly '+\
                    'followed by integer\n' + self.mark_tree.func_doc
                node.add_feature('mark', ' '+marks[node_ids.index(node.idname)])
            elif not 'mark' in node.features:
                node.add_feature('mark', '')

    def get_descendant_by_idname(self, idname):
        '''
        returns node list corresponding to a given idname
        #TODO: perhaps put this in core :P
        '''
        return filter(lambda x: x.idname == idname, self.iter_descendants())

    def link_to_evol_model(self, path, model, rst='rst', ndata=1):
        '''
        link CodemlTree to evolutionary model
          * free-branch model ('fb') will append evol values to tree
          * Site models (M0, M1, M2, M7, M8) will give evol values by site
            and likelihood
        rst parameter stands for the path were is your rst file, in case it
        is not "conventional"... if rst=None, skip parsing it.
        '''
        if not os.path.isfile(path):
            print >> sys.stderr, "ERROR: not a file: "+path
            return 1
        self._dic[model] = \
                         parse_paml(path, model, rst=rst, \
                                    ndata=ndata, codon_freq=\
                                    not (hasattr (self, '_codon_freq')))
        if not hasattr (self, '_codon_freq'):
            self._codon_freq = self._dic[model]['codonFreq']
            self._kappa = self._dic[model]['kappa']
            del (self._dic[model]['codonFreq'])
            del (self._dic[model]['kappa'])
        if model == 'fb':
            self._getfreebranch()
        elif self._dic[model].has_key('rst'):
            self._dic[model+'_sites'] = get_sites(self._dic[model]['rst'], \
                                                  ndata=ndata)

    def add_histface(self, mdl, down=True, lines=[1.0], header='', \
                     col_lines=['grey'], typ='hist',col=None, extras=['']):
        '''
        To add histogram face for a given site mdl (M1, M2, M7, M8)
        can choose to put it up or down the tree.
        2 types are available:
           * hist: to draw histogram.
           * line: to draw plot.
        You can define color scheme by passing a diccionary, default is:
            col = {'NS' : 'grey',
                   'RX' : 'green',
                   'RX+': 'green',
                   'CN' : 'cyan',
                   'CN+': 'blue',
                   'PS' : 'orange',
                   'PS+': 'red'}
        '''
        if typ == 'hist':
            from HistFace import HistFace as face
        elif typ == 'line':
            from HistFace import LineFaceBG as face
        elif typ == 'error':
            from HistFace import ErrorLineFace as face
        if self._dic[mdl + '_sites'] == None:
            print >> sys.stderr, \
                  "WARNING: model %s not computed." % (mdl)
            return None
        if header == '':
            header = 'Omega value for sites under %s model' % (mdl)
        ldic = self._dic[mdl + '_sites']
        hist = face(values = ldic['w.' + mdl], \
                    lines = lines, col_lines=col_lines, \
                    colors=colorize_rst(ldic['pv.'+mdl], \
                                        mdl, ldic['class.'+mdl], col=col), \
                    header=header, errors=ldic['se.'+mdl], extras=extras)
        hist.aligned = True
        if down:
            self.down_faces = [hist]
        else:
            self.up_faces   = [hist]

    def write(self, features=None, outfile=None, format=9):
        """ Returns the newick-PAML representation of this node
        topology. Several arguments control the way in which extra
        data is shown for every node:

        features: a list of feature names that want to be shown
        (when available) for every node.

        'format' defines the newick standard used to encode the
        tree. See tutorial for details.

        Example:
             t.get_newick(["species","name"], format=1)
        """
        from re import sub
        nwk = sub('\[&&NHX:mark=([ #0-9.]*)\]', r'\1', \
                  write_newick(self, features=['mark'],format=format))
        if outfile is not None:
            open(outfile, "w").write(nwk)
            return nwk
        else:
            return nwk

    def get_most_likely(self, altn, null):
        '''
        Returns pvalue of LRT between alternative model and null model.
        
        usual comparison are:
         * altern vs null
         -------------------
         * M2     vs M1     -> PS on sites
         * M8     vs M7     -> PS on sites
         * M8     vs M8a    -> RX on sites?? think so....
         * bsA    vs bsA1   -> PS on sites on specific branch
         * bsA    vs M1     -> RX on sites on specific branch
         * bsD    vs bsC    -> different omegas on clades branches sites
         * b_free vs b_neut -> PS on branch
         * b_neut vs M0     -> RX on branch?? not sure :P
        '''
        try:
            if self._dic[altn].has_key('lnL') and self._dic[null].has_key('lnL'):
                from scipy.stats import chisqprob
                return chisqprob(2*(float(self._dic[altn]['lnL']) - \
                                    float(self._dic[null]['lnL'])),\
                                 df=(int (self._dic[altn]['np'])-\
                                     int(self._dic[null]['np'])))
            else:
                return 1
        except KeyError:
            print >> sys.stderr, \
                  "at least one of %s or %s, was not calculated\n"\
                  % (altn, null)
            sys.exit(self.get_most_likely.func_doc)

    def _getfreebranch(self):
        '''
        to convert tree strings of paml into tree strings readable
        by ETE2_codeml.
        returns same dic with CodemlTree.
        #TODO: be abble to undestand how codeml put ids to tree nodes
        '''
        for evol in ['bL', 'dN', 'dS', 'w']:
            if not self._dic['fb'].has_key(evol):
                print >> sys.stderr, \
                      "Warning: this file do not cotain info about " \
                      + evol + " parameter"
                continue
            if not self._dic['fb'][evol].startswith('('):
                print >> sys.stderr, \
                      "Warning: problem with tree string for "\
                      + evol +" parameter"
                continue
            tdic = self._dic['fb'][evol]
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


