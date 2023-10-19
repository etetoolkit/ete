"""
This module provides the SeqGroup class with methods to operate with
Multiple Sequence Files, including Multiple Sequence Alignments.

Currently, Fasta, Phylip sequencial and Phylip interleaved formats are
supported.
"""

from ..parser.fasta import read_fasta, write_fasta
from ..parser.paml import read_paml, write_paml
from ..parser.phylip import read_phylip, write_phylip


__all__ = ['SeqGroup']


class SeqGroup:
    """Class to store a set of sequences (aligned or not)."""

    def __init__(self, sequences=None, format='fasta',
                 fix_duplicates=True, **kwargs):
        r"""
        :param sequences: Path to the file containing the sequences or,
            alternatively, the text string containing them.
        :param format: Encoding format of sequences. Supported formats
            are: ``fasta``, ``phylip`` (phylip sequencial) and
            ``iphylip`` (phylip interleaved). Phylip format forces
            sequence names to a maximum of 10 chars. To avoid this
            effect, you can use the relaxed phylip format:
            ``phylip_relaxed`` and ``iphylip_relaxed``.

        Example::

          seqs_str = ('>seq1\n'
                      'AAAAAAAAAAA\n'
                      '>seq2\n'
                      'TTTTTTTTTTTTT\n')
          seqs = SeqGroup(seqs_str, format='fasta')
          print(seqs.get_seq('seq1'))
        """
        self.parsers = {
            'fasta': [read_fasta, write_fasta, {}],
            'phylip': [read_phylip, write_phylip, {'interleaved': False, 'relaxed': False}],
            'iphylip': [read_phylip, write_phylip, {'interleaved': True, 'relaxed': False}],
            'phylip_relaxed': [read_phylip, write_phylip, {'interleaved': False, 'relaxed': True}],
            'iphylip_relaxed': [read_phylip, write_phylip, {'interleaved': True, 'relaxed': True}],
            'paml': [read_paml, write_paml, kwargs]
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
                read(sequences, obj=self, fix_duplicates=fix_duplicates, **args)
            else:
                raise ValueError(f'Unsupported format: {format}')

    def __len__(self):
        return len(self.id2seq)

    def __contains__(self, item):
        return item in self.name2id

    def __str__(self):
        return write_fasta(self)

    def __iter__(self):
        return self.iter_entries()

    def __repr__(self):
        return 'SeqGroup (%s)' % hex(self.__hash__())

    def write(self, format='fasta', outfile=None):
        """Return the text representation of the sequences.

        :param format: Format for the output representation.
        :param outfile: If given, the result is written to that file.
        """
        format = format.lower()
        if format in self.parsers:
            write = self.parsers[format][1]
            args = self.parsers[format][2]
            return write(self, outfile, **args)
        else:
            raise ValueError('Unsupported format: [%s]' % format)

    def iter_entries(self):
        """Return an iterator over all sequences in the collection.

        Each item is a tuple with the sequence name, sequence, and
        sequence comments.
        """
        for i, seq in self.id2seq.items():
            yield self.id2name[i], seq, self.id2comment.get(i, [])

    def get_seq(self, name):
        """Return the sequence associated to a given entry name."""
        return self.id2seq[self.name2id[name]]

    def get_entries(self):
        """Return the list of entries currently stored."""
        keys = list(self.id2seq.keys())
        seqs = list(self.id2seq.values())
        comments = [self.id2comment.get(x, []) for x in  keys]
        names = [self.id2name[x] for x in keys]
        return list(zip(names, seqs, comments))

    def set_seq(self, name, seq, comments=None):
        """Add or update a sequence."""
        name = name.strip()

        for c in ' \t\n\r':
            seq = seq.replace(c, '')

        seqid = self.name2id.get(name, max([0]+list(self.name2id.values()))+1)

        self.name2id[name] = seqid
        self.id2name[seqid] = name
        self.id2comment[seqid] = comments or []
        self.id2seq[seqid] = seq
