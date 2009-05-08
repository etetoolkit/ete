#! /usr/bin/env python

import sys
import re

### Alignment format converter
class alignment:
    def __init__(self):
        self.seqs      = {}
        self.seq_order = []
        self.length    = 0

def read_fasta(infile):
    """ Reads FASTA alignment """ 
    a = alignment()

    seq_name = None

    # reads fasta file    
    for line in open(infile):
        line = line.strip()
        
        if line[0]=='#' or not line:
            continue
        # Reads seq number 
        elif line[0]=='>':
            # Checks if previous name had seq
            if seq_name and a.seqs[seq_name] == "":
                print seq_name,"has no sequence"
                return None

            # Takes next seq_name
            r = re.search("^>(\s+)?([^\s]+)",line)
            seq_name = r.groups()[1]

            # Checks for duplicated seq names
            if seq_name in a.seqs:
                print "Warning! Name [",seq_name,"] is duplicated"

            # stores seq_name
            a.seq_order.append(seq_name)
            a.seqs[seq_name] = ""
            
        else:
            if not seq_name:
                print "Error! Wrong fasta format. I need a sequence name before thi line:\n",line

            # removes all white spaces in line
            s = line.strip().replace(" ","")

            # append to seq_string
            a.seqs[seq_name] += s

    if seq_name and a.seqs[seq_name] == "":
        print seq_name,"has no sequence"
        return None


    for n in a.seqs:
        if  a.length != 0 and len(a.seqs[n]) !=  a.length:
            print "Warning!. Unequal length of sequences."
        if  a.length == 0 or  len(a.seqs[n])<0:
            a.length = len(a.seqs[n])
            

    # Everything ok
    return a

def read_nexus(infile):
    """ Reads nexus alignment. Input file has to be simple nexus
    alignment without extra information"""
    # Takes alignment data block
    fs = open(infile).read()
    fs = re.sub("\r\n","\n",fs)
    # Removes spaces between command and ;
    fs = re.sub("[\n\r\s]+;",";",fs)
    # Removes spaces between command and =
    fs = re.sub("[\n\r\s]+=","=",fs)
    fs = re.sub("=[\n\r\s]+","=",fs)
    # Extracts alignment matrix block
    m = re.search("begin data;",fs,re.IGNORECASE)
    if not m:
        print "Wrong Nexus alignment"
        print 'Cannot find "begin data;"'
        return None
    fs =  fs[m.start():]
    m = re.search("end;",fs,re.IGNORECASE)

    if not m:
        print "Wrong Nexus alignment"
        print 'Cannot find "end;"'
        return None
    fs = fs[:m.start()]

    # Reads dimensions 
    m = re.search("dimensions(\n|.)+;",fs,re.IGNORECASE)
    if not m:
        print ' Wrong Nexus alignment\n Cannot find "dimensions"'
        return None

    dim = m.group()
    m = re.search("ntax\s*=\s*(\d+)",dim,re.IGNORECASE)
    if not m:
        print ' Wrong Nexus alignment\n Cannot find "ntax"'
        return None
    ntax  =  int(m.groups()[0])
    m = re.search("nchar\s*=\s*(\d+)",dim,re.IGNORECASE)
    if not m:
        print ' Wrong Nexus alignment\n Cannot find "nchar"'
        return None
    nchar =  int(m.groups()[0])

    print nchar,ntax;

    # Reads format
    interleave  =  None
    matchchar   =  None
    gap         =  None
    datatype    =  None
    m = re.search("format(\n|.)+;",fs,re.IGNORECASE)
    if not m:
        print ' Wrong Nexus alignment\n Cannot find "format"'
        return None

    format = m.group()
    m = re.search("gap\s*=\s*(.)",format,re.IGNORECASE)
    if m:
        gap         =  m.groups()[0]
    m = re.search("matchchar\s*=\s*(\d+)",format,re.IGNORECASE)
    if m:
        matchchar   =  m.groups()[0]
    m = re.search("interleave\s*=\s*([yesno]+)",format,re.IGNORECASE)
    if m:
        interleave  =  m.groups()[0]

    print interleave

    # Reads sequences
    m = re.search("matrix\s*\r?\n((.|\n)+);",fs,re.IGNORECASE)
    if not m:
        print ' Wrong Nexus alignment\n Cannot find "matrix"'
        return None
    # Convert string to lines
    aln = m.groups()[0]
    aln_lines = aln.split("\n")

    # Makes new alignment object

    a = alignment()    
    for line in aln_lines:
       
        #Remove comments
        line = re.sub("\[[^\]]+\]","",line)
        # Clean line
        line = line.strip()
        
        if not line: continue
        m = re.match("^([^\s]+)\s+([^\n]+)",line)
        if not m:
            print line
            return None
        name = m.groups()[0]
        seq  = re.sub("\s","",m.groups()[1])
        if not name in a.seqs:
            a.seqs[name]=seq
            a.seq_order.append(name)
        else:
            a.seqs[name]+=seq

    for n in a.seqs:
        if len(a.seqs) != ntax:
            print "Wrong phylip file.",len(a.seqs),"sequence names found.",ntax,"expected"
            return None

        if len(a.seqs[n]) != nchar:
            print "Wrong phylip file.\n",n,"has",len(a.seqs[n]),"sites.",nchar,"expected"
            return None
    a.length = nchar
    print ntax,"taxa with",nchar,"sites each"
    return a

def read_interleaved_phylip(infile,interleaved = True):
    a = alignment()

    nchar, ntax = None, None
    counter = 0
    for line in open(infile):
        line = line.strip()

        # Passes comments and blank lines
        if not line or line[0] == "#" : continue

        # Reads head
        if not nchar or not ntax:
            m = re.match("^\s*(\d+)\s+(\d+)",line)
            if m:
                ntax  = int (m.groups()[0])
                nchar = int (m.groups()[1])
                print nchar, ntax

            else:
                print "Wrong phylip format.\nI need a first line with alignment dimension"
                return None
        # Reads sequences
        else:
            # Reads names and sequences
            if not interleaved or len(a.seqs) < ntax:
                m = re.match("^\s*(.{10})\s+(.+)",line)
                if m:
                    name =  re.sub("\s","_",m.groups()[0])
                    seq  =  re.sub("\s","",m.groups()[1])
                    a.seq_order.append(name)
                    a.seqs[name] = seq
                else:
                    print "Wrong phylip format.\nNot enough sequence names."
                    return None
            # Reads sequences
            else:
                if counter == len(a.seq_order):
                    counter = 0
                next_name = a.seq_order[counter]
                seq  =  re.sub("\s","",line)
                a.seqs[next_name] += seq
                counter += 1


    for n in a.seqs:
        if len(a.seqs) != ntax:
            print "Wrong phylip file.",len(a.seqs),"sequence names found.",ntax,"expected"
            return None

        if len(a.seqs[n]) != nchar:
            print "Wrong phylip file.\n",n,"has",len(a.seqs[n]),"sites.",nchar,"expected"
            return None
            
    print ntax,"taxa with",nchar,"sites each"
    a.length = nchar
    return a

      
def read_clustal(infile):
    pass

# Write functions
def write_fasta(aln,outfile):
    of = open(outfile,"w")
    width = 80
    for a in aln.seq_order:
        seq = aln.seqs[a]
        print >>of, ">"+a
        for i in xrange(0,len(seq),width):
            print  >>of,seq[i:i+width]
    of.close()

def write_phylip(aln,outfile, interleaved = True):
    width = 50
    names_visited = {}
    alg_text = ""
    
    if interleaved:
        for i in xrange(0,aln.length,width):
            for a in aln.seq_order:
                name =  a[:10]
                if len(a)>10: print "Warning: PHYLIP format does not accept seq names longer than 10 letters.", a,"will be truncated to",name

                # If first time, print names 
                if name not in names_visited:
                    names_visited [name] =1
                    alg_text += "%-10s " % name
                # Duplicated name
                elif len(names_visited) < len(aln.seq_order):
                    print "Error: Duplicated seq name",name
                    return 
                # Print only seq
                else:
                    pass

                seq = aln.seqs[a][i:i+width]
                for j in xrange(0,len(seq),10):
                    alg_text += seq[j:j+10]+" "
                alg_text += "\n"
    else:
        for a in aln.seq_order:
            name =  a[:10]
            if len(a)>10: print "Warning: PHYLIP format does not accept seq names longer than 10 letters.", a,"will be truncated to",name
            seq = aln.seqs[a]
            alg_text += "%s\n%s\n" %(name,seq)
            

    of = open(outfile,"w")
    print >>of," ",len(aln.seqs),aln.length
    print >>of,alg_text
    of.close()
    
            

def write_nexus(aln,outfile):
    width = 60

    of = open(outfile,"w")
    print >>of,"#NEXUS"
    print >>of,"BEGIN DATA;"
    print >>of,"    dimensions ntax=%d nchar=%d;" % ( len(aln.seqs),aln.length )
    print >>of,"    format gap=%s ;" 
    print >>of,"    matrix"
    for i in xrange(0,aln.length,width):
        for a in aln.seq_order:
            print >>of,"   ",a,
            seq = aln.seqs[a][i:i+width]
            print  >>of,"   ",seq
        print >>of,""
    print >>of,";"
    print >>of,"END;"
    of.close()


def write_clustal(aln):
    print "NOT IMPLEMENTED"
    pass


