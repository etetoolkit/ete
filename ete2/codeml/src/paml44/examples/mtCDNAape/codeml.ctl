      seqfile = mtCDNAape.txt
     treefile = mtCDNAape.trees

      outfile = mlc           * main result file name
        noisy = 3  * 0,1,2,3,9: how much rubbish on the screen
      verbose = 0  * 0: concise; 1: detailed, 2: too much
      runmode = 0

      seqtype = 1  * 1:codons; 2:AAs; 3:codons-->AAs
    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table
                   * 4:F1x4MG, 5:F3x4MG, 6:FMutSel3x4, 7:FMutSelCodon
        clock = 0 * 0:no clock, 1:global clock; 2:local clock
       aaDist = 7  * 0:equal, +:geometric; -:linear, 1-6:G1974,Miyata,c,p,v,a
   aaRatefile = ../../dat/wag.dat * only used for aa seqs with model=empirical(_F)
                   * dayhoff.dat, jones.dat, wag.dat, mtmam.dat, or your own

        model = 2
                   * models for codons:
                      * 0:one, 1:b, 2:2 or more dN/dS ratios for branches

      NSsites = 0 * 0:one w;1:neutral;2:selection; 3:discrete;4:freqs;
                   * 5:gamma;6:2gamma;7:beta;8:beta&w;9:beta&gamma;
                   * 10:beta&gamma+1; 11:beta&normal>1; 12:0&2normal>1;
                   * 13:3normal>0; 

        icode = 1  * 0:universal code; 1:mammalian mt; 2-10:see below
        Mgene = 0
                   * codonml: 0:rates, 1:separate; 2:diff pi, 3:diff kapa, 4:all diff

    fix_kappa = 0  * 1: kappa fixed, 0: kappa to be estimated
        kappa = 1.234567    * initial or fixed kappa
    fix_omega = 0  * 1: omega or omega_1 fixed, 0: estimate 
        omega = 1.414  * initial or fixed omega, for codons or codon-based AAs

    fix_alpha = 1  * 0: estimate gamma shape parameter; 1: fix it at alpha
        alpha = 0. * initial or fixed alpha, 0:infinity (constant rate)
        ncatG = 3  * # of categories in dG of NSsites models

        getSE = 0  * 0: don't want them, 1: want S.E.s of estimates

   Small_Diff = .5e-6
*    cleandata = 0  * remove sites with ambiguity data (1:yes, 0:no)?
*        ndata = 10
*  fix_blength = -1  * 0: ignore, -1: random, 1: initial, 2: fixed
        method = 0   * 0: simultaneous; 1: one branch at a time
