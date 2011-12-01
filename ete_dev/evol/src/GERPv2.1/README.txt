Overview
--------
GERP is a package for analyzing evolutionary rates and finding constrained elements in a multiple alignment.  We use the notion of "rejected substitutions" (RS) in order to quantify constraint at individual positions as well as over elements spanning multiple positions.

GERP consists of two main components:  gerpcol, which analyzes multiple alignments and computes RS scores for all positions, and gerpelem, which finds constrained elements given the RS scores produced by gerpcol.  Gerpcol and gerpelem are described in detail below.

Both gerpcol and gerpelem use the -h flag to display a help menu and a -v flag for verbose/more detailed output.


Setup
-----
Using the provided Makefile ('make') will compile both gerpcol and gerpelem.  If necessary, each program can be compiled individually using 'make gerpcol' or 'make gerpelem'.

If typing 'make' results in a 'command not found' error, this indicates that the g++ compilier (necessary to compile GERP) may not be installed.  

Mac OSX users can get g++ by installing Xcode, either from the OSX install disk, or by downloading it from http://developer.apple.com/tools/.

Gerpcol Summary
---------------
Given an evolutionary tree and one or more multiple alignments, gerpcol will compute RS scores for every position of each alignment by doing the following:

1) Project the evolutionary tree to the set of species that are present at that position. If there are fewer than 3 species remaining, gerpcol will not perform the main computation and will instead output a neutral rate and RS score of 0 for this position.

2) Compute the total neutral rate N of the projected tree from (1) by summing the branch lengths of the tree.

3) Compute the scaling factor k that will maximize the probability of the leaf nucleotides given the scaled tree.  This probability is computed using the HKY85 model of evolution with nucleotide frequencies f(N) estimated from the multiple alignment data and the Tr/Tv rate parameter r settable by the user (default = 2.0).  The HKY85 matrix used:

        A       C       G        T
A       *      f(C)   f(G)r     f(T)
C      f(A)     *      f(G)    f(T)r
G     f(A)r    f(C)     *       f(T)
T      f(A)   f(C)r    f(G)      *


The optimal scaling factor k is computed using numerical optimization.

4) Compute the rejected substitution score for the position by computing the quantity S = N - N*k.  This represents the number of substitutions "rejected" by evolutionary constraint, i.e. the difference between the expected (i.e. neutral rate) and the observed (maximum likelihood estimate).  This quantity will be capped from below at -2*N; since k is by definition nonnegative, the final RS score will be between -2*N and N, inclusive.


Gerpcol Input
-------------
Gerpcol requires an evolutionary tree and at least one multiple alignment file to be processed.  The tree is specified using the -t parameter and the filename.  The tree file should contain exactly one line specifying the tree in the standard nested parentheses/Newick format, including branch lengths.  The tree may be either rooted or unrooted, for example:

rooted
((human:0.02,chimp:0.03):0.72,(cat:0.48,dog:0.61):1.09);

unrooted
(human:0.02,chimp:0.03,(cat:0.48,dog:0.61):1.91);

If the branch lengths are in units other than subsitutions per site, it may be necessary to scale the input tree by a certain amount or to have a specific total neutral rate.  This functionality is provided by the parameters -s and -n, respectively.  If both parameters are used, the -n parameter takes precedence and the tree will be scaled to the specified total neutral rate.

Multiple alignments to be processed must be in the mfa format and can be specified one at a time using the -f flag, e.g.

./gerpcol -f region1.mfa -f region2.mfa -f region3.mfa ...

Alternatively, it is possible to make a list of all files that need to be processed and specify that list using the -F parameter, i.e.

./gerpcol -F regionlist.txt ...

where the file regionlist.txt will contain the filenames, one per line:

region1.mfa
region2.mfa
region3.mfa


Gerpcol Output
--------------
For each multiple alignment file that is processed, gerpcol will create an output file in the same directory by adding a suffix to the mfa filename.  This suffix defaults to ".rates" and can be changed using the -x parameter, e.g.

./gerpcol -f region1.mfa -f region2.mfa -x ".out" ...

will produce output files region1.mfa.out and region2.mfa.out.

These output files contain one line for each position of the alignment. Each line consists of the neutral rate N (from step 2) and RS score S (from step 4), separated by a tab character, for that alignment position.  Sample output may look like this:

1.05	-1.1
1.05	1.05
1.23	1.23
1.23	-1.98
1.23	-1.23
1.23	0.288
...



Gerpelem Summary
----------------
Given a rates file as output by gerpcol, gerpelem will find and report a list of elements that appear constrained beyond what is likely to occur by chance.  However, repetitive elements present only in a shallow subset of the alignment can appear to fit this criterion. Therefore, gerpelem incorporates certain heuristic measures to remove such elements from consideration; (it does not utilize repeat annotations).  The main steps of the gerpelem algorithm are as follows:

1) Calculate the median neutral rate of the alignment columns.  This value is different from (smaller than) the neutral tree length because many columns will have one or more species missing due to indels or incomplete data.

2) Mark all columns whose neutral rate is below a given depth  as shallow; this depth can be specified using the -d parameter and defaults to 0.5 subsitutions per site.  Rather than the rejected substitution score computed by gerpcol, these columns will be penalized as a multiple of the median neutral rate (calculated in 1) of the alignment:  they will get the score -k * neutral_rate, where the parameter k can be set using the -p flag (default = 0.5).  All columns where gerpcol failed to perform the computation due to an insufficient number of species present will automatically be penalized in this way.

3) Generate a list of candidate constrained elements or all segments that fit the following criteria:
 (a) Starts on a position with positive RS score.
 (b) Ends on a position with positive RS score.
 (c) Cannot be extended further without violating (a) or (b).
 (d) Has length at least Lmin, specified by the -l parameter, defaults = 4
 (e) Has length no more than Lmax, specified by the -L parameter, default = 2000
 (f) Score is at least (neutral_rate / q) * length ^ r, where the parameters q and r can be specified using the -q and -r flags and default to 10.0 and 1.15 respectively. [Note:  this is done to keep memory requirements in check, and will result in a large number of virtually unconstrained candidate elements to be excluded.]
 (g) No more than a pre-allowed number (controlled by the -a parameter, default = 10) of shallow columns that are in the middle of a longer shallow region.  In any consecutive segment of shallow columns we permit a border of b columns at the start and end that do not count towards this total; this number is controlled by the -b parameter and defaults to 2.

4) Each candidate element of length L and score S is assigned a p-value, corresponding to the probability that a score of at least S occurs at random in a block of L positions.  For computational purposes, all position and element scores are rounded to a predefined tolerance, which defaults to 0.1 and can be changed using the -t parameter to specify the inverse of this tolerance (for example, -t 20 to round to the nearest 0.05).  To model the null distribution we use the RS scores from the alignment, except the non-border shallow columns described in 3(g).  We also add a small uniform smoothing prior over the set of possible scores to avoid having 0 probabilities.

5) The candidate elements are sorted and reported in order of increasing p-value as long as they do not overlap any previously reported elements.  This procedure continues until we exceed a cutoff false positive rate, which is specified using the -e parameter and defaults to 0.01 (1%).  To estimate the number of false positives at a given p-value, we randomly shuffle the positions of the alignment, apply steps (2)-(5) to generate elements, and consider those elements as false positives.  This is performed multiple times and the results averaged in order to attain a more accurate estimation of the false positive rate.

6) In order to make the background distribution more accurately reflect the score distribution in neutral regions, we exclude not only non-border shallow columns but also a set of clearly constrained elements.  Thus, a predefined fraction (controlled by the -u parameter, default = 0.5) of the elements found in step (5) are excluded from the background distribution in step (4) and the shuffled alignments in step (5).  (These exclusion regions can be written to a file by using the -w parameter along with a suffix; by default no such file is output.)  The computation is then repeated and the resulting set of elements is reported.

Gerpelem Input
--------------
The input to gerpelem is a single file in precisely the same format as the output of gerpcol.  The filename is specified using the -f flag.  Please see the Gerpcol Output section for details.


Gerpelem Output
---------------
Gerpelem will create an output file in the same directory as the input rates file by adding a suffix to the that filename.  This suffix defaults to ".elems" and can be changed using the -x parameter similar to gerpcol.  Optionally, if the -w parameter and suffix is specified, gerpelem will also output a list of exclusion regions as described in part (5) of the Gerpelem Summary section.

The output file(s) will contain one line for each constrained element found, listed in order of increasing p-value.  We report the following values for each element, separated by spaces:

start	end	length	     RS-score	p-value


Contacts
--------
For additional information and/or updated versions of this package contact:

Eugene Davydov		edavydov@cs.stanford.edu
David Goode		dgoode@stanford.edu
GERP is available at http://mendel.stanford.edu/downloads/GERP/index.html

