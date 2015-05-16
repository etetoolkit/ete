.. module:: ete2
  :synopsis: Converts evolutionary events into OrthoXML format

.. moduleauthor:: Jaime Huerta-Cepas
.. currentmodule:: ete2

.. _etree2orthoxml:

SCRIPTS: orthoXML
************************************

.. contents::

OrthoXML parser
============================

:attr:`etree2orthoxml` is a python script distributed as a part of the
ETE toolkit package. It uses an automatic python parser generated on
the basis of the OrthoXML schema to convert the evolutionary events in
phylogenetic tree topologies into the orthoXML format.

ETE OrthoXML parser is a low level python module that allows to
operate with the orthoXML structure using python objects. Every
element defined in the orthoXML schema has its akin in the parser
module, so a complete orthoXML structure can be generated from scratch
within a python script. In other words, low level access to the
orthoXML parser allows to create orthoxml documents in a programmatic
way.


The following example will create a basic orthoXML document
:: 

    from ete2 import orthoxml
    # Creates an empty orthoXML object
    oxml = orthoxml.orthoXML()

    # Add an ortho group container to the orthoXML document
    ortho_groups = orthoxml.groups()
    oxml.set_groups(ortho_groups)

    # Add an orthology group including two sequences
    orthologs = orthoxml.group()
    orthologs.add_geneRef(orthoxml.geneRef(1))
    orthologs.add_geneRef(orthoxml.geneRef(2))
    ortho_groups.add_orthologGroup(orthologs)

    oxml_file = open("test_orthoxml.xml", "w")
    oxml.export(oxml_file, level=0)
    oxml_file.close()

    # producing the following output
    #<ortho:orthoXML>
    #   <ortho:groups>
    #       <ortho:orthologGroup>
    #           <ortho:geneRef id="1"/>
    #           <ortho:geneRef id="2"/>
    #       </ortho:orthologGroup>
    #   </ortho:groups>
    #</ortho:orthoXML>


The etree2orthoxml script 
================================

:attr:`etree2orthoxml` is a standalone python script that allows to
read a phylogenetic tree in newick format and export their
evolutionary events (duplication and speciation events) as an orthoXML
document. The program is installed along with ETE, so it should be
found in your path. Alternatively you can found it in the script
folder of the latest ETE package release
(http://etetoolkit.org/releases/ete2/).

To work, :attr:`etree2orthoxml` requires only one argument containing
the newick representation of a tree or the name of the file that
contains it. By default, automatic detection of speciation and
duplication events will be carried out using the built-in
:ref:`species overlap algorithm <spoverlap>`, although this behavior
can be easily disabled when event information is provided along with
the newick tree. In the following sections you will find some use case
examples.

Also, consider reading the source code of the script. It is documented
and it can be used as a template for more specific applications. Note
that :attr:`etree2orthoxml` is a work in progress, so feel free to use
the `etetoolkit mailing list
<https://groups.google.com/forum/#!forum/etetoolkit>`_ to report any
feedback or improvement to the code.

Usage
----------------

::

   usage: etree2orthoxml [-h] [--sp_delimiter SPECIES_DELIMITER]
                         [--sp_field SPECIES_FIELD] [--root [ROOT [ROOT ...]]]
                         [--skip_ortholog_detection]
                         [--evoltype_attr EVOLTYPE_ATTR] [--database DATABASE]
                         [--show] [--ascii] [--newick]
                         tree_file
    
   etree2orthoxml is a python script that extracts evolutionary events
   (speciation and duplication) from a newick tree and exports them as a
   OrthoXML file.
    
   positional arguments:
     tree_file             A tree file (or text string) in newick format.
    
   optional arguments:
     -h, --help            show this help message and exit
     --sp_delimiter SPECIES_DELIMITER
                           When species names are guessed from node names, this
                           argument specifies how to split node name to guess the
                           species code
     --sp_field SPECIES_FIELD
                           When species names are guessed from node names, this
                           argument specifies the position of the species name
                           code relative to the name splitting delimiter
     --root [ROOT [ROOT ...]]
                           Roots the tree to the node grouping the list of node
                           names provided (space separated). In example:'--root
                           human rat mouse'
     --skip_ortholog_detection
                           Skip automatic detection of speciation and duplication
                           events, thus relying in the correct annotation of the
                           provided tree using the extended newick format (i.e.
                           '((A, A)[&&NHX:evoltype=D], B)[&&NHX:evoltype=S];')
     --evoltype_attr EVOLTYPE_ATTR
                           When orthology detection is disabled, the attribute
                           name provided here will be expected to exist in all
                           internal nodes and read from the extended newick
                           format
     --database DATABASE   Database name
     --show                Show the tree and its evolutionary events before
                           orthoXML export
     --ascii               Show the tree using ASCII representation and all its
                           evolutionary events before orthoXML export
     --newick              print the extended newick format for provided tree
                           using ASCII representation and all its evolutionary
                           events before orthoXML export



Example: Using custom evolutionary annotation 
------------------------------------------------------

If all internal nodes in the provided tree are correctly label as
duplication or speciation nodes, automatic detection of events can be
disabled using the :attr:`--skip_ortholog_detection` flag. 

Node labeling should be provided using the extended newick
format. Duplication nodes should contain the label :attr:`evoltype`
set to :attr:`D`, while speciation nodes should be set to
:attr:`evoltype=S`. If tag names is different, the option
:attr:`evoltype_attr` can be used as convenient.


In the following example, we force the HUMAN clade to be considered a
speciation node.

:: 

   # etree2orthoxml --skip_ortholog_detection '((HUMAN_A, HUMAN_B)[&&NHX:evoltype=S], MOUSE_B)[&&NHX:evoltype=S];'

    <orthoXML>
        <species name="A">
            <database name="">
               <genes>
                    <gene protId="HUMAN_A" id="0"/>
                </genes>
            </database>
        </species>
        <species name="B">
            <database name="">
                <genes>
                    <gene protId="HUMAN_B" id="1"/>
                    <gene protId="MOUSE_B" id="2"/>
                </genes>
            </database>
        </species>
        <groups>
            <orthologGroup>
                <geneRef id="2"/>
                <orthologGroup>
                    <geneRef id="0"/>
                    <geneRef id="1"/>
                </orthologGroup>
            </orthologGroup>
        </groups>
    </orthoXML>


You can avoid tree reformatting when node labels are slightly
different by using the :attr:`evoltype_attr`: 

:: 

   # etree2orthoxml --evoltype_attr E --skip_ortholog_detection '((HUMAN_A, HUMAN_B)[&&NHX:E=S], MOUSE_B)[&&NHX:E=S];'

However, more complex modifications on raw trees can be easily
performed using the core methods of the ETE library, so they match the
requirements of the :attr:`etree2orthoxml` script.

:: 

   from ete2 import Tree
   # Having the followin tree
   t = Tree('((HUMAN_A, HUMAN_B)[&&NHX:speciation=N], MOUSE_B)[&&NHX:speciation=Y];')

   # We read the speciation tag from nodes and convert it into a vaild evoltree label
   for node in t.traverse():
      if not node.is_leaf():
         etype = "D" if node.speciation == "N" else "S"
         node.add_features(evoltype=etype)
 
   # We the export a newick string that is compatible with etree2orthoxml script
   t.write(features=["evoltype"], format_root_node=True)

   # converted newick:
   # '((HUMAN_A:1,HUMAN_B:1)1:1[&&NHX:evoltype=D],MOUSE_B:1)1:1[&&NHX:evoltype=S];'


Example: Automatic detection of species names 
--------------------------------------------------
As different databases and software may produce slightly different
newick tree formats, the script provides several customization
options.

In gene family trees, species names are usually encoded as a part of
leaf names (i.e. P53_HUMAN). If such codification follows a simple
rule, :attr:`etree2orthoxml` can automatically detect species name and
used to populate the relevant sections within the orthoXML document. 

For this, the :attr:`sp_delimiter` and :attr:`sp_field` arguments can
be used. Note how species are correctly detected in the following example:

:: 

   # etree2orthoxml --database TestDB --evoltype_attr E --skip_ortholog_detection --sp_delimiter '_' --sp_field 0  '((HUMAN_A, HUMAN_B)[&&NHX:E=S], MOUSE_B)[&&NHX:E=S];'
   <orthoXML>
    <species name="HUMAN">
        <database name="TestDB">
            <genes>
                <gene protId="HUMAN_A" id="0"/>
                <gene protId="HUMAN_B" id="1"/>
            </genes>
        </database>
    </species>
    <species name="MOUSE">
        <database name="TestDB">
            <genes>
                <gene protId="MOUSE_B" id="2"/>
            </genes>
        </database>
    </species>
    <groups>
        <orthologGroup>
            <geneRef id="2"/>
            <orthologGroup>
                <geneRef id="0"/>
                <geneRef id="1"/>
            </orthologGroup>
        </orthologGroup>
    </groups>
   </orthoXML>


Example: Tree rooting
---------------------------

When evolutionary events are expected to be automatically inferred
from tree topology, outgroup information can be passed to the program to
root the tree before performing the detection. 

::

   # etree2orthoxml --ascii --root FLY_1 FLY_2 --sp_delimiter '_' --sp_field 0  '((HUMAN_A, HUMAN_B), MOUSE_B, (FLY_1, FLY_2));' 



                         /-FLY_1
                /D, NoName
               |         \-FLY_2
       -S, NoName
               |                  /-HUMAN_A
               |         /D, NoName
                \S, NoName        \-HUMAN_B
                        |
                         \-MOUSE_B


       <orthoXML>
           <species name="FLY">
               <database name="">
                   <genes>
                       <gene protId="FLY_1" id="0"/>
                       <gene protId="FLY_2" id="1"/>
                   </genes>
               </database>
           </species>
           <species name="HUMAN">
               <database name="">
                   <genes>
                       <gene protId="HUMAN_A" id="2"/>
                       <gene protId="HUMAN_B" id="3"/>
                   </genes>
               </database>
           </species>
           <species name="MOUSE">
               <database name="">
                   <genes>
                       <gene protId="MOUSE_B" id="4"/>
                   </genes>
               </database>
           </species>
           <groups>
               <orthologGroup>
                   <paralogGroup>
                       <geneRef id="0"/>
                       <geneRef id="1"/>
                   </paralogGroup>
                   <orthologGroup>
                       <geneRef id="4"/>
                       <paralogGroup>
                           <geneRef id="2"/>
                           <geneRef id="3"/>
                       </paralogGroup>
                   </orthologGroup>
               </orthologGroup>
           </groups>
       </orthoXML>
























