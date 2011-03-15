.. module:: ete_dev

*********************************
Changelog ete 2.1
*********************************

* The drawing engine has been fully rewritten to provide many new features:
   * Show aligned faces as a table.
   * Support for faces around trees (header, footers)
   * Circular and rectangular rendering modes
   * Support for floating faces in nodes
   * Support for margins and opacity in all faces
   * node styles can be set outside layout function (allows to save and export fixed drawing attributes)
   * Added support for branch-top and branch-down face positions 
   * Added Circle Faces
   * Added Tree Faces (tree instances can be drawn as faces of other trees)
   * Added support for QGraphicsItem based faces
   * AttrFace accepts prefix and suffix text 
   * Added :class:`TreeImage` class to control general aspects regarding tree drawing
   * added support for SVG image rendering   

* Core methods:
   * Added :func:`Tree.copy`:  returns an exact and independent copy of node and all its attributes
   * Added :func:`Tree.convert_to_ultrametric`: converts all branch lengths to allow leaves to be equidistant to root
   * Added :func:`Tree.sort_descendants`: sort tree branches according to node names.
   * nodes can now be fully exported using cPickle 
   * newick parser can read distances and support values using scientific notation

* Added :mod:`nexml` module (supports read and write nexml format)

* Added :mod:`phyloxml` module (supports read and write phyloxml format)

* Added :mod:`webplugin` module: Allows to create interactive web tree applications 

* Added :class:`PhylomeDB3Connector`

* Improved documentation and reference guide

* Bug Fixes and improvements: 
  
   * Fix: :func:`Tree.get_common_ancestor` accepts a list of nodes 
   * Fix: Fast scroll based zooming produced tree inversion 
   * Fix: Phylip parser does not truncate long names by default
   * Fix: "if not node: do something" syntax was using a len(node)
     test, which made it totally inefficient. Now, any node instance
     returns always True.


