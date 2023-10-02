"""
Tests of core functionality of Alignmnets objects.
"""

from tempfile import NamedTemporaryFile

from ete4 import SeqGroup
from . import datasets as ds


def test_fasta_parser():
    """Test fasta read an write."""
    # FASTA IO.
    SEQS = SeqGroup(ds.fasta_example)  # reading from string

    with NamedTemporaryFile('wt') as f_fasta:
        f_fasta.write(ds.fasta_example)
        f_fasta.flush()

        SEQS2 = SeqGroup(f_fasta.name)  # reading from file

    # Assert the results are the same.
    assert SEQS.write() == SEQS2.write() == ds.fasta_example_output

    # Test writing into file.
    with NamedTemporaryFile('wt') as f_fastaio:
        SEQS.write(format="fasta", outfile=f_fastaio.name)
        assert open(f_fastaio.name).read() == ds.fasta_example_output

    # Test SeqGroup obj integrity
    assert SEQS.get_seq("Ago0000003") == ds.Ago0000003
    assert SEQS2.get_seq("Ago0000003") == ds.Ago0000003
    assert len(SEQS) == len(SEQS.id2seq)
    assert "Ago0000003" in SEQS
    assert "Ago" not in SEQS
    assert SEQS.get_entries() == [e for e in SEQS]

    # Check that the default write format is FASTA.
    assert str(SEQS) == SEQS.write(format="fasta")


def test_phylip_parser():
    """Test phylip read and write."""
    # PHYLIP INTERLEAVED.
    SEQS2 = SeqGroup(ds.phylip_interleaved, format="iphylip")  # from string

    with NamedTemporaryFile('wt') as f_iphylip:
        f_iphylip.write(ds.phylip_interleaved)
        f_iphylip.flush()

        SEQS = SeqGroup(f_iphylip.name, format="iphylip")  # from file

    assert SEQS.write() == SEQS2.write()

    # Test writing into file.
    with NamedTemporaryFile('wt') as f_iphylipio:
        SEQS.write(format="iphylip",  outfile=f_iphylipio.name)
        assert open(f_iphylipio.name).read() == ds.phylip_interleaved

    assert SEQS.write(format="iphylip") == ds.phylip_interleaved

    # Test SeqGroup obj integrity.
    assert SEQS.get_seq("CYS1_DICDI") == ds.CYS1_DICDI
    assert SEQS2.get_seq("CYS1_DICDI") == ds.CYS1_DICDI
    assert len(SEQS) == len(SEQS.id2seq)
    assert "CYS1_DICDI" in SEQS
    assert SEQS.get_entries() == [e for e in SEQS]

    # PHYLIP SEQUENCIAL FORMAT.
    SEQS2 = SeqGroup(ds.phylip_sequencial, format="phylip")

    with NamedTemporaryFile('wt') as f_sphylip:
        f_sphylip.write(ds.phylip_sequencial)
        f_sphylip.flush()

        SEQS = SeqGroup(f_sphylip.name, format="phylip")  # from file

    assert SEQS.write() == SEQS2.write()

    # Test writing into file.
    with NamedTemporaryFile('wt') as f_sphylipio:
        SEQS.write(format="phylip",  outfile=f_sphylipio.name)
        assert open(f_sphylipio.name).read() == ds.phylip_sequencial

    # Test SeqGroup obj integrity
    assert SEQS.get_seq("CYS1_DICDI") == ds.CYS1_DICDI
    assert SEQS2.get_seq("CYS1_DICDI") == ds.CYS1_DICDI
    assert len(SEQS) == len(SEQS.id2seq)
    assert "CYS1_DICDI" in SEQS
    assert "CYS1" not in SEQS
    assert SEQS.get_entries() == [e for e in SEQS]


def test_alg_from_scratch():
    alg = SeqGroup(ds.phylip_sequencial, format="phylip")

    random_seq = alg.get_seq("CATH_HUMAN")

    # Add a new sequence to the alg
    alg.set_seq("randomseq", random_seq.replace("A", "X"))

    assert alg.get_seq("randomseq") == random_seq.replace("A", "X")

    # Exports the alignment to different formats
    assert alg.write(format="fasta").startswith('>CYS1_DICDI\n-----MKVILL')
    assert alg.write(format="iphylip").startswith(' 4 384\nCYS1_DICDI   -----MKVIL L')
    assert alg.write(format="phylip").startswith(' 4 384\nCYS1_DICDI   -----MKVILL')
