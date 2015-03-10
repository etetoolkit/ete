What's new in ETE 2.3 (XX March 2015)
*********************************
.. currentmodule:: ete2

.. contents::

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

     * `ete build`: allows to build phylogenetic tree using a using a number of
       predefined built-in gene-tree and species-tree workflows. 

       - gene tree phylogenetic reconstruction. Input file is a single fasta file with homologous sequences. 

       - species tree reconstruction using super-matrix (concatenated alignment)
         methodology. Input file is a list of clusters of orthologous groups,
         and a fasta file containing all sequences.

       - automatic switch from amino acid to codon alignments if necessary 

       - software support include FastTree, Phyml, Raxml, Muscle, MAFFT,
         ClustalOmega, Dialign-tx, MCoffee, Trimal, ProtTest


     * `ete mod`: modify tree topologies directly from the command line. Allows
       rooting, sorting leaves, pruning and more

     * `ete annotate`: add features to the tree nodes by combining newick and text files.
    
     * `ete view`: visualize and generate tree images directly form the command
       line. 

       - Many customization options are allowed, from basic size, color and
       shape options to the possibility of rendering tree annotations over the tree image.
       
       - Predefined layouts are provided for phylogenetic tree + alignments and custom heatmaps.  

      * `ete compare`: compare tree topologies based on any node feature
        (i.e. name, species name, etc) using the Robinson-Foulds distance and
        edge compatibility scores. 

        - Automatic handling of trees with different sizes
        
        - Automatic handling of trees containing duplicated features

        - Allows to discard edges based on their support values. 


      * `ete ncbiquery`: query the ncbi taxonomy tree directly from the
      database. 

        - Retrieves annotated tree topology of the selected taxa,
      translates between taxid and species names, and extract lineage, rank and
      other taxa information.

      * `ete generate`: generate random trees, mostly for testing

  .. figure:: ../ex_figures/M2_super_profesional.png
            :scale: 100 %
      
  Highlights: 
  - accept pipes    

Dependencies
------------------

removed numpy and scipy dependencies
PyQt4 moved to optional
better warnings 

New features
=================

**News in Tree instances**

* added :func:`TreeNode.iter_edges` and :func:`TreeNode.get_edges`

* added :func:`TreeNode.compare` function

* added :func:`TreeNode.standarize` utility function to quickly get rid of  multifurcations, single-child nodes in a tree.  

* added :func:`TreeNode.get_topology_id` utility function to get an unique identifier of a tree based on their content and topology. 

* added :func:`TreeNode.expand_polytomies` 

* improved :func:`TreeNode.robinson foulds` function to auto expand polytomies, filter by branch support, and auto prune. 

* improved :func:`TreeNode.check_monophyly` function now accepts unrooted trees as input

* Default node is set to blank instead of the "NoName" string, which saves memory in large. 

* The branch length distance of root nodes is set to 0.0 by default.   

* newick export allows to control the format of branch distance and support values
 
**News in PhyloTree instances**

* added new reconciliation algorithm: Zmasek and Eddy's 2001, implemented by  ?????

**News in the treeview module** 

* improved random_color function (a color schema return as a whole) 

* improved SVG tree image support

* improved :class:`SeqMotifFace` 

* Added RectFace

* improved heatmap support


  
