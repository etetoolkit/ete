#!/usr/bin/python
"""
ugly parsers for outfiles of codeml, rst file for sites,
and main outfile
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

import sys, re
from warnings import warn

def parse_rst (path):
    '''
    parse rst files from codeml, all site, branch-site models.
    return 2 dicts "classes" of sites, and values at each site "sites"
    '''
    typ     = None
    classes = {}
    sites   = {}
    k       = 0
    i       = 0
    path = '/'.join (path.split('/')[:-1]) + '/rst'
    for line in open (path):
        # get number of classes of sites
        if line.startswith ('dN/dS '):
            k = int (re.sub ('.* \(K=([0-9]+)\)\n', '\\1', line))
            continue
        # get values of omega and proportions
        if typ is None and \
           re.match ('^[a-z]+.*(\d+\.\d{5} *){'+ str(k) +'}', line):
            var = re.sub (':', '', line.split('  ')[0])
            if var.startswith ('p'):
                var = 'proportions'
            classes [var] = re.findall ('\d+\.\d{5}', line)
            continue
        # parse NEB and BEB tables
        if '(BEB)' in line :
            k = int (re.sub ('.*for (\d+) classes .*\n', '\\1', line))
            typ = 'BEB'
            sites [typ] = {}
            continue
        if '(NEB)' in line :
            typ = 'NEB'
            sites [typ] = {}
            continue
        # at the end of some BEB/NEB tables:
        if line.startswith ('Positively '):
            typ = None
        # continue if we are not in table
        if not re.match ('^ *[0-9]+ [A-Z*] ', line) or typ == None:
            continue
        # line to list
        line = re.sub ('[()+-]', '', line.strip ()).split ()
        # get amino-acid
        sites [typ].setdefault ('aa', []).append (line[1])
        # get site class probability
        probs = []
        for i in xrange (k):
            probs.append (float (line[2+i]))
            sites [typ].setdefault ('p'+str(i), []).append (float (line[2+i]))
        sites [typ].setdefault ('pv', []).append (max (probs))
        # get most likely site class
        sites [typ].setdefault ('class', []).append (int (line [3 + i]))
        # if there, get omega and error
        try:
            sites [typ].setdefault ('w' , []).append (float (line [4 + i]))
        except IndexError:
            del (sites [typ]['w'])
        try:
            sites [typ].setdefault ('se', []).append (float (line [5 + i]))
        except IndexError:
            del (sites [typ]['se'])

    return {'classes': classes,
            'sites' :sites}


def divide_data (pamout, model):
    '''
    for multiple dataset, divide outfile.
    '''
    for num in range (1, int (model.properties['params']['ndata'])):
        model.name = model.name + '_' + str(num)
        out = open (pamout + '_' + str(num), 'w')
        copy = False
        for line in open (pamout):
            if copy == False and \
                   line.startswith('Data set '+ str (num) + '\n'):
                copy = True
                continue
            if copy == True and \
                   line.startswith('Data set '+ str (num+1) + '\n'):
                break
            if copy == True:
                out.write(line)
        out.close()
        if copy == False:
            warn ('WARNING: seems that you have no multiple dataset here...'\
                  + '\n    trying as with only one dataset')
        if model.typ == 'site':
            rst = '/'.join (pamout.split('/')[:-1])+'/rst'
            rstout = open (rst + '_' + str(num), 'w')
            copy = False
            for line in open(rst):
                if copy == False and \
                       re.match('\t' + str (num)+'\n', line) != None:
                    copy = True
                    continue
                if copy == True and \
                       re.match('\t' + str (num + 1)+'\n', line) != None:
                    copy = False
                if copy == True:
                    rstout.write(line)
            rstout.close()
            setattr (model, 'data_' + str (num), 
                     parse_paml (pamout + '_' + str(num), model))
        else:
            setattr (model, 'data_' + str (num),
                     parse_paml (pamout + '_' + str(num), model))


def get_ancestor (pamout, model):
    '''
    only for fb_ancestor model, retrieves ancestral sequences also
    from rst file.
    '''
    for line in open ('/'.join (pamout.split('/')[:-1])+'/rst'):
        if line.startswith ('node #'):
            pamlid, seq = re.sub ('node#([0-9]+)([A-Z]*)\n', '\\1\t\\2',
                                  re.sub (' ', '', line)).split ('\t')
            n = model._tree.get_descendant_by_pamlid (int (pamlid))
            n.add_feature ('nt_sequence', seq)
        elif line.startswith ('Node #'):
            pamlid, seq = re.sub ('Node#([0-9]+)([A-Z]*)\n', '\\1\t\\2',
                                  re.sub (' ', '', line)).split ('\t')
            n = model._tree.get_descendant_by_pamlid (int (pamlid))
            n.add_feature ('sequence', seq)
        elif line.startswith ('Counts of changes at sites'):
            break

def parse_paml (pamout, model):
    '''
    parser function for codeml files,
    with values of w,dN,dS etc... dependending of the model
    tested.
    '''
    # if multiple dataset in same file we divide the outfile and model.name+x
    if not '*' in str (model.properties['params']['ndata']):
        divide_data (pamout, model)
        return
    # starts parsing
    passe = True
    for line in open (pamout):
        if line is '\n':
            continue
        if line.startswith('Codon frequencies under model'):
            model.stats ['codonFreq'] = []
            passe = False
            continue
        if passe:
            continue
        ######################
        # start serious staff
        # codon frequency
        line = line.rstrip()
        if line.startswith ('  0.'):
            line = map (float, re.findall ('\d\.\d+', line))
            model.stats ['codonFreq'] += [line]
            continue
        # lnL and number of parameters
        if line.startswith ('lnL'):
            line = re.sub ('.* np: *(\d+)\): +(-\d+\.\d+).*',
                           '\\1 \\2', line)
            model.stats ['np' ] = int   (line.split()[0])
            model.stats ['lnL'] = float (line.split()[1])
            continue
        # get labels of internal branches
        if line.count('..') >= 2:
            labels = re.findall ('\d+\.\.\d+', line + ' ')
            _get_paml_labels (model._tree, labels, pamout)
            continue
        # retrieve kappa
        if line.startswith ('kappa '):
            model.stats ['kappa'] = float (re.sub ('.*(\d+\.\d+).*',
                                                   '\\1', line))
        # retrieve dS dN t w N S and if present, errors. from summary table
        if line.count('..') == 1 and line.startswith (' '):
            if not re.match (' +\d+\.\.\d+ +\d\.\d+ ', line):
                continue
            _get_values (model, line)
            continue

def _get_values(model, line):
    '''
    just to ligther main parser
    '''
    vals = line.split()
    # store values under paml_id
    paml_id = int (vals[0].split('..')[1])
    model.branches [paml_id] = {
        'bL'  : float (vals [1]),
        'N'   : float (vals [2]),
        'S'   : float (vals [3]),
        'w'   : float (vals [4]),
        'dN'  : float (vals [5]),
        'dS'  : float (vals [6]),
        'SEdN': float (vals[vals.index ('dN') + 4]) if 'dN' in line else None,
        'SEdS': float (vals[vals.index ('dS') + 4]) if 'dS' in line else None
        }

def _get_paml_labels (tree, paml_labels, pamout):
    '''
     * check paml labels
    '''
    try:
        relations = sorted (map (lambda x: map( int, x.split('..')),
                                 paml_labels),
                            key=lambda x: x[1])
    except IndexError:
        return
    # check that labelling corresponds with paml...
    for rel in relations:
        try:
            node = tree.search_nodes(paml_id=rel[1])[0]
            if int (node.up.paml_id) != int (rel[0]):
                #warn ('WARNING: labelling does not correspond!!\n' + \
                #      '         Getting them from ' + pamout)
                get_labels_from_paml(tree, relations, pamout)
                break
        except IndexError:
            #warn ('ERROR: labelling does not correspond!!\n' + \
            #      '       Getting them from ' + pamout)
            get_labels_from_paml(tree, relations, pamout)

def get_labels_from_paml (tree, relations, pamout):
    '''
    in case problem in labelling... and of course it is not my fault...
    retrieve paml_ids from outfile... from relations line.
    '''
    for line in open (pamout, 'r').readlines():
        # label leaves
        if re.search ('^#[0-9][0-9]*:', line):
            nam, paml_id = re.sub ('#([0-9]+): (.*)', '\\2 \\1',
                                   line.strip()).split()
            tree.search_nodes (name=nam)[0].add_feature ('paml_id',
                                                         int (paml_id))
        if line.startswith ('Sums of codon'):
            break
    tree.add_feature ('paml_id', int (len (tree) + 1))
    for n in tree.traverse(strategy='postorder'):
        if n.is_root():
            continue
        n.up.paml_id = filter (lambda x: x[1]==n.paml_id, relations)[0][0]

