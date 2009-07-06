"""
The 'seqgroup' module provides methods and classes to operate with
Multiple Sequence Files, including Multiple Sequence Alignments.

Currently, Fasta, Phylip sequencial and Phylip interleaved formats are
supported.
"""

from ete2.parser.fasta import read_fasta, write_fasta
from ete2.parser.phylip import read_phylip, write_phylip

__all__ = ["SeqGroup"]

class SeqGroup(object):
    """
    SeqGroup class can be used to store a set of sequences (aligned
    or not).

    CONSTRUCTOR ARGUMENTS:
    ======================

      * sequences: Path to the file containing the sequences or,
        alternatively, the text string containing the same information.
         
      * format (optional): the format in which sequences are encoded. Current
        supported formats are: "fasta", "phylip" (phylip sequencial)
        and "iphylip" (phylip interleaved)

    RETURNS: 
    ========
     A SeqGroup object to operate with sequencies.

    EXAMPLES:
    =========
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
		raise "Unsupported format: [%s]" %format

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
	    raise "Unssupported format: [%s]" %format

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
