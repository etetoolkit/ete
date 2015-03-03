Changelog
*********************************
.. currentmodule:: ete2

.. contents::

ETE 2.3
===================

Bug fixes 
==============
  
* fixes several minor bugs when retrieving extra attributes in
  :func:`PhyloNode.get_speciation_trees`.

New Modules
=============

* **ncbi taxonomy** 

It provides the class `class:NCBITaxa`, which allows to query a locally parsed
taxonomy database. It provides taxid-name translations, tree annotation tools
and other handy tools.

* **tools**

  * Several command line tools, implementing common tree operations have been
  added and are available through the `ete` command that should become available
  in your shell after installation.

     * `ete build`: build phylogenetic with a single command line using a number of predefined workflows. 

     * `ete mod`: modify tree topologies by rooting, sorting leaves, pruning,

       * `ete annotate`: add features to tree nodes by combining newick and text files.
    
      * `ete view`: visualize trees form the command line
    
      * `ete compare`: compare tree topologies using the Robinson-Foulds distance,
    including trees from different sizes or with duplication events.

      * `ete ncbiquery`: query the ncbi taxonomy tree directly from the
      database. Retrieves annotated tree topology of the selected taxa,
      translates between taxid and species names, and extract lineage, rank and
      other taxa information.

      * `ete generate`: generate random trees, mostly for testing

  .. figure:: ../ex_figures/M2_super_profesional.png
            :scale: 100 %
      
  Highlights: 
  - accept pipes    


removed numpy and scipy dependencies
PyQt4 moved to optional
better warnings 

New features
=================

**News in Tree instances**

* added :func:`TreeNode.iter_edges` and :func:`TreeNode.get_edges`

* added :func:`TreeNode.compare` function

* improved :func:`TreeNode.robinson foulds` functio to expand polytomies, filter by branch support, and auto prune. 

* improved :func:`TreeNode.check_monophyly` function now accepts unrooted trees as input

* Default node is set to blank instead of the "NoName" string, which saves memory in large. 

* The branch length distance of root nodes is set to 0.0 by default.   

* newick export allows to control the format of branch distance and support values

 
**News in PhyloTree instances**

* added new reconciliation algorithm: Zmasek and Eddy's 2001, implemented by 

**News in the treeview module** 

* improved random_color functio 

* improved SVG tree image support

* improved :class:`SeqMotifFace` 

* improved heatmap support

* Added RectFace
  
