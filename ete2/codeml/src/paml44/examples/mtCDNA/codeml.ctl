      seqfile = mtCDNApri.nuc
     treefile = mtCDNApri.trees

      outfile = mlc           * main result file name
        noisy = 9  * 0,1,2,3,9: how much rubbish on the screen
      verbose = 1  * 0: concise; 1: detailed, 2: too much
      runmode = 0

      seqtype = 1  * 1:codons; 2:AAs; 3:codons-->AAs
    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table
        clock = 0
       aaDist = 0  * 0:equal, +:geometric; -:linear, 1-6:G1974,Miyata,c,p,v,a
   aaRatefile = wag.dat * only used for aa seqs with model=empirical(_F)
                   * dayhoff.dat, jones.dat, wag.dat, mtmam.dat, or your own

        model = 0
                   * models for codons:
                       * 0:one, 1:b, 2:2 or more dN/dS ratios for branches
                   * models for AAs or codon-translated AAs:
                       * 0:poisson, 1:proportional, 2:Empirical, 3:Empirical+F
                       * 6:FromCodon, 7:AAClasses, 8:REVaa_0, 9:REVaa(nr=189)
      NSsites = 0
        icode = 1  * 0:universal code; 1:mammalian mt; 2-10:see below
    fix_kappa = 0
        kappa = 5
    fix_omega = 0
        omega = 0.2

        getSE = 0
 RateAncestor = 0

   Small_Diff = .5e-6
     cleandata = 1  * remove sites with ambiguity data (1:yes, 0:no)?
        method = 0   * 0: simultaneous; 1: one branch at a time
