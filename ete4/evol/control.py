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


PARAMS_DESCRIPTION = {
    'CodonFreq'    : '0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table. The equilibrium codon frequencies in codon substitution model. Can be assumed to be equal (1/61 each for the standard genetic code, CodonFreq = 0), calculated from the average nucleotide frequencies (CodonFreq = 1), from the average nucleotide frequencies at the three codon positions (CodonFreq = 2), or used as free parameters (CodonFreq = 3). The number of parameters involved in those models of codon frequencies is 0, 3, 9, and 60 (for the universal code), for CodonFreq = 0, 1, 2, and 3 respectively.',
    'aaDist'       : '0:equal, +:geometric; -:linear, 1-6:G1974,Miyata,c,p,v,a 7:AAClasses. Specifies whether equal amino acid distances are assumed (= 0) or Grantham\'s matrix is used (= 1) (Yang et al. 1998).',
    'alpha'        : 'initial or fixed alpha, 0:infinity (constant rate). For codon models, the pair fix_alpha and alpha specify the model of gamma rates for sites, in which the relative rate for a site varies among codons according to the gamma distribution, but the omega ratio stays the same over all sites.',
    'cleandata'    : '1 means sites involving ambiguity characters (undetermined nucleotides such as N, ?, W, R, Y, etc. anything other than the four nucleotides) or alignment gaps are removed from all sequences. This leads to faster calculation. cleaddata = 0 (default) uses those sites',
    'clock'        : '0:no clock, 1:clock; 2:local clock. Specifies models concerning rate constancy or variation among lineages. clock = 0 means no clock and rates are entirely free to vary from branch to branch. An unrooted tree should be used under this model. clock = 1 means the global clock, and all branches have the same rate. The option clock = 3 is for combined analysis of multiple-gene or multiple-partition data, allowing the branch rates to vary in different ways among the data partitions (Yang and Yoder 2003). Also the variable (= 5 or 6) is used to implement the ad hoc rate smoothing procedure of Yang (2004). For clock = 1 or 2, a rooted tree should be used.',
    'fix_alpha'    : '0: estimate gamma shape parameter; 1: fix it at alpha. For codon models, the pair fix_alpha and alpha specify the model of gamma rates for sites, in which the relative rate for a site varies among codons according to the gamma distribution, but the omega ratio stays the same over all sites.',
    'fix_blength'  : '0: ignore, -1: random, 1: initial, 2: fixed. This tells the program what to do if the tree has branch lengths. Use 0 if you want to ignore the branch lengths. Use -1 if you want the program to start from random starting points. This might be useful if there are multiple local optima. Use 1 if you want to use the branch lengths as initial values for the ML iteration. Use 2 if you want the branch lengths to be fixed at those given in the tree file (rather than estimating them by ML).',
    'fix_kappa'    : '1: kappa fixed, 0: kappa to be estimated. Specifies whether kappa in K80, F84, or HKY85 is given at a fixed value or is to be estimated by iteration from the data. If fix_kappa = 1, the value of another variable, kappa , is the given value, and otherwise the value of kappa is used as the initial estimate for iteration. The variables fix_kappa and kappa have no effect with JC69 or F81 which does not involve such a parameter, or with TN93 and REV which have two and five rate parameters respectively, when all of them are estimated from the data.',
    'fix_omega'    : '1: omega or omega_1 fixed, 0: estimate',
    'getSE'        : '0: don\'t want them, 1: want S.E.s of estimates. Tells whether we want estimates of the standard errors of estimated parameters.',
    'icode'        : 'specifies the genetic code. Eleven genetic code tables are implemented using icode = 0 to 10 corresponding to transl_table 1 to 11 in GenBank. These are 0 for the universal code; 1 for the mammalian mitochondrial code; 3 for mold mt., 4 for invertebrate mt.; 5 for ciliate nuclear code; 6 for echinoderm mt.; 7 for euplotid mt.; 8 for alternative yeast nuclear; 9 for ascidian mt.; and 10 for blepharisma nuclear. There is also an additional code, called Yang\'s regularized code, specified by icode = 11.',
    'kappa'        : '0: estimate gamma shape parameter; 1: fix it at alpha. Initial or fixed kappa',
    'Malpha'       : 'different alphas for genes. Specifies whether one gamma distribution will be applied across all sites (Malpha = 0) or a different gamma distribution is used for each gene (or codon position).',
    'method'       : '0: simultaneous; 1: one branch at a time. This variable controls the iteration algorithm for estimating branch lengths under a model of no clock. method = 0 implements the old algorithm in PAML, which updates all parameters including branch lengths simultaneously. method = 1 specifies an algorithm newly implemented in PAML, which updates branch lengths one by one. method = 1 does not work under the clock models (clock = 1, 2, 3).',
    'Mgene'        : '0:rates, 1:separate. In combination with option G in the sequence data file, specifies partition models (Yang and Swanson 2002)',
    'model'        : 'specifies the branch models (Yang 1998; Yang and Nielsen 1998). model = 0 means one omega ratio for all branches; 1 means one ratio for each branch (the free-ratio model); and 2 means an arbitrary number of ratios (such as the 2-ratios or 3-ratios models). When model = 2, you have to group branches on the tree into branch groups using the symbols # or $ in the tree. With model = 2, the variable fix_omega fixes the last omega ratio ( omega(k-1) if you have k ratios in total) at the value of omega specified in the file.',
    'ncatG'        : 'is then the number of categories for the discrete-gamma model ( baseml ). Values such as 5, 4, 8, or 10 are reasonable. Note that the discrete gamma model has one parameter (alpha), like the continuous gamma model, and the number of categories is not a parameter.',
    'ndata'        : 'specifies the number of separate data sets in the file.',
    'noisy'        : '0,1,2,3,9: how much rubbish on the screen.',
    'NSsites'      : '0:one w; 1:neutral; 2:selection; 3:discrete; 4:freqs; 5:gamma; 6:2gamma; 7:beta; 8:beta&w; 9:beta&gamma; 10:beta&gamma+1; 11:beta&normal>1; 12:0&2normal>1; 13:3normal>0. Specifies the site models, with NSsites = m corresponds to model Mm in Yang et al. (2000b). The variable ncatG is used to specify the number of categories in the omega distribution under some models. In Yang et al. (2000b), this is 3 for M3 (discrete), 5 for M4 (freq), 10 for the continuous distributions (M5: gamma, M6: 2gamma, M7: beta, M8:beta&w, M9:beta&gamma, M10: beta&gamma+1, M11:beta&normal>1, and M12:0&2normal>1, M13:3normal>0).',
    'omega'        : 'initial or fixed omega, for codons or codon-based AAs',
    'outfile'      : 'specifies the names of the sequence data file, main result file, and the tree structure file, respectively. You should not have spaces inside a file name. In general try to avoid special characters in a file name as they might have special meanings under the OS.',
    'RateAncestor' : 'Usually use 0. The value 1 forces the program to do two additional analyses, which you can ignore if you don\'t need the results. First under a model of variable rates across sites such as the gamma, RateAncestor = 1 forces the program to calculate rates for individual sites along the sequence (output in the file rates ), using the empirical Bayes procedure (Yang and Wang 1995).',
    'runmode'      : '0: user tree; 1: semi-automatic; 2: automatic 3: StepwiseAddition; (4,5):PerturbationNNI; -2: pairwise.',
    'seqfile'      : 'specifies the names of the sequence data file, main result file, and the tree structure file, respectively. You should not have spaces inside a file name. In general try to avoid special characters in a file name as they might have special meanings under the OS.',
    'seqtype'      : '1:codons; 2:AAs; 3:codons-->AAs',
    'Small_Diff'   : 'is a small value used in the difference approximation of derivatives. Use a value between 1e-8 and 1e-5 and check that the results are not sensitive to the value used.',
    'treefile'     : 'specifies the names of the sequence data file, main result file, and the tree structure file, respectively. You should not have spaces inside a file name. In general try to avoid special characters in a file name as they might have special meanings under the OS.',
    'verbose'      : '1: detailed output, 0: concise output',
    }

AVAIL = {
    'XX'    :  {'typ': 'Unknown'       , 'evol': 'User defined',
                'exec': 'codeml',
                'allow_mark': True,
                'changes': []},
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
                'changes': [(x[0], '*') for x in [x for x in list(PARAMS.items()) if 'file' not in x[0]]] + \
                [('positive_only', '0')]}
    }

