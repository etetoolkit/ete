#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/20 21:20:31
#
# This script is GPL. que pasa?!!

import sys,os,re
from ete_dev import Tree

sys.path.append('/home/francisco/franciscotools/4_codeml_pipe/')
from control import label_tree

def main():    
    pamouts = []
    pamouts.append(('/home/francisco/project/patata/dataset/all_1l_2/paml/b_free.6/b_free.6.out','b_free'))
    pamouts.append(('/home/francisco/project/patata/hernan_sol/sol_1l_2/paml/Sol_1_A/A.out','bsA'))
    pamouts.append(('/home/francisco/project/patata/hernan_sol/sol_1l_2/paml/fb/fb.out','fb'))
    pamouts.append(('/home/francisco/project/protamine/dataset/primt-prm1/paml/fb/fb.out','fb'))
    
    for pamout,m in pamouts:
        dic = parsePaml(pamout,m)
        _readTrees(dic)

def parsePaml(pamout,model):
    '''
    parser function for codeml files, returns a diccionary
    with values of w,dN,dS etc... dependending of the model
    tested.
    '''
    dic = {}
    nams = {}
    if model.startswith('b_'):
        val = ['w','dN','dS','bL','bLnum']
        for l in open(pamout):
            if l.startswith('lnL'):
                dic = _getlnL(dic,l)
            elif l.startswith('(') and l.endswith(');\n'):
                dic[val.pop()] = l.strip()
    elif model.startswith('fb'):
        val = ['w','dN','dS','bL','bLnum']
        chk=False
        for l in open(pamout):
            if l.startswith('lnL'):
                dic = _getlnL(dic,l)
            elif l.startswith('(') and l.endswith(');\n'):
                dic[val.pop()] = l.strip()
            elif l.startswith('dN & dS for'): chk = True
            elif '..' in l and chk:
                chk = False
                dic['N'], dic['S'] = l.strip().split()[2:4]
    elif model.startswith('M'):
        val = ['w','dN','dS','bL','bLnum']
        for l in open(pamout):
            if l.startswith('lnL'):
                dic = _getlnL(dic,l)
            elif l.startswith('(') and l.endswith(');\n'):
                dic[val.pop()] = l.strip()
            elif l.startswith('p: '):
                for i in range (0,len (l.strip().split()[1:])):
                    dic['p'+str(i)]=l.strip().split()[i+1]
            elif l.startswith('w: '):
                for i in range (0,len (l.strip().split()[1:])):
                    dic['w'+str(i)]=l.strip().split()[i+1]
    elif model.startswith('bs'):
        val = ['w','dN','dS','bL','bLnum']
        for l in open(pamout):
            if l.startswith('lnL'):
                dic = _getlnL(dic,l)
            elif l.startswith('(') and l.endswith(');\n'):
                dic[val.pop()] = l.strip()
            elif l.startswith('proportion '):
                dic['p0' ] = l.strip().split()[1]
                dic['p1' ] = l.strip().split()[2]
                dic['p2a'] = l.strip().split()[3]
                dic['p2b'] = l.strip().split()[4]
            elif l.startswith('background w '):
                dic['wbkg0']  = l.strip().split()[2]
                dic['wbkg1']  = l.strip().split()[3]
                dic['wbkg2a'] = l.strip().split()[4]
                dic['wbkg2b'] = l.strip().split()[5]
            elif l.startswith('foreground w'):
                dic['wfrg0']  = l.strip().split()[2]
                dic['wfrg1']  = l.strip().split()[3]
                dic['wfrg2a'] = l.strip().split()[4]
                dic['wfrg2b'] = l.strip().split()[5]
    # convert paml tree format to 'normal' newick format.
    for k in ['w','dN','dS','bL','bLnum']:
        if not dic.has_key(k): continue
        if not dic[k].startswith('('): continue
        dic[k] = _convtree(dic[k])
    return dic

def _getlnL(dic,l):
    l = l.strip()
    dic['lnL'] = re.sub('  *.*','', re.sub('.*: *'   ,'', l))
    dic['lnL'] = re.sub('  *.*','', re.sub('.*: *'   ,'', l))
    dic['np' ] = re.sub('\).*' ,'', re.sub('.*np: * ','', l))
    return dic
    

def _convtree(l):
    t = re.sub('#[0-9]* #',' #',l)
    t = re.sub('\'','',t)
    t = re.sub('#',':',t)
    t = re.sub(' : [0-9]*\.[0-9]*','',t)
    t = re.sub(' *: *',':',t)
    return t


def parse_rst(path):
    K = 0
    EB=False
    EBend=False
    PS=False
    lnL = ''
    for line in open(path,'r'):
        line = line.strip()
        if line.startswith('lnL = '):
            lnL = line.split()[-1]
            if not (EB == False or EB == True):
                EB['lnL.'+m]=lnL
        if line.startswith('dN/dS for site classes'):
            K = re.sub('.*K=','',line)
            K = int (re.sub('\)','',K))
            if K < 4: m = 'M'+str(K-1)
            else:     m = 'M'+str(K-3)
        if K % 2 == 0:
            if line.startswith('Naive Empirical Bayes'): EB = True
            elif(EB==False):continue
        else:
            if line.startswith('Bayes Empirical Bayes'): EB = True
            elif(EB==False):continue
        if re.match('^ *[0-9]* [A-Z*] *',line)==None and \
               EBend==False:
            continue
        if re.match('^ *[0-9]* [A-Z*] *',line)==None: PS = True
        EBend=True
        if EB==True:
            EB={'aa.'+m:[], 'w.'+m:[], 'class.'+m:[],
                'pv.'+m:[],'se.'+m:[], 'lnL.'+m:lnL}
        if PS == False:
            EB['aa.'+m].append(line.split()[1])
            EB['w.' +m].append(re.sub('\+.*','',line).split()[-1])
            if m=='M1'or m=='M7': EB['se.'+m].append('')
            else: EB['se.'+m].append(line.split()[-1])
            classes = map(float,re.sub('\(.*','',line).split()[2:])
            EB['class.'+m].append(\
                '('+\
                re.sub('\).*','',re.sub('.*\( *','',line.strip()))\
                +'/'+str (len (classes))+')')
            EB['pv.'+m].append(str (\
                max (classes)))
    return EB


def parse_codemlOut(out, phylo_tree):
    dS=False
    dN=False
    w=False
    bL=0
    for line in open(out,'r').readlines():
        if line.startswith('tree length ='):
            bL=1
            continue
        if bL > 0 and line=='\n' :
            bL = bL + 1
            continue
        if bL == 3 :
            t = PhyloTree(re.sub(' ','',line.strip()))
            bL = 0
            continue
        if line.startswith('dN tree:'):
            dN =True
            continue
        if dN == True:
            dN=False
            tdN = PhyloTree(re.sub(' ','',line.strip()))
        if line.startswith('dS tree:'):
            dS =True
            continue
        if dS == True:
            dS=False
            tdS = PhyloTree(re.sub(' ','',line.strip()))
        if line.startswith('w ratios as labels for TreeView:'):
            w =True
            continue
        if w == True:
            w=False
            tw = PhyloTree(re.sub(' : [0-9][0-9]*\.*[0-9]*','',re.sub('#?[0-9]?[0-9]* *#',':',line.strip())))
    label_tree(t)
    label_tree(tw)
    label_tree(tdS)
    label_tree(tdN)
    label_tree(phylo_tree)
    for n in phylo_tree.iter_descendants():
        for n2 in t.iter_descendants():
            if n2.idname==n.idname:
                n.dist = n2.dist
        for n2 in tw.iter_descendants():
            if n2.idname==n.idname:
                n.add_feature('omega',n2.dist)
                n.add_feature('omega_val',n2.dist)
        for n2 in tdN.iter_descendants():
            if n2.idname==n.idname:
                n.add_feature('dN',n2.dist)
        for n2 in tdS.iter_descendants():
            if n2.idname==n.idname:
                n.add_feature('dS',n2.dist)
        if (n.omega > 900):
            n.omega = 3
            continue
        if (n.omega > 100):
            n.omega = 2.5
            continue
        if (n.omega > 10) :
            n.omega = 2
            continue
        if (n.omega > 1):
            n.omega =1.5
    phylo_tree.get_tree_root().dist = 0
    return phylo_tree


