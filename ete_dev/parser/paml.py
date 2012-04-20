# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################

import os
import string
from sys import stderr as STDERR
from re import search

def read_paml (source, obj=None):
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
    num_seq = 0
    len_seq = 0
    in_seq  = False
    for line in _source:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        # Reads seq number
        elif line.startswith('>') or ((num_seq and len_seq) and not in_seq):
            line = line.replace('>','')
            # Checks if previous name had seq
            if seq_id>-1 and SC.id2seq[seq_id] == "":
                raise Exception, "No sequence found for "+seq_name

            seq_id += 1
            # Takes header info
            seq_header_fields = map(string.strip, line.split("\t"))
            seq_name = seq_header_fields[0]

            # Checks for duplicated seq names
            if seq_name in names:
                tag = str(len([k for k in SC.name2id.keys() if k.endswith(seq_name)]))
                old_name = seq_name
                seq_name = tag+"_"+seq_name
                print >>STDERR, "Duplicated entry [%s] was renamed to [%s]" %(old_name, seq_name)

            # stores seq_name
            SC.id2seq[seq_id]     = ""
            SC.id2name[seq_id]    = seq_name
            SC.name2id[seq_name]  = seq_id
            SC.id2comment[seq_id] = seq_header_fields[1:]
            names.add(seq_name)
            in_seq = True
        else:
            if seq_name is None:
                if search ('^[0-9]+  *[0-9]+$', line):
                    num_seq, len_seq = line.strip().split()
                    num_seq = int(num_seq)
                    len_seq = int(len_seq)
                    continue
                if line.startswith('\n'):
                    continue
                raise Exception, "Error reading sequences: Wrong format.\n"+line
            elif in_seq:
                # removes all white spaces in line
                s = line.strip().replace(" ","")

                # append to seq_string
                SC.id2seq[seq_id] += s
                if len_seq:
                    if len(SC.id2seq[seq_id]) == len_seq:
                        in_seq=False
                    elif len(SC.id2seq[seq_id]) > len_seq:
                        raise  Exception, "Error reading sequences: Wrong sequence length.\n"+line

    if seq_name and SC.id2seq[seq_id] == "":
        print >>STDERR, seq_name,"has no sequence"
        return None

    # Everything ok
    return SC

def write_paml(sequences, outfile = None, seqwidth = 80):
    """ Writes a SeqGroup python object using PAML format. """
    text =  ' %d %d\n' % (len (sequences), len (sequences.get_entries()[0][1]))
    text += '\n'.join(["%s\n%s" %( "\t".join([name]+comment), _seq2str(seq)) for
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

