#!/usr/bin/python
"""
this module defines the EvolNode dataytype to manage evolutionary
variables and integrate them within phylogenetic trees. It inheritates
the coretype PhyloNode and add some speciall features to the the node
instances.
"""

__author__     = "Francois-Jose Serra"
__email__      = "francois@barrabin.org"
__licence__    = "GPLv3"
__version__    = "0.0"
__references__ = '''
Yang, Z., Nielsen, R., Goldman, N., & Pedersen, A. M. 2000.
    Codon-substitution models for heterogeneous selection pressure at amino acid sites.
    Genetics 155: 431-49.
    Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1461088&tool=pmcentrez&rendertype=abstract
Yang, Z., & Nielsen, R. 2002.
    Codon-substitution models for detecting molecular adaptation at individual sites along specific lineages.
    Molecular biology and evolution 19: 908-17.
    Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/12032247
Bielawski, J. P., & Yang, Z. 2004.
    A maximum likelihood method for detecting functional divergence at individual codon sites, with application to gene family evolution.
    Journal of molecular evolution 59: 121-32.
    Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/15383915
Zhang, J., Nielsen, R., & Yang, Z. 2005.
    Evaluation of an improved branch-site likelihood method for detecting positive selection at the molecular level.
    Molecular biology and evolution 22: 2472-9.
    Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/16107592
Yang, Z. 2007.
    PAML 4: phylogenetic analysis by maximum likelihood.
    Molecular biology and evolution 24: 1586-91.
    Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/17483113
'''

import os
from warnings import warn

from ete_dev               import PhyloNode
from ete_dev               import SeqGroup
from ete_dev.evol          import __path__ as ete_path
from ete_dev.evol          import evol_layout
from ete_dev.evol.model    import Model, PARAMS, AVAIL
from ete_dev.evol.utils    import translate
from ete_dev.parser.newick import write_newick
from ete_dev               import TreeStyle

__all__ = ["EvolNode", "EvolTree"]

def _parse_species (name):
    '''
    just to return specie name from fasta description
    '''
    return name[:3]

class EvolNode (PhyloNode):
    """ Re-implementation of the standart TreeNode instance. It adds
    attributes and methods to work with phylogentic trees. """

    def __init__ (self, newick=None, alignment=None, alg_format="fasta",
                 sp_naming_function=_parse_species, format=0, 
                  binpath=os.path.join(ete_path[0], "bin")
                  ):
        '''
        freebranch: path to find codeml output of freebranch model.
        '''
        # _update names?
        self._name = "NoName"
        self._speciesFunction = None
        self.img_prop = None
        self.workdir = '/tmp/ete2-codeml/'
        self.execpath = binpath
        self._models = {}
        # Caution! native __init__ has to be called after setting
        # _speciesFunction to None!!
        PhyloNode.__init__(self, newick=newick, format=format)

        # This will be only executed after reading the whole tree,
        # because the argument 'alignment' is not passed to the
        # PhyloNode constructor during parsing
        if alignment:
            self.link_to_alignment(alignment, alg_format)
        if newick:
            self.set_species_naming_function(sp_naming_function)
            self.sort_descendants()
        self.mark_tree([])

        
    def _label_as_paml (self):
        '''
        to label tree as paml, nearly walking man over the tree algorithm
        WARNING: sorted names in same order that sequence
        WARNING: depends on tree topology conformation, not the same after a swap
        '''
        def __label_internal_nodes(self, paml_id):
            for node in self.get_children():
                if node.is_leaf():
                    continue
                paml_id += 1
                node.add_feature ('paml_id', paml_id)
                __label_internal_nodes(node, paml_id)
        paml_id = 1
        for leaf in sorted (self, key=lambda x: x.name):
            leaf.add_feature ('paml_id', paml_id)
            paml_id += 1
        self.add_feature ('paml_id', paml_id)
        __label_internal_nodes(self, paml_id)
    
    ## def _label_as_paml (self):
    ##     '''
    ##     to label tree as paml, nearly walking man over the tree algorithm
    ##     WARNING: sorted names in same order that sequence
    ##     WARNING: depends on tree topology conformation, not the same after a swap
    ##     '''
    ##     paml_id = 1
    ##     for leaf in sorted (self, key=lambda x: x.name):
    ##         leaf.add_feature ('paml_id', paml_id)
    ##         paml_id += 1
    ##     self.add_feature ('paml_id', paml_id)
    ##     node = self
    ##     while True:
    ##         node = node.get_children()[0]
    ##         if node.is_leaf():
    ##             node = node.up
    ##             while hasattr (node.get_children()[1], 'paml_id'):
    ##                 node = node.up
    ##                 if not node:
    ##                     break
    ##             if not node:
    ##                 break
    ##             node = node.get_children()[1]
    ##         if not hasattr (node, 'paml_id'):
    ##             paml_id += 1
    ##             node.add_feature ('paml_id', paml_id)
    ##     def get_descendant_by_pamlid (idname):
    ##         '''
    ##         returns node list corresponding to a given idname
    ##         '''
    ##         for n in self.iter_descendants():
    ##             if n.paml_id == idname:
    ##                 return n
    ##         if self.paml_id == idname:
    ##             return self
    ##     vars (self)['get_descendant_by_pamlid'] = get_descendant_by_pamlid

    def __write_algn(self, fullpath):
        """
        to write algn in paml format
        """
        seq_group = SeqGroup ()
        for n in self:
            seq_group.id2seq  [n.paml_id] = n.nt_sequence
            seq_group.id2name [n.paml_id] = n.name
            seq_group.name2id [n.name   ] = n.paml_id
        seq_group.write (outfile=fullpath, format='paml')

    def run_model (self, model_name, ctrl_string='', keep=True, **kwargs):
        ''' To compute evolutionnary models with paml
        extra parameters should be in '''
        from subprocess import Popen, PIPE
        model_obj = Model(model_name, self, **kwargs)
        fullpath = os.path.join (self.workdir, model_obj.name)
        os.system("mkdir -p %s" %fullpath)
        # write tree file
        self.__write_algn (fullpath + '/algn')
        if model_obj.properties['exec'] == 'Slr':
            self.write (outfile=fullpath+'/tree',
                        format = (11))
        else:
            self.write (outfile=fullpath+'/tree',
                        format = (10 if model_obj.properties['allow_mark'] else 9))
        # write algn file
        ## MODEL MODEL MDE
        if ctrl_string == '':
            ctrl_string = model_obj.get_ctrl_string(fullpath+'/tmp.ctl')
        else:
            open (fullpath+'/tmp.ctl', 'w').write (ctrl_string)
        hlddir = os.getcwd()
        os.chdir(fullpath)
        bin = os.path.join(self.execpath, model_obj.properties['exec'])
        proc = Popen([bin, 'tmp.ctl'], stdout=PIPE)
        run, err = proc.communicate()
        if err is not None:
            warn ("ERROR: codeml not found!!!\n" + \
                  "       define your variable EvolTree.execpath")
            return 1
        if 'error' in run:
            warn ("ERROR: inside codeml!!\n" + run)
            return 1
        os.chdir(hlddir)
        if keep:
            setattr (model_obj, 'run', run)
            self.link_to_evol_model (os.path.join(fullpath,'out'), model_obj)
    run_model.__doc__ += '''%s
    to run paml, needs tree linked to alignment.
    model name needs to start by one of:
%s
    
    e.g.: b_free_lala.vs.lele, will launch one free branch model, and store 
    it in "WORK_DIR/b_free_lala.vs.lele" directory
    
    WARNING: this functionality needs to create a working directory in "rep"
    WARNING: you need to have codeml in your path
    starting values of omega, alpha etc...
    ''' % ('['+', '.join (PARAMS.keys())+']\n', '\n'.join (map (lambda x: \
    '           * %-9s %-18s model at  %-15s level.' % \
    ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
    sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
    cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True))))


    def link_to_alignment (self, alignment, alg_format="paml",
                           nucleotides=True):
        '''
        same function as for phyloTree, but translate sequences if nucleotides
        '''
        super(EvolTree, self).link_to_alignment(alignment,
                                                alg_format=alg_format)
        for leaf in self.iter_leaves():
            leaf.nt_sequence = str(leaf.sequence)
            if nucleotides:
                leaf.sequence = translate(leaf.nt_sequence)
        self._label_as_paml()

    def show(self, layout=evol_layout, tree_style=None, histfaces=None):
        '''
        call super show
        histface should be a list of models to be displayes as histfaces
        '''
        if not tree_style:
            ts = TreeStyle()
        else: 
            ts = tree_style
        if histfaces:
            for hist in histfaces:
                try:
                    mdl = self.get_evol_model (hist)
                except AttributeError:
                    warn ('model %s not computed' % (hist))
                if not mdl.properties.has_key ('histface'):
                    mdl.set_histface ()
                if mdl.properties ['histface'].up:
                    ts.aligned_header.add_face (\
                        mdl.properties['histface'], 1)
                else:
                    ts.aligned_foot.add_face (\
                        mdl.properties['histface'], 1)
        super(EvolTree, self).show(layout=layout,
                                     tree_style=ts)

    def render (self, file_name, layout=evol_layout, w=None, h=None,
                tree_style=None, header=None, histfaces=None):
        '''
        call super show adding up and down faces
        '''
        if not tree_style:
            ts = TreeStyle()
        else: 
            ts = tree_style
        if histfaces:
            for hist in histfaces:
                try:
                    mdl = self.get_evol_model (hist)
                except AttributeError:
                    warn ('model %s not computed' % (hist))
                if mdl.histface is None:
                    mdl.set_histface()
                if mdl.histface.up:
                    ts.aligned_header.add_face (mdl.histface, 1)
                else:
                    ts.aligned_foot.add_face (mdl.histface, 1)
        return super(EvolTree, self).render(file_name, layout=layout,
                                            tree_style=ts,
                                            w=w, h=h)
        

    def mark_tree (self, node_ids, verbose=False, **kargs):
        '''
        function to mark branches on tree in order that paml could interpret it.
        takes a "marks" argument that should be a list of #1,#1,#2
        e.g.: t=Tree.mark_tree([2,3], marks=["#1","#2"])
        '''
        from re import match
        node_ids = map (str , node_ids)
        if kargs.has_key('marks'):
            marks = list(kargs['marks'])
        else:
            marks = ['#1']*len (node_ids)
        for node in self.traverse():
            if not hasattr (node, '_nid'):
                continue
            if node._nid in node_ids:
                if ('.' in marks[node_ids.index(node._nid)] or \
                       match ('#[0-9][0-9]*', \
                              marks[node_ids.index(node._nid)])==None)\
                              and not kargs.has_key('silent') and not verbose:
                    warn ('WARNING: marks should be "#" sign directly '+\
                          'followed by integer\n' + self.mark_tree.func_doc)
                node.add_feature('mark', ' '+marks[node_ids.index(node._nid)])
            elif not 'mark' in node.features:
                node.add_feature('mark', '')

    def link_to_evol_model (self, path, model):
        '''
        link EvolTree to evolutionary model
          * free-branch model ('fb') will append evol values to tree
          * Site models (M0, M1, M2, M7, M8) will give evol values by site
            and likelihood
        '''
        if type (model) == str :
            model = Model (model, self, path)
        else:
            model._load (path)
        # new entry in _models dict
        while self._models.has_key (model.name):
            model.name = model.name.split('__')[0] + str (
                (int (model.name.split('__')[1])
                 +1)  if '__' in model.name else 0)
        self._models[model.name] = model
        if not os.path.isfile(path):
            warn ("ERROR: not a file: " + path)
            return 1
        if len (self._models) == 1:
            self.change_dist_to_evol ('bL', model, fill=True)

        def get_evol_model (modelname):
            '''
            returns one precomputed model
            '''
            try:
                return self._models [modelname]
            except KeyError:
                warn ("Model %s not found." % (modelname))
                
        if not hasattr (self, "get_evol_model"):
            vars (self)["get_evol_model"] = get_evol_model

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
        if int (format)==11:
            nwk = ' %s 1\n' % (len (self))
            nwk += sub('\[&&NHX:mark=([ #0-9.]*)\]', r'\1', \
                       write_newick(self, features=['mark'],format=9))
        elif int (format)==10:
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
         * altern vs null model
         ------------------------
         * M2     vs M1     -> PS on sites (M2 prone to miss some sites)
                               ref: Yang 2000
         * M3     vs M0     -> test of variability among sites
         * M8     vs M7     -> PS on sites
                               ref: Yang 2000
         * M8     vs M8a    -> RX on sites?? think so....
         * bsA    vs bsA1   -> PS on sites on specific branch
                               ref: Zhang 2005
         * bsA    vs M1     -> RX on sites on specific branch
                               ref: Zhang 2005
         * bsC    vs M1     -> different omegas on clades branches sites
                               ref: Yang Nielsen 2002
         * bsD    vs M3     -> different omegas on clades branches sites
                               ref: Yang Nielsen 2002
                                    Bielawski 2004
         * b_free vs b_neut -> foreground branch not neutral (w != 1)
                              - RX if P<0.05 (means that w on frg=1)
                              - PS if P>0.05 and wfrg>1
                              - CN if P>0.05 and wfrg>1
                               ref: Yang Nielsen 2002
         * b_free vs M0     -> different ratio on branches
                               ref: Yang Nielsen 2002
        '''
        altn = self.get_evol_model (altn)
        null = self.get_evol_model (null)
        if null.np > altn.np:
            warn ("first model should be the alternative, change the order")
            return 1.0
        try:
            if hasattr (altn, 'lnL') and hasattr (null, 'lnL'):
                from scipy.stats import chisqprob
                return chisqprob(2*(altn.lnL - null.lnL),
                                 df=(altn.np - null.np))
            else:
                return 1
        except KeyError:
            warn ("at least one of %s or %s, was not calculated" % (altn.name,
                                                                    null.name))
            exit (self.get_most_likely.func_doc)

    def change_dist_to_evol (self, evol, model, fill=False):
        '''
        change dist/branch length of the tree to a given evolutionnary
        varaiable (dN, dS, w or bL), default is bL.
        '''
        # branch-site outfiles do not give specific branch info
        if not model.branches:
            return
        for node in self.iter_descendants():
            node.dist = model.branches [node.paml_id][evol]
            if fill:
                for e in ['dN', 'dS', 'w', 'bL']:
                    node.add_feature (e, model.branches [node.paml_id][e])


# cosmetic alias
EvolTree = EvolNode

