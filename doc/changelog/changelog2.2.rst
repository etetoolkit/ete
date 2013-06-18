What's new in ETE 2.2
*********************************
.. currentmodule:: ete_dev

BUGFIXES
==========

* Fixes in NeXML parser and exporting functions
* Fixed 'paste newick' functionality on the GUI
* Fixed :func:`PhyloNode.is_monophyletic` behaviour (returns True if a
  provided species matched node content and no other species are
  present).
* Fixed consistency issued in :func:`TreeNode.sort_nodes` function. 

SCRIPTS
==========
* Improvements in the standalone visualization script (a.k.a. ete2) 

??
* Added ete2dist script to calculate robinson foulds distances among trees

MINOR UNCONSISTENCIES WITH ETE 2.1           ????? PERHAPS BETTER TO move THIS TO 3.0
=============================================================================================
* Default values for :attr:`TreeNode.dist` and
  :attr:`TreeNode.support` are now set to 0.0. This fixes the problem
  of long branches leading to the root node in trees loaded from
  newick and provides. 


NEW MODULES
====================
* New :class:`EvolNode` tree object type is available as a part of
  adaptation-test extension recently developed by François Serra (see
  :doc:`../tutorial/tutorial_adaptation` in the tutorial).

  .. figure:: ../ex_figures/M2_super_profesional.png
            :scale: 100 %


NEW FEATURES
====================

* **News in core Tree instances:**

  * Added :func:`TreeNode.robinson_foulds` distance to compare the
    topology of two trees (i.e. tree.robinson_foulds(tree2)). It
    includes automatic pruning to compare trees of different
    sizes. :ref:`See tutorial and examples <robinson_foulds>`

  * Added new options to :func:`TreeNode.copy` function, allowing
    faster methods to duplicate tree node instances.
    :ref:`See tutorial and examples <copying_trees>`

  * Added :attr:`preserve_branch_length` argument to
    :func:`TreeNode.prune` and :func:`TreeNode.delete`, which allows
    to remove nodes from a tree while keeping original branch length
    distances among the remaining nodes.

  * Added :func:`TreeNode.resolve_polytomy` function to convert
    multifurcated nodes into an arbitrary structure of binary split
    nodes with distance. :ref:`See tutorial and examples
    <resolve_polytomy>`

  * Added :func:`TreeNode.get_cached_content` function, which returns
    a dictionary linking each node instance with its leaf
    content. Such a dictionary might be used as a cache to speed up
    functions that require intensive use of node
    traversing. :ref:`See tutorial and examples <cache_node_content>`
  
  * Improved :func:`TreeNode.get_ascii` function for text-based
    visualization of trees. A new `attributes` argument can be passed
    to display node attributes within the ASCII tree representation.

    :: 

        from ete2 import Tree
        t = Tree("((A, B)Internal_1:0.7, (C, D)Internal_2:0.5)root:1.3;", format=1)
        t.add_features(size=4)
        print t.get_ascii(attributes=["name", "dist", "size"])
        #
        #                            /-A, 0.0
        #             /Internal_1, 0.7
        #            |               \-B, 0.0
        # -root, 1.3, 4
        #            |               /-C, 0.0
        #             \Internal_2, 0.5
        #                            \-D, 0.0
        #


  * Random branch length and support values generation is now available
    for the :func:`TreeNode.populate` function.

  * a new argument :attr:`is_leaf_fn` is available for a number of
    traversing functions, thus allowing to provide custom stopping
    criteria when browsing a tree. This is, any node matching the
    function provided through the :attr:`is_leaf_fn` argument will be
    temporarily considered as a terminal/leaf node by the traversing
    function (tree will look as a pruned version of itself).
    :ref:`See tutorial and examples <is_leaf_fn>`

  * Added :func:`TreeNode.iter_ancestors` and
    :func:`TreeNode.get_ancestors` functions.

  * Newick parser accepts now the creation of single node trees. For
    example, a text string such as :attr:`"node1;"` will be parsed as
    a single tree node whose name is :attr:`node1`. By contrast, the
    newick string :attr:`(node1);` will be interpreted as an unnamed
    root node plus a single child named :attr:`name1`.

  * The new :func:`TreeNode.check_monophyly` method allows to check
    if a node is mono, poly or paraphyletic for a given attribute and
    values (i.e. grouped species). Although monophyly is actually a
    phylogenetic concept, the idea can be applied to any tree, so any
    topology could be queried for the monophyly of certain attribute
    values. If not monophyletic, the method will return also the type
    of relationship connecting the provided values (para- or
    poly-phyletic). :ref:`See tutorial and examples <check_monophyly>`

  * New :func:`TreeNode.get_monophyletic` method that returns a list
    of nodes in a tree matching a custom monophyly criteria.


* **News PhyloTree instances:**

  * Added :func:`PhyloNode.get_speciation_trees` method, which returns
    all possible species topologies present in a gene family tree as
    described in `Treeko <http://treeko.cgenomics.org>`_  (see `Marcet and
    Gabaldon, 2011 <http://www.ncbi.nlm.nih.gov/pubmed/21335609>`_ ).
    :ref:`See tutorial and examples <treeko>`

  * Added :func:`PhyloNode.split_by_dups` method, which returns a list
    of partial subtrees resulting from splitting a tree at duplication
    nodes. :ref:`See tutorial and examples <split_by_dup>`

  * !!! Return the distance between a species tree and a gene tree
    with multiple duplications using Treeko distance.

  * Added :func:`PhyloNode.collapse_lineage_specific_expansions` method,
    which returns a pruned version of a tree, where nodes representing
    lineage specific expansions are converted into a single leaf node. 
    :ref:`See tutorial and examples <collapse_expansions>`

* **News on sequence and multiple sequence alignment parsing:** 

  * added the option to disable the automatic correction of duplicated
    names when loading :class:`SeqGroup` data from phylip and fasta
    files.

* **News on tree visualization and image rendering:**

  * node style attributes can now be modified without the need of
    initialisation by directly accessing the
    :attr:`TreeNode.img_style` attribute.

  * Multiple layout functions can now be provided to combine their
    functionality.

  * Several predefined :attr:`COLOR_SCHEMES` are provided for help
    creating better chart face representations convenience.

* **News on node faces:**

  * Improved :class:`SequenceFace`: Sequence sites are now rendered
    one by one, allowing interaction with each of them and getting rid
    of the previous pixmap size limitation. Site image dimensions and
    colours are now configurable.

  * Added new :class:`SeqMotifFace` class, which extends
    :class:`SequenceFace`. This new face type allows to represent
    sequences as a succession of domain/motif elements, as a condensed
    color based sequence representation or as a combination of
    all. Gaps in sequences are also taken into account and shown as
    black space or a flat line.  You can check some examples at the
    tutorial?????

  * Added :class:`PieChartFace` and :class:`BarChartFace` face types
    for built-in representation of statistics attached to nodes.

  * Improved :class:`ImgFace` class, now accepting on the fly image
    scaling.

  * Shape Faces, RoundRect, Triangle, Diamond, RectFace

* **News on the GUI**

  * Allows image region selection.
  * Allows zooming on selected regions or specific nodes (Z - zoomIn, X - zoomOut, R - focus region).
  * :kbd:`C-c` will now interrupt the GUI application when started
    from a terminal.
  * Added keyboard-based node navigation (click on a node and play the
    arrow keys).

