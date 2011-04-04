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
"""
The 'seqgroup' module provides methods and classes to operate with
Multiple Sequence Files, including Multiple Sequence Alignments.

Currently, Fasta, Phylip sequencial and Phylip interleaved formats are
supported.
"""

from ete_dev.parser.fasta import read_fasta, write_fasta
from ete_dev.parser.phylip import read_phylip, write_phylip

__all__ = ["SeqGroup"]

class SeqGroup(object):
    """
    SeqGroup class can be used to store a set of sequences (aligned
    or not).

    CONSTRUCTOR ARGUMENTS:


      * sequences: Path to the file containing the sequences or,
        alternatively, the text string containing the same information.

      * format (optional): the format in which sequences are encoded. Current
        supported formats are: "fasta", "phylip" (phylip sequencial)
        and "iphylip" (phylip interleaved)

    RETURNS:

     A SeqGroup object to operate with sequencies.

    EXAMPLES:

     msf = ">seq1\\nAAAAAAAAAAA\\n>seq2\\nTTTTTTTTTTTTT\\n"
     seqs = SeqGroup(msf, format="fasta")
     print seqs.get_seq("seq1")
     """

    def __len__(self):
        return len(self.id2seq)

    def __contains__(self, item):
        return item in self.name2id

    def __str__(self):
        return write_fasta(self)

    def __iter__(self):
        return self.iter_entries()

    def __init__(self, sequences = None , format="fasta"):
        self.parsers = {
            "fasta": [read_fasta, write_fasta, {}],
            "phylip": [read_phylip, write_phylip, {"interleaved":False}],
            "iphylip": [read_phylip, write_phylip, {"interleaved":True}]
            }

        self.id2name = {}
        self.name2id = {}
        self.id2comment= {}
        self.id2seq = {}

        if sequences is not None:
            format = format.lower()
            if format in self.parsers:
                read = self.parsers[format][0]
                args = self.parsers[format][2]
                read(sequences, obj=self, **args)
            else:
                raise ValueError, "Unsupported format: [%s]" %format

    def __repr__(self):
        return "SeqGroup (%s)" %hex(self.__hash__())

    def write(self, format="fasta", outfile=None):
        """ Returns the text representation of the sequences in the
        supplied given format (default=FASTA). If "oufile" argument is
        used, the result is written into the given path."""

        format = format.lower()
        if format in self.parsers:
            write = self.parsers[format][1]
            args = self.parsers[format][2]
            return write(self, outfile, **args)
        else:
            raise ValueError, "Unssupported format: [%s]" %format

    def iter_entries(self):
        """ Returns an iterator over all sequences in the
        collection. Each item is a tuple with the sequence name,
        sequence, and sequence comments """
        for i, seq in self.id2seq.iteritems():
            yield self.id2name[i], seq,  self.id2comment.get(i, [])

    def get_seq(self, name):
        """ Returns the sequence associated to a given entry name."""
        return self.id2seq[self.name2id[name]]

    def get_entries(self):
        """ Returns the list of entries currently stored."""
        keys = self.id2seq.keys()
        seqs = self.id2seq.values()
        comments = [self.id2comment.get(x, []) for x in  keys]
        names = map(lambda x: self.id2name[x], keys)
        return zip(names, seqs, comments)

    def set_seq(self, name, seq, comments = []):
        """Updates or creates the sequence of "name" """
        name = name.strip()
        seq = seq.replace(" ", "")
        seq = seq.replace("\t", "")
        seq = seq.replace("\n", "")
        seq = seq.replace("\r", "")
        seqid = self.name2id.get(name, None)
        if not seqid:
            for i in xrange(len(self.id2seq)):
                if i not in self.id2seq:
                    seqid = i
                    break
            if not seqid:
                seqid = i+1

        self.name2id[name] = seqid
        self.id2name[seqid] = name
        self.id2comment[seqid] = comments
        self.id2seq[seqid] = seq
