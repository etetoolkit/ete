README.txt
Ziheng Yang, January 2004

(A)  Overview

This folder includes the files used in Yang (2004) and this file
describes the use of the AHRS algorithm described in that paper.  Two
options (clock = 5 and 6) are implemented in baseml and codeml.  clock
= 5 is for the global clock, and clock = 6 implements the heuristic
rate smoothing (AHRS) algorithm combined with maximum likelihood
estimation of divergence dates.  The mouse lemur files are used as an
example.  The control files for the nucleotide, amino acid, and codon
based analysis published in Yang (2004) are baseml2.ctl, aaml2.ctl,
and codonml2.ctl.  You can open those files to check them.

The models in Yang (2004) have two features compared with the previous
models (clock = 1, 2, 3), which were described in Yang and Yoder
(2003).  The first is that the new models deal with multiple-loci data
sets in which some species are missing at some loci.  The second is
that the AHRS algorithm attempts to automatically assign branches to
rate groups, which are then used for maximum likelihood estimation of
divergence dates using the method of Yang and Yoder (2003).  So the
new global-clock option (clock = 5) is identical to the old global
clock option (clock = 3) if every locus has all the species.  Note
however that there are some differences in the data formats between
the new models and the old ones, due to the need to deal with missing
species at some loci.  See section (B) for details.


(B) Data Format

Have a look at the sequence data file MouseLemurs123.nuc and the tree
file MouseLemurs.trees in this folder.

The new models, clock = 5 (global clock or simply clock) and 6 (local
clock) are for combined analysis of data from multiple loci (or site
partitions).  An important difference from the old options, clock = 0,
1, 2, 3, is that some species can be missing at some loci.  Specify
the number of loci using the variable ndata in the control file
baseml.ctl or codeml.ctl.  Prepare a tree file, including a tree for
all species that occur in the sequence data.  This will be called the
species tree or master tree.  The beginning of the tree file should
have the number of species and the number of trees (which is usually
1) on the first line.  Also prepare a sequence data file, with the
sequence alignments listed one after another for the loci.  The
example file MouseLemurs123.nuc lists data from the 3 codon
positions as if they were three different genes.  When the program
runs, it reads the master tree first, and then the sequence alignments
locus by locus.  For each locus, it constructs (extracts) the sub-tree
from the master tree.

For example, suppose the master tree is for six species with two
fossil calibration points:

      (((S1, S2), S3) @0.10, ((S4, S5) @0.20, S6));

Suppose we have sequences for 4 species at the first locus and 5
species at the second locus (with ndata = 2).  The data file looks as
follows.

     4 100
     S1       TCTATGTTATATGTATGAGTATGA ...
     S3       TCGATATTATGTGTATGAGTATGA ...
     S4       TCTATATTACATGTATGAGTATGA ...
     S6       TCCATATTAAATGTATGAGTATGA ...

     5 200
     S1       GTTATATGTATGAGTATGATCTAT ...
     S2       GTTATATGCGTGAGTATGAACTAT ...
     S4       ATTATGTGTATGAGTATGATCGAT ...
     S5       GCTACATGTATGAGTATGATCTAT ...
     S6       ATTAAATGTATGAGTATGATCCAT ...


The program will then construct the "gene tree" for locus 1 to be 
      ((S1, S2), S3) @0.10;

You should have at least one calibration node for each locus.  If two
"sister" species never occur simultaneously at one locus so that there
is no way of identifying the date of their divergence, you might want
to consider them as one "species".  For example, if donkey is
sequenced at some loci and horse at others and at no locus both are
sequenced, you can rename the two species equus in the tree and
sequence data files.


(C) Models clock = 5 (clock) and clock = 6 (local clock)

When you run clock = 5, a global clock is assumed.  If all species are
present in every locus, this analysis can be achieved by using clock =
3 (combined analysis) as in Yang & Yoder (2003).  This is the case for
the included example data file MouseLemurs123.nuc.  Note again however
that the data formats are different.  clock = 3 uses MouseLemurs.nuc
while clock = 5 uses MouseLemurs124.nuc.  If some species are missing
at some loci in your data, you can't use clock = 3 anymore and clock =
5 is the only choice.

The AHRS algorithm (clock = 6) works in 3 steps.  Here is a brief
description.  See Yang (2004) for more details.

   Step 1: Estimate branch lengths on each gene tree without the
           clock.

   Step 2: Heuristic rate smoothing, to estimate one set of divergence
           times for the nodes in the species tree and as many sets of
           branch rates as the number of loci.  Each branch in the
           gene tree is assigned and estimated one rate.  For the
           above toy example, the program estimates 3 divergence times
           (five ancestral nodes minus two calibration nodes), plus 6
           rates (six branches in a rooted tree of four species) for
           the first locus and 8 rates for the second locus (eight
           branches in a rooted tree of five species).  A smoothing
           parameter called \nu is also estimatd for each locus.  Rate
           estimation is achieved by minimizing the discrepancy
           between the predicted branch lengths and the estimates
           obtained in Step 1, and by minimizing rate changes over
           time (across lineages).  The estimated rates for branches
           in the gene trees are then collapsed into a few branch rate
           categories.  The number of rate categories is set by a
           variable called nbrate=4 in the routine DatingHeteroData()
           in the file treesub.c.  You can change this and recompile.
           The program also allows you to manually classify the rates
           into groups.  When it asks for the number of rate groups,
           you can reply with 0: meaning no change, 1: meaning one
           rate (same as using clock = 5), or say 5 (in which case the
           program will further ask to input 4 cutting points to
           separate the rates into 5 groups).

   Step 3: Maximum likelihood estimation of divergence times using the
           assigned branch rate groups.  Divergence times are estimated
           simultaneously with the rates for branch rate groups.  For
           the toy example mentioned above, this estimates 3 = 5 - 2
           node ages in the species tree, plus 3 rates at each locus,
           with 9 time and rate parameters in all.


(D) Output

The output is fairly self-explanatory.  For clock = 6, look at the
output on the screen at each of the three steps:

   Step 1: Estimating branch lengths under no clock.
   Step 2: Ad hoc rate smoothing to estimate branch rates.
   Step 3: ML estimation of times and rates.

In particular, read in the output at the end of step 2 and check the
branch labels (say, using Rod Page's TreeView) and see whether the
assignment is reasonable and whether you want to use your own
classification scheme.  The programs print out a file named
RateDist.txt, which contains a distance matrix for each locus, with
the distance calculated as the difference between two rates.  You can
use an algorithm such as UPGMA to cluster the rates into groups
(clades) to help with the classification.  I used the neighbor program
in J. Felsenstein's phylip package to do this (figure 5b and the
4-rate manual (4RM) model in Yang 2004).


(E)  Notes

 1.  The example control files are baseml2.ctl, aaml2.ctl, codonml2.ctl.

 2.  In early versions of baseml and codeml, the order of the control
     variables in the control files does not matter to the
     specification.  Unfortunately that is not the case anymore for
     clock = 5 or 6.  The variables clock and ndata should be
     specified in the control file before some other variables such as
     fix_kappa, kappa, fix_alpha, alpha etc.  See the example files
     baseml2.ctl and codonml2.ctl etc. included in the same folder.
     The reason for this is that you can fix the kappa values for
     different genes at certain values during Step 1, and for the
     program to know how many kappa values to read, it needs to know
     the number of genes (ndata); see note 5 below.

 3.  The options are implemented in baseml for nucleotide sequences
     and in codeml for amino acid and codon sequences.  

 4.  Only rooted binary trees are accepted in the tree file.

 5.  Estimating and fixing substitution parameters in step 1.  If the
     model involves substitution parameters such as kappa, alpha, you
     can run the program multiple times to guarantee getting correct
     estimates for them Step 1 of the algorithm and then use them as
     fixed constants in both Step 1 (when you rerun the program) and
     Step 3.  (Step 2 does not use a substitution model and so those
     parameters are irrelevant.)  Step 1 in the clock = 6 model always
     uses the algorithm of iterating one branch at a time, and may be
     problematic if the gamma shape parameter (for rate variation
     among sites) is estimated at the same time.  Note that the
     calculation in step 1 is just the old clock = 0 analysis and is
     in older versions of the programs, if the coccrect tree files are
     supplied for each locus.  In that case you can use clock = 0
     method = 0 to try and estimate the substitution parameters and
     then fix them when you run clock = 6.  If you have different
     numbers of species at different loci, the tree for each locus is
     different and it would be awkward to use clock = 0 to complete
     step 1.  In that case you can use clock = 6 so that the correct
     trees are extracted and used for each locus, but you run the
     algorithms multiple times to make sure the correct MLEs are
     obtained.  Either way, when step 1 is successful, you can fix the
     parameters in the control file, by say,

                  data = 3
             fix_alpha = 1
                 alpha = 0.29169  0.16392  1.24726

     which means that the alpha parameter is fixed at the three values
     above for the three genes (codon positions in this case).  Other
     parameters that can be fixed this way and that can vary for site
     partitions or genes or proteins include kappa and alpha for
     baseml, alpha and aaRatefile for amino acid sequences, and icode
     (genetic code table) kappa, and omega for codon-based analsis.
 
 6.  I notice that minor differences in the rate estimates might lead
     to assignment of one or two branches in a different rate group,
     leading to differences in final time estimates.  As a result,
     multiple runs using the same setting may lead to slightly
     different time estimates.  You should watch out for failure of
     the iteration algorithm in any of the three steps, which can
     cause differences between runs.

 7.  For protein sequences, you can use different substitution rate
     matrices.  In the following, three nuclear proteins (using wag)
     are followed by one mitochondrial protein (using mtmam).

        aaRatefile = wag.dat wag.dat wag.dat mtmam.dat

     For codon sequences, you can use different genetic codes.  In the
     following, three nuclear genes are followed by one mitochondrial
     gene.

             icode = 0 0 0 1

 8.  Separating codon positions into different files.  You can use
     Mgene = 1 option in baseml to separate the three codon positions
     into three different files (named Gene1.seq, Gene2.seq, etc.).
     You need to use verbose = 1 to do this, I think.  Then you can
     copy and paste those files into one sequence data file, which
     will be in the format required by the options here.

Good luck.

References

Yang, Z. 2004. A heuristic rate smoothing procedure for maximum likelihood estimation of species divergence times. Acta Zoologica Sinica 50:645-656.

//end of file
