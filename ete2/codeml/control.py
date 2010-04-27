#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44
#
# This script 

import re, os
from ete2 import Tree
from hashlib import md5
import errno

def controlGenerator(model, inTree='tree', inAlg='algn', out='out', gappy=False):
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

def translate(sequence):
    '''
    little function to translate DNA to protein...
    from: http://python.genedrift.org/
    #TODO: place it in seqgroup functions?
    '''
    #dictionary with the genetic code
    gencode = {
    'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
    'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
    'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L', 
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
    'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
    'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
    'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
    'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
    'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
    'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
    'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
    '---':'-'
    }
    proteinseq = ''
    #loop to read DNA sequence in codons, 3 nucleotides at a time
    for n in range(0,len(sequence),3):
        #checking to see if the dictionary has the key
        if gencode.has_key(sequence[n:n+3]) == True:
            proteinseq += gencode[sequence[n:n+3]]
        else:
            proteinseq += 'X'
    #return protein sequence
    return proteinseq


def label_tree(t):
    """ This function sort the branches of a given tree by
    considerening node names. After the tree is sorted, nodes are
    labeled using ascendent numbers.  This can be used to ensure that
    nodes in a tree with the same node names are always labeled in
    the same way.  Note that if duplicated names are present, extra
    criteria should be added to sort nodes.
    """
    key2node = {}
    for n in t.traverse(strategy="postorder"):
        if n.is_leaf():
            key = md5(str(n.name)).hexdigest()
            n.__idname=key
        else:
            key = md5(str(sorted([c.__idname for c in n.children]))).hexdigest()
            n.__idname=key
            children = [[c.__idname, c] for c in n.children]
            children.sort() # sort list by idname
            n.children = [item[1] for item in children]
        counter = 1
    for n in t.traverse(strategy="postorder"):
        n.add_features(idname=counter)
        counter += 1

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise
