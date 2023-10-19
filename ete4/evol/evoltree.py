#!/usr/bin/python3

"""
This module defines the EvolNode dataytype to manage evolutionary
variables and integrate them within phylogenetic trees. It inherits
the PhyloTree and add some speciall features to the the node
instances.
"""
from __future__ import absolute_import
from ..tools.utils import which
from .utils import translate
from .model import Model, PARAMS, AVAIL
from .. import PhyloTree, SeqGroup
from warnings import warn
import sys
import os

__author__ = "Francois-Jose Serra"
__email__ = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"
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


try:
    from scipy.stats import chi2
    def chi_high(x, y): return 1 - chi2.cdf(x, y)
except ImportError:
    from .utils import chi_high

try:
    from ..treeview import TreeStyle
except ImportError:
    TREEVIEW = False
else:
    TREEVIEW = True

__all__ = ["EvolNode", "EvolTree"]


def _parse_species(name):
    return name[:3]  # just to return specie name from fasta description


class EvolNode(PhyloTree):
    """Re-implementation of the standart Tree instance. It adds
    attributes and methods to work with phylogentic trees.

    :param newick: Path to tree in newick format, can also be a string
    :param alignment: Path to alignment, can also be a string.
    :param fasta alg_format: Alignment format.
    :param sp_naming_function: Function to infer species name.
    :param format: Type of newick format
    :param binpath: Path to binaries, in case codeml or SLR are not in global path.
    """

    def __init__(self, newick=None, alignment=None, alg_format="fasta",
                 sp_naming_function=_parse_species, parser=0,
                 binpath='', **kwargs):
        '''
        freebranch: path to find codeml output of freebranch model.
        '''
        # _update names?
        self.workdir = '/tmp/ete3-tmp/'
        if not binpath:
            ete3_path = which("ete3")
            binpath = os.path.split(ete3_path)[0]

        self.execpath = binpath
        self._models = {}
        self.__gui_mark_mode = False

        PhyloTree.__init__(self, newick=newick, parser=parser,
                           sp_naming_function=sp_naming_function, **kwargs)

        if newick:
            self._label_as_paml()
        # initialize node marks
        self.mark_tree([])

    def _set_mark_mode(self, val):
        self.__gui_mark_mode = val

    def _is_mark_mode(self):
        return self.__gui_mark_mode

    def _label_internal_nodes(self, nid=None):
        """
        nid needs to be a list in order to keep count through recursivity
        """
        for node in self.get_children():
            if node.is_leaf:
                continue
            nid[0] += 1
            node.add_prop('node_id', nid[0])
            node._label_internal_nodes(nid)

    def _label_as_paml(self):
        '''
        to label tree as paml, nearly walking man over the tree algorithm
        WARNING: sorted names in same order that sequence
        WARNING: depends on tree topology conformation, not the same after a swap
        activates the function get_descendants_by_pamlid
        '''
        nid = 1
        # check we do not have dupplicated names in tree
        if (len(self)) != len(set(self.leaf_names())):
            duplis = [n for n in self.leaf_names(
            ) if self.leaf_names().count(n) > 1]
            raise Exception('EvolTree require unique names for leaves', duplis)
        # put ids
        for leaf in sorted(self, key=lambda x: x.name):
            leaf.add_prop('node_id', nid)
            nid += 1
        self.add_prop('node_id', nid)
        self._label_internal_nodes([nid])

    def get_descendant_by_node_id(self, idname):
        '''
        returns node list corresponding to a given idname
        '''
        try:
            for n in self.descendants():
                if n.props.get('node_id') == idname:
                    return n
            if self.props.get('node_id') == idname:
                return self
        except AttributeError:
            warn('Should be first labelled as paml ' +
                 '(automatically done when alignemnt is loaded)')

    def _write_algn(self, fullpath):
        """
        to write algn in paml format
        """
        seq_group = SeqGroup()
        for n in self:
            seq_group.id2seq  [n.props.get('node_id')] = n.props.get('nt_sequence')
            seq_group.id2name [n.props.get('node_id')] = n.name
            seq_group.name2id [n.name   ] = n.props.get('node_id')
        seq_group.write(outfile=fullpath, format='paml')

    def run_model(self, model_name, ctrl_string='', keep=True, **kwargs):
        '''
        To compute evolutionnary models.     e.g.: b_free_lala.vs.lele, will launch one free branch model, and store
        it in "WORK_DIR/b_free_lala.vs.lele" directory

        WARNING: this functionality needs to create a working directory in "rep"

        WARNING: you need to have codeml and/or SLR in your path

        The models available are:

        =========== ============================= ==================
        Model name  Description                   Model kind
        =========== ============================= ==================\n%s
        =========== ============================= ==================\n

        **Note that M1 and M2 models are making reference to the new versions
        of these models, with continuous omega rates (namely M1a and M2a in the
        PAML user guide).**

        :argument model_name: a string like "model-name[.some-secondary-name]" (e.g.: "fb.my_first_try", or just "fb")
                              * model-name is compulsory, is the name of the model (see table above for the full list)
                              * the second part is accessory, it is to avoid over-writing models with the same name.
        :argument ctrl_string: list of parameters that can be used as control file.
        :argument True keep: links the model to the tree (equivalen of running `EVOL_TREE.link_to_evol_model(MODEL_NAME)`)
        :argument kwargs: extra parameters should be one of: %s.
        '''
        from subprocess import Popen, PIPE
        model_obj = Model(model_name, self, **kwargs)
        fullpath = os.path.join(self.workdir, model_obj.name)
        os.system("mkdir -p %s" % fullpath)
        # write tree file
        self._write_algn(fullpath + '/algn')
        if model_obj.properties['exec'] == 'Slr':
            self.write(outfile=fullpath+'/tree', format=(11))
        else:
            self.write(outfile=fullpath+'/tree',
                       format=(10 if model_obj.properties['allow_mark'] else 9))
        # write algn file
        # MODEL MODEL MDE
        if ctrl_string == '':
            ctrl_string = model_obj.get_ctrl_string(fullpath+'/tmp.ctl')
        else:
            open(fullpath+'/tmp.ctl', 'w').write(ctrl_string)
        hlddir = os.getcwd()
        os.chdir(fullpath)
        bin_ = os.path.join(self.execpath, model_obj.properties['exec'])
        try:
            proc = Popen([bin_, 'tmp.ctl'], stdout=PIPE,
                         stdin=PIPE, stderr=PIPE)
        except OSError:
            raise Exception(('ERROR: {} not installed, ' +
                             'or wrong path to binary\n').format(bin_))
        # send \n via stdin in case codeml/slr asks something (note on py3, stdin needs bytes)
        run, err = proc.communicate(b'\n')
        run = run.decode(sys.stdout.encoding)

        os.chdir(hlddir)
        if err:
            warn("ERROR: inside codeml!!\n" + err)
            return 1
        if keep:
            setattr(model_obj, 'run', run)
            self.link_to_evol_model(os.path.join(fullpath, 'out'), model_obj)
    sep = '\n'
    run_model.__doc__ = run_model.__doc__ % \
        (sep.join(['          %-8s   %-27s   %-15s  ' %
                   ('%s' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']) for x in sorted(sorted(AVAIL.keys()), key=lambda x:
                                                                                   AVAIL[x]['typ'],
                                                                                   reverse=True)]),
         ', '.join(list(PARAMS.keys())))

    # def test_codon_model(self):
    #    for c_frq in range(4):
    #        self.run_model('M0.model_test-'+str(c_frq), CodonFreq=c_frq)
    #    if self.get_most_likely('M0.model_test-1', 'M0.model_test-0') > 0.05:
    #
    #    self.get_most_likely('M0.model_test-2', 'M0.model_test-0')
    #    self.get_most_likely('M0.model_test-3', 'M0.model_test-0')
    #    self.get_most_likely('M0.model_test-2', 'M0.model_test-1')
    #    self.get_most_likely('M0.model_test-3', 'M0.model_test-1')
    #    self.get_most_likely('M0.model_test-3', 'M0.model_test-2')

    def link_to_alignment(self, alignment, alg_format="paml",
                          nucleotides=True, **kwargs):
        '''
        same function as for phyloTree, but translate sequences if nucleotides
        nucleotidic sequence is kept under node.get('nt_sequence')

        :argument alignment: path to alignment or string
        :argument alg_format: one of fasta phylip or paml
        :argument True alignment: set to False in case we want to keep it untranslated

        '''
        super(EvolTree, self).link_to_alignment(alignment,
                                                alg_format=alg_format, **kwargs)
        check_len = 0
        for leaf in self.leaves():
            seq_len = len(str(leaf.props.get('sequence')))
            if check_len and check_len != seq_len:
                warn('WARNING: sequences with different lengths found!')
            check_len = seq_len
            leaf.add_prop('nt_sequence', str(leaf.props.get('sequence')))
            if nucleotides:
                leaf.add_prop('sequence', translate(leaf.props.get('nt_sequence')))

    def show(self, layout=None, tree_style=None, histfaces=None):
        '''
        call super show of PhyloTree
        histface should be a list of models to be displayes as histfaces

        :argument layout: a layout function
        :argument None tree_style: tree_style object
        :argument Nonehistface: an histogram face function. This is only to plot selective pressure among sites

        '''
        if TREEVIEW:
            if not tree_style:
                ts = TreeStyle()
            else:
                ts = tree_style
            if histfaces:
                for hist in histfaces:
                    try:
                        mdl = self.get_evol_model(hist)
                    except AttributeError:
                        warn('model %s not computed' % (hist))
                    if not 'histface' in mdl.properties:
                        if len(histfaces) > 1 and histfaces.index(hist) != 0:
                            mdl.set_histface(up=False)
                        else:
                            mdl.set_histface()
                    if mdl.properties['histface'].up:
                        ts.aligned_header.add_face(
                            mdl.properties['histface'], 1)
                    else:
                        ts.aligned_foot.add_face(
                            mdl.properties['histface'], 1)
            super(EvolTree, self).show(layout=layout, tree_style=ts)
        else:
            raise ValueError("Treeview module is disabled")

    def render(self, file_name, layout=None, w=None, h=None,
               tree_style=None, header=None, histfaces=None):
        """Add up and down faces and render the tree representation to a file.

        :param histface: A histogram face function. This is only to
            plot selective pressure among sites.
        """
        if not TREEVIEW:
            raise ValueError("Treeview module is disabled")

        ts = tree_style or TreeStyle()

        for hist in (histfaces or []):
            try:
                mdl = self.get_evol_model(hist)
            except AttributeError:
                warn('model %s not computed' % (hist))

            if not 'histface' in mdl.properties:
                if len(histfaces) > 1 and histfaces.index(hist) != 0:
                    mdl.set_histface(up=False)
                else:
                    mdl.set_histface()

            if mdl.properties['histface'].up:
                ts.aligned_header.add_face(mdl.properties['histface'], 1)
            else:
                ts.aligned_foot.add_face(mdl.properties['histface'], 1)

        return super().render(file_name, layout=layout, tree_style=ts, w=w, h=h)

    def mark_tree(self, node_ids, verbose=False, **kargs):
        '''
        function to mark branches on tree in order that paml could interpret it.
        takes a "marks" argument that should be a list of #1,#1,#2
        e.g.:
        ::

          t=Tree.mark_tree([2,3], marks=["#1","#2"])

        :argument node_ids: list of node ids (have a look to node.props.get('node_id'))
        :argument False verbose: warn if marks do not correspond to codeml standard
        :argument kwargs: mainly for the marks key-word which needs a list of marks (marks=['#1', '#2'])

        '''
        from re import match
        node_ids = list(map(int, node_ids))
        if 'marks' in kargs:
            marks = list(kargs['marks'])
        else:
            marks = ['#1']*len(node_ids)
        for node in self.traverse():
            if not node.props.get('node_id'):
                continue
            if node.props.get('node_id') in node_ids:
                if ('.' in marks[node_ids.index(node.props.get('node_id'))] or
                    match('#[0-9]+',
                          marks[node_ids.index(node.props.get('node_id'))]) is None) and verbose:
                    warn('WARNING: marks should be "#" sign directly ' +
                         'followed by integer\n' + self.mark_tree.__doc__)
                node.add_prop('mark', ' '+marks[node_ids.index(node.props.get('node_id'))])
            elif node.props.get('mark') == None:
                node.add_prop('mark', '')

    def link_to_evol_model(self, path, model):
        '''
        link EvolTree to evolutionary model
          * free-branch model ("fb") will append evol values to tree
          * Site models (M0, M1, M2, M7, M8) will give evol values by site
            and likelihood

        :argument path: path to outfile containing model computation result
        :argument model: either the name of a model, or a Model object (usually empty)

        '''
        if isinstance(model, str):
            model = Model(model, self, path)
        else:
            model._load(path)
        # new entry in _models dict
        while model.name in self._models:
            model.name = model.name.split('__')[0] + str(
                (int(model.name.split('__')[1]) + 1)
                if '__' in model.name else 0)
        self._models[model.name] = model
        if not os.path.isfile(path):
            warn("ERROR: not a file: " + path)
            return 1
        if len(self._models) == 1 and model.properties['exec'] == 'codeml':
            self.change_dist_to_evol('bL', model, fill=True)

    def get_evol_model(self, modelname):
        '''
        returns one precomputed model

        :argument modelname: string of the name of a model object stored
        :returns: Model object
        '''
        try:
            return self._models[modelname]
        except KeyError:
            Exception("ERROR: Model %s not found." % (modelname))

    def write(self, properties=None, outfile=None, format=10):
        """
        Inherits from Tree but adds the tenth format, that allows to display marks for CodeML.
        TODO: internal writting format need to be something like 0
        """
        from re import sub
        if int(format) == 11:
            nwk = ' %s 1\n' % (len(self))
            nwk += sub(r'\[&&NHX:mark=([ #0-9.]*)\]', r'\1', \
                       write_newick(self, properties=['mark'],format=9))
        elif int(format)==10:
            nwk = sub(r'\[&&NHX:mark=([ #0-9.]*)\]', r'\1', \
                      write_newick(self, properties=['mark'],format=9))
        else:
            nwk = write_newick(self, properties=properties,format=format)
        if outfile is not None:
            open(outfile, "w").write(nwk)
            return nwk
        else:
            return nwk
    #write.__doc__ += super(PhyloTree, PhyloTree()).write.__doc__.replace(
    #    'argument format', 'argument 10 format')

    def get_most_likely(self, altn, null):
        """Return pvalue of LRT between alternative model and null model.

        Usual comparison are:

        .. table::

            =========== ======= ===========================================
            Alternative  Null   Test
            =========== ======= ===========================================
            M2          M1      PS on sites (M2 prone to miss some sites)
                                (Yang 2000).
            M3          M0      test of variability among sites
            M8          M7      PS on sites
                                (Yang 2000)
            M8          M8a     RX on sites?? think so....
            bsA         bsA1    PS on sites on specific branch
                                (Zhang 2005)
            bsA         M1      RX on sites on specific branch
                                (Zhang 2005)
            bsC         M1      different omegas on clades branches sites
                                ref: Yang Nielsen 2002
            bsD         M3      different omegas on clades branches sites
                                (Yang Nielsen 2002, Bielawski 2004)
            b_free      b_neut  foreground branch not neutral (w != 1)
                                - RX if P<0.05 (means that w on frg=1)
                                - PS if P>0.05 and wfrg>1
                                - CN if P>0.05 and wfrg>1
                                (Yang Nielsen 2002)
            b_free      M0      different ratio on branches
                                (Yang Nielsen 2002)
            =========== ======= ===========================================

        Note that M1 and M2 models are making reference to the new
        versions of these models, with continuous omega rates (namely
        M1a and M2a in the PAML user guide).

        :param altn: model with higher number of parameters (np).
        :param null: model with lower number of parameters (np).
        """
        altn = self.get_evol_model(altn)
        null = self.get_evol_model(null)
        if null.np > altn.np:
            warn("first model should be the alternative, change the order")
            return 1.0
        try:
            if hasattr(altn, 'lnL') and hasattr(null, 'lnL'):
                if null.lnL - altn.lnL < 0:
                    return chi_high(2 * abs(altn.lnL - null.lnL),
                                    float(altn.np - null.np))
                else:
                    warn("\nWARNING: Likelihood of the alternative model is "
                         "smaller than null's (%f - %f = %f)" % (
                             null.lnL, altn.lnL, null.lnL - altn.lnL) +
                         "\nLarge differences (> 0.1) may indicate mistaken "
                         "assigantion of null and alternative models")
                    return 1
        except KeyError:
            warn("at least one of %s or %s, was not calculated" % (altn.name,
                                                                   null.name))
            exit(self.get_most_likely.__doc__)

    def change_dist_to_evol(self, evol, model, fill=False):

        """Change dist/branch length of tree to a given evolutionary variable.

        :param evol: Evolutionary variable (dN, dS, w, bL, by default bL).
        :param model: Model obj from which to retrieve evolutionary variables.
        :param fill: In addition to changing the dist parameter, annotate nodes
            with all evolutionary variables (add to their props: dN, w...).
        """
        # branch-site outfiles do not give specific branch info
        if not model.branches:
            return
        for node in self.descendants():
            if not evol in model.branches[node.props.get('node_id')]:
                continue
            node.dist = model.branches[node.props.get('node_id')][evol]
            if fill:
                for e in ['dN', 'dS', 'w', 'bL']:
                    node.add_prop(e, model.branches [node.props.get('node_id')][e])


# cosmetic alias
EvolTree = EvolNode
