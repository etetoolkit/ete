#!/usr/bin/python
"""
this module defines the evolutionary Model that can be linked
to phylogeny, and computed by one of codeml, gerp, slr.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from re                   import sub
from sys                  import stderr
from ete_dev.evol.control import PARAMS, AVAIL
from ete_dev.evol.parser   import parse_paml, get_sites, get_ancestor

class Model:
    '''Evolutionnary model.
    available models are:
    '''
    def __init__(self, model, tree, path=None, **kwargs):
        '''
        "omega" stands for starting value of omega, in the computation. Qs
        Zihen Yang says, it is good to try with different starting values.
        '''
        self.ctrl_string = ''
        self.tree        = tree
        self.evol        = None
        self.changes     = {}
        self.name, args  = check_name(model)
        for a, b in args.items():
            setattr (self, a, b)
        self.params = dict (PARAMS.items())
        for key, arg in kwargs.items():
            if not self.params.has_key(key):
                print >> stderr, \
                      'WARNING: unknown param %s, will not be used'% (key)
                continue
            if key == 'gappy':
                arg = not arg
            self.params[key] = arg
        if self.evol == 'posistive-selection' \
               and self.params['omega'] < 1:
            self.params['omega'] += 1
        self._change_params()
        self.histface = None
        if path:
            self._load (path)

    def _load (self, path):
        '''
        parse outfiles and load in model object
        '''
        parse_paml (path, self)
        if self.typ == 'site':
            setattr (self, 'sites', get_sites (path))
        if self.typ == 'branch_ancestor':
            get_ancestor (path, self)
        
    def _change_params(self):
        '''
        change model specific values
        '''
        for key, change in self.changes:
            self.params[key] = change

    def set_histface (self, up=True, lines=[1.0], header='',
                      col_lines=['grey'], typ='hist',
                      col=None, extras=[''], col_width=11):
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
        from ete_dev.evol import colorize_rst
        if typ   == 'hist':
            from ete_dev.evol import HistFace as face
        elif typ == 'line':
            from ete_dev.evol import LineFaceBG as face
        elif typ == 'error':
            from ete_dev.evol import ErrorLineFace as face
        elif typ == 'protamine':
            from ete_dev.evol import ErrorLineProtamineFace as face
        if self.sites == None:
            print >> stderr, \
                  "WARNING: model %s not computed." % (self.name)
            return None
        if header == '':
            header = 'Omega value for sites under %s model' % (self.name)
        ldic = self.sites
        self.histface = face(values = ldic['w.' + self.name], 
                             lines = lines, col_lines=col_lines,
                             colors=colorize_rst(ldic['pv.'+self.name],
                                                 self.name,
                                                 ldic['class.'+self.name],
                                                 col=col),
                             header=header, errors=ldic['se.'+self.name],
                             extras=extras, col_width=col_width)
        if up:
            setattr (self.histface, 'up', True)
        else:
            setattr (self.histface, 'up', False)

    def get_ctrl_string(self, outfile=None):
        '''
        generate ctrl string to write to a file, if fil is given,
        write it, otherwise returns the string
        '''
        string = ''
        for p in ['seqfile', 'treefile', 'outfile']:
            string += '%15s = %s\n' % (p, str(self.params[p]))
        string += '\n'
        for p in sorted (self.params.keys(), cmp=lambda x, y: \
                        cmp(sub('fix_', '', x.lower()), \
                            sub ('fix_', '', y.lower()))):
            if p in ['seqfile', 'treefile', 'outfile']:
                continue
            if str(self.params[p]).startswith('*'):
                string += ' *'+'%13s = %s\n' % (p, str(self.params[p])[1:])
            else:
                string += '%15s = %s\n' % (p, str (self.params[p]))
        if outfile == None:
            return string
        else:
            open (outfile, 'w').write (string)

def check_name(model):
    '''
    check that model name corresponds to opne of the availables
    TODO: accept personal models
    '''
    if AVAIL.has_key (sub ('\..*', '', model)):
        return model, AVAIL [sub ('\..*', '', model)]

Model.__doc__ += '\n%s\n' % '\n'.join (map (lambda x: \
        '           * %-9s model of %-18s at  %-12s level.' % \
        ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
        sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
        cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True)))
