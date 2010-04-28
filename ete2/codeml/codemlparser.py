#!/usr/bin/python env
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/20 21:20:31
#
# This script is GPL. que pasa?!!

import sys, re

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')

def get_sites(path):
    '''
    for models M1, M2, M7, M8
    '''
    check   = 0
    vals    = False
    valsend = False
    psel    = False
    lnl     = ''
    mod     = ''
    for line in open(path, 'r'):
        l = line.strip()
        if l.startswith('lnL = '):
            lnl = l.split()[-1]
            if not (vals == False or vals == True):
                vals['lnL.'+mod] = lnl
        if l.startswith('dN/dS '):
            check = re.sub('.*K=', '', l)
            check = int (re.sub('\)', '', check))
            mod = ('M'+str(check-1 if check < 4 else 'M'+str(check-3)))
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
    return vals

def parse_paml(pamout, model, rst=None):
    '''
    parser function for codeml files, returns a diccionary
    with values of w,dN,dS etc... dependending of the model
    tested.
    '''
    dic = {}
    if model.startswith('b_'):
        val = ['w', 'dN', 'dS', 'bL', 'bLnum']
        for line in open(pamout):
            if line.startswith('lnL'):
                dic = _getlnL(dic, line)
            elif line.startswith('(') and line.endswith(');\n'):
                dic[val.pop()] = line.strip()
    elif model.startswith('fb'):
        val = ['w', 'dN', 'dS', 'bL', 'bLnum']
        chk = False
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
    elif model.startswith('M'):
        if rst == None:
            dic['rst'] = re.sub('/out$', '/rst', pamout)
        val = ['w', 'dN', 'dS', 'bL', 'bLnum']
        for line in open(pamout):
            if line.startswith('lnL'):
                dic = _getlnL(dic, line)
            elif line.startswith('(') and line.endswith(');\n'):
                dic[val.pop()] = line.strip()
            elif line.startswith('p: '):
                for i in range (0, len (line.strip().split()[1:])):
                    dic['p'+str(i)] = line.strip().split()[i+1]
            elif line.startswith('w: '):
                for i in range (0, len (line.strip().split()[1:])):
                    dic['w'+str(i)] = line.strip().split()[i+1]
    elif model.startswith('bs'):
        val = ['w', 'dN', 'dS', 'bL', 'bLnum']
        for line in open(pamout):
            if line.startswith('lnL'):
                dic = _getlnL(dic, line)
            elif line.startswith('(') and line.endswith(');\n'):
                dic[val.pop()] = line.strip()
            elif line.startswith('proportion '):
                dic['p0' ] = line.strip().split()[1]
                dic['p1' ] = line.strip().split()[2]
                dic['p2a'] = line.strip().split()[3]
                dic['p2b'] = line.strip().split()[4]
            elif line.startswith('background w '):
                dic['wbkg0']  = line.strip().split()[2]
                dic['wbkg1']  = line.strip().split()[3]
                dic['wbkg2a'] = line.strip().split()[4]
                dic['wbkg2b'] = line.strip().split()[5]
            elif line.startswith('foreground w'):
                dic['wfrg0']  = line.strip().split()[2]
                dic['wfrg1']  = line.strip().split()[3]
                dic['wfrg2a'] = line.strip().split()[4]
                dic['wfrg2b'] = line.strip().split()[5]
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
    dic['lnL'] = re.sub('  *.*', '', re.sub('.*: *'   , '', line))
    dic['lnL'] = re.sub('  *.*', '', re.sub('.*: *'   , '', line))
    dic['np' ] = re.sub('\).*' , '', re.sub('.*np: * ', '', line))
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




