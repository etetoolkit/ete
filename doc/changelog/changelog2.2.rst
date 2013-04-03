What's new in ETE 2.2
*********************************
.. currentmodule:: ete_dev

BUGFIXES
^^^^^^^^^^

* NeXML parser and exporting functions
* Fixed 'paste newick' functionality on the GUI

SCRIPTS
^^^^^^^^^^^
* Improvements in ete2 script

MINOR UNCONSISTENCIES WITH ETE 2.1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Default value of :attr:`TreeNode.dist` and :attr:`TreeNode.support`
  is now 0.0. Fixes the problem of long branches leading to the root
  node in trees loaded from plain newick.


NEW FEATURES
^^^^^^^^^^^^^^

* News in core Tree instances: 

  * Added :func:`TreeNode.robinson_foulds` distance to compare the
    topology of two trees (i.e. tree.robinson_foulds(tree2)). It
    includes automatic pruning to compare trees of different sizes. 

  * Added new options to :func:`TreeNode.copy` function, allowing
    faster methods to duplicate tree node instances.

  * Added :attr:`preserve_branch_length` argument to
    :func:`TreeNode.prune` and :func:`TreeNode.delete`, which allows
    to remove nodes from a tree while keeping original branch length
    distances among the remaining nodes.

  * Added :func:`TreeNode.resolve_polytomy` function to convert
    multifurcated nodes into an arbitrary structure of binary split
    nodes with distance. 

  * Added :func:`TreeNode.get_tree_content_cache` function, which
    returns a dictionary linking each node instance with its leaf
    content. Such a dictionary might be used as a cache to speed up
    functions that require intensive use of node traversing. 
  
  * Improved :func:`TreeNode.get_ascii` function for text-based
    visualization of trees. A new `attributes` argument can be passed
    to display the value of node features. 

  * Random branch support and lengths generation can be switched off
    and on when :func:`TreeNode.populate` is used. 

  * a new argument `is_leaf_fn` is available if several traversing
    functions allowing to provide custom stopping criteria when
    browsing a tree. This is, any node matching the function provided
    using `is_leaf_fn` will be considered as a terminal/leaf node,
    thus preventing descend through its children. 

  * Added :func:`TreeNode.iter_ancestors` and
    :func:`TreeNode.get_ancestors` functions.

  * Newick parser accepts now the creation of single node trees. For
    example, a text string as `"node1;"` will be parsed as a single
    tree node with names `node1`. By contrast, `(node1);` will be
    interpreted as a tree with a single child node named `name1`.

  * sort_nodes changed ???????????????   hmg?????????

* News PhyloTree instances: 

  * Added :func:`PhyloNode.get_speciation_trees` method, which returns
    all possible species topologies present in a gene family tree. This 
    function used the method described in XXXXXX as XXXXXX, 

  * Added :func:`PhyloNode.split_by_dup` method, which returns a list
    of partial subtrees resulting from splitting a tree at duplication
    nodes.

  * !!! Return the distance between a species tree and a gene tree
    with multiple duplications using Treeko distance.

  * get_speciation_trees_recursive?, split_by_dups

  * get_node2species

  * Added :func:`PhyloNode.get_age_balanced_outgroup`, a better way to
    root gene trees based on species content and size of duplications.

* News on sequence and multiple sequence alignment parsing 

  * added the option to switch off duplicate name correction when
    loading :class:`SeqGroup` data from phylip and fasta files.

* News on tree visualization and image rendering

  * node style attributes can now be modified without need of
    initialisation by accessing the :attr:`TreeNode.img_style`
    attribute.

  * Multiple layout functions can now be provided for combined
    rendering.

  * Several predefined :attr:`COLOR_SCHEMES` are provided for
    convenience.

* News on node faces

  * Added new :class:`SeqMotifFace` class, which extends and improves
    older :class:`SequenceFace` (now deprecated and not
    maintained). The new face type allows to represent sequences as a
    succession of domain/motif elements, as a condensed color based
    sequence representation or as a combination of all. Gaps in
    sequences are also taken into account. You can check some examples
    at the tutorial?????

  * Added :class:`PieChartFace` and :class:`BarChartFace` types to
    add built-in representation of statistics attached to nodes. 

  * Improved :class:`ImgFace` class, that now accepts on the fly image
    scaling. 

  * Shape Faces, RoundRect, Triangle, Diamond, RectFace

* News on the GUI

    * Allows image region selection 
    * Allows zooming on selected nodes or image regions
    * :kbd:`C-x C-f` will now interrupt the GUI application. 
    * Added keyboard-based node navigation

NEW MODULES

* New EvolTree module
    * Added new Tree class method :class:`EvolTree`, implementing a number of
      options for selection tests.
