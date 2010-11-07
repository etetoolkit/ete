Notes by Ziheng Yang
Last modified: 22 July2003

(I) Data files for NSsites models used by Yang, Swanson & Vacquier (2000):

    README.txt
    lysin.trees (tree file)
    lysin.nuc  (sequence data file, with 135 codons)
    codeml.ctl  (control file)
    lysinResult.txt (results under M0 and M3)
    lysinPosteriorP.txt (posterior probabilities under M3)
    SiteNumbering.txt (site numbering according to the structure file)
    1LIS.pdb            (structure file for red abalone sperm lysin)


(II) Data files for fixed-sites models of Yang & Swanson (2002).  Note
    that the tree file is shared as above, but the sequence data file is 
    different, with one site with gaps in the red abalone deleted.  
    Yang & Swanson (2002 table 5) also fitted two random-sites (NSsites) 
    models, using the following data:

    codemlYangSwanson2002.ctl (controld file)
    lysinYangSwanson2002.nuc  (sequence data file, with 134 codons)
    lysin.trees


More details follow.

(Ia) 
This folder contains the control file, the sequence data file and
the tree file for demonstrating codon models that assign different
dN/dS ratios among sites in the sequence (Nielsen & Yang 1998; Yang,
Nielsen, Goldman & Pedersen 2000).  The included data set is the sperm
lysin genes from 25 abalone species used in Yang, Swanson & Vacquier
(2000).  The default control file (with NSsites = 3) lets you
duplicate the results in table 1 of that paper.  To run the program,
try

	codeml

The file lysinPosteriorP.txt includes part of the output from the file
rst for model M3 (NSsites=3).  The first 3 columns are the three
probabilities for the three site classes; you can use them to make
figure 1 of Yang, Swanson & Vacquier (2000).  In parentheses are the
most likely class numbers.  The last two columns are the posterior
average w for the site and the probability for the most likely class
(redundant).

(Ib) Colouring the Crystal Structure

If you choose verbose = 1 and provide a file named SiteNumbering.txt
with numbering of sites in the alignment, codeml will generate a file
named RasMol.txt, which collects RasMol (RasWin) scripts for coloring
the amino acid residues in the structure according to the approximate
posterior mean_w.  Look at SiteNumbering.txt.  The sequence data
file lysin.nuc has 135 amino acid (codon) sites in the alignment, but
one site is a gap, represented by the ? in SiteNumbering.txt, which is
not in the pdf file.  Compare this with Figures 4 and 5 in Yang,
Swanson, and Vacquier (2000).  

Here are the rules codeml uses right now.  The program copies your
site labels in SiteNumbering.txt verbatim as "text" (not as number)
when it prints to RasMol.txt.  If the label has a question mark in it,
codeml won't print that site, but all other sites with no ? in the
labels are printed (using the format "select ###", "color ....".  So
if you change the ? in the included SiteNumbering.txt for the lysin
into 133a, you will get the following output in RasMol.txt for that
site:

	select 133a
        color [250, 35, 35]

After codeml has generated RasMol.txt, you read the structure file
1LIS.PDB into RasMol.  Choose "Display-Cartoon".  Then in the
command-line window, type the following command to color the amino
acids.

       script RasMol.txt

My version of RasMol (RasWin2.7.2.1) does not seem to be properly
installed, and I can't tell it to look for the file from the right
folder.  So I copied RasMol.txt into the same folder as
raswin2.7.1.1.exe and it reads the script fine.  I got a warning
message from RasWin: "Unable to allocate shade".  I don't know what it
means, but it does not seem to do any harm.

Both filenames SiteNumbering.txt and RosMol.txt are hard-coded in
codeml.c.  I implemented three colour schemes, hard-coded as well,
with the colour-coded temperature matching the posterior mean w.  If
you want to change the source code, go to the routine
lfunNSsites_rate() and change continuous, ncolors, colorvalues (RGB
values).

The red abalone lysin structure file 1LIS.pdb can be downloaded from
http://www.rcsb.org/pdb/ (choose download - text format).  The RasMol
site is at http://www.umass.edu/microbio/rasmol/.


(II)

The lysin gene data used by Yang & Swanson (2002) to demonstrate the
fixed-sites models are included here as well.  The sequence data file
lysinYangSwanson2002.nuc has one fewer codon than lysin.nuc.  Look at
the beginning of the sequence data file, copied below, which says
there are 25 sequences in the file, each with 402 nucleotides (134
codons).  The 134 codons are partitioned into two "genes", which are
marked by 1 or 2, for buried and exposed residues, respectively.  

  25   402  G
G2
22222222221222112111221121122212211222122122222211211112211221221122122
212222222222112211221122221222122122222112122212211222222121212

In the control file, note the variable Mgene, which is used to run the
models described in Yang & Swanson (2002, table 1), with results shown
in table 6 of the same paper.  To run the program, you type
    codeml codemlYangSwanson2002.ctl

If you are using an old mac with OS 9 or earlier, you make a copy of 
codeml.ctl and then copy codemlYangSwanson2002.ctl into codeml.ctl and 
then run 
   codeml

method = 0 is probably faster for those Mgene models than method = 1.


References

Nielsen, R., and Z. Yang. 1998. Likelihood models for detecting
positively selected amino acid sites and applications to the HIV-1
envelope gene. Genetics 148:929-936.

Yang, Z., R. Nielsen, N. Goldman and A.-M. K. Pedersen. 2000. 
Codon-substitution models for heterogeneous selection pressure at amino 
acid sites. Genetics 155:431-449.

Yang, Z., W. J. Swanson and V. D. Vacquier. 2000. Maximum likelihood
analysis of molecular adaptation in abalone sperm lysin reveals
variable selective pressures among lineages and
sites. Mol. Biol. Evol. 17:1446-1455.

Yang, Z., and W. J. Swanson. 2002. Codon-substitution models to detect
adaptive evolution that account for heterogeneous selective pressures
among site classes. Mol. Biol. Evol. 19:49-57.
