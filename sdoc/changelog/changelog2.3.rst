What's new in ETE 2.3 
*********************************
.. currentmodule:: ete2

Update 2.3.2
=================
* added :func:`NCBITaxa.get_descendant_taxa` 
* added :func:`NCBITaxa.get_common_names` 
* `ete ncbiquery <http://etetoolkit.org/documentation/ete-ncbiquery/>`_: dump descendant taxa given a taxid or taxa name. new option `--descendants`_; renamed `--taxonomy`_ by `--tree`_ 
* fixes <misaligned branches <https://github.com/jhcepas/ete/issues/113>`_ in ultrametric tree images using vt_line_width > 0
* fixes <windows installation problem <https://github.com/jhcepas/ete/issues/114>`_

New Modules
=============

tools
--------

A collection of `command line tools
<http://etetoolkit.org/documentation/tools/>`_, implementing common tree
operations has been added to the ETE core package. All tools are wrapped by the
**ete** command, which should become available in your path after installation.

* `ete build <http://etetoolkit.org/documentation/ete-build/>`_: Build phylogenetic trees using a using a number of predefined built-in gene-tree and species-tree workflows. `Watch example <http://etetoolkit.org/static/img/etebuild.gif>`_
* `ete view <http://etetoolkit.org/documentation/ete-view/>`_: visualize and generate tree images directly form the command line. 
* `ete compare <http://etetoolkit.org/documentation/ete-compare/>`_: compare tree topologies based on any node feature (i.e. name, species name, etc) using the Robinson-Foulds distance and edge compatibility scores. 
* `ete ncbiquery <http://etetoolkit.org/documentation/ete-ncbiquery/>`_: query the ncbi taxonomy tree directly from the database.
* **ete mod**: modify tree topologies directly from the command line. Allows rooting, sorting leaves, pruning and more
* **ete annotate**: add features to the tree nodes by combining newick and text files.
* **ete generate**: generate random trees, mostly for teaching and testing

.. figure:: http://etetoolkit.org/static/img/ete23_demo.gif
   :scale: 50%

ncbi taxonomy
---------------------

The new **ncbi_taxonomy** module provides the class :class:`NCBITaxa`, which allows to query a locally parsed
NCBI taxonomy database. It provides taxid-name translations, tree annotation tools
and other handy functions. A brief tutorial and examples on how to use it is
available `here <../tutorial/tutorial_ncbitaxonomy.html>`_


New features
=================

**News in Tree instances**

* added :func:`TreeNode.iter_edges` and :func:`TreeNode.get_edges`

* added :func:`TreeNode.compare` function

* added :func:`TreeNode.standardize` utility function to quickly get rid of  multifurcations, single-child nodes in a tree.  

* added :func:`TreeNode.get_topology_id` utility function to get an unique identifier of a tree based on their content and topology. 

* added :func:`TreeNode.expand_polytomies` 

* improved :func:`TreeNode.robinson_foulds` function to auto expand polytomies, filter by branch support, and auto prune. 

* improved :func:`TreeNode.check_monophyly` function now accepts unrooted trees as input

* Default node is set to blank instead of the "NoName" string, which saves memory in very large trees. 

* The branch length distance of root nodes is set to 0.0 by default.   

* newick export allows to control the format of branch distance and support values. 

* Tree and SeqGroup instances allow now to open gzipped files transparently. 

..
   **News in PhyloTree instances**

   * added new reconciliation algorithm: Zmasek and Eddy's 2001, implemented by  ?????

**News in the treeview module** 

* improved SVG tree rendering 

* improved :func:`random_color` function (a list of colors can be fetch with a single call)

* improved :class:`SeqMotifFace` 

* Added :class:`RectFace`

* Added :class:`StackedBarFace`



..
   * Improved heatmap support???
  
Highlighted Bug Fixes 
============================

* `Newick parser <https://github.com/jhcepas/ete/issues/97>`_ is now more strict  when reading node names and branch distances, avoiding silent errors when  parsing node names containing illegal symbols (i.e. ][)(,: )
* fixes several minor bugs when retrieving extra attributes in  :func:`PhyloNode.get_speciation_trees`. 
* Tree viewer `crashes <https://github.com/jhcepas/ete/issues/94>`_ when redrawing after changing node properties. 
* fixed `installation problem <https://github.com/jhcepas/ete/issues/82>`_ using pip. 
* visualizing internal tree nodes as a circular tree `produce crashes <https://github.com/jhcepas/ete/issues/84>`_
* `math domain error <https://github.com/jhcepas/ete/issues/98>`_ in SequencePlotFace. 
* Fix likelihood calculation bug in EvolTree 
* Fix `BarChartFace problem with negative numbers <https://github.com/jhcepas/ete/issues/109>`_
* Fix problem that produced `TreeStyle attributes to be ignored in PhyloTree instances. <https://github.com/jhcepas/ete/issues/75>`_ 
