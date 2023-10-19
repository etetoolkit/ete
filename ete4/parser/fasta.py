import os
import textwrap
from sys import stderr as STDERR

from ete4.core import seqgroup


def read_fasta(source, obj=None, header_delimiter="\t", fix_duplicates=True):
    """ Reads a collection of sequences econded in FASTA format."""

    if obj is None:
        SC = seqgroup.SeqGroup()
    else:
        SC = obj

    names = set()
    seq_id = -1

    # Prepares handle from which read sequences
    if os.path.isfile(source):
        if source.endswith('.gz'):
            import gzip
            _source = gzip.open(source)
        else:
            _source = open(source, "r")
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
                raise Exception("No sequence found for "+seq_name)

            seq_id += 1
            # Takes header info
            seq_header_fields = [_f.strip() for _f in line[1:].split(header_delimiter)]
            seq_name = seq_header_fields[0]

            # Checks for duplicated seq names
            if fix_duplicates and seq_name in names:
                tag = str(len([k for k in list(SC.name2id.keys()) if k.endswith(seq_name)]))
                old_name = seq_name
                seq_name = tag+"_"+seq_name
                print("Duplicated entry [%s] was renamed to [%s]" %(old_name, seq_name), file=STDERR)

            # stores seq_name
            SC.id2seq[seq_id] = ""
            SC.id2name[seq_id] = seq_name
            SC.name2id[seq_name] = seq_id
            SC.id2comment[seq_id] = seq_header_fields[1:]
            names.add(seq_name)

        else:
            if seq_name is None:
                raise Exception("Error reading sequences: Wrong format.")

            # removes all white spaces in line
            s = line.strip().replace(" ","")

            # append to seq_string
            SC.id2seq[seq_id] += s

    if os.path.isfile(source):
        _source.close()

    if seq_name and SC.id2seq[seq_id] == "":
        print(seq_name,"has no sequence", file=STDERR)
        return None

    # Everything ok
    return SC

def write_fasta(sequences, outfile = None, seqwidth = 80):
    """ Writes a SeqGroup python object using FASTA format. """

    wrapper = textwrap.TextWrapper()
    wrapper.break_on_hyphens = False
    wrapper.replace_whitespace = False
    wrapper.expand_tabs = False
    wrapper.break_long_words = True
    wrapper.width = 80
    text =  '\n'.join([">%s\n%s\n" %( "\t".join([name]+comment), wrapper.fill(seq)) for
                       name, seq, comment in sequences])

    if outfile is not None:
        with open(outfile, 'w') as fout:
            fout.write(text)
    else:
        return text
