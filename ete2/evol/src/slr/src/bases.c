/*
 *  Copyright 2003-2008 Tim Massingham (tim.massingham@ebi.ac.uk)
 *  Funded by EMBL - European Bioinformatics Institute
 */
/*
 *  This file is part of SLR ("Sitewise Likelihood Ratio")
 *
 *  SLR is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  SLR is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with SLR.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <float.h>
#include <math.h>
#include "gencode.h"
#include "bases.h"

char Amino[22] = "ARNDCQEGHILKMFPSTWYV-";
char Nucleo[6] = "ACGT-";



/*  Convert a single character alphabetical representation of an amino acid to
 * integer*/
int ToAmino (char c)
{

  c = toupper (c);
  switch (c) {
  case 'A':
    return 0;
  case 'R':
    return 1;
  case 'N':
    return 2;
  case 'D':
    return 3;
  case 'C':
    return 4;
  case 'Q':
    return 5;
  case 'E':
    return 6;
  case 'G':
    return 7;
  case 'H':
    return 8;
  case 'I':
    return 9;
  case 'L':
    return 10;
  case 'K':
    return 11;
  case 'M':
    return 12;
  case 'F':
    return 13;
  case 'P':
    return 14;
  case 'S':
    return 15;
  case 'T':
    return 16;
  case 'W':
    return 17;
  case 'Y':
    return 18;
  case 'V':
    return 19;
  case '-':
    return 20;
  }

  return -1;
}


/*  Convert single character alphabetic representation of nucleotide to integer i
 */
int ToNucleo (char c)
{
  c = toupper (c);
  switch (c) {
  case 'A':
    return 0;
  case 'C':
    return 1;
  case 'G':
    return 2;
  case 'T':
    return 3;
  case '-':
    return 4;
  }

  return -1;
}


/*  Returns number of possible bases for each sequence type. Bases are numbered
 * zero to NumberPossibleBases(). The number representing gap is equal to
 * NumberPossibleBases(), except for SEQTYPE_CODONQ
 */
int NumberPossibleBases (const int seqtype, const int gencode)
{
  assert (IsSeqtype (seqtype));
  assert ( seqtype!=SEQTYPE_CODONQ || IsValidGencode(gencode));


  switch (seqtype) {
  case SEQTYPE_NUCLEO:
    return 4;
  case SEQTYPE_AMINO:
    return 20;
  case SEQTYPE_CODON:
    return 64;
  case SEQTYPE_CODONQ:
    return NumberSenseCodonsInGenCode (gencode);
  }

  return -1;
}


/*  Convert a codon into Q coordinates (0...63 enumberation into one which does not
 * enumerate stop codons
 */
int CodonAsQcoord (int base, int seqtype, int gencode)
{
  assert(seqtype==SEQTYPE_CODON);
  assert(IsValidGencode(gencode));
  assert(IsValidBase(base,seqtype,gencode));

  return CodonToQcoord (base, gencode);

  return base;
}


/*  Return integer corresponding to gapchar for sequence type
 */
int GapChar (int seqtype)
{
  assert(IsSeqtype(seqtype));

  switch (seqtype) {
  case SEQTYPE_NUCLEO:
    return 4;
  case SEQTYPE_AMINO:
    return 20;
  case SEQTYPE_CODON:
  case SEQTYPE_CODONQ:
    return 64;
  }

  puts ("Valid sequence type but no gap char entry in \"GapChar\".");
  abort();
}


/*  Convert nucleotide integer into single character alphabetical code
 */
char NucleoAsChar (int a)
{
  assert(IsValidBase(a,SEQTYPE_NUCLEO,0));
  assert(a>=0 && a<=strlen(Nucleo));

  return Nucleo[a];
}

/*  Convert amino acid integer into single character alphabetical code
 */
char AminoAsChar (int a)
{
  assert(IsValidBase(a,SEQTYPE_AMINO,0));
  assert(a>=0 && a<=strlen(Amino));

  return Amino[a];
}


/*  Is sequence type valid?
 */
int IsSeqtype (const int seqtype)
{
  switch (seqtype) {
  case SEQTYPE_NUCLEO:
  case SEQTYPE_AMINO:
  case SEQTYPE_CODON:
  case SEQTYPE_CODONQ:
    return 1;
  }

  return 0;
}

/*  Is base valid for sequence type? For non-codon data, or codons in Q coord's,
 * the gencode argument in not needed and can be set to any value
 */ 
int IsValidBase ( const int base, const int seqtype, const int gencode){
  int gapchar;

  gapchar = GapChar(seqtype);
  
  if ( 0<=base  &&  (base<NumberPossibleBases(seqtype,gencode)  || base==gapchar) )
    return 1;

  return 0;
}


double *  ConvertCodonFreqsToQcoord ( const double * freqs, const int gencode){
  double * qfreqs;
  int max_codon,max_qcodon,codon,qcodon;

  assert(NULL!=freqs);
  assert(IsValidGencode(gencode));
  max_codon = NumberPossibleBases(SEQTYPE_CODON,gencode);
  max_qcodon = NumberPossibleBases(SEQTYPE_CODONQ,gencode);

  #ifndef NDEBUG
  {
    double sum = 0.;
    for ( codon=0 ; codon<max_codon ; codon++){
      assert(freqs[codon]>=0. && freqs[codon]<=1.);
      sum += freqs[codon];
    }
    assert(fabs(1.-sum)<DBL_EPSILON*max_codon);
  }
  #endif

  qfreqs = calloc ( max_qcodon,sizeof(double));
  if(NULL==qfreqs)
    return NULL;

  for ( codon=0 ; codon<max_codon; codon++){
    qcodon = CodonToQcoord (codon,gencode);
    if ( -1 != qcodon){
      qfreqs[qcodon] = freqs[codon];
    }
  }

  #ifndef NDEBUG
  {
    double sum = 0.;
    for ( qcodon=0 ; qcodon<max_qcodon ; qcodon++){
      assert(qfreqs[qcodon]>=0. && qfreqs[qcodon]<=1.);
      sum += qfreqs[qcodon];
    }
    assert(fabs(1.-sum)<DBL_EPSILON*max_qcodon);
  }
  #endif

  return qfreqs;
}
