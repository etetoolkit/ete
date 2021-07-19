.. image:: https://travis-ci.org/etetoolkit/ete.svg?branch=master
   :target: https://travis-ci.org/etetoolkit/ete

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/jhcepas/ete
   :target: https://gitter.im/jhcepas/ete?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge 
..
   .. image:: https://coveralls.io/repos/jhcepas/ete/badge.png

.. image:: http://img.shields.io/badge/stackoverflow-etetoolkit-blue.svg
   :target: https://stackoverflow.com/questions/tagged/etetoolkit+or+ete3

.. image:: http://img.shields.io/badge/biostars-etetoolkit-purple.svg
   :target: https://www.biostars.org/t/etetoolkit,ete3,ete,ete2/


Overview
-----------

ETE (Environment for Tree Exploration) is a Python programming toolkit that
assists in the automated manipulation, analysis and visualization of
phylogenetic trees. Clustering trees or any other tree-like data structure are
also supported.

Given that ETE is mainly developed as a tool for researchers working in phylogenetics
and genomics, it also provides specialized tools in that context (e.g. reconstructing, comparing and visualizing
phylogenetic trees). If you use ETE in a published work, please cite:

::

   Jaime Huerta-Cepas, François Serra and Peer Bork. "ETE 3: Reconstruction,
   analysis and visualization of phylogenomic data."  Mol Biol Evol (2016) doi:
   10.1093/molbev/msw046

Install and Documentation
-----------------------------

- The official web site of ETE is http://etetoolkit.org. Downloading
  instructions and further documentation can be found there.

- News and announcements are usually posted on twitter:
  http://twitter.com/etetoolkit

Gallery of examples
--------------------
  
.. image:: https://raw.githubusercontent.com/jhcepas/ete/master/sdoc/gallery.png
   :width: 600
  
Getting Support
------------------
**Please, whenerver possible, avoid sending direct support-related emails to
the developers. Keep communication public:**

- For any type of question on how to use ETE in the bioinformatics context, use BioStars (http://biostars.org) or even StackOverflow forums. 

  Please use the **"etetoolkit"** tag for your questions: 

   .. image:: http://img.shields.io/badge/stackoverflow-etetoolkit-blue.svg
      :target: https://stackoverflow.com/questions/tagged/etetoolkit+or+ete3

   .. image:: http://img.shields.io/badge/biostars-etetoolkit-purple.svg
      :target: https://www.biostars.org/t/etetoolkit,ete3,ete,ete2/

- Bug reports, feature requests and general discussion should be posted into github:
  https://github.com/etetoolkit/ete/issues

- For more technical problems, you can also use the
  official ETE mailing list at https://groups.google.com/d/forum/etetoolkit. To
  avoid spam, messages from new users are moderated. Expect some delay until
  your first message and account is validated.

- For any other inquire (collaborations, sponsoring, etc), please contact *jhcepas /at/ gmail.com*
   

Contributing and BUG reporting
---------------------------------
https://github.com/etetoolkit/ete/wiki/Contributing

ETE-diff module documentation
---------------------------------
NAME
    ete3.tools.ete_diff

DESCRIPTION
    # #START_LICENSE###########################################################
    #
    #
    # This file is part of the Environment for Tree Exploration program
    # (ETE).  http://etetoolkit.org
    #
    # ETE is free software: you can redistribute it and/or modify it
    # under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # ETE is distributed in the hope that it will be useful, but WITHOUT
    # ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    # or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
    # License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with ETE.  If not, see <http://www.gnu.org/licenses/>
    #
    #
    #                     ABOUT THE ETE PACKAGE
    #                     =====================
    #
    # ETE is distributed under the GPL copyleft license (2008-2015).
    #
    # If you make use of ETE in published work, please cite:
    #
    # Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
    # ETE: a python Environment for Tree Exploration. Jaime BMC
    # Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
    #
    # Note that extra references to the specific methods implemented in
    # the toolkit may be available in the documentation.
    #
    # More info at http://etetoolkit.org. Contact: huerta@embl.de
    #
    #
    # #END_LICENSE#############################################################

FUNCTIONS
    EUCL_DIST(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the formula:
            1 - (Shared attributes / maximum length of the two nodes)
        
        Parameters:
            a:  (reference node as tree object, observed attributes as set), as tuple
            b:  (target node as tree object, observed attributes as set), as tuple
            support:  flag indicating the use of support values, as boolean (this argument has no effect in this function)
            attr1:  observed attribute from reference node, as string (this argument has no effect in this function)
            attr2:  observed attribute from target node, as string (this argument has no effect in this function)
        
        Returns:
            float: distance value between the two nodes
    
    EUCL_DIST_B(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the formula:
            1 - (Shared attributes / maximum length of the two nodes) + absoulte value of the distance difference between shared leaves from both nodes to their parents
        
        Parameters:
            a:  (reference node as tree object, observed attributes as set), as tuple
            b:  (target node as tree object, observed attributes as set), as tuple
            support:  flag indicating the use of support values, as boolean (this argument has no effect in this function)
            attr1:  observed attribute from reference node, as string
            attr2:  observed attribute from target node, as string
        
        Returns:
            float: distance value between the two nodes
    
    EUCL_DIST_B_ALL(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the formula:
            1 - (Shared attributes / maximum length of the two nodes) + absoulte value of the distance difference between all leaves from both nodes to their parents
        
        Parameters:
            a:  (reference node as tree object, observed attributes as set), as tuple
            b:  (target node as tree object, observed attributes as set), as tuple
            support:  flag indicating the use of support values, as boolean (this argument has no effect in this function)
            attr1:  observed attribute from reference node, as string (this argument has no effect in this function)
            attr2:  observed attribute from target node, as string (this argument has no effect in this function)
        
        Returns:
            float: distance value between the two nodes
    
    EUCL_DIST_B_FULL(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the formula:
            1 - (Shared attributes / maximum length of the two nodes) + absoulte value of the distance difference between shared leaves from both nodes to their parents
            Branch distances are calculated as the entire path leave to root
        
        Parameters:
            a:  (reference node as tree object, observed attributes as set), as tuple
            b:  (target node as tree object, observed attributes as set) as tuple
            support:  flag indicating the use of support values, as boolean
            attr1:  observed attribute from reference tree, as string
            attr2:  observed attribute from target tree, as string
        
        Returns:
            float: distance value between the two nodes
    
    RF_DIST(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the formula:
            Robinson-Foulds distance / Maximum possible Robinson-Foulds distance
        
        Parameters:
            a:  (reference node as tree object, observed attributes as set), as tuple
            b:  (target node as tree object, observed attributes as set), as tuple
            support:  flag indicating the use of support values, as boolean (this argument has no effect in this function)
            attr1:  observed attribute from reference tree, as string (this argument has no effect in this function)
            attr2:  observed attribute from target tree as, string (this argument has no effect in this function)
        
        Returns:
            float: distance value between the two nodes
    
    SINGLECELL(a, b, support, attr1, attr2)
        Calculates the distance between two nodes using the precomputed distances obtained from the formula: 
            1 - Pearson correlation between reference node and target node
            The final distance is calculated as the percentile 50 of all leave distances between the compared nodes.
        
        
        Parameters:
            a:  (reference node as tree object, Pearson correlation from both trees as dictionary), as tuple
            b:  (target node as tree object, Pearson correlation from both trees as dictionary), as tuple
            support:  flag indicating the use of support values, as boolean (this argument has no effect in this function)
            attr1:  observed attribute from reference node, as string (this argument has no effect in this function)
            attr2:  observed attribute from target node, as string (this argument has no effect in this function)
        
        Returns:
            float: distance value between the two nodes
    
    be_distance(t1, t2, support, attr1, attr2)
        Calculates a Branch-Extended Distance. 
        This distance is intended as an extension for the main distance used by ETE-diff to link similar nodes without altering the results
        
        Parameters:
            t1: reference node, as tree object
            t2: target node, as tree object
            support: whether to use support values to calculate the distance, as boolean
            attr1: observed attribute for the reference node, as string
            attr2: observed attribute for the target node, as string
           
        Returns:
            float distance value
    
    cc_distance(t1, t2, support, attr1, attr2)
        Calculates a Cophenetic-Compared Distance. 
        This distance is intended as an extension for the main distance used by ETE-diff to link similar nodes without altering the results
        
        Parameters:
            t1: reference node, as tree object
            t2: target node, as tree object
            support: whether to use support values to calculate the distance, as boolean
            attr1: observed attribute for the reference node, as string
            attr2: observed attribute for the target node, as string
           
        Returns:
            float distance value
    
    dict2tree(treedict, jobs=1, parallel=None)
        Generates a tree object from a dictionary using UPGMA algorithm and Pearson correlations between observations
        
        Parameters:
            treedict: dictionary with key values:
                idx: values are row indexes, as integers
                headers: values are column names, as strings
                dict: values are dictionary of columns as key values and their expression values, as lists
            jobs: maximum number of jobs to use when parallel argument is provided, as integer
            parallel: parallelization method, as string. Options are:
                async for asyncronous parallelization
                sync for asyncronous parallelization
        
        Returns:
            tree object
    
    lapjv(...)
        Solve linear assignment problem using Jonker-Volgenant algorithm.
        
        cost: an N x N matrix containing the assignment costs. Entry cost[i, j] is
          the cost of assigning row i to column j.
        extend_cost: whether or not extend a non-square matrix [default: False]
        cost_limit: an upper limit for a cost of a single assignment
                    [default: np.inf]
        return_cost: whether or not to return the assignment cost
        
        Returns (opt, x, y) where:
          opt: cost of the assignment, not returned if return_cost is False.
          x: a size-N array specifying to which column each row is assigned.
          y: a size-N array specifying to which row each column is assigned.
        
        When extend_cost and/or cost_limit is set, all unmatched entries will be
        marked by -1 in x/y.
    
    load_matrix(file, separator)
        Digests files containing a expression matrix and translates it to a dictionary
        
        Parameters:
            file: expression matrix filename, as string
            separator: Column separator, as string
        
        Returns:
            dictionary with key values:
                idx: values are row indexes, as integers
                headers: values are column names, as strings
                dict: values are dictionary of columns as key values and their expression values, as lists
    
    pearson_corr(rdict, tdict)
        Generates a dictionary of precomputed pearson correlations for all observations of two trees
        
        Parameters:
            rdict: dictionary with key values:
                idx: values are row indexes as integers
                headers: values are column names as strings
                dict: values are dictionary of columns as key values and their expression values as lists
            tdict: dictionary with key values:
                idx: values are row indexes as integers
                headers: Values are column names as strings
                dict: values are dictionary of columns as key values and their expression values as lists
           
        Returns:
            Dictionary of pearson correlations formed by sub dictionaries. 
            Each value is accessed introducing the reference observation as first key and the target observation as second key
                (e.g. dictionary['reference_observation']['target_observation'])
    
    populate_args(diff_args_p)
        Loads arguments on the argument parser object used by ETE wrapper module
        
        Parameters:
            argument parser object for ETE-diff module
        
        Returns:
            None
    
    run(args)
        Carries ETE wrapper workflow when ETE-diff is called from command line and prints selected report on terminal
        
        Parameters:
            argument parser object for ETE-diff module
        
        Returns:
            None
    
    sepstring(items, sep=', ')
    
    show_difftable(difftable, extended=False)
        Generates a table report from the result of treediff function
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Table report of treediff function, as string
    
    show_difftable_SCA(difftable, extended=False)
        Generates a table report from the result variant of treediff function for the Single Cell Analysis 
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Table report of treediff function, as string
    
    show_difftable_summary(difftable, rf=-1, rf_max=-1, extended=None)
        Generates a summary report from the result of treediff function and the Robinson-Foulds distance between two trees
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            rf: Robinson-Foulds distance for reference and target tree, as float
            rf_max: maximum Robinson-Foulds distance for reference and target tree, as float
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Summary report of treediff function and robinson_foulds method, as string
    
    show_difftable_summary_SCA(difftable, rf=-1, rf_max=-1, extended=None)
        Generates a summary report variant from the result of treediff function and the Robinson-Foulds distance between two trees for the Single Cell Analysis 
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            rf: Robinson-Foulds distance for reference and target tree, as float
            rf_max: maximum Robinson-Foulds distance for reference and target tree, as float
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Summary report of treediff function and robinson_foulds method, as string
    
    show_difftable_tab(difftable, extended=None)
        Generates a tabulated table report from the result of treediff function
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Tabulated table report of treediff function, as string
    
    show_difftable_tab_SCA(difftable, extended=None)
        Generates a tabulated table report variant from the result of treediff function for the Single Cell Analysis
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Table report of treediff function, as string
    
    show_difftable_topo(difftable, attr1, attr2, usecolor=False, extended=None)
        Generates a topology table report from the result of treediff function
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            attr1: observed attribute from the reference tree, as string
            attr2: observed attribute from the target tree, as string
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Topology table report of treediff function, as string
    
    show_difftable_topo_SCA(difftable, attr1, attr2, usecolor=False, extended=None)
        Generates a topology table report from the result of treediff function for the Single Cell Analysis
        
        Parameters:
            difftable: list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object
            attr1: observed attribute from the reference tree, as string
            attr2: observed attribute from the target tree, as string
            extended: whether to show extended distance in final report, as boolean
        
           
        Returns:
            Topology table report of treediff function, as string
    
    tree_from_matrix(matrix, sep=',', dictionary=False, jobs=1, parallel=None)
        Wrapps a tree object recontruction using load_matrix and dict2tree functions
        
        Parameters:
            matrix: expression matrix filename, as string
            sep: column separator, as string
            dictionary: whether to return source dictionary used to generate the tree object, as boolean
            jobs: maximum number of jobs to use when parallel argument is provided, as integer
            parallel: parallelization method, as string. Options are:
                async for asyncronous parallelization
                sync for asyncronous parallelization
           
        Returns:
            tree object
    
    treediff(t1, t2, attr1='name', attr2='name', dist_fn=<function EUCL_DIST at 0x7f04f01e8048>, support=False, reduce_matrix=False, extended=None, jobs=1, parallel=None)
        Main function of ETE-diff module.
        Compares two trees and returns a list of differences for each node from the reference tree
        
        Parameters:
            t1: reference tree, as tree object
            t2: target tree, as tree object
            attr1: observed attribute for the reference node, as string
            attr2: observed attribute for the target node, as string
            dist_fn: distance function that will be used to calculate the distances between nodes, as python function
            support: whether to use support values for the different calculations, as boolean
            reduce_matrix: whether to reduce the distances matrix removing columns and rows where observations equal to 0 (perfect matches) are found, as boolean
            extended: whether to use an extension function, as python function
            jobs: maximum number of parallel jobs to use if parallel argument is given, as integer
            parallel: parallelization method, as string. Options are:
                async for asyncronous parallelization
                sync for asyncronous parallelization
        
           
        Returns:
            list where each entry contains a list with:
                distance, as float
                extended distance, as float (-1 if not calculated)
                observed attributes on reference node, as set
                observed attributes on target node, as set
                observed attributes disfferent between both nodes, as set
                reference node, as tree object
                target node, as tree object

DATA
    DESC = ''
    absolute_import = _Feature((2, 5, 0, 'alpha', 1), (3, 0, 0, 'alpha', 0...
    log = <Logger main (NOTSET)>
    print_function = _Feature((2, 6, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0)...
  
ROADMAP
--------
https://github.com/etetoolkit/ete/wiki/ROADMAP


