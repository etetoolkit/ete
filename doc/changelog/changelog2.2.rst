What's new in ETE 2.2
*********************************

.. currentmodule:: ete_dev

* Improvements in ete2 script

* Default value of :attr:`TreeNode.dist` and :attr:`TreeNode.support`
  is now 0.0. Fixes the problem of long branches leading to the root
  node in trees loaded from plain newick.

* News in Tree instances: 

  * Added :func:`TreeNode.robinson_foulds` distance to compare the
    topology of two trees.

  * Added new options to :func:`TreeNode.copy` function, allowing
    faster methods to duplicate tree node instances.

  * Added :attr:`preserve_branch_length` argument to
    :func:`TreeNode.prune` and :func:`TreeNode.delete`, which allows
    to remove nodes for a tree while keeping original branch length
    distances among the remaining nodes.

* News PhyloTree instances: 

  * Added :func:`PhyloNode.get_speciation_trees` method, which returns
    all possible species topologies present in a gene family tree.

  * :func:`PhyloNode.split_by_dup`

  * Return the distance between a species tree and a gene tree with
    multiple duplications using Treeko distance.

  * Added :func:`PhyloNode.get_age_balanced_outgroup`

* News on Faces

  SeqFace improvements
  ImgFace accepts scaling
  added COLOR_SCHEMES
  improved ChartFaces
  rectFace

* GUI

    Allows image region selection 
    Allows zoom of selected nodes or image regions
    Ctrl-C will now interrupt the GUI application. 
    Added keyboard-based node navigation
    Fixed 'paste newick' functionality

* New EvolTree module

    Added new Tree class method :class:`EvolTree`, implementing a number of
    options for selection tests.
