import os
import re
from sys import stderr as STDERR

def read_phylip(source, interleaved=True, obj=None):
    if obj is None:
	from ete_dev.coretype import SeqGroup
	SG = SeqGroup()
    else:
	SG = obj 

    # Prepares handle from which read sequences
    if os.path.isfile(source):
	_source = open(source, "rU")
    else:
	_source = iter(source.split("\n"))

    nchar, ntax = None, None
    counter = 0
    id_counter = 0
    for line in _source:
        line = line.strip("\n")
        # Passes comments and blank lines
        if not line or line[0] == "#":
	    continue
        # Reads head
        if not nchar or not ntax:
            m = re.match("^\s*(\d+)\s+(\d+)",line)
            if m:
                ntax  = int (m.groups()[0])
                nchar = int (m.groups()[1])
            else:
                raise Exception, \
		    "A first line with the alignment dimension is required"
        # Reads sequences
        else:
	    if not interleaved:
		# Reads names and sequences
		if SG.id2name.get(id_counter, None) is None:
		    m = re.match("^\s*(.{10})(.+)", line)
		    if m:
			name = m.groups()[0].strip()
			if name in SG.name2id:
			    tag = str(len(k for k in SEG.name2id.keys() \
					      if k.endswith(name)))
			    old_name = name
			    name = tag+"_"+name
			    print >>STDERR, \
				"Duplicated entry [%s] was renamed to [%s]" %\
				(old_name, name)
			SG.id2name[id_counter] = name
			SG.name2id[name] = id_counter
			SG.id2seq[id_counter] = ""
			line = m.groups()[1]
		    else:
			raise Exception, \
			    "Wrong phylip sequencial format."
		SG.id2seq[id_counter] += re.sub("\s","", line)
		if len(SG.id2seq[id_counter]) == nchar:
		    id_counter += 1
		    name = None
		elif len(SG.id2seq[id_counter]) > nchar:
		    raise Exception, \
			"Unexpected length of sequence [%s] [%s]." %(name,SG.id2seq[id_counter])
	    else:
		if len(SG)<ntax:
		    m = re.match("^(.{10})(.+)",line)
		    if m:
			name = m.groups()[0].strip()
			seq  =  re.sub("\s","",m.groups()[1])
			SG.id2seq[id_counter] = seq
			SG.id2name[id_counter] = name
			if name in SG.name2id:
			    tag = str(len(k for k in SEG.name2id.keys() \
					      if k.endswith(name)))
			    old_name = name
			    name = tag+"_"+name
			    print >>STDERR, \
				"Duplicated entry [%s] was renamed to [%s]" %\
				(old_name, name)
			SG.name2id[name] = id_counter
			id_counter += 1
		    else:
			raise Exception, \
			    "Unexpected number of sequences."
		else:
		    seq = re.sub("\s", "", line)
		    if id_counter == len(SG):
			id_counter = 0
		    SG.id2seq[id_counter] += seq
		    id_counter += 1

    if len(SG) != ntax:
	raise Exception, \
	    "Unexpected number of sequences."

    # Check lenght of all seqs
    for i in SG.id2seq.keys():
        if len(SG.id2seq[i]) != nchar:
            raise Exception, \
		"Unexpected lenght of sequence [%s]" %SG.id2name[i]

    return SG

def write_phylip(aln, outfile=None, interleaved=True):
    width = 60
    seq_visited = set([])

    show_name_warning = False
    lenghts = set((len(seq) for seq in aln.id2seq.values()))
    if len(lenghts) >1:
	raise Exception, "Phylip format requires sequences of equal lenght."
    seqlength = lenghts.pop()

    alg_text = " %d %d\n" %(len(aln), seqlength)
    if interleaved:
	visited = set([])
        for i in xrange(0, seqlength, width):
            for j in xrange(len(aln)):
                name =  aln.id2name[j]
                if len(name)>10: 
		    name = name[:10]
		    show_name_warning = True
	    
                seq = aln.id2seq[j][i:i+width]
		if j not in visited:
		    alg_text += "%10s   " %name
		    visited.add(j)
		else:
		    alg_text += " "*13
        
		alg_text += ' '.join([seq[k:k+10] for k in xrange(0, len(seq), 10)])
                alg_text += "\n"
	    alg_text += "\n"
    else:
	for name, seq, comments in aln.iter_entries():
	    if len(name)>10: 
		name = name[:10]
		show_name_warning = True
            alg_text += "%10s   %s\n%s\n" %\
		(name, seq[0:width-13], '\n'.join([seq[k:k+width]  \
				      for k in xrange(width-13, len(seq), width)]))
    if show_name_warning:
	print >>STDERR, "Warning! Some seqnames were truncated to 10 characters"
            
    if outfile is not None:
	OUT = open(outfile, "w")
	OUT.write(alg_text)
	OUT.close()
    else:
	return alg_text
