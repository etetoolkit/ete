readme.txt
30 October 2000, 24 January 2003 (modified), Ziheng Yang

Rambaut's TipDate model is implemented using the symbol @ in the
sequence data file to specify the date of determination of each
sequence.  Note that the symbol and the date are considered part of
the sequence name, so that they should be used in the tree file.  Note
that to use the TipDate models, every sequence in the data file must
have a known date, and the program does not work if some sequences are
dated while other are not.  Have a look at both TipDate.phy and
TipDate.trees for the notation.  The sequence data file TipDate.phy is
directly usable by Rambaut's TipDate program, so you can use the @
notation to prepare a file readable by both programs.  Then choose
clock = 1 (global clock) to run the TipDate model.  To allow local
branch rates, you can use the symbol # in the tree file.  Look at the
files in the examples/mouselemurs/ for implementation of local clock
models.

The rest of the file contains two parts, as follows.

   (A) Results from running Andrew Rambaut's TipDate program.
   (B) baseml HKY85 global clock (clock=1)

References

Rambaut, A. 2000. Estimating the rate of molecular evolution: incorporating 
non-comptemporaneous sequences into maximum likelihood phylogenetics. 
Bioinformatics 16:395-399.

Yang, Z., and A. D. Yoder. 2003. Comparison of likelihood and Bayesian methods for estimating divergence times using multiple gene loci and calibration points, with application to a radiation of cute-looking mouse lemur species. Syst. Biol. 52:705-716.

Ziheng Yang




*************************************************
(A) Results from Andrew Rambaut's TipDate program

Note that I changed the file name from Andrew's example.phy to
TipDate.phy.  The command to run Andrew's TipDate is 

	tipdate -mHKY +s -v < TipDate.phy >out

Analysis of trees with dated tips - TipDate
Version 1.2
(c) Copyright, 1997-2001 Andrew Rambaut
Department of Zoology, University of Oxford
South Parks Road, Oxford OX1 3PS, U.K.

17 taxa, 1485 bases
        138 distinct patterns
Calculating likelihood of user supplied tree,
  iterating to find maximum likelihood branch lengths,
  assuming a molecular clock with dated taxa (SRDT model).
    Taxa dates range between 56 and 94,
    estimating the absolute rate of molecular evolution.
    and using the rate of change rate supplied = 0.000000
Rate homogeneity assumed.
Model=HKY
HKY85 model
  estimating ML transition/transversion ratio
  estimating base frequences from data
    frequencies = A:0.307506 C:0.187681 G:0.272450 T:0.232363
Tree in units of time:
(((((((((Brazi@82:1.52387882,(ElSal@83:0.86955431,NewCal@84:1.86955431):1.65432451):0.00001293,Mexico@84:3.52389175):1.37695033,ElSal@94:14.90084208):1.90479505,(PRico@86:7.72505490,Tahiti@85:6.72505490):1.08058224):0.00000000,Tahiti@79:1.80563713):4.79198989,Indon@77:4.59762703):1.05572925,Indon@76:4.65335628):39.69611913,(((Philip@64:3.86265651,Philip@84:23.86265651):7.33594953,Philip@56:3.19860604):13.22151465,(SLanka@78:21.63676446,(Thai@78:6.99850875,Thai@84:12.99850875):14.63825571):16.78335624):7.92935471):7.55525759,Thai@63:38.90473300);
Estimated value of Ts/Tv: 8.901642 (kappa=17.022524)
Estimated absolute rate of molecular evolution: 0.00077366
Absolute age of tree: 69.904733 (in the same units as the taxon dates,
        measured to the most recent tip).

Tree ln Likelihood = -3849.932714

Time taken - core: 4.827, total: 4.887 seconds


******************
(B) baseml clock=1

BASEML (in paml 3.13b, February 2003)  TipDate.phy  HKY85  Global clock 
ns = 17  	ls = 1485
# site patterns = 138

TREE #  1:  (((((((((1, (2, 7)), 6), 3), (11, 14)), 13), 5), 4), (((8, 10), 9), (12, (16, 17)))), 15);  MP score: 312.00
lnL(ntime: 17  np: 18):  -3849.932737   +0.000000
  18..19   19..20   20..21   21..22   22..23   23..24   24..25   25..26   26..1    26..27   27..2    27..7    25..6    24..3    23..28   28..11   28..14   22..13   21..5    20..4    19..29   29..30   30..31   31..8    31..10   30..9    29..32   32..12   32..33   33..16   33..17   18..15 
  0.36792  0.32816  0.11923  0.11367  0.08845  0.08845  0.07843  0.07118  0.07118  0.06247  0.08276  0.28642  0.21684  0.17823  0.19809  0.12105  0.14699 17.02252
SEs for parameters:
  0.03565  0.03264  0.00829  0.00795  0.00479  0.00480  0.00702  0.00454  0.00454  0.00463  0.00550  0.02551  0.00860  0.01028  0.02008  0.01185  0.01934  2.97312

Note: mutation rate is not applied to tree length.  Tree has times, for TreeView

(((((((((Brazi@82, (ElSal@83, NewCal@84)), Mexico@84), ElSal@94), (PRico@86, Tahiti@85)), Tahiti@79), Indon@77), Indon@76), (((Philip@64, Philip@84), Philip@56), (SLanka@78, (Thai@78, Thai@84)))), Thai@63);

(((((((((Brazi@82: 1.523930, (ElSal@83: 0.869570, NewCal@84: 1.869570): 1.654360): 0.000002, Mexico@84: 3.523932): 1.376981, ElSal@94: 14.900913): 1.904789, (PRico@86: 7.725130, Tahiti@85: 6.725130): 1.080572): 0.000005, Tahiti@79: 1.805707): 4.792057, Indon@77: 4.597763): 1.055732, Indon@76: 4.653495): 39.696751, (((Philip@64: 3.862769, Philip@84: 23.862769): 7.335980, Philip@56: 3.198749): 13.222004, (SLanka@78: 21.637157, (Thai@78: 6.998700, Thai@84: 12.998700): 14.638457): 16.783596): 7.929492): 7.555240, Thai@63: 38.905485);

Detailed output identifying parameters

Substitution rate is per time unit
    0.000774 +- 0.000101

Nodes and Times
(JeffNode is for Thorne's multidivtime.  ML analysis uses ingroup data only.)

Node   1 (Jeffnode   0) Time   82.00 
Node   2 (Jeffnode   1) Time   83.00 
Node   3 (Jeffnode   2) Time   94.00 
Node   4 (Jeffnode   3) Time   76.00 
Node   5 (Jeffnode   4) Time   77.00 
Node   6 (Jeffnode   5) Time   84.00 
Node   7 (Jeffnode   6) Time   84.00 
Node   8 (Jeffnode   7) Time   64.00 
Node   9 (Jeffnode   8) Time   56.00 
Node  10 (Jeffnode   9) Time   84.00 
Node  11 (Jeffnode  10) Time   86.00 
Node  12 (Jeffnode  11) Time   78.00 
Node  13 (Jeffnode  12) Time   79.00 
Node  14 (Jeffnode  13) Time   85.00 
Node  15 (Jeffnode  14) Time   63.00 
Node  16 (Jeffnode  15) Time   78.00 
Node  17 (Jeffnode  16) Time   84.00 
Node  18 (Jeffnode  32) Time   24.09  +-   6.73
Node  19 (Jeffnode  31) Time   31.65  +-   6.17
Node  20 (Jeffnode  30) Time   71.35  +-   1.57
Node  21 (Jeffnode  29) Time   72.40  +-   1.51
Node  22 (Jeffnode  28) Time   77.19  +-   0.91
Node  23 (Jeffnode  27) Time   77.19  +-   0.91
Node  24 (Jeffnode  26) Time   79.10  +-   1.33
Node  25 (Jeffnode  25) Time   80.48  +-   0.86
Node  26 (Jeffnode  24) Time   80.48  +-   0.86
Node  27 (Jeffnode  23) Time   82.13  +-   0.88
Node  28 (Jeffnode  22) Time   78.27  +-   1.04
Node  29 (Jeffnode  21) Time   39.58  +-   4.82
Node  30 (Jeffnode  20) Time   52.80  +-   1.63
Node  31 (Jeffnode  19) Time   60.14  +-   1.95
Node  32 (Jeffnode  18) Time   56.36  +-   3.80
Node  33 (Jeffnode  17) Time   71.00  +-   2.25

Parameters (kappa) in the rate matrix (HKY85) (Yang 1994 J Mol Evol 39:105-111):
 17.02252

//end of file
