
To start
  Slr -seqfile alignment.paml -treefile tree_file

E.g. (In Examples/bglobin)
  Slr -seqfile bglobin.paml -treefile bglobin.trees


Options
-------
  Options may be specified in two ways, in a control file or on the
command line. Options given on the command line override those given 
in a control file, which in turn override the default options. The
format for calling Slr is:

  Slr [control_file] [-option value ...]

  The name of a control file can be given as the first argument to the
program, otherwise Slr expects "-option value" pairs, where
"option" is the name of the option to set and "value" what to set it
to. If no control file is given, Slr attempts to read options from
the default control file "slr.ctl".

Examples:
Read options from default control file or to use default
options.
  Slr
As above, but over-ride output file
  Slr -outfile outfile.new
Read options from the file "myoptions.ctl"
  Slr myoptions.ctl
Same, but use different tree
  Slr myoptions.ctl -treefile newtree

Control file
------------
  The format of the control file is option, value pairs. The options
and allowed values being the same those that may be specified on the
command line. Each option should be on a separate line.
option1: value1
option2: value2
 etc....
  If a line contains a '#', then all text after the symbol is ignored.

E.g.
  # Control file for beta-globin example
  seqfile: bglobin.paml
  treefile: bglobin.trees
  outfile: out.res
  positive_only: 0



Allowed options
---------------

Default values for each option are given in square brackets.

seqfile [incodon]
  File from which to read alignment of codon sequences. The file
  should be in PAML format.

treefile [intree]
  File from which tree should be read. The tree should be in Nexus
  format

outfile	[slr.res]
  File to which results are written. If the file already exists, it will
  be overwritten.

reoptimise [1]
  Should the branch lengths, omega and kappa be reoptimized?
  0 - no.
  1 - yes.
  2 - yes; set initial branch lengths to random values.

kappa [2.0]
  Value for kappa. If 'reoptimize' is specified, the value
  given will be used as an initial estimate. If less than zero, a
  random value will be used as an initial estimate.

omega [0.1]
  Value for omega (dN/dS). If 'reoptimize' is specified, the value
  given will be used as an initial estimate. If less than zero, a
  random value will be used as an initial estimate.

branopt [1]
  Whether and how to optimise branches.
  0 - hold branches fixed
  1 - optimise branch lengths (if reoptimise specified)
  2 - hold branch lengths proportional to initial in optimisation
(if done).

codonf [0]
  How codon frequencies are estimated:
    0: F61/F60	Estimates used are the empirical frequencies from the
  data.
    1: F3x4	The frequencies of nucleotides at each codon position
  are estimated from the data and then multiplied together to get the
  frequency of observing a given codon. The frequency of stop codons is
  set to zero, and all other frequencies scaled appropriately.
    2: F1x4	Nucleotide frequencies are estimated from the data
  (not taking into account at which position in the codon it occurs).
  The nucleotide frequencies are multiplied together to get the frequency 
  of observing and then corrected for stop codons.

freqtype [0]
  How codon frequencies are incorporated into the substitution matrix.
  0: q_{ij} = pi_{j} s_{ij}
  1: q_{ij} = \sqrt(pi_j/pi_i) s_{ij}
  2: q_{ij} = \pi_{n} s_{ij}, where n is the nucleotide that the 
  subsitution is to.
  3: q_{ij} = s_{ij} / pi_i
  Option 0 is the tradition method of incorporating equilibrium frequencies
  into subsitution matrices (Felsenstein 1981; Goldman and Yang, 1994)
  Option 1 is described by Goldman and Whelan (2002), in this case with the
  additional parameter set to 0.5.
  Option 2 was suggested by Muse and Gaut (1994).
  Option 3 is included as an experiment, originally suggested by Bret Larget.
  it does not appear to describe evolution very successfully and should not
  be used for analyses.

  Kosakovsky-Pond has repeatedly stated that he finds incorporating codon
  frequencies in the manner of option 2 to be superior to option 0. We find
  that option 1 tends to perform better than either of these options.
  
positive_only [0]
  If only positively selected sites are of interest, set this to "1".
  Calculation will be slightly faster, but information about sites under
  purifying selection is lost. 

gencode [universal]
  Which genetic code to use when determining whether a given mutation
  is synonymous or nonsynonymous. Currently only "universal" and
  "mammalian" mitochondrial are supported.

nucleof [0]
  Allow for empirical exchangabilities for nucleotide substitution.
  0: No adjustment. All nucleotides treated the same, modulo 
  transition / transversion.
  1: The rate at which a substitution caused a mutation from nucleotide
  a to nucleotide b is adjust by a constant N_{ab}. This adjustment is 
  in addition to other adjustments (e.g. transition / transversion or
  base frequencies).
  

aminof [0]
  Incorporate amino acid similarity parameters into substitution matrix,
  adjusting omega for a change between amino acid i and amino acid j.
  A_{ij} is a symmetric matrix of constants representing amino acid
  similarities.
  0: Constant omega for all amino acid changes
  1: omega_{ij} = omega^{A_{ij}}
  2: omega_{ij} = a_{ij} log(omega) / [ 1 - exp(-a_{ij} log(omega)) ]
  Option 1 has the same form as the original codon subsitution model 
  proposed by Goldman and Yang (but with potentially different 
  constants).
  Option 2 has a more population genetic derivtion, with omega being
  interpreted as the ratio of fixation probabilities.

nucfile [nuc.dat]
  If nucleof is non-zero, read nucleotide substitution constants from
  nucfile. If this file does not exist, hard coded constants are used.

aminofile [amino.dat]
  If aminof is non-zero, read amino acid similarity constants from
  aminofile. If this file does not exist, hard coded constants are used.

timemem [0]
  Print summary of real time and CPU time used. Will eventually print
  summary of memory use as well.

ldiff [3.841459]
  Twice log-likelihood difference used as a threshold for calculating 
  support (confidence) intervals for sitewise omega estimates. This 
  value should be the quantile from a chi-square distribution with one
  degree of freedom corresponding to the support required. 
  E.g. qchisq(0.95,1) = 3.841459
     0.4549364 = 50% support
     1.323304  = 75% support
     2.705543  = 90% support
     3.841459  = 95% support
     6.634897  = 99% support
     7.879439  = 99.5% support
    10.82757   = 99.9% support

paramin []
  If not blank, read in parameters from file given by the argument.

paramout []
  If not blank, write out parameter estimates to file given.

skipsitewise [0]
  Skip sitewise estimation of omega. Depending on other options given, 
  either calculate maximum likelihood or likelihood fixed at parameter
  values given.

seed [0]
  Seed for random number generator. If seed is 0, then previously 
  produced seed file (~/.rng64) is used. If this does not exist, the
  random number generator is initialised using the clock.

saveseed [1]
  If non-zero, save finial seed in file (~/.rng64) to be used as initial
  seed in future runs of program.
