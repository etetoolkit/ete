import os
import string 
from sys import stderr as STDERR

def read_fasta(source, obj=None):
    """ Reads a collection of sequences econded in FASTA format.""" 

    if obj is None:
	from ete_dev.coretype import seqgroup
	SC = seqgroup.SeqGroup()
    else:
	SC = obj

    names = set([])
    seq_id = -1

    # Prepares handle from which read sequences
    if os.path.isfile(source):
	_source = open(source, "rU")
    else:
	_source = iter(source.split("\n"))

    seq_name = None
    for line in _source:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        # Reads seq number 
        elif line.startswith('>'):
            # Checks if previous name had seq
            if seq_id>-1 and SC.id2seq[seq_id] == "":
                raise Exception, "No sequence found for "+seq_name

	    seq_id += 1
            # Takes header info
	    seq_header_fields = map(string.strip, line[1:].split("\t"))
            seq_name = seq_header_fields[0]

            # Checks for duplicated seq names
	    if seq_name in names:
		tag = str(len(k for k in SEG.name2id.keys() if k.endswith(name)))
		old_name = name
		name = tag+"_"+name
		print >>STDERR, "Duplicated entry [%s] was renamed to [%s]" %(old_name, name)
		
            # stores seq_name
            SC.id2seq[seq_id] = ""
	    SC.id2name[seq_id] = seq_name
	    SC.name2id[seq_name] = seq_id
	    SC.id2comment[seq_id] = seq_header_fields[1:]
            names.add(seq_name)

        else:
            if seq_name is None:
                raise Exception, "Error readind sequences: Wrong format."

            # removes all white spaces in line
            s = line.strip().replace(" ","")

            # append to seq_string
            SC.id2seq[seq_id] += s

    if seq_name and SC.id2seq[seq_id] == "":
        print >>STDERR, seq_name,"has no sequence"
        return None

    # Everything ok
    return SC

def write_fasta(sequences, outfile = None, seqwidth = 80):
    """ Writes a SeqGroup python object using FASTA format. """ 

    text =  '\n'.join([">%s\n%s" %( "\t".join([name]+comment), _seq2str(seq)) for
		       name, seq, comment in sequences])

    if outfile is not None:
	OUT = open(outfile,"w")
	OUT.write(text)
	OUT.close()
    else:
	return text

def _seq2str(seq, seqwidth = 80):
    sequence = ""
    for i in xrange(0,len(seq),seqwidth):
	sequence+= seq[i:i+seqwidth] + "\n"
    return sequence
