Notes by Ziheng Yang
Last modified: 25 March 2009

(A) This is the MHC dataset analyzed by Yang & Swanson (2002: table 2) and
also Yang (2006: table 8.3 and figures 8.4 & 8.5).  Note that Yang &
Swanson implemented models M1 and M2 instead of M1a and M2a.  The
modified models M1a & M2a were introduced in 2004 (paml 3.14), so if
you run the current version of paml/codeml, the results for M1a and
M2a will be different from those listed in the paper.  One other
difference is that in the Y&S2002 paper, the branch lengths were
optimized under each model, whereas the default setting in codeml.ctl
(with fix_blength = 2) has the branch lengths fixed at the values in
the tree file, which are the MLEs under M0.  Thus if you run codeml
using the default codeml.ctl, only the results for M0 match those in
table 2.  To get the same estimates for M7 and M8, you need to use
fix_blength = 1 (and the computation will take much longer).  

The default codeml.ctl should produce the results in the book, which
were obtained by fixing the branch lengths under the M0 estimates.  I
just did a run, and got the following lnL values.  The value for M7 is
lower than in the book.  The difference may be due to numerical
inaccuracies in the discretization of the beta distribution in
different versions of the program.

Model (#p):   lnL
M0     (2):  -8225.154790
M1a    (2):  -7490.993363
M2a    (4):  -7231.154540
M7     (3):  -7502.792534 (-7498.97 in the book)
M8     (5):  -7238.014961


The lysin dataset analyzed in Yang and Swanson (2002) is also included
in the package, in the examples/lysin/ folder.

References

Yang, Z., and W. J. Swanson. 2002. Codon-substitution models to detect
adaptive evolution that account for heterogeneous selective pressures
among site classes. Mol. Biol. Evol. 19:49-57.

Yang, Z. 2006. Computational Molecular Evolution. Oxford University Press, Oxford, England.
