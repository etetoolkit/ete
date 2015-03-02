# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
#!/usr/bin/python
"""
Parameters for running codeml
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


PARAMS = {
    'seqfile'      : 'algn',
    'treefile'     : 'tree',
    'outfile'      : 'out',
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
    'ndata'        : '*10',
    'fix_omega'    : 0,
    'omega'        : 0.7,
    'fix_alpha'    : 1,
    'alpha'        : 0.,  # if 0 -> infinity
    'Malpha'       : 0,
    'ncatG'        : 8,
    'getSE'        : 0,
    'RateAncestor' : 0,
    'fix_blength'  : 0,
    'Small_Diff'   : '1e-6',
    'cleandata'    : 0,
    'method'       : 0
    }

AVAIL = {
    'M0'    :  {'typ': 'null'       , 'evol': 'negative-selection',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 0),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M1'    :  {'typ': 'site'       , 'evol': 'relaxation',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 1),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M2'    :  {'typ': 'site'       , 'evol': 'positive-selection',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 2),
                            ('omega'       , 1.7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M3'    :  {'typ': 'site'       , 'evol': 'discrete',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 3),
                            ('omega'       , .7),
                            ('ncatG'       , 3),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M4'    :  {'typ': 'site'       , 'evol': 'frequencies',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 4),
                            ('omega'       , .7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M5'    :  {'typ': 'site'       , 'evol': 'gamma',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 5),
                            ('omega'       , .7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M6'    :  {'typ': 'site'       , 'evol': '2 gamma',
                'exec': 'codeml',
                'allow_mark': False,
                'changes': [('NSsites'     , 5),
                            ('omega'       , .7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M7'    :  {'typ': 'site'       , 'evol': 'relaxation',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M8a'   :  {'typ': 'site'       , 'evol': 'relaxation',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 8),
                            ('fix_omega'   , 1),
                            ('omega'       , 1),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M8'    :  {'typ': 'site'       , 'evol': 'positive-selection',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 8),
                            ('omega'       , 1.7),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M9'    :  {'typ': 'site'       , 'evol': 'beta and gamma',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 9),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M10'   :  {'typ': 'site'       , 'evol': 'beta and gamma + 1',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 10),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M11'   :  {'typ': 'site'       , 'evol': 'beta and normal > 1',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 11),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M12'   :  {'typ': 'site'       , 'evol': '0 and 2 normal > 2',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 12),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'M13'   :  {'typ': 'site'       , 'evol': '3 normal > 0',
                'exec': 'codeml',
                'allow_mark': False, 
                'changes': [('NSsites'     , 13),
                            ('alpha'       , '*'),
                            ('method'      , '*'),
                            ('Malpha'      , '*'),
                            ('fix_alpha'   , '*')]},
    'fb'    :  {'typ': 'branch'     , 'evol': 'free-ratios',
                'exec': 'codeml',
                'allow_mark': False , 
                'changes': [('model'       , 1),
                            ('NSsites'     , 0)]},
    'fb_anc':  {'typ': 'branch_ancestor'   , 'evol': 'free-ratios',
                'exec': 'codeml',
                'allow_mark': False , 
                'changes': [('model'       , 1),
                            ('RateAncestor', 1),
                            ('NSsites'     , 0)]},
    'b_free':  {'typ': 'branch'     , 'evol': 'positive-selection',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 0)]},
    'b_neut':  {'typ': 'branch'     , 'evol': 'relaxation',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 0),
                            ('fix_omega'   , 1),
                            ('omega'       , 1)]},
    'bsA1'  :  {'typ': 'branch-site', 'evol': 'relaxation',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 2),
                            ('fix_omega'   , 1),
                            ('omega'       , 1),
                            ('ncatG'       , '*')]},
    'bsA'   :  {'typ': 'branch-site', 'evol': 'positive-selection',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 2),
                            ('omega'       , 1.7),
                            ('ncatG'       , '*')]},
    'bsB'   :  {'typ': 'branch-site', 'evol': 'positive-selection',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 2),
                            ('NSsites'     , 3),
                            ('omega'       , 1.7),
                            ('ncatG'       , '*')]},
    'bsC'   :  {'typ': 'branch-site', 'evol': 'different-ratios',
                'exec': 'codeml',
                'allow_mark': True , 
                'changes': [('model'       , 3),
                            ('NSsites'     , 2),
                            ('ncatG'       , 3)]},
    'bsD'   :  {'typ': 'branch-site', 'evol': 'different-ratios',
                'exec': 'codeml',
                'allow_mark': True ,
                'changes': [('model'       , 3),
                            ('NSsites'     , 3),
                            ('ncatG'       , 3)]},
    'SLR'   :  {'typ' : 'site', 'evol': 'positive/negative selection',
                'exec': 'Slr',
                'sep' : '= ',
                'allow_mark': False ,
                'changes': map (lambda x: (x[0], '*'),
                                filter (lambda x: 'file' not in x[0],
                                        PARAMS.items())) + \
                [('positive_only', '0')]}
    }

