.. module:: ete_dev.phylo
  :synopsis: Extends Tree object: add orthology and paralogy methods, species aware node, links to multiple sequence alignments
.. moduleauthor:: Jaime Huerta-Cepas
:Author: Jaime Huerta-Cepas


********************
Phylogenetic Trees
********************
.. versionadded:: 2.1


Phylogenetic trees are the result of most evolutionary analyses. They represent
the evolutionary relationships among a set of species or, in molecular biology,
a set of homologous sequences.

The :class:`PhyloTree` class provides a proper way to deal with phylogenetic trees.
Thus, while leaves are assumed to represent species (or sequences from a given
species genome), internal nodes are considered the ancestral states leading to
current species. A consequence of this is, for instance, that each bifurcation
can be considered as a speciation or a duplication event.

**PhyloTree** instances extend the **Tree** class with several specific method
that apply only for the analysis of phylogenetic trees.


Linking Phylogenetic Trees and Multiple Sequence Alignments
===========================================================

:class:`PhyloTree` instances allow molecular phylogenies to be linked
to the Multiple Sequence Alignments (MSA). To associate a MSA with a
phylogenetic tree you can use the **link_to_alignment()** method
present in any PhyloTree instance, which receives the path of an MSA
file as first argument or, alternatively, a text string containing the
MSA. Currently, **the following sequence file formats are supported:
**

.. % 

**Fasta** format is assumed by default, but you can change this by setting the
**alg_format** argument. Given that such formats are not only applicable for MSA
but also for **Unaligned Sequences**, you may also associate sequences of
different lengths with tree nodes. Alternatively to this method, MSAs can be
directly passed to the PhyloTree constructor and sequences will be automatically
linked with terminal nodes: i.e.) **PhyloTree("mytreeFile", "myAlginmentFile",
format=0, alg_format="iphylip") **

As currently implemented, sequence linking process is not strict, which means
that a perfect match between all node names and sequences names is **not
required**. Thus, if only one match is found between sequences names within the
MSA file and tree node names, only one tree node will contain an associated
sequence. Also, it is important to note that sequence linking is not limited to
terminal nodes. If internal nodes are named, and such names find a match within
the provided MSA file, their corresponding sequences will be also loaded into
the tree structure. Once a MSA is linked, sequences will be available for every
tree node through its** node.sequence** attribute.


.. _sec:using-taxonomic-data:

Using Taxonomic Data
====================

PhyloTree instances allow to deal with leaf names and species names separately.
This is useful when working with molecular phylogenies, in which leaves are
usually encoded using sequence names but species names. You could easily solve
this by annotating each terminal node according to its source species. However,
PhyloTree instances can automatically deal with this issue. Thus, when a
phylogenetic tree is loaded, species names (codes, key names or fingerprints)
are automatically derived from the **three first letters of leaf names**.
Although, you can indeed change this behavior by using a custom parsin function.
By doing this, you can easily load taxonomy-aware molecular phylogenies. The
attribute **node.species** will be present in every node and stores the inferred
species name, while the method **get_species()** can be used to retrieve all
species names under a given ancestral node.

There are two ways of setting the automatic species name generation:

#. using the** **PhyloTree **sp_naming_function** argument. The whole tree
   structure will be initialized to use the provided parsing function to obtain
   species name information.

#. using the **set_species_naming_function** method (present in all tree nodes),
   which can be used to change the behavior in a previously loaded tree, or to set
   different parsing function to different

#. parts of the tree.

In both cases, possible values are **None **(to disable automatic generation of
species names)** **or the **reference to a custom python function**.


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
suffer from several limitations (REF). An alternative approach that has been
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
**node.get_descendant_evol_events()** method (it will map all events under the
current node) or the** node.get_my_evol_events()** method (it will map only the
events involving the current node, usually a leaf node).

By default the **species overlap score (SOS) threshold** is set to 0.0, which
means that a single species in common between two node branches will rise a
duplication event. This has been shown to preform the best with real data,
however you can adjust the threshold using the **sos_thr** argument present in
both methods.


Example2: Tree reconciliation algorithm
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

As a result, the **reconcile()** method will label the original gene tree nodes
as duplication or speciation, will return the list of inferred events, and will
return a new **reconcilied tree**, in which inferred gene losses are present and
labeled.


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
