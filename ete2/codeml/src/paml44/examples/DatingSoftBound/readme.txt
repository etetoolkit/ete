MCMCTREE
Ziheng Yang

4 October 2005, modified in March 2007 & August 2009

(A) You can use the files in this folder to run mcmctree to duplicate the
results of Yang and Rannala (2006: table 3) and Rannala and Yang
(2007, table table 2).  

    ..\..\bin\mcmctree

Make your window wider (100 columns) before running the program.  See
the section on mcmctree in the paml manual for a description of the
program.  The default control file with usedata = 1 means the use of
the exact likelihood calculation.

(B) To use the approximate likelihood calculation, do the following.

(b1) Copy baseml.exe from the paml/bin folder to the current folder.
(b2) Edit mcmctree.ctl to use usedata = 3.  Run mcmctree.  
     ..\..\bin\mcmctree
     This generates a file named out.BV.  Rename it in.BV
(b3) Edit mcmctree.ctl to use usedata = 2.  Run mcmctree again.  
     ..\..\bin\mcmctree

The exact and approximate likelihood calculations generate very
similar results for this dataset.


References

Rannala, B., and Z. Yang. 2007. Inferring speciation times under an
episodic molecular clock. Syst. Biol. 56: 453-466.

Yang, Z., and B. Rannala. 2006. Bayesian estimation of species
divergence times under a molecular clock using multiple fossil
calibrations with soft bounds. Mol. Biol. Evol.: 23: 212-226.
