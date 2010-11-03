      seqfile = bigmhc.phy
     treefile = bigmhc.trees

      outfile = mlc
        noisy = 3
      verbose = 0
      runmode = 0

      seqtype = 1
    CodonFreq = 2
   aaRatefile = jones.dat
        model = 0
      NSsites = 0 1 2 7 8
        icode = 0
        Mgene = 0  * for codons:
                     * 0:rates, 1:separate; 2:diff pi, 3:diff k&w, 4:all diff
    fix_kappa = 0
        kappa = 1.6
    fix_omega = 0
        omega = .9

    fix_alpha = 1
        alpha = 0
        ncatG = 10

        clock = 0
        getSE = 0
 RateAncestor = 0

   Small_Diff = .1e-6
*    cleandata = 1
        method = 1
   fix_blength = 2  * 0: ignore, -1: random, 1: initial, 2: fixed
