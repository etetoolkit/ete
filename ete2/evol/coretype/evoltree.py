#!/usr/bin/python
"""
this module defines the EvolNode dataytype to manage evolutionary
variables and integrate them within phylogenetic trees. It inheritates
the coretype PhyloNode and add some speciall features to the the node
instances.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

import os
from sys import stderr

from ete_dev                   import PhyloNode, TreeImageProperties
from ete_dev.evol.parser       import parse_paml, get_sites
from ete_dev.evol              import evol_layout
from ete_dev.evol.codeml.model import Model, AVAIL, PARAMS
from utils                     import translate, label_tree
from ete_dev.parser.newick     import write_newick

__all__ = ["EvolNode", "EvolTree"]

def _parse_species (name):
    '''
    just to return specie name from fasta description
    '''
    return name[:3]

class EvolNode (PhyloNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def __init__ (self, newick=None, alignment=None, alg_format="fasta", \
                 sp_naming_function=_parse_species):
        '''
        freebranch: path to find codeml output of freebranch model.
        '''
        # _update names?
        self._name = "NoName"
        self._speciesFunction = None
        self.img_prop = None
        self.workdir = '/tmp/ete2-codeml/'
        self.codemlpath = 'codeml'
        self._models = {}
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

    def _label_as_paml (self):
        '''
        to label tree as paml, nearly walking man over the tree algorithm
        WARNING: sorted names in same order that sequence
        WARNING: depends on tree topology conformation, not the same after a swap
        '''
        paml_id = 1
        for leaf in sorted (self, key=lambda x: x.name):
            leaf.add_feature ('paml_id', paml_id)
            paml_id += 1
        self.add_feature ('paml_id', paml_id)
        node = self
        while True:
            node = node.get_children()[0]
            if node.is_leaf():
                node = node.up
                while hasattr (node.get_children()[1], 'paml_id'):
                    node = node.up
                    if not node: break
                if not node: break
                node = node.get_children()[1]
            if not hasattr (node, 'paml_id'):
                paml_id += 1
                node.add_feature ('paml_id', paml_id)
        def get_descendant_by_pamlid (idname):
            '''
            returns node list corresponding to a given idname
            #TODO: perhaps put this in core :P
            '''
            for n in self.iter_descendants():
                if n.paml_id == idname:
                    return n
        self.__dict__['get_descendant_by_pamlid'] = get_descendant_by_pamlid
    
    def link_to_alignment (self, alignment, alg_format="fasta",
                          nucleotides=True):
        '''
        same function as for phyloTree, but translate sequences if nucleotides
        '''
        super(EvolTree, self).link_to_alignment(alignment, alg_format=alg_format)
        for leaf in self.iter_leaves():
            leaf.nt_sequence = str(leaf.sequence)
            if nucleotides:
                leaf.sequence = translate(leaf.nt_sequence)

    def show (self, layout=evol_layout, img_properties=None):
        '''
        call super show adding up and down faces
        '''
        super(EvolTree, self).show(layout=layout,
                                     img_properties=img_properties)

    def render (self, filename, layout=evol_layout, w=None, h=None,
               img_properties=None, header=None):
        '''
        call super show adding up and down faces
        '''
        super(EvolTree, self).render(filename, layout=layout,
                                       img_properties=img_properties,
                                       w=w, h=h)

    def run_paml (self, model, ctrl_string='', keep=True, paml=False, **kwargs):
        ''' To compute evolutionnary models with paml
        extra parameters should be in '''
        from subprocess import Popen, PIPE
        fullpath = os.path.join(self.workdir, model)
        os.system("mkdir -p %s" %fullpath)
        model = Model(model, self, **kwargs)
        # write tree file
        self.write (outfile=fullpath+'/tree', 
                    format = (10 if model.allow_mark else 9))
        # write algn file
        self._write_ali(fullpath, paml)
        ## MODEL MODEL MDE
        if ctrl_string == '':
            ctrl_string = model.get_ctrl_string(fullpath+'/tmp.ctl')
        else:
            open(fullpath+'/tmp.ctl', 'w').write (ctrl_string)

        hlddir = os.getcwd()
        os.chdir(fullpath)
        proc = Popen([self.codemlpath, 'tmp.ctl'], stdout=PIPE)
        run, err = proc.communicate()
        if err is not None:
            print >> stderr, err + \
                  "ERROR: codeml not found!!!\n" + \
                  "       define your variable EvolTree.codemlpath"
            return 1
        os.chdir(hlddir)
        if keep:
            setattr (model, 'run', run)
            self.link_to_evol_model (os.path.join(fullpath,'out'),
                                     model)

    run_paml.__doc__ += '''%s
    to run paml, needs tree linked to alignment.
    model name needs to start by one of:
%s

    e.g.: b_free_lala.vs.lele, will launch one free branch model, and store 
    it in "WORK_DIR/b_free_lala.vs.lele" directory
    
    WARNING: this functionality needs to create a working directory in "rep"
    WARNING: you need to have codeml in your path
    TODO: add feature lnL to nodes for branch tests. e.g.: "n.add_features"
    TODO: add possibility to avoid local minima of lnL by rerunning with other
    starting values of omega, alpha etc...
    ''' % ('['+', '.join (PARAMS.keys())+']\n', '\n'.join (map (lambda x: \
    '           * %-9s model of %-18s at  %-12s level.' % \
    ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
    sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
    cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True))))

    def _write_ali (self, fullpath, paml=False):
        '''
        just to write alignment
        '''
        if not paml:
            seqs = []
            nams = []
            try:
                for leaf in sorted (self, key=lambda x: x.name):
                    nams.append(leaf.name)
                    seqs.append(leaf.nt_sequence)
            except AttributeError:
                print >> stderr, \
                "ERROR: you first need to link your tree to an alignment.\n" + \
                self.link_to_alignment.func_doc
                return 1
            if float(sum(map(len, seqs)) != len (seqs)* len(seqs[0])):
                print >> stderr, \
                      "ERROR: sequences of different length"
                exit()
            if len (self) != len (seqs):
                print >> stderr, \
                      "ERROR: number of sequences different of number of leaves"
                exit()
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

    def mark_tree (self, node_ids, **kargs):
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
                    print >> stderr, \
                          'WARNING: marks should be "#" sign directly '+\
                    'followed by integer\n' + self.mark_tree.func_doc
                node.add_feature('mark', ' '+marks[node_ids.index(node.idname)])
            elif not 'mark' in node.features:
                node.add_feature('mark', '')

    def get_descendant_by_idname (self, idname):
        '''
        returns node list corresponding to a given idname
        #TODO: perhaps put this in core :P
        '''
        return filter(lambda x: x.idname == idname, self.iter_descendants())

    def get_evol_model (self, modelname):
        '''
        returns one precomputed model
        '''
        try:
            return self._models [modelname]
        except KeyError:
            print >> stderr, "Model %s not found." % (modelname)

    def link_to_evol_model (self, path, model):
        '''
        link EvolTree to evolutionary model
          * free-branch model ('fb') will append evol values to tree
          * Site models (M0, M1, M2, M7, M8) will give evol values by site
            and likelihood
        '''
        if not hasattr (self, 'paml_id'):
            self._label_as_paml()
        if type (model) == str :
            model = Model (model, self)
        # new entry in _models dict
        while self._models.has_key (model.name):
            model.name = model.name.split('__')[0] + str (
                (int (model.name.split('__')[1])
                 +1)  if '__' in model.name else 0)
        self._models[model.name] = model
        if not os.path.isfile(path):
            print >> stderr, "ERROR: not a file: "+path
            print model.run
            return 1
        parse_paml(path, model)
        if model.typ == 'site':
            setattr (model, 'sites',
                     get_sites (self.workdir + '/' + model.name + '/rst'))
        if len (self._models) == 1:
            self.change_dist_to_evol ('bL')

    def write (self, features=None, outfile=None, format=10):
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
        if int (format)==10:
            nwk = sub('\[&&NHX:mark=([ #0-9.]*)\]', r'\1', \
                      write_newick(self, features=['mark'],format=9))
        else:
            nwk = write_newick(self, features=features,format=format)
        if outfile is not None:
            open(outfile, "w").write(nwk)
            return nwk
        else:
            return nwk

    def get_most_likely (self, altn, null):
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
         * bsC    vs M1     -> different omegas on clades branches sites
         * bsD    vs M3     -> different omegas on clades branches sites
         * b_free vs b_neut -> PS on branch
         * b_neut vs M0     -> RX on branch?? not sure :P
        '''
        try:
            if hasattr (self._models[altn], 'lnL')\
                   and hasattr (self._models[null], 'lnL'):
                from scipy.stats import chisqprob
                return chisqprob(2*(self._models[altn].lnL - \
                                    self._models[null].lnL),\
                                 df=(self._models[altn].np -\
                                     self._models[null].np))
            else:
                return 1
        except KeyError:
            print >> stderr, \
                  "at least one of %s or %s, was not calculated\n"\
                  % (altn, null)
            exit(self.get_most_likely.func_doc)

    def change_dist_to_evol (self, evol):
        '''
        change dist/branch length of the tree to a given evolutionnary
        varaiable (dN, dS, w or bL), default is bL.
        '''
        for node in self.iter_descendants():
            node.dist = node.__dict__[evol]


# cosmetic alias
EvolTree = EvolNode

