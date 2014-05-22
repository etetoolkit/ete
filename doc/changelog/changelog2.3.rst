What's new in ETE 2.3
*********************************
.. currentmodule:: ete_dev

BUGFIXES
==========
fixed bug when retreiving extra attributes in get_speciation_trees

SCRIPTS
==========
ete_tools/
  

NEW MODULES
====================

ncbi taxonomy module

NEW FEATURES
====================
added tree.iter_edges
improved tree.robinson foulds function: expand, polytomies, branch support filter and auto prune
improved tree.check monophyly function: accepts unrooted trees
added new reconciliation algorithm: Zmasek and Eddy's 2001, implemented by 
%%return option in render
improved random_color
improved SVG export
