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
from ete_dev.treeview.faces import SequencePlotFace

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
        marks = {}
        rootid = self._tree.paml_id
        if self._tree:
            has_mark = any([n.mark for n in self._tree.iter_descendants()])
            is_branch = True if self.branches else False
            if is_branch and has_mark:
                for m in set([n.mark for n in self._tree.iter_descendants()]):
                    marks[m if m else ' #0'] = [n.paml_id for n in \
                                                self._tree.search_nodes(mark=m) \
                                                if not n.paml_id == rootid]
            elif is_branch:
                for b in self.branches:
                    marks[' #'+str(b)] = [b]
        str_mark = ''
        str_line = '\n           mark:%-5s, omega: %-10s, nodes paml_ids: %s'
        for m in marks:
            nids = ' '.join([str(i) for i in marks[m]])
            str_mark +=  str_line % (m, self.branches[marks[m][0]]['w'], nids)
        str_site = ''
        str_line = '\n           %-12s: %s '
        if self.classes:
            for t in [t for t in self.classes]:
                str_site += str_line % (t, ' '.join(['%s%s=%-9s' % (t[0], j, i)\
                                                     for j, i in \
                                                     enumerate(self.classes[t])]))
        return ''' Evolutionary Model %s:
        log likelihood       : %s
        number of parameters : %s
        sites inference      : %s
        sites classes        : %s
        branches             : %s
        ''' % (self.name,
               self.lnL if 'lnL' in self.stats else 'None',
               self.np  if 'np'  in self.stats else 'None',
               ', '.join(self.sites.keys())  if self.sites else 'None',
               str_site if self.classes else 'None',
               str_mark if self.branches else 'None'
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
        
    def set_histface (self, up=True, hlines=[1.0,0.3], kind='bar',
                      errors=False, colors=None, **kwargs):
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
        if self.sites == None:
            warn ("WARNING: model %s not computed." % (self.name))
            return None
        if not 'header' in kwargs:
            kwargs['header'] = 'Omega value for sites under %s model' % (self.name)
        if self.sites.has_key ('BEB'):
            bayes = 'BEB'
        elif self.sites.has_key ('NEB'):
            bayes = 'NEB'
        else:
            bayes = 'SLR'
        colors = colorize_rst(self.sites [bayes]['pv'], self.name,
                              self.sites[bayes]['class'], col=colors)
        if not 'ylim' in kwargs:
            kwargs['ylim'] = (0,2)
        if errors:
            errors=self.sites[bayes]['se'] if self.sites[bayes].has_key ('se') else None
        self.properties ['histface'] = SequencePlotFace(self.sites [bayes]['w'],
                                                        hlines=hlines,
                                                        colors=colors,
                                                        errors=errors,
                                                        ylabel=u'Omega (\u03c9)',
                                                        kind=kind,
                                                        **kwargs)
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



def colorize_rst(vals, winner, classes,col=None):
    '''
    Colorize function, that take in argument a list of values
    corresponding to a list of classes and returns a list of
    colors to paint histogram.
    '''
    col = {'NS' : 'grey',
           'RX' : 'green',
           'RX+': 'green',
           'CN' : 'cyan',
           'CN+': 'blue',
           'PS' : 'orange',
           'PS+': 'red'} if col==None else col
    colors = []
    for i in range (0, len (vals)):
        class1 = classes[i] #int(sub('\/.*', '', sub('\(', '', classes[i])))
        class2 = max (classes)# int(sub('.*\/', '', sub('\)', '', classes[i])))
        pval = float (vals[i])
        if pval < 0.95:
            colors.append(col['NS'])
        elif (class1 != class2 and class1 != 1) \
                 and (winner == 'M2' or winner == 'M8' or winner == 'SLR'):
            if pval < 0.99:
                colors.append(col['RX'])
            else:
                colors.append(col['RX+'])
        elif class1 == 1:
            if pval < 0.99:
                colors.append(col['CN'])
            else:
                colors.append(col['CN+'])
        elif class1 == class2 and (winner == 'M2' or winner == 'M8' or winner == 'SLR'):
            if pval < 0.99:
                colors.append(col['PS'])
            else:
                colors.append(col['PS+'])
        elif class1 == class2:
            if pval < 0.99:
                colors.append(col['RX'])
            else:
                colors.append(col['RX+'])
        else:
            colors.append(col['NS'])
    return colors


        
sep = '\n        +----------+-----------------------------+-----------------+\n'
Model.__doc__ = Model.__doc__ % \
                    (sep.join(map (lambda x: \
                                   '        | %-8s | %-27s | %-15s |' % \
                                   ('%s' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']),
                                   sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
                                           cmp(AVAIL[x]['typ'], AVAIL[y]['typ']),
                                           reverse=True))) + sep)
