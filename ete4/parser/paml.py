import os
import string
from sys import stderr as STDERR
from re import search

from ete4.core import seqgroup

def read_paml (source, obj=None, header_delimiter="\t", fix_duplicates=True):
    """ Reads a collection of sequences econded in PAML format... that is, something between PHYLIP and fasta

     3 6
    seq1
    ATGATG
    seq2
    ATGATG
    seq3
    ATGATG

    or

     3 6
    >seq1
    ATGATG
    >seq2
    ATGATG
    >seq3
    ATGATG

    or

    >seq1
    ATGATG
    >seq2
    ATGATG
    >seq3
    ATGATG

    """

    if obj is None:
        SC = seqgroup.SeqGroup()
    else:
        SC = obj

    names = set([])
    seq_id = -1

    # Prepares handle from which read sequences
    if os.path.isfile(source):
        _source = open(source, "r")
    else:
        _source = iter(source.split("\n"))

    seq_name = None
    num_seq = 0
    len_seq = 0
    in_seq  = False
    for line in _source:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        if line.startswith('// end of file'):
            break
        # Reads seq number
        elif line.startswith('>') or ((num_seq and len_seq) and not in_seq):
            fasta = line.startswith('>')
            line = line.replace('>','')
            # Checks if previous name had seq
            if seq_id>-1 and SC.id2seq[seq_id] == "":
                raise Exception("No sequence found for "+seq_name)

            seq_id += 1
            # Takes header info
            seq_header_fields = [_f.strip() for _f in line.split(header_delimiter)]
            in_seq = True
            if (not fasta) and '   ' in seq_header_fields[0].strip():
                seq_header_fields = seq_header_fields[0].split('   ')[0]
                seq_header_fields = [seq_header_fields]
                SC.id2seq[seq_id] = line.split('   ')[-1].strip().replace(' ', '')
                if len_seq:
                    if len(SC.id2seq[seq_id]) == len_seq:
                        in_seq=False
                    elif len(SC.id2seq[seq_id]) > len_seq:
                        raise  Exception("Error reading sequences: Wrong sequence length.\n"+line)
            else:
                SC.id2seq[seq_id]     = ""
            seq_name = seq_header_fields[0]
            # Checks for duplicated seq names
            if fix_duplicates and seq_name in names:
                tag = str(len([k for k in list(SC.name2id.keys()) if k.endswith(seq_name)]))
                old_name = seq_name
                seq_name = tag+"_"+seq_name
                print("Duplicated entry [%s] was renamed to [%s]" %(old_name, seq_name), file=STDERR)

            # stores seq_name
            SC.id2name[seq_id]    = seq_name
            SC.name2id[seq_name]  = seq_id
            SC.id2comment[seq_id] = seq_header_fields[1:]
            names.add(seq_name)
        else:
            if seq_name is None:
                if search ('^[0-9]+  *[0-9]+ *[A-Z]*', line):
                    try:
                        num_seq, len_seq = line.strip().split()
                    except ValueError:
                        num_seq, len_seq, _ = line.strip().split()
                    num_seq = int(num_seq)
                    len_seq = int(len_seq)
                    continue
                if line.startswith('\n'):
                    continue
                raise Exception("Error reading sequences: Wrong format.\n"+line)
            elif in_seq:
                # removes all white spaces in line
                s = line.strip().replace(" ","")

                # append to seq_string
                SC.id2seq[seq_id] += s
                if len_seq:
                    if len(SC.id2seq[seq_id]) == len_seq:
                        in_seq=False
                    elif len(SC.id2seq[seq_id]) > len_seq:
                        raise  Exception("Error reading sequences: Wrong sequence length.\n"+line)

    if seq_name and SC.id2seq[seq_id] == "":
        print(seq_name,"has no sequence", file=STDERR)
        return None

    # Everything ok
    return SC

def write_paml(sequences, outfile = None, seqwidth = 80):
    """
    Writes a SeqGroup python object using PAML format.
    sequences are ordered, because PAML labels tree according to this.
    """
    text =  ' %d %d\n' % (len (sequences), len (sequences.get_entries()[0][1]))
    text += '\n'.join(["%s\n%s" %( "\t".join([name]+comment), _seq2str(seq)) for
                       name, seq, comment in sorted(sequences)])
    if outfile is not None:
        OUT = open(outfile,"w")
        OUT.write(text)
        OUT.close()
    else:
        return text

def _seq2str(seq, seqwidth = 80):
    sequence = ""
    for i in range(0,len(seq),seqwidth):
        sequence+= seq[i:i+seqwidth] + "\n"
    return sequence
