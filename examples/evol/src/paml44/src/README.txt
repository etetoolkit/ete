Notes for compiling PAML on UNIX systems, including MAC OS X

Ziheng Yang (z.yang@ucl.ac.uk)
Last updated, 10 December 2003


Instructions for compiling 
==========================

Method I

Use the Makefile.  The default Makefile is for MS Windows/MSVC++.  You use Makefile.UNIX for UNIX/Linux/OSX:

   make -f Makefile.UNIX

   cp baseml basemlg codeml evolver pamp yn00 mcmctree chi2 ..
   rm *.o
   cd ..

On some systems you might have to edit the Makefile and change a few
flags at the beginning of the file.


Method II

You can also compile the programs from the command line.  Here are the
commands for the cc and gcc compilers.  You might have to recombine
the different choices (cc vs. gcc, -fast vs. -O2 or -O3, and with or
without -lm).  Make sure you turn on some optimization options (-O2,
-O3, -fast, etc.) as otherwise the code can be several times slower.
Below are a few possibilities.

(2a) MAC OS X Developer's Toolkit

cc -O2 -o baseml baseml.c tools.c -lm
cc -O2 -o basemlg basemlg.c tools.c -lm
cc -O2 -o codeml codeml.c tools.c -lm
cc -O2 -o pamp pamp.c tools.c -lm
cc -O2 -o mcmctree mcmctree.c tools.c -lm
cc -O2 -o evolver evolver.c tools.c -lm
cc -O2 -o yn00 yn00.c tools.c -lm
cc -O2 -o chi2 chi2.c -lm


(2b) gcc compiler

gcc -O3 -o baseml baseml.c tools.c
gcc -O3 -o basemlg basemlg.c tools.c
gcc -O3 -o codeml codeml.c tools.c
gcc -O3 -o pamp pamp.c tools.c
gcc -O3 -o mcmctree mcmctree.c tools.c
gcc -O3 -o evolver evolver.c tools.c
gcc -O3 -o yn00 yn00.c tools.c 
gcc -O3 -o chi2 chi2.c 

(2c) Digital UNIX/Digital cc compiler

cc -fast -o baseml baseml.c tools.c -lm
cc -fast -o basemlg basemlg.c tools.c -lm
cc -fast -o codeml codeml.c tools.c -lm
cc -fast -o pamp pamp.c tools.c -lm
cc -fast -o mcmctree mcmctree.c tools.c -lm
cc -fast -o evolver evolver.c tools.c -lm
cc -fast -o yn00 yn00.c tools.c -lm
cc -fast -o chi2 chi2.c -lm


// EOF
