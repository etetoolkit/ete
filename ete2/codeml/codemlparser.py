#!/usr/bin/python env
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/20 21:20:31
#
# This script is GPL. que pasa?!!

import sys, re
from os.path import isfile

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')

def get_sites(path,ndata=1):
    '''
    for models M1, M2, M7, M8, M8a
    '''
    check   = 0
    vals    = False
    valsend = False
    psel    = False
    lnl     = ''
    mod     = ''
    if not isfile(path):
        print >> sys.stderr, \
              "Error: no rst file found at " + path
        return None
    for line in open(path, 'r'):
        l = line.strip()
        if l.startswith('lnL = '):
            lnl = l.split()[-1]
            if not (vals == False or vals == True):
                vals['lnL.'+mod] = lnl
        if l.startswith('dN/dS '):
            check = re.sub('.*K=', '', l)
            check = int (re.sub('\)', '', check))
            mod = (('M'+str(check-1) if check < 4 else 'M'+str(check-1)))
        expr = 'Naive' if check % 2 == 0 else 'Bayes'
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
            vals = {'aa.'+mod:[], 'w.'+mod:[],  'class.'+mod:[],
                    'pv.'+mod:[], 'se.'+mod:[], 'lnL.'  +mod:lnl}
        if psel == False:
            vals['aa.'+mod].append(l.split()[1])
            vals['w.' +mod].append(re.sub('\+.*', '', l).split()[-1])
            if mod == 'M1'or mod == 'M7':
                vals['se.'+mod].append('')
            else:
                vals['se.'+mod].append(l.split()[-1])
            classes = map (float, re.sub('\(.*', '', l).split()[2:])
            vals['class.'+mod].append(\
                '('+\
                re.sub('\).*', '', re.sub('.*\( *', '', l.strip()))\
                +'/'+str (len (classes))+')')
            vals['pv.'+mod].append(str (max (classes)))
    if vals == True:
        print >> sys.stderr, \
              'WARNING: rst file path not specified, site model will not' + \
              '\n         be linked to site information.'
        return None
    return vals


def parse_paml(pamout, model, rst='rst', ndata=1, codon_freq=True):
    '''
    parser function for codeml files, returns a diccionary
    with values of w,dN,dS etc... dependending of the model
    tested.
    '''
    if ndata != 1:
        dic = {}
        for num in range (1, ndata):
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
                #return parse_paml (pamout, model, rst=rst, ndata=1)
            if model.startswith('M') and model != 'M0' and rst!=None:
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
                dic['data_'+str (num)] = \
                                parse_paml(pamout + '_' + str(num), \
                                           model, rst=rst + '_' + str (num))
            else:
                dic['data_'+str (num)] = \
                                parse_paml(pamout + '_' + str(num), model)
        return dic
    dic = {}
    val = ['w', 'dN', 'dS', 'bL', 'bLnum']
    chk = False
    if model.startswith('M') and model != 'M0' and rst!=None:
        if rst == 'rst':
            rst = re.sub('out$', 'rst', pamout)
        dic['rst'] = rst
    for line in open(pamout):
        if line.startswith('lnL'):
            dic = _getlnL(dic, line)
        elif line.startswith('(') and line.endswith(');\n'):
            dic[val.pop()] = line.strip()
        elif line.startswith('dN & dS for'):
            chk = True
        elif '..' in line and chk:
            chk = False
            dic['N'], dic['S'] = line.strip().split()[2:4]
        elif codon_freq == True:
            if line.startswith('Codon frequencies under model'):
                dic['codonFreq'] = []
                continue
            if line.startswith('  0.'):
                    line = re.sub('  ([0-9.]*)  ([0-9.]*)  ([0-9.]*)  ([0-9.]*)', \
                                  '\\1 \\2 \\3 \\4', line.strip())
                    dic['codonFreq'] += [line.split()]
            elif line.startswith('kappa (ts/tv)'):
                dic['kappa'] = re.sub('kappa .* =  *([0-9.]+)$', \
                                      '\\1', line.strip())
        if model.startswith('M'):
            if int(model[1])>6 and 'p=' in line and 'q=' in line:
                dic['p'], dic['q'] = re.sub(\
                    '.*p=  *([0-9]+\.[0-9]+)  *q=  *([0-9]+\.[0-9]+)'\
                    , '\\1 \\2', line.strip()).split()
            if line.startswith('omega (dN'): # than we are in M0....
                dic['p0'] = '1.0'
                line = re.sub('^omega \(dN/dS\) = ', 'w: ', line)
            if line.startswith('p: '):
                for i in range (0, len (line.strip().split()[1:])):
                    dic['p'+str(i)] = line.strip().split()[i+1]
            elif line.startswith('w: '):
                while re.match('.*[0-9][0-9]*\.[0-9]{5}[0-9].*', line)!=None:
                    line = re.sub('([0-9][0-9]*\.[0-9]{5})([0-9].*)', \
                                  '\\1 \\2', line.strip())
                for i in range (0, len (line.strip().split()[1:])):
                    dic['w'+str(i)] = line.strip().split()[i+1]
        if model.startswith('bs'):
            vals = []
            if line.startswith ('site class'):
                vals = line.strip().split()[1:]
            elif line.startswith ('proportion '):
                for n, val in enumerate (vals):
                    dic['p'    + val] = line.strip().split() [n+1]
            elif line.startswith('background w '):
                for n, val in enumerate (vals):
                    dic['wbkg' + val] = line.strip().split() [n+1]
            elif line.startswith('foreground w'):
                for n, val in enumerate (vals):
                    dic['wfrg' + val] = line.strip().split() [n+1]
    # convert paml tree format to 'normal' newick format.
    for k in ['w', 'dN', 'dS', 'bL', 'bLnum']:
        if not dic.has_key(k):
            continue
        if not dic[k].startswith('('):
            continue
        dic[k] = _convtree(dic[k])
    return dic

def _getlnL(dic, line):
    '''
    shht pylint
    '''
    line = line.strip()
    dic['lnL'] = re.sub('  *.*', '', re.sub('.*: *'  , '', line))
    dic['lnL'] = re.sub('  *.*', '', re.sub('.*: *'  , '', line))
    dic['np' ] = re.sub('\).*' , '', re.sub('.*np: *', '', line))
    return dic
    

def _convtree(line):
    '''
    shhht pylint
    '''
    t = re.sub('#[0-9]* #', ' #', line)
    t = re.sub('\'', '', t)
    t = re.sub('#', ':', t)
    t = re.sub(' : [0-9]*\.[0-9]*', '', t)
    t = re.sub(' *: *', ':', t)
    return t

