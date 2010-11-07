Notes by Ziheng Yang
Last modified 16 May 2003

This folder contains example data files for the HIV-1 env V3 region
analyzed in Yang et al. (2000).  This is the 10th data set analyzed
and the results are in table 12 in that paper.  The default
specification in the control file codeml.ctl

      NSsites = 0 1 2

will fit the onw-ratio model (M0), neutral (M0) and selection (M2)
models.  You can fit more models if you want.  Note that the lysin and 
lysozyme example folders contain files for similar analyses of bigger 
data sets.

You run the program by typing

    codeml

or 

   ..\..\codeml 

   ../../codeml 


References

Nielsen, R., and Z. Yang. 1998. Likelihood models for detecting
positively selected amino acid sites and applications to the HIV-1
envelope gene. Genetics 148:929-936.

Yang, Z., R. Nielsen, N. Goldman and A.-M. K. Pedersen. 2000. 
Codon-substitution models for heterogeneous selection pressure at amino 
acid sites. Genetics 155:431-449.
