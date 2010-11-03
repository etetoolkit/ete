README.txt
Ziheng Yang, 27 January 2003


This folder contains files for the local-clock likelihood analysis of Yoder 
and Yang (2003).

(A) 
The clock models are re-written.  Note that the fossil calibration
points are specified using the symbol '@' in the tree file; the symbol
is used in the same way as the more familiar symbol ':' for branch
lengths.  TipDate models are implemented using @ in the sequence name
to specify the date of determination of the sequence.  Look at the
examples/TipDate folder for an example.  Local clock models are
specified by assigning rates to branches, using the symbol # to label
the branch/node.  The symbol $ is used as a clade label; $ stands
for the capital greek symbol \Delta, which looks somewhat like a clade.  

Use clock = 2 for local clock models.  For models of multiple genes,
clock = 3 represents the "combined analysis" in Yang & Yoder (2003).
The program assumes the same set of species and the same phylogeny at
the mutliple loci.

      clock = 1: global clock, deals with TipDate with no or many fossils, 
                 ignores branch rates (#) in tree if any.
            = 2: local clock models, as (1) above, but requires branch 
                 rates (#) tree.
            = 3: as (2) above, but requires Mgene and option G in sequence 
                 file.


(B) 

The following describes specifications in baseml.ctl to duplicate the
ML results in tables 4 and 5 of Yang and Yoder (2003).  Note that the
ML analysis uses the ingroup sequences only, and the assumed ingroup
tree is rooted.  In the Bayes analysis of that paper, Thorne's program
(estbranches) requires an outgroup to root the ingroup tree.  The
"JeffNode" node numbering corresponds to the the node numbering by
Jeff Thorne's Bayes MCMC programs divtime5b and multidivtime, used in
our paper.  My output is correct only if you do what we did, that is,
only if you use the outgroup in Jeff's estbranches program and do not
use the outgroup sequences in the baseml ML analysis.  Note that the
node numbering in Tables 4 and 5 of that paper is according to Jeff's
programs divtime5b and multidivtime.


JC69 analysis in Tables 4 and 5
===============================

Columns b, c, d.  Use optoin GC on the first line of the sequence data file
MouseLemurs.nuc.  

        35 1818  GC

The tree in the tree file has seven @ specifying seven calibration
dates.  Use Mgene = 1 for separate analysis.  Other options are

     model = 0 
     Mgene = 1
     fix_alpha = 1
     alpha = 0
     clock = 1

These options should generate the three columns in one analysis.  The
option clock = 1 has precedence over the branch rate labels # in the
tree file.  So clock = 1 above means that the model is a global clock
and the rate labels # are ignored.  

Columns b, c, d in table 5 (local clock analysis).  If you choose
clock = 2 in the above, you should recover results for the local clock
analysis.

Column i in table 4 (combined global clock analysis under JC69) is
produced by the following options:

     model = 0 
     Mgene = 0
     fix_alpha = 1
     alpha = 0
     clock = 1

Column i in table 5 (combined local clock analysis under JC69) is
produced by changing clock = 3 in the above.




F84G analysis in Tables 4 and 5
===============================

Use the following to specify the gamma model.  

     fix_alpha = 0
     alpha = 0.5 (or any other initial value)
     ncatG = 5

Columns f, g, h in table 4 (global clock analysis).  Use optoin GC on
the first line of the sequence data file.  The tree in the tree file
has seven @ specifying seven calibration dates.  Use Mgene = 1 for
separate analysis.  Other options are

     model = 3
     Mgene = 1
     fix_alpha = 0
     alpha = 0.5 (or any other initial value)
     clock = 1

Columns f, g, h in table 5 (F84G local clock analysis).  Change clock
= 2 in the above.

Column j in table 4 (combined global clock analysis under F84G) is
produced by the following options:

     model = 3
     Mgene = 4
     fix_alpha = 0
     alpha = 0.5
     Malpha = 1
     ncatG = 5
     clock = 1

Column j in table 5 (combined local clock analysis under F84G) is
produced by setting clock = 3 in the above.

Good luck.

//end of file
