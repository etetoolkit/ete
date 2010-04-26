#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2009/08/14 13:56:44
#
# This script 

import sys,os,re
from ete2 import PhyloTree, Tree
from hashlib import md5

def controlGenerator(model, inTree, inAlg, out, gappy=False):
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

def markTree(intree,ID,model):
    ID = map(int, str (ID).split('_'))
    namy = ''
    t = Tree(intree)
    label_tree(t)
    if 'neut' in model:
        c = len (t.get_leaves())-1
        for n in t.iter_descendants():
            if n.idname in ID:
                n.name = n.name + ' #'+str (len (t.get_leaves())-1)
            else:
                c -= 1
                n.name = n.name + ' #'+str(c)
    else:
        for n in t.iter_descendants():
            if n.idname in ID:
                n.name = n.name+' #'+str(1)
    return re.sub('NoName','',t.write(format=8))

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


def setMarks(t,model,node):
    try:
        treeString = ''.join(\
        re.search(\
        '(.*)\[&&NHX:mark=(#[0-9]*)\](.*)',\
        t.write(features=['mark'],format=9)).groups())
    except AttributeError:
        treeString = t.write(features=['mark'],format=9)
    return treeString


