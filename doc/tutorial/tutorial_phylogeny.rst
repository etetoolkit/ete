Phylogenetic trees
==================

.. contents::

Overview
--------

Phylogenetic trees are the result of most evolutionary analyses. They
represent the evolutionary relationships among a set of species or, in
molecular biology, a set of homologous sequences.

The :class:`PhyloTree` class is an extension of the base :class:`Tree`
class, providing an appropriate way to deal with phylogenetic trees.
Thus, while leaves are considered to represent species (or sequences
from a given species genome), internal nodes are considered ancestral
nodes. A direct consequence of this is, for instance, that every split
in the tree will represent a speciation or duplication event.


Linking phylogenetic trees with multiple sequence alignments
------------------------------------------------------------

:class:`PhyloTree` instances allow molecular phylogenies to be linked
to Multiple Sequence Alignments (MSA). To associate an MSA with a
phylogenetic tree you can use the :func:`PhyloNode.link_to_alignment`
method. You can use the :attr:`alg_format` argument to specify its
format (See :class:`SeqGroup` documentation for available formats).

Given that the `FASTA format
<https://en.wikipedia.org/wiki/FASTA_format>`_ is not only applicable
for MSA but also for **unaligned sequences**, you may also associate
sequences of different lengths with tree nodes.

Example::

  from ete4 import PhyloTree

  fasta_txt = """
  >seqA
  MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
  >seqB
  MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
  >seqC
  MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
  >seqD
  MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
  """

  # Load a tree and link it to an alignment.
  t = PhyloTree('(((seqA,seqB),seqC),seqD);')
  t.link_to_alignment(alignment=fasta_txt, alg_format='fasta')

  print(t.to_str(props=['name', 'sequence']))
  #                  ╭╴seqA,MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
  #            ╭╴⊗,⊗╶┤
  #      ╭╴⊗,⊗╶┤     ╰╴seqB,MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
  #      │     │
  # ╴⊗,⊗╶┤     ╰╴seqC,MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
  #      │
  #      ╰╴seqD,MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH

The same could be done at the time the tree is being loaded, by using
the :attr:`alignment` and :attr:`alg_format` arguments of
:class:`PhyloTree`::

  # Load a tree and link it to an alignment.
  t = PhyloTree('(((seqA,seqB),seqC),seqD);',
                alignment=fasta_txt, alg_format='fasta')

ETE's sequence linking process is not strict, which means that a
perfect match between all node names and sequences names is not
required. Thus, if only one match is found between sequences names
within the MSA file and tree node names, only one tree node will
contain an associated sequence.

Also, it is important to note that sequence linking is not limited to
terminal nodes. If internal nodes are named, and such names find a
match within the provided MSA file, their corresponding sequences will
be also loaded into the tree structure.

Once a MSA is linked, sequences will be available for every tree node
through its :attr:`node.sequence` attribute.

.. literalinclude:: ../../examples/phylogenies/link_sequences_to_phylogenies.py


Visualization of phylogenetic trees
-----------------------------------

PhyloTree instances can benefit from all the features of the
programmable drawing engine. However, a built-in phylogenetic layout
is provided for convenience.

All PhyloTree instances are, by default, attached to such layout for
tree visualization, thus allowing for in-place alignment visualization
and evolutionary events labeling.

.. figure:: ../../examples/phylogenies/phylotree.png

.. literalinclude:: ../../examples/phylogenies/phylotree_visualization.py


.. _taxonomic_info:

Adding taxonomic information
----------------------------

:class:`PhyloTree` instances allow to deal with leaf names and species
names separately. This is useful when working with molecular
phylogenies, in which node names usually represent sequence
identifiers.

Species names will be stored in the :attr:`PhyloNode.species`
attribute of each leaf node. The method :func:`PhyloNode.get_species`
can be used obtain the set of species names found under a given
internal node (speciation or duplication event). Often, sequence names
do contain species information as a part of the name, and ETE can
parse this information automatically.

There are three ways to establish the species of the different tree
nodes:

- By using the three first letters of the node's name (default)
- By dynamically calling a function based on the node's name
- By setting it manually for each node


Automatic control of species info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of the default retrieval of species information::

  from ete4 import PhyloTree

  t = PhyloTree('(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));')

  print(t)
  #    ╭─┬╴Hsa_001
  #  ╭─┤ ╰╴Ptr_001
  # ─┤ ╰─┬╴Cfa_001
  #  │   ╰╴Mms_001
  #  ╰─┬╴Dme_001
  #    ╰╴Dme_002

  for n in t:
      print('Node:', n.name, '  Species:', n.species)
  # Node: Hsa_001   Species: Hsa
  # Node: Ptr_001   Species: Ptr
  # Node: Cfa_001   Species: Cfa
  # Node: Mms_001   Species: Mms
  # Node: Dme_001   Species: Dme
  # Node: Dme_002   Species: Dme


Automatic (custom) control of the species info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default behavior can be changed by using the
:func:`PhyloNode.set_species_naming_function` method or by using the
:attr:`sp_naming_function` argument of the :class:`PhyloTree` class.

Note that, using the :attr:`sp_naming_function` argument, the whole
tree structure will be initialized to use the provided parsing
function to obtain species name information.
:func:`PhyloNode.set_species_naming_function` (present in all tree
nodes) can be used to change the behavior in a previously loaded tree,
or to set different parsing functions to different parts of the tree.

Example::

  from ete4 import PhyloTree

  t = PhyloTree('(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));')

  # Let's use our own leaf name parsing function to obtain species names.
  # We just need to create a function that takes a node's name as argument
  # and return its corresponding species name.
  def get_species_name(node_name_string):
      # Species code is the first part of leaf name (separated by an
      # underscore character).
      spcode = node_name_string.split('_')[0]

      # We could even translate the code to complete names.
      code2name = {
          'Dme':'Drosophila melanogaster',
          'Hsa':'Homo sapiens',
          'Ptr':'Pan troglodytes',
          'Mms':'Mus musculus',
          'Cfa':'Canis familiaris'
      }
      return code2name[spcode]

  # Now, let's ask the tree to use our custom species naming function.
  t.set_species_naming_function(get_species_name)

  for n in t:
      print('Node:', n.name, '  Species:', n.species)
  # Node: Hsa_001   Species: Homo sapiens
  # Node: Ptr_001   Species: Pan troglodytes
  # Node: Cfa_001   Species: Canis familiaris
  # Node: Mms_001   Species: Mus musculus
  # Node: Dme_001   Species: Drosophila melanogaster
  # Node: Dme_002   Species: Drosophila melanogaster


Manual control of the species info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To disable the automatic generation of species names based on node
names, a ``None`` value can be passed to the
:func:`PhyloNode.set_species_naming_function` function. From then on,
the species attribute will not be automatically updated based on the name
of nodes and it could be controlled manually.

Example::

  from ete4 import PhyloTree

  # You can disable the automatic generation of species names.
  # To do so, you can set the species naming function to None.
  # This is useful to set the species names manually, or for reading them
  # from a newick file. Otherwise, the species property would be overwriten.
  mynewick = """
  (((Hsa_001[&&NHX:species=Human],Ptr_001[&&NHX:species=Chimp]),
  (Cfa_001[&&NHX:species=Dog],Mms_001[&&NHX:species=Mouse])),
  (Dme_001[&&NHX:species=Fly],Dme_002[&&NHX:species=Fly]));
  """

  t = PhyloTree(mynewick, sp_naming_function=None)

  for n in t:
      print('Node:', n.name, '  Species:', n.species)
  # Node: Hsa_001   Species: Human
  # Node: Ptr_001   Species: Chimp
  # Node: Cfa_001   Species: Dog
  # Node: Mms_001   Species: Mouse
  # Node: Dme_001   Species: Fly
  # Node: Dme_002   Species: Fly
