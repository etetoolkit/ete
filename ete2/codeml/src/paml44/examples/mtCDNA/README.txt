readme.txt
May 2002

Files included in the folder:

      mtCDNApri.nuc:  codon sequences from 7 apes (small data set in Yang et al. 1998)
      mtCDNApri.trees: tree file for the data
      OmegaAA.dat: file specifying different types of amino acid substitutions
      codeml.ctl: control file 

Also the following two files are incldued (large data set in Yang et al. 1998)
      mtCDNApri.nuc
      mtCDNApri.trees

This directory contains example files for estimating
nonsynonymous/synonymous substitution rate ratios for different types
of amino acid changes.  The data were used in Yang et al. (1998), so
you can use the data to duplicate results in that paper.

(1) Table 5 and the section titled "Different types of amino acid
substitutions".  This model assumes different dn/ds (w) ratios for
different types of amino acid substitutions.  You specify how many
amino acid substitution types you would like to have and which amino
acid pairs (changes) should be in each type.  The data should be codon
sequences (seqtype = 1), and the model is specified by aaDist = 7
(AAClasses).  The details of amino acid substitution types are
specified in a file called OmegaAA.dat.  See that file for details.
The model can be used to fit different rates for "radical" and
"conserved" amino acid substitutions.

Yang et al. (1998) implemented the model for codon sequences only
(seqtype = 1).  In theory the model should be applicable to amino acid
sequences as well (seqtype = 2), with one fewer parameter required.
However, such models (for amino acid sequences) are either not tested
properly or never made to work.  If you need to apply such models to 
amino acid sequences, you can let me know and I'll try to savalge the model.


(2) Table 4.  Mechanistic models of codon substitution.  You should have
seqtype = 1, model = 0, NSsites = 0.  Then the models are specified
using aaDist as follows.  You need to copy files with names like
g1974c.dat, g1974p.dat, g1974v.dat, g1974a.dat, grantham.dat, or
miyata.dat into the current folder to run those models.

       aaDist = 1  * geometric relationship using Grantham
       aaDist = 2  * geometric relationship using Miyata & Yasunaga
       aaDist = 3  * geometric relationship using c (composition)
       aaDist = 4  * geometric relationship using p (polarity)
       aaDist = 5  * geometric relationship using v (volume)
       aaDist = 6  * geometric relationship using a (aromaticity)

       aaDist = -1  * linear relationship using Grantham
       aaDist = -2  * linear relationship using Miyata & Yasunaga
       aaDist = -3  * linear relationship using c (composition)
       aaDist = -4  * linear relationship using p (polarity)
       aaDist = -5  * linear relationship using v (volume)
       aaDist = -6  * linear relationship using a (aromaticity)


(3) Table 3.  Mechanistic models of amino acid substitution.  As above
for table 4, but you should have seqtype = 2, model = 6 (FromCodon),
NSsites = 0.  Note that with amino acid sequences only, we cannot
estimate synonymous rate, and the models have one fewer parameter than
when codon sequences are used.

The models were implemented several years ago and not carefully
maintained since then.  So let me know you notice anything strange.
You should always run the example data set to duplicate the results in
the paper.

Reference:

Yang, Z., R. Nielsen, and M. Hasegawa, 1998.  Models of amino acid
substitution and applications to mitochondrial protein
evolution. Mol. Biol. Evol. 15: 1600-1611.

Ziheng Yang
