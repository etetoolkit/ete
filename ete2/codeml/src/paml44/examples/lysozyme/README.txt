This folder contains files for the branch (Yang 1998) and branch-site
(Yang and Nielsen 2002; Yang et al. 2005; Zhang et al. 2005) analyses
using the lysozyme data set of Messier and Stewart (1997).


(A) 
This folder contains the control file, the sequence data file and
the tree file for demonstrating codon models that use different dN/dS
ratios among lineages (Yang 1998).  The data set is the "small" data
set analyzed in Yang (1998).  The default control file let you
duplicate the results for the small data set in table 1 of Yang
(1998).  Also look at the tree file about specifying the branches of
interest, for which positive selection is tested.

To fix a particular w to 1, arrange the labels so the concerned branch
is the last and then use

       model = 2
   fix_omega = 1
       omega = 1

For example, the tree

 ((1,2) #2, ((3,4) #1, 5), (6,7) );     / * table 1E&J */

fits a model with w0 (background), w1, and w2.  Then the above
specification will force w2 = 1 to be fixed.

Usage:

	codeml lysozymeSmall.ctl

Or you can rename the file lysozyme.ctl as codeml.ctl, and then run 

         codeml


(B) The folder also contains another set of files for the "large" data
set analyzed under the branch models by Yang (1998).  This data set is
used by Yang and Nielsen (2002) and Zhang et al. (2005) to test the
branch-site models, which are specified as follows

   Model A:  model = 2    NSsites = 2
   Model B:  model = 2    NSsites = 3

A complication is that from version 3.14, branch-site model A was
modified slightly.  In the old model of Yang and Nielsen (2002), w0 =
0 was fixed, while in the new models (described in Yang et al. 2005
and tested in Zhang et al. 2005), 0 < w0 < 1 is estimated from the
data.  The old branch-site model A is not in the program anymore.
Furthermore, version 3.14 or later implements the BEB procedure for
identifying sites (Yang et al. 2005), although the NEB results are
still included in the output.  Our suggestion is that you use
branch-site model A to construct branch-site test 2, which is also
called the branch-site test of positive selectin.  We advise that you
do not use branch-site test 1 or branch-site model B.  

The control file lysozymeLarge.ctl specifies branch-site model A, the
alternative hypothesis.  Here are specifications to implement both the
null and alternative hypotheses.  See Zhang et al. (2005; table 5).


Null hypothesis (branch site model A, with w2 = 1 fixed):

    model = 2    NSsites = 2   fix_omega = 1   omega = 1


Alternative hypothesis (branch site model A, with w2 estimated):

    model = 2    NSsites = 2   fix_omega = 0   omega = 1.5 (or any value > 1)

Look at the tree file lysozymeLarge.trees for specification of the
"branch of interest" of "foreground" branch.  You can remove the first
line of numbers and the file will be readable from TreeView, which
allows you to show the branch (node) labels as well.

The variable ncatG is ignored by the program, since the number of site
classes is fixed under both models A and B.  (To run the site model
"discrete" with only 2 site classes, which is the null model to be
compared with model B in Yang & Nielsen 2002, you should specify model
= 0, NSsites = 3, ncatG = 2.  Note that this test is not recommended.)
See the paper for details.  Also please heed the warnings in the
Discussion section of that paper.

The branch-site models are very difficult to use, as the numerical
iteration algorithm often has problems.  You are advised to run the
program multiple times, using different initial values.  If you know
how to generate a file or initial values called in.codeml (see
Manual), you can edit that file to change initial values.  For
example, you can use the estimates of branch lengths and other
parameters from the null model to start the iteration for the
alternative model.


References

Yang, Z. 1998. Likelihood ratio tests for detecting positive selection
and application to primate lysozyme evolution. Mol. Biol. Evol. 15:568-573.

Yang, Z., and R. Nielsen, 2002 Codon-substitution models for detecting
molecular adaptation at individual sites along specific
lineages. Mol. Biol. Evol. 19: 908-917.

Yang, Z., W. S. W. Wong, and R. Nielsen. 2005. Bayes empirical Bayes
inference of amino acid sites under positive selection. Molecular
Biology and Evolution 22:1107-1118.

Zhang, J., R. Nielsen, and Z. Yang. 2005. Evaluation of an improved
branch-site likelihood method for detecting positive selection at the
molecular level. Molecular Biology and Evolution 22:2472-2479.

Ziheng Yang

11 September 2001, last modified on 24 November 2005
