What's new in ETE 2.1
*********************************
.. currentmodule:: ete_dev

* The drawing engine has been fully rewritten to provide many new features:

  * Added *circular tree drawing* mode
  * Added support for *floating faces* in nodes
  * Added tree *title face block* (Text or images that rendered on top of the tree)
  * Added tree *legend face block* (Text or images that rendered as image legend)
  * Possibility of drawing *aligned faces as a table*
  * Added several *face attributes*:

    * face border
    * face background color
    * left, right, top and bottom margins
    * face opacity
    * horizontal and vertical alignment (useful when faces are rendered as table)
  * node styles can be set outside layout function (allows to save and export fixed drawing attributes)
  * Added support for branch-top and branch-down face positions 
  * Added Circle Faces
  * Added Tree Faces (tree instances can be drawn as faces of other trees)
  * Added support for QGraphicsItem based faces
  * AttrFace accepts prefix and suffix text 
  * Added :class:`treeview.TreeImage` class to control general aspects regarding tree drawing
  * added full support for SVG image rendering   
* Core methods:

   * Added :func:`TreeNode.copy`:  returns an exact and independent copy of node and all its attributes
   * Added :func:`TreeNode.convert_to_ultrametric`: converts all branch lengths to allow leaves to be equidistant to root
   * Added :func:`TreeNode.sort_descendants`: sort tree branches according to node names.
   * nodes can now be fully exported using cPickle 
   * newick parser can read distances and support values using scientific notation
   * :func:`TreeNode.swap_childs` method has changed to :func:`TreeNode.swap_children`
* Added :mod:`ete_dev.nexml` module (read and write nexml format)
* Added :mod:`ete_dev.phyloxml` module (read and write phyloxml format)
* Added :mod:`ete_dev.webplugin` module: Allows to create interactive web tree applications 
* Added :class:`PhylomeDB3Connector`

* Added new examples

* Bug Fixes and improvements: 
  
   * Fix: :func:`TreeNode.get_common_ancestor` accepts a list of nodes 
   * Fix: Fast scroll based zooming produced tree inversion 
   * Fix: Phylip parser does not truncate long names by default
   * Fix: "if not node: do something" syntax was using a len(node)
     test, which made it totally inefficient. Now, any node instance
     returns always True.


* Improved documentation tutorial and reference guide!
