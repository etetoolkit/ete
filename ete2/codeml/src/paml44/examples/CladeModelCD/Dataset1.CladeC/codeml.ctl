      seqfile = ECP_EDN_15.nuc * sequence data filename
     treefile = tree.txt      * tree structure file name
      outfile = results.txt           * main result file name

        noisy = 9  * 0,1,2,3,9: how much rubbish on the screen
      verbose = 0  * 0: concise; 1: detailed, 2: too much
      runmode = 0  * 0: user tree

      seqtype = 1  * 1:codons; 2:AAs; 3:codons-->AAs
    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table
        clock = 0  * 0:no clock, 1:clock; 2:local clock; 3:CombinedAnalysis

  			 * Model C: model = 3  NSsites = 2 
   			 * Model D: model = 3  NSsites = 3

        model = 3  * 3 = clade models
      NSsites = 2  * choose "2" or "3"
			 
        icode = 0  * 0:universal code; 1:mammalian mt; 2-10:see below

    fix_kappa = 0  * 1: kappa fixed, 0: kappa to be estimated
        kappa = 2  * initial or fixed kappa

    fix_omega = 0  * 1: omega or omega_1 fixed, 0: estimate 
        omega = 0.1 * initial or fixed omega, for codons or codon-based AAs

    fix_alpha = 1  * 0: estimate gamma shape parameter; 1: fix it at alpha
        alpha = 0. * initial or fixed alpha, 0:infinity (constant rate)

        ncatG = 2  * # of categories in dG of NSsites models

        getSE = 0  * 0: don't want them, 1: want S.E.s of estimates
 RateAncestor = 0  * (0,1,2): rates (alpha>0) or ancestral states (1 or 2)

   Small_Diff = .5e-6
    cleandata = 0  * remove sites with ambiguity data (1:yes, 0:no)?

