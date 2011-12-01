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

#ifndef _BASES_H_
#define _BASES_H_

int NumberPossibleBases ( const int seq_type, const int gencode);
int CodonAsQcoord (int base, int seqtype, int gencode);
int GapChar(int seqtype);
char NucleoAsChar ( int a);
char AminoAsChar ( int a);
int ToAmino ( char c);
int ToNucleo ( char c);
int IsSeqtype ( const int seqtype);
int IsValidBase ( const int base, const int seqtype, const int gencode);


double *  ConvertCodonFreqsToQcoord ( const double * freqs, const int gencode);


#define	SEQTYPE_NUCLEO		0
#define SEQTYPE_AMINO		1
#define SEQTYPE_CODON		2
#define SEQTYPE_CODONQ		3

#endif
