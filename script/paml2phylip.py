#!/usr/bin/python

#        Author: Leonardo Arbiza
# Creation Date: 2008/03/11 11:18:07
#
# This script converts paml formatted alignments to
# phylip interleaved

import sys,os,re


class read_paml_aln:
    ''' read a paml aln to get an aln dict '''
    def __init__(self,infile):        
        self.error = None
        self.infile = infile        
        lines = []
        try:
            lines = open(infile,'r').readlines()
        except:
            self.error = 'could not read from '+infile
        else:
            block = ''.join(lines)
            self._read_aln(lines)
            del(lines, block)

        
    def _read_aln(self,lines):
        ''' read numspec, chars, and data '''
        self.alndict = {}
        self.numspec, self.chars = lines[0].strip().split()
        self.original_order = []
        seqdat = re.findall('''(\w+)\n(\S+)\s*\n''',
                        ''.join(lines[1:]))
        for spec,seq in seqdat:
            if self.alndict.has_key(spec):
                self.error = 'repeated sequence '+spec+\
                             ' in alignment'
                return
            else:
                self.original_order.append(spec)
                self.alndict[spec]=seq

        if self.numspec != str(len(self.alndict)):
            self.error = str(self.numspec)+' specs wanted but only '+\
                         str(len(self.alndict))+ ' found in aln'
        first_seq = self.alndict[self.alndict.keys()[0]]
        if self.chars != str(len(first_seq)):
            self.error = str(self.chars)+' chars expected but only '+\
                         str(len(first_seq))+' were obtained'        

def paml2phylip_aln(aln):

    buff = ' '.join([aln.numspec, aln.chars])+'\n'
    species = aln.original_order
    length = len(aln.alndict[species[0]])
    nowlen = int(length)
    first = True
    while nowlen > 0:
        prev = length - nowlen
        for spec in species:            
            if first:
                buff += spec[:10].ljust(10)+' '
            else:
                buff += ' '*11

            for i in xrange(5):
                low = prev + 10*i
                high = prev + 10*(i+1) 
                buff += aln.alndict[spec][low:high]+' '                
            buff += '\n'

        buff += '\n'
        nowlen -= 50
        first = False

    return buff

def main():

    inf =     sys.argv[1]
    pth, f =  os.path.split(inf)
    sn, ext = os.path.splitext(f)

    aln = read_paml_aln(inf)

    phyaln= paml2phylip_aln(aln)

    OF = open(sn+'.phy','w')
    print >> OF, phyaln
    OF.close()
    




if __name__ == '__main__': main()    
