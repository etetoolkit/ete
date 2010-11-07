Notes by Ziheng, 12 August 2003, modified in October 2008

(A) This is about codon models for McDonald & Kreithman-style test using
the ape mt data used in Hasegawa et al. (1998).

mtCDNAape.nuc
mtCDNAape.trees

The following are model specifications and log likelihood values, as
well as MLEs.  "W" and "B" refer to within- and between-species
branches.  "R" and "C" refer to radical and conserved amino acid
changes.


np=11 model=0 aaDist=0: lnL=-20486.034301  k=20.74839  w=0.04414

np=12 model=2 aaDist=0: lnL=-20444.099676  k=21.59077  wW=0.28638  wB=0.03693

np=12 model=0 aaDist=7: lnL=-20482.229434  k=20.52018  wR=0.02745  wC=0.04658

np=14 model=2 aaDist=7: lnL=-20440.382774  k=21.36004  wWR=0.15012  wWC=0.30470  wBR=0.02380  wBC=0.03885


(B) mtCDNA.HC.txt (control file codeml.HC.ctl) has the human and chimp sequences only, and is the dataset 
analyzed by Yang and Nielsen (2008, table 1).  The new models described in that 
paper are implemented using the two control variables CodonFreq and estFreq in 
the control file codeml.ctl.  You can try to duplicate our results.

    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table
                   * 4:F1x4MG, 5:F3x4MG, 6:FMutSel0, 7:FMutSel
      estFreq = 0

Run the analysis by 
    codeml codeml.HC.ctl

In this case, the control file specifies clock = 1.  The clock is used
as there are only 2 sequences and the tree (2s.trees) is rooted.  If
you have more than 2 sequences, you should use an unrooted tree and
clock = 0.




References

Hasegawa, M., Y. Cao and Z. Yang. 1998. Preponderance of slightly
deleterious polymorphism in mitochondrial DNA: replacement/synonymous
rate ratio is much higher within species than between
species. Molecular Biology and Evolution 15:1499-1505.

Yang Z, Nielsen R. 2008. Mutation-selection models of codon substitution 
and their use to estimate selective strengths on codon usage. 
Molecular Biology and Evolution 25:568-579.

Yang, Z., R. Nielsen and M. Hasegawa. 1998. Models of amino acid
substitution and applications to mitochondrial protein
evolution. Molecular Biology and Evolution 15:1600-1611.
