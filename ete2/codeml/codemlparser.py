# #START_LICENSE###########################################################
#
# Copyright (C) 2010 by Francois-Jose Serra. All rights reserved.
# email: francois@barrabin.org
#
# you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################

import sys, re
from os.path import isfile

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')

def get_sites(path, model = ''):
    '''
    for models M1, M2, M7, M8, M8a but also branch-site models
    '''
    check   = 0
    vals    = False
    valsend = False
    psel    = False
    lnl     = ''
    if not isfile(path):
        print >> sys.stderr, \
              "Error: no rst file found at " + path
        return None
    for line in open(path, 'r'):
        l = line.strip()
        if l.startswith('lnL = '):
            lnl = l.split()[-1]
            if not (vals == False or vals == True):
                vals['lnL.'+model] = lnl
        if l.startswith('dN/dS '):
            check = re.sub('.*K=', '', l)
            check = int (re.sub('\)', '', check))
            if model == '':
                model = (('M'+str(check-1) if check < 4 else 'M'+str(check-1)))
        expr = 'Naive' if re.sub ('\..*', '', model) in \
               ['M1', 'M7', 'bsD', 'bsA1'] else 'Bayes'
        if l.startswith(expr+' Empirical Bayes'):
            vals = True
        elif vals == False:
            continue
        if l.startswith('Positively '):
            break
        if re.match('^ *[0-9]* [A-Z*] *', l) == None and \
               valsend == False:
            continue
        psel = re.match('^ *[0-9]* [A-Z*] *', l) == None
        valsend = True
        if vals == True:
            vals = {'aa.'+model:[], 'w.'+model:[],  'class.'+model:[],
                    'pv.'+model:[], 'se.'+model:[], 'lnL.'  +model:lnl}
        if psel == False:
            vals['aa.'+model].append(l.split()[1])
            if not 'bs' in model:
                vals['w.' +model].append(re.sub('\+.*', '', l).split()[-1])
            if model == 'M1'or model == 'M7':
                vals['se.'+model].append('')
            elif model == 'M2'or model == 'M8' or model == 'M8a':
                vals['se.'+model].append(l.split()[-1])
            classes = map (float, re.sub('\(.*', '', l).split()[2:])
            vals['class.'+model].append(\
                '('+\
                re.sub('\).*', '', re.sub('.*\( *', '', l.strip()))\
                +'/'+str (len (classes))+')')
            vals['pv.'+model].append(str (max (classes)))
    if vals == True:
        print >> sys.stderr, \
              'WARNING: rst file path not specified, site model will not' + \
              '\n         be linked to site information.'
        return None
    return vals


def parse_paml(pamout, model, rst='rst', codon_freq=True):
    '''
    parser function for codeml files,
    with values of w,dN,dS etc... dependending of the model
    tested.
    '''
    if not '*' in model.params['ndata']:
        for num in range (1, int (model.params['ndata'])):
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
                print >> sys.stderr, \
                      'WARNING: seems that you have no multiple dataset here...'\
                      + '\n    trying as with only one dataset'
            if model.typ == 'site' and rst != None:
                rst = rst if rst != 'rst' else re.sub('out$', 'rst', pamout)
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
                            parse_paml (pamout + '_' + str(num), \
                                        model, rst=rst + '_' + str (num)))
            else:
                setattr (model, 'data_'+str (num),
                                parse_paml (pamout + '_' + str(num), model))
        return
    # STARTS here. ugly but.... ugly
    dN, dS = None, None
    chk = False
    labels = []
    if model.typ == 'site' and rst != None:
        if rst == 'rst':
            rst = re.sub('out$', 'rst', pamout)
        model.rst = rst
    for line in open(pamout):
        line = line.strip()
        if line.startswith('lnL'):
            model.lnL = float (re.sub('  *.*', '', re.sub('.*: *'  , '', line)))
            model.np  = int   (re.sub('\).*' , '', re.sub('.*np: *', '', line)))
        elif hasattr (model, 'lnL') and labels == []:
            if re.search ('  *([0-9]+\.\.[0-9]+  *){2}', line):
                labels = line.split()
        elif labels != [] and not hasattr (model, 'kappa'):
            _get_paml_labels (model, model.tree, labels, line)
            model.kappa = line.split()[len (labels)]
        elif line.startswith ('dS tree:'):
            dS, dN = True, True
        elif dS == True and line.startswith('(') and line.endswith(');'):
            paml_ids = re.sub ('[A-Za-z_:\(\),\-;]*', '', re.sub (
                '\[&&NHX:paml_id=([0-9]+)\]', ' \\1',
                model.tree.write(features=['paml_id'], format=9))).split()
            dS = re.sub ('[A-Za-z_:\(\),\-;]*', '', line).split()
        elif dN == True and line.startswith('(') and line.endswith(');'):
            dN = re.sub ('[A-Za-z_:\(\),\-;]*', '', line).split()
            for i in xrange (len (paml_ids)-1):
                node = model.tree.search_nodes(paml_id=int (paml_ids[i]))[0]
                node.add_feature ('dN', dN[i])
                node.add_feature ('dS', dS[i])
        elif line.startswith('dN & dS for'):
            chk = True
        elif '..' in line and chk:
            vals = line.split()
            node = model.tree.search_nodes (
                paml_id=int (vals[0].split('..')[1]))[0]
            node.SEdN = vals[13] if 'dN' in line else None
            node.SEdS = vals[18] if 'dS' in line else None
            if not hasattr (model.tree, 'N') and not filter(
                lambda x: not hasattr(x, 'SEdN'), model.tree.get_descendants()):
                model.tree.N = vals[2]
                model.tree.S = vals[3]
                chk = False
        elif not hasattr (model.tree, 'codonFreq'):
            if line.startswith('Codon frequencies under model'):
                model.tree.codonFreq = []
                continue
            if line.startswith('  0.'):
                line = re.sub('  ([0-9.]*)  ([0-9.]*)  ([0-9.]*)  ([0-9.]*)', \
                              '\\1 \\2 \\3 \\4', line)
                model.tree.codonFreq += [line.split()]
        if model.typ == 'site' or model.typ == 'null':
            if 'p=' in line and 'q=' in line: # only for M7 and M8
                model.p, model.q = re.sub(\
                    '.*p=  *([0-9]+\.[0-9]+)  *q=  *([0-9]+\.[0-9]+)'\
                    , '\\1 \\2', line).split()
            if line.startswith('omega (dN'): # than we are in M0....
                model.p0 = '1.0'
                line = re.sub('^omega \(dN/dS\) = ', 'w: ', line)
            if line.startswith('p: '):
                for i in range (0, len (line.split()[1:])):
                    setattr (model, 'p'+str(i), line.split()[i+1])
            elif line.startswith('w: '):
                while re.match('.*[0-9][0-9]*\.[0-9]{5}[0-9].*', line)!=None:
                    line = re.sub('([0-9][0-9]*\.[0-9]{5})([0-9].*)', \
                                  '\\1 \\2', line)
                for i in range (0, len (line.split()[1:])):
                    setattr (model, 'w'+str(i), line.split()[i+1])
        if model.typ == 'branch-site':
            if line.startswith ('site class'):
                vals = line.split()[2:]
            elif line.startswith ('proportion '):
                for n, v in enumerate (vals):
                    setattr (model, 'p' + v, line.split() [n+1])
            elif line.startswith('background w '):
                for n, v in enumerate (vals):
                    setattr (model, 'wbkg' + v, line.split() [n+1])
            elif line.startswith('foreground w'):
                for n, v in enumerate (vals):
                    setattr (model, 'wfrg' + v, line.split() [n+1])

def _get_paml_labels(model, tree, paml_labels, line):
    '''
    map tree to paml labels, and place w and bL values
    '''
    bL = line.split()[:len (paml_labels)]
    w  = line.split()[len (paml_labels)+1:]
    try:
        relations = sorted (map (lambda x: map( int, x.split('..')),
                                 paml_labels),
                            key=lambda x: x[1])
    except IndexError:
        return
    # optional just to check that labelling corresponds with paml...
    for rel in relations:
        node = tree.search_nodes(paml_id=rel[1])[0]
        if int (node.up.paml_id) != int (rel[0]):
            print node
            print node.up
            print node.up.paml_id, rel
            sys.exit('labelling does not correspond!! check')
    #####
    for lab in paml_labels:
        node = tree.search_nodes(paml_id=int (lab.split('..')[1]))[0]
        if model.typ == 'branch':
            node.add_feature ('w', w.pop(0))
        node.add_feature ('bL', bL.pop(0))

