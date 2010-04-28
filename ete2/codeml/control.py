#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44
#
# This script 


def controlGenerator(model, inTree='tree', inAlg='algn', \
                     out='out', gappy=False):
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
              'fix_omega'    : 0,
              'omega'        : 1.0,
              'fix_alpha'    : 1,
              'alpha'        : 0.,
              'Malpha'       : 0,
              'ncatG'        : 8,
              'getSE'        : 0,
              'RateAncestor' : 0,
              'fix_blength'  : 0,
              'Small_Diff'   : '.5e-6',
              'cleandata'    : int (not gappy),
              'method'       : 0}
    if model == 'fb':
        params['model']       = 1
        params['NSsites']     = 0
        params['omega']       = 0.4
        del(params['fix_blength'])
    elif model == 'M0':
        params['NSsites']     = 0
        params['kappa']       = .3
        params['omega']       = 1.3
        params['ncatG']       = 3
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model == 'M1':
        params['NSsites']     = 1
        params['kappa']       = .3
        params['omega']       = 1.3
        params['ncatG']       = 10
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model == 'M2':
        params['NSsites']     = 2
        params['kappa']       = .3
        params['omega']       = 1.3
        params['ncatG']       = 10
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model == 'M7':
        params['NSsites']     = 7
        params['kappa']       = .3
        params['omega']       = 1.3
        params['ncatG']       = 10
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model == 'M8':
        params['NSsites']     = 8
        params['kappa']       = .3
        params['omega']       = 1.3
        params['ncatG']       = 10
        del(params['alpha'])
        del(params['method'])
        del(params['Malpha'])
        del(params['fix_alpha'])
    elif model == 'bsA':
        params['model']       = 2
        params['NSsites']     = 2
        params['kappa']       = 2
        params['omega']       = 0.7
        del(params['fix_blength'])
    elif model == 'bsA1':
        params['model']       = 2
        params['NSsites']     = 2
        params['kappa']       = 2
        params['fix_omega']   = 1
        params['omega']       = 1.0
        del(params['fix_blength'])
    elif model == 'b_free':
        params['model']       = 2
        params['NSsites']     = 0
        params['kappa']       = 2
        params['omega']       = 0.4
        del(params['fix_blength'])
    elif model == 'b_neut':
        params['model']       = 2
        params['NSsites']     = 0
        params['kappa']       = 2
        params['fix_omega']   = 1
        params['omega']       = 1
        del(params['fix_blength'])
    String = ''
    for p in params.keys():
        String = String + p + ' '*(12-len(p)) + ' = ' + \
                 str(params[p]) + '\n'
    return String
