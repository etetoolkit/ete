What's new in ETE 2.1
*********************************

.. currentmodule:: ete_dev

* The drawing engine has been completely rewritten to provide the
  following new features:

  * Added :class:`TreeStyle` class allowing to set the following

    * Added **circular tree drawing** mode
    * Added tree *title face block* (Text or images that rendered on top of the tree)
    * Added tree *legend face block* (Text or images that rendered as image legend)
    * Added support for *tree rotation and orientation*
    * Possibility of drawing *aligned faces as a table*
    * Added header and footer regions for aligned faces.
    * And more! Check :class:`TreeStyle` documentation
  * Added new face positions **float**, **branch-top** and
    **branch-bottom**. See tutorial (:ref:`sec:node_faces`) for more details.

  * Added several *face attributes*:

    * face border
    * face background color
    * left, right, top and bottom margins
    * face opacity
    * horizontal and vertical alignment (useful when faces are rendered as table)
  * Added support for predefined :class:`NodeStyle`, which can be set
    outside the layout function (allows to save and export image rendering info)
  * Added new face types:
     * :class:`CircleFace` (basic circle/sphere forms)
     * :class:`TreeFace` (trees within trees)
     * :class:`ItemFace` (create custom and interactive QtGraphicsItems)
  * Improved faces:
     * :class:`AttrFace` accepts prefix and suffix text, as well as a
       text formatter function. :attr:`fstyle` argument can be set to
       ``italic``
     * :class:`TextFace`: :attr:`fstyle` argument  can be set to ``italic``
  * Save and export images
     * Added full support for SVG image rendering  
     * Added more options to the :func:`TreeNode.render` function to
       control image size and resolution
  * Added support for :data:`SVG_COLORS` names in faces and node styles
* Core methods:
   * Added :func:`TreeNode.copy`:  returns an exact and independent copy of node and all its attributes
   * Added :func:`TreeNode.convert_to_ultrametric`: converts all branch lengths to allow leaves to be equidistant to root
   * Added :func:`TreeNode.sort_descendants`: sort tree branches according to node names.
   * Added :func:`TreeNode.ladderize`: sort tree branches according to partition size
   * Added :func:`TreeNode.get_partitions`: return the set of all possible partitions grouping leaf nodes
   * nodes can now be fully exported using cPickle 
   * newick parser can read distances and support values using scientific notation
   * :func:`TreeNode.swap_childs` method has changed to :func:`TreeNode.swap_children`
* Added :mod:`ete_dev.nexml` module (read and write nexml format)
* Added :mod:`ete_dev.phyloxml` module (read and write phyloxml format)
* Added :mod:`ete_dev.webplugin` module: Allows to create interactive web tree applications 
* Added :class:`PhylomeDB3Connector`
* Bug Fixes and improvements: 
   * Fix: :func:`TreeNode.get_common_ancestor` accepts a single argument (node or list of nodes) instead of a succession or nodes. It can also return the path of each node to the parent.
   * Fix: Fast scroll based zoom-in was producing tree image inversions
   * Fix: Phylip parser does not truncate long names by default
   * Fix: "if not node" syntax was using a len(node) test, which made
     it totally inefficient. Now, the same expression returns always *True*
   * Improvement: Traversing methods are now much faster (specially preorder and levelorder)
   * Improvement: Faster populate function (added possibility of random and non-random branch lengths)
   * Improvement: Faster prune function
   * Improvement: unicode support for tree files
   * Improvement: Added newick support for scientific notation in branch lengths
* Improved documentation tutorial and reference guide!
   * A better library reference 
   * New examples section
