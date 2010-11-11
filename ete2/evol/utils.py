#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/22 16:05:46


import os, re
import errno
from hashlib import md5
from ete_dev import Tree

def mkdir_p(path):
    '''
    equivalent to "mkdir -p"
    '''
    try:
        os.makedirs(path)
    except OSError, (exc): # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def get_rooting(tol, seed_species, agename = False):
    '''
    returns dict of species age for a given TOL and a given seed
    usage:
    tol  = "((((((((Drosophila melanogaster,(Drosophila simulans,Drosophila secchellia)),(Drosophila yakuba,Drosophila erecta))[&&NHX:name=melanogaster subgroup],Drosophila ananassae)[&&NHX:name=melanogaster group],(Drosophila pseudoobscura,Drosophila persimilis)[&&NHX:name=obscura group])[&&NHX:name=Sophophora Old World],Drosophila willistoni)[&&NHX:name=subgenus Sophophora],(Drosophila grimshawi,(Drosophila virilis,Drosophila mojavensis))[&&NHX:name=subgenus Drosophila])[&&NHX:name=genus Drosophila],(Anopheles gambiae,Aedes aegypti)[&&NHX:name=Culicidae])[&&NHX:name=Arthropoda],Caenorhabditis elegans)[&&NHX:name=Animalia];"
    seed = "Drosophila melanogaster"
    ROOTING, age2name = get_rooting (tol, seed, True)

    ROOTING == {"Aedes aegypti"           : 7,
                "Anopheles gambiae"       : 7,
                "Caenorhabditis elegans"  : 8,
                "Drosophila ananassae"    : 3,
                "Drosophila erecta"       : 2,
                "Drosophila grimshawi"    : 6,
                "Drosophila melanogaster" : 1,
                "Drosophila mojavensis"   : 6,
                "Drosophila persimilis"   : 4,
                "Drosophila pseudoobscura": 4,
                "Drosophila secchellia"   : 1,
                "Drosophila simulans"     : 1,
                "Drosophila virilis"      : 6,
                "Drosophila willistoni"   : 5,
                "Drosophila yakuba"       : 2}

    age2name == {1: "Drosophila melanogaster. Drosophila simulans. Drosophila secchellia",
                 2: "melanogaster subgroup",
                 3: "melanogaster group",
                 4: "Sophophora Old World",
                 5: "subgenus Sophophora",
                 6: "genus Drosophila",
                 7: "Arthropoda",
                 8: "Animalia"}
    '''

    tol = Tree (tol)
    try:
        node = tol.search_nodes (name=seed_species)[0]
    except IndexError:
        exit ('ERROR: Seed species not found in tree\n')
    age = 1
    ROOTING = {}
    if agename:
        age2name = {}
    while not node.is_root():
        node = node.up
        for leaf in node.get_leaf_names():
            if agename:
                if node.name == 'NoName':
                    nam = '.'.join (node.get_leaf_names())
                else:
                    nam = node.name
                age2name.setdefault (age, nam)
            ROOTING.setdefault (leaf, age)
        age += 1
    if agename:
        return ROOTING, age2name
    return ROOTING



def label_tree(t):
    """
    WARNING: deprecated, use sort_tree function of Tree    
    This function sort the branches of a given tree by
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
