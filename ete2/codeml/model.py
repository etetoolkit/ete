#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44

from re import sub
from sys import stderr
from control import PARAMS, AVAIL

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
        self.params = dict (PARAMS.items())
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
            string += '%15s = %s\n' % (p, str(self.params[p]))
        string += '\n'
        for p in sorted (self.params.keys(), cmp=lambda x, y: \
                        cmp(sub('fix_', '', x.lower()), \
                            sub ('fix_', '', y.lower()))):
            if p in ['seqfile', 'treefile', 'outfile']: continue
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
    if AVAIL.has_key (sub('\..*', '', model)):
        return model, AVAIL[sub('\..*', '', model)]

Model.__doc__ += '\n%s\n' % '\n'.join (map (lambda x: \
        '           * %-9s model of %-18s at  %-12s level.' % \
        ('"%s"' % (x), AVAIL[x]['evol'], AVAIL[x]['typ']), \
        sorted (sorted (AVAIL.keys()), cmp=lambda x, y : \
        cmp(AVAIL[x]['typ'], AVAIL[y]['typ']), reverse=True)))
