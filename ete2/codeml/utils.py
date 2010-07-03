#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/22 16:05:46


import os, re
import errno
from hashlib import md5


def mkdir_p(path):
    '''
    equivalent to "mkdir -p"
    '''
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def colorize_rst(vals, winner, classes):
    '''
    Colorize function, that take in argument a list of values
    corresponding to a list of classes and returns a list of
    colors to paint histogram.
    '''
    colors = []
    for i in range (0, len (vals)):
        class1 = int(re.sub('\/.*', '', re.sub('\(', '', classes[i])))
        class2 = int(re.sub('.*\/', '', re.sub('\)', '', classes[i])))
        pval = float (vals[i])
        if pval < 0.95:
            colors.append('grey')
        elif class1 != class2 and class1 != 1:
            colors.append('green')
        elif class1 == 1:
            if pval < 0.99:
                colors.append('cyan')
            else:
                colors.append('blue')
        elif class1 == class2 and (winner == 'M2' or winner == 'M8'):
            if pval < 0.99:
                colors.append('orange')
            else:
                colors.append('red')
        elif class1 == class2:
            colors.append('grey')
    return colors



def label_tree(t):
    """ This function sort the branches of a given tree by
    considerening node names. After the tree is sorted, nodes are
    labeled using ascendent numbers.  This can be used to ensure that
    nodes in a tree with the same node names are always labeled in
    the same way.  Note that if duplicated names are present, extra
    criteria should be added to sort nodes.
    """
    for n in t.traverse(strategy="postorder"):
        if n.is_leaf():
            key = md5(str(n.name)).hexdigest()
            n.__idname = key
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


def translate(sequence):
    '''
    little function to translate DNA to protein...
    from: http://python.genedrift.org/
    TODO : inseqgroup functions?
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
    ambig = {'Y':['A', 'G'], 'R':['C', 'T'], 'M':['G', 'T'], 'K':['A', 'C'], \
             'S':['G', 'C'],'W':['A', 'T'], 'V':['C', 'G', 'T'], \
             'H':['A', 'G', 'T'], 'D':['A', 'C', 'T'], 'B':['A', 'C', 'G'], \
             'N':['A', 'C', 'G', 'T']}
    proteinseq = ''
    #loop to read DNA sequence in codons, 3 nucleotides at a time
    for n in range(0, len(sequence), 3):
        #checking to see if the dictionary has the key
        try:
            proteinseq += gencode[sequence[n:n+3]]
        except KeyError:
            newcod = []
            for nt in sequence[n:n+3]:
                if ambig.has_key(nt):
                    newcod.append(ambig[nt])
                else :
                    newcod.append(list (nt))
            aa = ''
            for nt1 in newcod[0]:
                for nt2 in newcod[1]:
                    for nt3 in newcod[2]:
                        try:
                            if aa == '':
                                aa  = gencode[nt1+nt2+nt3]
                            elif gencode[nt1+nt2+nt3] != aa:
                                aa = 'X'
                                break
                        except KeyError:
                            aa = 'X'
                            break
            proteinseq += aa
    return proteinseq
