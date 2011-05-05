.. module:: ete_dev.phylo
  :synopsis: Extends Tree object: add orthology and paralogy methods, species aware nodes, links to multiple sequence alignments
.. moduleauthor:: Jaime Huerta-Cepas
:Author: Jaime Huerta-Cepas

Phylogenetic Trees
********************

.. contents::

Overview
================

Phylogenetic trees are the result of most evolutionary analyses. They
represent the evolutionary relationships among a set of species or, in
molecular biology, a set of homologous sequences.

The :class:`PhyloTree` class is an extension of the base :class:`Tree`
object, providing a appropriate way to deal with phylogenetic trees.
Thus, while leaves are considered to represent species (or sequences
from a given species genome), internal nodes are considered ancestral
nodes. A direct consequence of this is, for instance, that every split
in the tree will represent a speciation or duplication event.


Linking Phylogenetic Trees and Multiple Sequence Alignments
===========================================================

:class:`PhyloTree` instances allow molecular phylogenies to be linked
to the Multiple Sequence Alignments (MSA). To associate a MSA with a
phylogenetic tree you can use the :func:`PhyloNode.link_to_alignment`
method. You can use the :attr:`alg_format` argument to specify its
format.  Phylip sequential ("**phylip**"), Phylip interleaved
("**iphylip**") and Fasta ("**fasta**") formats are currently
supported. Given that Fasta format are not only applicable for MSA but
also for **Unaligned Sequences**, you may also associate sequences of
different lengths with tree nodes.  

::
  
  from ete_dev import PhyloTree
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
  t = PhyloTree("(((seqA,seqB),seqC),seqD);")
  t.link_to_alignment(alignment=fasta_txt, alg_format="fasta") 

The same could be done at the same time the tree is being loaded, by
using the :attr:`alignment` and :attr:`alg_format` arguments of
:class:`PhyloTree`.

::

  # Load a tree and link it to an alignment. 
  t = PhyloTree("(((seqA,seqB),seqC),seqD);", alignment=fasta_txt, alg_format="fasta")


As currently implemented, sequence linking process is not strict,
which means that a perfect match between all node names and sequences
names **is not required**. Thus, if only one match is found between
sequences names within the MSA file and tree node names, only one tree
node will contain an associated sequence. Also, it is important to
note that sequence linking is not limited to terminal nodes. If
internal nodes are named, and such names find a match within the
provided MSA file, their corresponding sequences will be also loaded
into the tree structure. Once a MSA is linked, sequences will be
available for every tree node through its :attr:`node.sequence`
attribute.

::
  
  from ete_dev import PhyloTree
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
  iphylip_txt = """
   4 76
        seqA   MAEIPDETIQ QFMALT---H NIAVQYLSEF GDLNEALNSY YASQTDDIKD RREEAHQFMA
        seqB   MAEIPDATIQ QFMALTNVSH NIAVQY--EF GDLNEALNSY YAYQTDDQKD RREEAHQFMA
        seqC   MAEIPDATIQ ---ALTNVSH NIAVQYLSEF GDLNEALNSY YASQTDDQPD RREEAHQFMA
        seqD   MAEAPDETIQ QFMALTNVSH NIAVQYLSEF GDLNEAL--- ---------- -REEAHQ---
               LTNVSHQFMA LTNVSH
               LTNVSH---- ------
               LTNVSH---- ------
               -------FMA LTNVSH
  """
  # Load a tree and link it to an alignment. As usual, 'alignment' can
  # be the path to a file or data in text format.
  t = PhyloTree("(((seqA,seqB),seqC),seqD);", alignment=fasta_txt, alg_format="fasta")
   
  #We can now access the sequence of every leaf node
  print "These are the nodes and its sequences:"
  for leaf in t.iter_leaves():
      print leaf.name, leaf.sequence
  #seqD MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
  #seqC MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
  #seqA MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
  #seqB MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
  #
  # The associated alignment can be changed at any time
  t.link_to_alignment(alignment=iphylip_txt, alg_format="iphylip")
  # Let's check that sequences have changed
  print "These are the nodes and its re-linked sequences:"
  for leaf in t.iter_leaves():
      print leaf.name, leaf.sequence
   
  #seqD MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAHQ----------FMALTNVSH
  #seqC MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAHQFMALTNVSH----------
  #seqA MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAHQFMALTNVSHQFMALTNVSH
  #seqB MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAHQFMALTNVSH----------
  #
  # The sequence attribute is considered as node feature, so you can
  # even include sequences in your extended newick format!
  print t.write(features=["sequence"], format=9)
   
  #
  #
  # (((seqA[&&NHX:sequence=MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAHQF
  # MALTNVSHQFMALTNVSH],seqB[&&NHX:sequence=MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSY
  # YAYQTDDQKDRREEAHQFMALTNVSH----------]),seqC[&&NHX:sequence=MAEIPDATIQ---ALTNVSHNIA
  # VQYLSEFGDLNEALNSYYASQTDDQPDRREEAHQFMALTNVSH----------]),seqD[&&NHX:sequence=MAEAPD
  # ETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAHQ----------FMALTNVSH]);
  #
  # And yes, you can save this newick text and reload it into a PhyloTree instance.
  sametree = PhyloTree(t.write(features=["sequence"]))
  print "Recovered tree with sequence features:"
  print sametree
   
  #
  #                              /-seqA
  #                    /--------|
  #          /--------|          \-seqB
  #         |         |
  #---------|          \-seqC
  #         |
  #          \-seqD
  #
   
  print "seqA sequence:", (t&"seqA").sequence
  # MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAHQFMALTNVSHQFMALTNVSH

.. _sec:using-taxonomic-data:

Using Taxonomic Data
====================

:class:`PhyloTree` instances allow to deal with leaf names and species
names separately.  This is useful when working with molecular
phylogenies, in which node names usually represent sequence
identifiers.  Species names will be stored in the :attr:`PhyloNode.species`
attribute of each leaf node. The method :func:`PhyloNode.get_species`
can be used obtain the set of species names found under a given
internal node (speciation or duplication event).

Often, sequence names do contain species information as a
part of the name, and ETE will help to do it automatically. By
default, **the first three letters** of every sequence name are taken
as species codes. 

::

  from ete_dev import PhyloTree
  # Reads a phylogenetic tree (using default species name encoding)
  t = PhyloTree("(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));")
  #                              /-Hsa_001
  #                    /--------|
  #                   |          \-Ptr_001
  #          /--------|
  #         |         |          /-Cfa_001
  #         |          \--------|
  #---------|                    \-Mms_001
  #         |
  #         |          /-Dme_001
  #          \--------|
  #                    \-Dme_002
  #
  # Prints current leaf names and species codes
  print "Deafult mode:"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species
  # node: Dme_001 Species name: Dme
  # node: Dme_002 Species name: Dme
  # node: Hsa_001 Species name: Hsa
  # node: Ptr_001 Species name: Ptr
  # node: Cfa_001 Species name: Cfa
  # node: Mms_001 Species name: Mms


However, this behavior can be changed by using the
:func:`PhyloNode.set_species_naming_funcion` method or by using the
:attr:`sp_naming_function` argument of the :class:`PhyloTree` class.
Note that, using the :attr:`sp_naming_function` argument, the whole
tree structure will be initialized to use the provided parsing
function to obtain species name
information. :func:`PhyloNode.set_species_naming_function` (present in
all tree nodes) can be used to change the behavior in a previously
loaded tree, or to set different parsing function to different parts
of the tree.

::

  from ete_dev import PhyloTree
  # Reads a phylogenetic tree
  t = PhyloTree("(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));")

  # Let's use our own leaf name parsing function to obtain species
  # names. All we need to do is create a python function that takes
  # node's name as argument and return its corresponding species name.
  def get_species_name(node_name_string):
      # Species code is the first part of leaf name (separated by an
      #  underscore character)
      spcode = node_name_string.split("_")[0]
      # We could even translate the code to complete names
      code2name = {
        "Dme":"Drosophila melanogaster",
        "Hsa":"Homo sapiens",
        "Ptr":"Pan troglodytes",
        "Mms":"Mus musculus",
        "Cfa":"Canis familiaris"
        }
      return code2name[spcode]
   
  # Now, let's ask the tree to use our custom species naming function
  t.set_species_naming_function(get_species_name)
  print "Custom mode:"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species

  # node: Dme_001 Species name: Drosophila melanogaster
  # node: Dme_002 Species name: Drosophila melanogaster
  # node: Hsa_001 Species name: Homo sapiens
  # node: Ptr_001 Species name: Pan troglodytes
  # node: Cfa_001 Species name: Canis familiaris
  # node: Mms_001 Species name: Mus musculus


To disable the automatic generation of species names (the user will be
expected to set such information manually), **None** can be passed as
the species naming function.

::

  from ete_dev import PhyloTree
  # Reads a phylogenetic tree
  t = PhyloTree("(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));")

  # Of course, you can disable the automatic generation of species
  # names. To do so, you can set the species naming function to
  # None. This is useful to set the species names manually or for
  # reading them from a newick file. Other wise, species attribute would
  # be overwriten
  mynewick = """
  (((Hsa_001[&&NHX:species=Human],Ptr_001[&&NHX:species=Chimp]),
  (Cfa_001[&&NHX:species=Dog],Mms_001[&&NHX:species=Mouse])),
  (Dme_001[&&NHX:species=Fly],Dme_002[&&NHX:species=Fly]));
  """
  t = PhyloTree(mynewick, sp_naming_function=None)
  print "Disabled mode (manual set)"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species
   
  # node: Dme_001 Species name: Fly
  # node: Dme_002 Species name: Fly
  # node: Hsa_001 Species name: Human
  # node: Ptr_001 Species name: Chimp
  # node: Cfa_001 Species name: Dog
  # node: Mms_001 Species name: Mouse  

Full example:

::

  from ete2 import PhyloTree
  # Reads a phylogenetic tree (using default species name encoding)
  t = PhyloTree("(((Hsa_001,Ptr_001),(Cfa_001,Mms_001)),(Dme_001,Dme_002));")
  #                              /-Hsa_001
  #                    /--------|
  #                   |          \-Ptr_001
  #          /--------|
  #         |         |          /-Cfa_001
  #         |          \--------|
  #---------|                    \-Mms_001
  #         |
  #         |          /-Dme_001
  #          \--------|
  #                    \-Dme_002
  #
  # Prints current leaf names and species codes
  print "Deafult mode:"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species
  # node: Dme_001 Species name: Dme
  # node: Dme_002 Species name: Dme
  # node: Hsa_001 Species name: Hsa
  # node: Ptr_001 Species name: Ptr
  # node: Cfa_001 Species name: Cfa
  # node: Mms_001 Species name: Mms
  #
  # We can also use our own leaf name parsing function to obtain species
  # names. All we need to do is create a python function that takes
  # node's name as argument and return its corresponding species name.
  def get_species_name(node_name_string):
      # Species code is the first part of leaf name (separated by an
      #  underscore character)
      spcode = node_name_string.split("_")[0]
      # We could even translate the code to complete names
      code2name = {
        "Dme":"Drosophila melanogaster",
        "Hsa":"Homo sapiens",
        "Ptr":"Pan troglodytes",
        "Mms":"Mus musculus",
        "Cfa":"Canis familiaris"
        }
      return code2name[spcode]
   
  # Now, let's ask the tree to use our custom species naming function
  t.set_species_naming_function(get_species_name)
  print "Custom mode:"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species
   
  # node: Dme_001 Species name: Drosophila melanogaster
  # node: Dme_002 Species name: Drosophila melanogaster
  # node: Hsa_001 Species name: Homo sapiens
  # node: Ptr_001 Species name: Pan troglodytes
  # node: Cfa_001 Species name: Canis familiaris
  # node: Mms_001 Species name: Mus musculus
  #
  # Of course, you can disable the automatic generation of species
  # names. To do so, you can set the species naming function to
  # None. This is useful to set the species names manually or for
  # reading them from a newick file. Other wise, species attribute would
  # be overwriten
  mynewick = """
  (((Hsa_001[&&NHX:species=Human],Ptr_001[&&NHX:species=Chimp]),
  (Cfa_001[&&NHX:species=Dog],Mms_001[&&NHX:species=Mouse])),
  (Dme_001[&&NHX:species=Fly],Dme_002[&&NHX:species=Fly]));
  """
  t = PhyloTree(mynewick, sp_naming_function=None)
  print "Disabled mode (manual set):"
  for n in t.get_leaves():
      print "node:", n.name, "Species name:", n.species
   
  # node: Dme_001 Species name: Fly
  # node: Dme_002 Species name: Fly
  # node: Hsa_001 Species name: Human
  # node: Ptr_001 Species name: Chimp
  # node: Cfa_001 Species name: Dog
  # node: Mms_001 Species name: Mouse
  #
  # Of course, once this info is available you can query any internal
  # node for species covered.
  human_mouse_ancestor = t.get_common_ancestor("Hsa_001", "Mms_001")
  print "These are the species under the common ancestor of Human & Mouse"
  print '\n'.join( human_mouse_ancestor.get_species() )
  # Mouse
  # Chimp
  # Dog
  # Human
   
  # We can also check for the monophyly of nodes:
  for node in t.traverse():
     if len(node)>1 and node.is_monophyletic(["Fly"]):
        print "Fly specific expansion!:"
        print node


  

:: 
   
  Example


.. _sec:dating-phylogenetic-nodes:

Dating Phylogenetic Nodes
=========================

Nodes in molecular phylogenies can be interpreted as evolutionary events. They
can represent the duplication of an ancestral sequence or the speciation event
that separated the evolution of two ancestral sequences. In any case, because
nodes represent ancestral events, they can be located at a given moment in the
evolution. This is, we can date evolutionary events.

There are many ways to infer such information. Most approaches are based on the
comparison of the sequences affected by a given event. However, these methods
suffer from several limitations. An alternative approach that has been
shown to overcome some of such limitations is to date evolutionary events
according the topology of phylogenetic trees ( In brief, the relative age of any
evolutionary event can be established by detecting the oldest taxonomic group
affected by such event. Given that in phylogenies nodes are events, this is
something that can be easily evaluated by looking at the species under each
node. Although this task can be done manually, ETE implements a method to
automatize the process. Thus, by defining a python dictionary containing the
conversion between **species names** and the considered **taxonomic levels,
**phylogenetic nodes can be easily dated. The **get_age() **method, found in
every node, can be used to this end. Obviously, the more taxonomic levels are
defined, the more precise is time estimation. For instance, if we consider a
tree in which several vertebrate species are represented, we could define an age
dictionary like this:

.. % 

In which each number refers to a taxonomic group, and older taxonomic groups
have higher values. Then, any internal node could be easily mapped to an
evolutionary period by executing: **node.get_date(vertebrates_taxa_levels)**.


Detecting evolutionary events
=============================

There are several ways to automatically detect duplication and speciation nodes
within molecular phylogenies. ETE provides the two most extended methodologies.
One implements the algorithm described in and is based on the species overlap
between partitions and thus does not depend on the availability of a species
tree (species overlap). The second one, which requires the comparison between
the gene tree and a previously defined species tree, implements a strict tree
reconciliation algorithm [Page and Charleston, 1997]. By detecting evolutionary
events, orthology and paralogy relationships among sequences are also inferred.

.. % 

Both methods, species overlap and tree reconciliation, can be used to **label
each tree node as a duplication or speciation event**.** **Thus, after applying
any of the algorithms, original tree nodes will contain a new attribute named
**evoltype**, which can take the following values: **"D" (duplication), "S"
(speciation), "L" (lost linage)**. Additionally, a list of all the detected
events is returned. Each event is a python object of type **EvolEvent**,
containing its basic information:

``event.etype:``
   ``event type (``\ D'', ``S'' or``\ L'')``

``event.in_seqs:``
   ``A list of sequences at one side of the event .``

``event.out_seqs:``
   ``A list of sequences at the other side of the event.``

``event.node:``
   ``Link to the phylogenetic node that defines the event``

``event.sos:``
   ``Species Overlap Score (None if tree reconciliation was used)``

Other attributes may be found in events instances, however they are not stable
yet.

If an event represents a duplication, ``in_seqs``\ ````**are all paralogous
**to`` out_seqs\ ``. Similarly, if an event represents a speciation,``\ in_seqs\
``````**are all orthologous **to\ ``out_seqs``.

While tree reconciliation must always be used from an internal node, species
overlap allows to track only all the evolutionary events involving a specific
tree leaf.


Species Overlap (SO) algorithm
------------------------------

In order to apply the SO algorithm, you can use the
:func:`PhyloNode.get_descendant_evol_events` method (it will map all
events under the current node) or the
:func:`PhyloNode.get_my_evol_events` method (it will map only the
events involving the current node, usually a leaf node).

By default the **species overlap score (SOS) threshold** is set to
0.0, which means that a single species in common between two node
branches will rise a duplication event. This has been shown to preform
the best with real data, however you can adjust the threshold using
the **sos_thr** argument present in both methods.


Tree reconciliation algorithm
---------------------------------------

Tree reconciliation algorithm uses a predefined species tree to infer the genes
losses that explain a given gene tree topology. By doing this, it infers also
the duplication and speciation events. To perform a strict tree reconciliation
analysis over a given node in a molecular phylogeny you can use the
**node.reconcile()** method, which requires a species tree as its first
argument. The species tree (another PhyloTree instance) must contain the
topology of the species represented in the gene tree. Moreover, leaf names in
the species tree must match the species names in the gene tree (by default, the
first 3 letters of the gene tree leaf names) (see
:ref:`sec:using-taxonomic-data`).

As a result, the :func:`PhyloNode.reconcile` method will label the
original gene tree nodes as duplication or speciation, will return the
list of inferred events, and will return a new **reconcilied tree**,
in which inferred gene losses are present and labeled.


Visualization of phylogenetic trees
===================================

A special set of visualization rules (see chapter
:ref:`cha:the-programmable-tree`) are provided with the phylogenetic extension
as the **phylogeny** layout function. By default, this layout function will be
used to show and render any PhyloTree instance, thus handling the visualization
of MSAs, evolutionary events, and taxonomic information. However, you can
change/extend this layout by providing a custom layout function.

The **SeqFace()** class is also provided for convenience. It allows to add nodes
faces with the coloured sequence associated to each node.


Example: A reconciled tree showing inferred evolutionary events, gene losses and node's sequences
-------------------------------------------------------------------------------------------------

.. % 
