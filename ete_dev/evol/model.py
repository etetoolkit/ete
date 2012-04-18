#!/usr/bin/python
"""
this module defines the evolutionary Model that can be linked
to phylogeny, and computed by one of codeml, gerp, slr.
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from re       import sub
from warnings import warn

from ete_dev.evol.control import PARAMS, AVAIL
from ete_dev.evol.parser  import parse_paml, parse_rst, get_ancestor, parse_slr

class Model:
    '''Evolutionary model.
    "omega" stands for starting value of omega, in the computation. As
    Zihen Yang says, it is good to try with different starting values...
    model linked to tree by _tree variable
    results of calculation are stored in dictionaries:
     * branches: w dN dS bL by mean of their paml_id
     * sites   : values at each site.
     * classes : classes of sites and proportions
     * stats   : lnL number of parameters kappa value and codon frequencies stored here.
    
    available models are:
        +----------+-----------------------------+-----------------+
        |Model name| description                 | Model kind      |
        +==========+=============================+=================+\n%s

    :argument model_name: string with model name. Add a dot followed by anything at the end of the string in order to extend the name of the model and avoid overwriting.
    :argument None tree: a Tree object
    :argument None path: path to outfile, were model computation output can be found.

    '''
    def __init__(self, model_name, tree=None, path=None, **kwargs):
        self._tree      = tree
        self.name, args = check_name(model_name)
        self.sites      = None
        self.classes    = None
        self.branches   = {}
        self.stats      = {}
        self.properties = {}
        for a, b in args.items():
            self.properties [a] = b
        params = dict (PARAMS.items ())
        for key, arg in kwargs.items():
            if not params.has_key (key):
                warn ('WARNING: unknown param %s, can cause problems...'% (key))
            if key == 'gappy':
                arg = not arg
            params[key] = arg
        self._change_params (params)
        if path:
            self._load (path)

    def __str__(self):
        '''
        to print nice info
        '''
        return ''' Evolutionary Model %s:
        log likelihood      : %s
        number of parameters: %s
        ''' % (self.name,
               self.lnL if 'lnL' in self.stats else 'None',
               self.np  if 'np'  in self.stats else 'None'
        )

    def _load (self, path):
        '''
        parse outfiles and load in model object
        '''
        if self.properties['exec'] == 'codeml':
            parse_paml (path, self)
            # parse rst file if site or branch-site model
            if 'site' in self.properties['typ']:
                # sites and classes attr
                for key, val in parse_rst (path).iteritems():
                    setattr (self, key, val)
            if 'ancestor' in self.properties['typ']:
                get_ancestor (path, self)
            vars (self) ['lnL'] = self.stats ['lnL']
            vars (self) ['np']  = self.stats ['np']
        elif self.properties['exec'] == 'Slr':
            for key, val in parse_slr (path).iteritems():
                setattr (self, key, val)
            vars (self) ['lnL'] = 0
            vars (self) ['np']  = 0
            
    def _change_params(self, params):
        '''
        change model specific values
        '''
        for key, change in self.properties ['changes']:
            params[key] = change
        self.properties ['params'] = params
        
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
            col = {'NS' : 'grey'  ,
                   'RX' : 'green' ,
                   'RX+': 'green' ,
                   'CN' : 'cyan'  ,
                   'CN+': 'blue'  ,
                   'PS' : 'orange',
                   'PS+': 'red'    }
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
            warn ("WARNING: model %s not computed." % (self.name))
            return None
        if header == '':
            header = 'Omega value for sites under %s model' % (self.name)
        if self.sites.has_key ('BEB'):
            bayes = 'BEB'
        elif self.sites.has_key ('NEB'):
            bayes = 'NEB'
        else:
            bayes = 'SLR'
        self.properties ['histface'] = \
                        face (values = self.sites [bayes]['w'], 
                              lines = lines, col_lines=col_lines,
                              colors=colorize_rst(self.sites [bayes]['pv'],
                                                  self.name,
                                                  self.sites[bayes]['class'],
                                                  col=col),
                              header=header,
                              errors=[] if not self.sites[bayes].has_key ('se')\
                              else self.sites[bayes]['se'],
                              extras=extras, col_width=col_width)
        if up:
            setattr (self.properties ['histface'], 'up', True)
        else:
            setattr (self.properties ['histface'], 'up', False)

            
    def get_ctrl_string(self, outfile=None):
        '''
        generate ctrl string to write to a file, if file is given,
        write it, otherwise returns the string

        :argument None outfile: if a path is given here, write control string into it.

        :returns: the control string
        
        '''
        string = ''
        if self.properties.has_key ('sep'):
            sep = self.properties ['sep']
        else:
            sep = ' = '
        for p in ['seqfile', 'treefile', 'outfile']:
            string += '%15s%s%s\n' % (p, sep, str(self.properties ['params'][p]))
        string += '\n'
        for p in sorted (self.properties ['params'].keys(), cmp=lambda x, y: \
                        cmp(sub('fix_', '', x.lower()),
                            sub ('fix_', '', y.lower()))):
            if p in ['seqfile', 'treefile', 'outfile']:
                continue
            if str(self.properties ['params'][p]).startswith('*'):
                continue
                #string += ' *'+'%13s = %s\n' \
                #          % (p, str(self.properties ['params'][p])[1:])
            else:
                string += '%15s%s%s\n' % (p, sep,
                                          str (self.properties ['params'][p]))
        if outfile == None:
            return string
        else:
            open (outfile, 'w').write (string)

def check_name(model):
    '''
    check that model name corresponds to one of the available
    '''
    if AVAIL.has_key (sub ('\..*', '', model)):
        return model, AVAIL [sub ('\..*', '', model)]

sep = '\n        +----------+-----------------------------+-----------------+\n'
Model.__doc__ = Model.__doc__ % \
                    (sep.join(map (lambda x: \
                                   '        | %-8s | %-27s | %-15s |' % \
                                   ('%s' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']),
                                   sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
                                           cmp(AVAIL[x]['typ'], AVAIL[y]['typ']),
                                           reverse=True))) + sep)
#Model.__doc__ += '\n%s\n' % '\n'.join (map (lambda x: \
#        '           * %-9s model of %-18s at  %-12s level.' % \
#        ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
#        sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
#        cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True)))
