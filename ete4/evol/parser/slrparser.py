#!/usr/bin/python3

"""
Parser for slr outfile
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"

from re import match

def parse_slr (slrout):
    SLR = {'pv':[],'w':[],'se':[], 'class':[],'note':[]}
    w   = ''
    apv = ''
    seP = ''
    seN = ''
    res = ''
    note= ''
    for line in open (slrout):
        if line.startswith('#'):
            w   = line.strip().split().index('Omega')-1
            apv = line.strip().split().index('Adj.Pval')-1
            res = line.strip().split().index('Result')-1
            note= line.strip().split().index('Note')-1
            try:
                seP = line.strip().split().index('upper')-1
                seN = line.strip().split().index('lower')-1
            except:
                continue
            continue
        SLR['pv' ].append(1-float (line.split()[apv]))
        SLR['w'  ].append(line.split()[w])
        corr = 0
        try:
            if not match('[-+]',line.split()[res]) is None:
                SLR['class'  ].append (5 - line.split()[res].count ('-') + line.split()[res].count ('+'))
            else:
                SLR['class'  ].append(5)
                corr = 1
        except IndexError:
            SLR['class'  ].append(5)
        try:
            SLR['note'  ].append(line.split()[note-corr])
        except IndexError:
            SLR['note'  ].append('')
        if not seN == '':
            SLR['se'].append ([float (SLR['w'][-1]) - float (line.split()[seN]),
                               float (line.split()[seP]) - float (SLR['w'][-1])])
    return {'sites': {'SLR': SLR},
            'n_classes': {'SLR': 8}}
