#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44

from re import sub
from sys import stderr
from ete_dev.codeml.control import PARAMS

class Model:
    '''Evolutionnary model, computed by PAML.

    available models are:
    '''
    def __init__(self, model, inTree='tree', inAlg='algn', \
                 out='out', **kwargs):
        '''
        "omega" stands for starting value of omega, in the computation. Qs
        Zihen Yang says, it is good to try with different starting values.
        '''
        self.ctrl_string = ''
        self.evol        = None
        self.changes     = {}
        self.name, args  = check_name(model)
        for a, b in args.items(): self.__dict__[a] = b
        self.params = PARAMS
        self.params['seqfile' ] = inAlg
        self.params['treefile'] = inTree
        self.params['outfile' ] = out
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

    def _change_params(self):
        '''
        change model specific values
        '''
        for key, change in self.changes:
            self.params[key] = change

    def get_ctrl_string(self, outfile=None):
        '''
        generate ctrl string to write to a file, if fil is given,
        write it, otherwise returns the string
        '''
        string = ''
        for p in ['seqfile', 'treefile', 'outfile']:
            string += '%15s = %s\n' % (p ,str(self.params[p]))
        string += '\n'
        for p in sorted(self.params.keys(), cmp=lambda x,y: \
                        cmp(sub('fix_', '', x.lower()), \
                            sub ('fix_', '', y.lower()))):
            if p in ['seqfile', 'treefile', 'outfile']: continue
            if str(self.params[p]).startswith('*'):
                string += ' *'+'%13s = %s\n' % (p ,str(self.params[p])[1:])
            else:
                string += '%15s = %s\n' %(p ,str(self.params[p]))
        if outfile == None:
            return string
        else:
            open (outfile, 'w').write (string)


def check_name(model):
    if AVAIL.has_key (sub('\..*', '', model)):
        return model, AVAIL[sub('\..*', '', model)]


global AVAIL

AVAIL = {
    'M0'    :  {'typ': 'null'       , 'evol': 'negative-selection',
                'allow_mark': False,
                'changes': [('NSsites'     , 0),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M1'    :  {'typ': 'site'       , 'evol': 'relaxation',
                'allow_mark': False,
                'changes': [('NSsites'     , 1),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M2'    :  {'typ': 'site'       , 'evol': 'positive-selection',
                'allow_mark': False,
                'changes': [('NSsites'     , 2),
                            ('omega'       , 1.7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M7'    :  {'typ': 'site'       , 'evol': 'relaxation',
                'allow_mark': False, 
                'changes': [('NSsites'     , 7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M8a'   :  {'typ': 'site'       , 'evol': 'relaxation',
                'allow_mark': False, 
                'changes': [('NSsites'     , 8),
                            ('fix_omega'   , 1),
                            ('omega'       , 1),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M8'    :  {'typ': 'site'       , 'evol': 'positive-selection',
                'allow_mark': False, 
                'changes': [('NSsites'     , 8),
                            ('omega'       , 1.7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'fb'    :  {'typ': 'branch'     , 'evol': 'free-ratios',
                'allow_mark': True , 
                'changes': [('model'       , 1),
                            ('NSsites'     , 0)]},
    'b_free':  {'typ': 'branch'     , 'evol': 'positive-selection',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 0)]},
    'b_neut':  {'typ': 'branch'     , 'evol': 'relaxation',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 0),
                            ('fix_omega'   , 1),
                            ('omega'       , 1)]},
    'bsA1'  :  {'typ': 'branch-site', 'evol': 'relaxation',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 2),
                            ('fix_omega'   , 1),
                            ('omega'       , 1),
                            ('ncatG'       , '*')]},
    'bsA'   :  {'typ': 'branch-site', 'evol': 'positive-selection',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 2),
                            ('omega'       , 1.7),
                            ('ncatG'       , '*')]},
    'bsB'   :  {'typ': 'branch-site', 'evol': 'positive-selection',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 3),
                            ('omega'       , 1.7),
                            ('ncatG'       , '*')]},
    'bsC'   :  {'typ': 'branch-site', 'evol': 'different-ratios',
                'allow_mark': True , 
                'changes': [('model'       , 3),
                            ('NSsites'     , 2),
                            ('ncatG'       , '*')]},
    'bsD'   :  {'typ': 'branch-site', 'evol': 'different-ratios',
                'allow_mark': True , 
                'changes': [('model'       , 3),
                            ('NSsites'     , 3),
                            ('ncatG'       , 2)]}
    }


Model.__doc__ += '\n%s\n' % '\n'.join (map (lambda x: \
        '           * %-9s model of %-18s at  %-12s level.' % \
        ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
        sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
        cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True)))
