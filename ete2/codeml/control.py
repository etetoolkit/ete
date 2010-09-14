#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44

from re import sub

def controlGenerator(model, inTree='tree', inAlg='algn', \
                     out='out', gappy=True, omega=0.7, ndata=1):
    '''
    "omega" stands for starting value of omega, in the computation. Qs
    Zihen Yang says, it is good to try with different starting values.
    '''
    model = model.split('.')[0]
    params = {'seqfile'      : inAlg,
              'treefile'     : inTree,
              'outfile'      : out,
              'noisy'        : 0,
              'verbose'      : 2,
              'runmode'      : 0,
              'seqtype'      : 1,
              'CodonFreq'    : 2,
              'clock'        : 0,
              'aaDist'       : 0,
              'model'        : 0,
              'NSsites'      : 2,
              'icode'        : 0,
              'Mgene'        : 0,
              'fix_kappa'    : 0,
              'kappa'        : 2,
              'ndata'        : '*10' if ndata==1 else ndata,
              'fix_omega'    : 0,
              'omega'        : omega,
              'fix_alpha'    : 1,
              'alpha'        : 0.,  # if 0 -> infinity
              'Malpha'       : 0,
              'ncatG'        : 8,
              'getSE'        : 0,
              'RateAncestor' : 0,
              'fix_blength'  : 0,
              'Small_Diff'   : '1e-6',
              'cleandata'    : int (not gappy),
              'method'       : 0}
    if model.startswith('fb'):
        params['model']       = 1
        params['NSsites']     = 0
    elif model.startswith('M0'):
        params['NSsites']     = 0
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M1'):
        params['NSsites']     = 1
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M2'):
        params['NSsites']     = 2
        params['omega']       = omega + 1
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M3'):
        params['NSsites']     = 3
        params['omega']       = omega
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M7'):
        params['NSsites']     = 7
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M8a'):
        params['NSsites']     = 8
        params['fix_omega']   = 1
        params['omega']       = 1
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('M8'):
        params['NSsites']     = 8
        params['omega']       = omega + 1
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model.startswith('bsA1'):
        params['model']       = 2
        params['NSsites']     = 2
        params['fix_omega']   = 1
        params['omega']       = 1
        del(params['ncatG'])
    elif model.startswith('bsA'):
        params['model']       = 2
        params['NSsites']     = 2
        params['omega']       = omega + 1
        del(params['ncatG'])
    elif model.startswith('bsB'):
        params['model']       = 2
        params['NSsites']     = 3
        params['omega']       = omega + 1
        del(params['ncatG'])
    elif model.startswith('bsC'):
        params['model']       = 3
        params['NSsites']     = 2
        del(params['ncatG'])
    elif model.startswith('bsD'):
        params['model']       = 3
        params['NSsites']     = 3
        params['ncatG']       = 2
    elif model.startswith('b_free'):
        params['model']       = 2
        params['NSsites']     = 0
    elif model.startswith('b_neut'):
        params['model']       = 2
        params['NSsites']     = 0
        params['fix_omega']   = 1
        params['omega']       = 1
    String = ''
    for p in ['seqfile', 'treefile', 'outfile']:
        String += '%15s = %s\n' % (p ,str(params[p]))
        del(params[p])
    String += '\n'
    for p in sorted(params.keys(), cmp=lambda x,y: \
                    cmp(sub('fix_', '', x.lower()), \
                        sub ('fix_', '', y.lower()))):
        if str(params[p]).startswith('*'):
            String += ' *'+'%13s = %s\n' % (p ,str(params[p])[1:])
        else:
            String += '%15s = %s\n' %(p ,str(params[p]))
    return String
